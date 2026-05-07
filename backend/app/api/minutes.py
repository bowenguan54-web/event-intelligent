"""
Minutes generation, editing and signing APIs.
"""

from datetime import datetime
import hashlib
import json
from typing import List, Optional

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.meeting import (
    Meeting,
    MeetingMinutes,
    MeetingStatus,
    MinutesSignature,
    MinutesVersion,
    Transcript,
    meeting_participants,
)
from app.models.user import User
from app.schemas.schemas import (
    MinutesCreateRequest,
    MinutesInfo,
    MinutesPublishRequest,
    MinutesUpdate,
    MinutesVersionInfo,
    PolishRequest,
    PublicSignRequest,
    RejectMinutesRequest,
    ResponseBase,
    SignatureSubmit,
    TTSRequest,
)
from app.services.llm_service import generate_text
from app.api.meeting import _sync_post_process_status

router = APIRouter(tags=["minutes"])


def _get_meeting(db: Session, meeting_id: int) -> Meeting:
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    return meeting


def _get_minutes(
    db: Session,
    meeting_id: int,
    minutes_id: Optional[int] = None,
    create_if_missing: bool = False,
) -> Optional[MeetingMinutes]:
    query = db.query(MeetingMinutes).filter(MeetingMinutes.meeting_id == meeting_id)
    if minutes_id:
        minutes = query.filter(MeetingMinutes.id == minutes_id).first()
    else:
        minutes = (
            query.order_by(
                MeetingMinutes.is_primary.desc(),
                MeetingMinutes.updated_at.desc(),
                MeetingMinutes.id.desc(),
            )
            .first()
        )
    if not minutes and create_if_missing:
        minutes = MeetingMinutes(meeting_id=meeting_id, title="默认纪要", status="draft", version=1, is_primary=True)
        db.add(minutes)
        db.flush()
    return minutes


def _participant_rows(db: Session, meeting_id: int):
    return db.execute(
        sa.select(
            meeting_participants.c.user_id,
            meeting_participants.c.is_expert,
            meeting_participants.c.is_leader,
        ).where(meeting_participants.c.meeting_id == meeting_id)
    ).fetchall()


def _build_default_signers(db: Session, meeting_id: int) -> List[dict]:
    rows = _participant_rows(db, meeting_id)
    users = {user.id: user for user in db.query(User).filter(User.id.in_([r.user_id for r in rows] or [-1])).all()}

    leaders = [r for r in rows if r.is_leader]
    targets = leaders or rows[:1]
    signers = []
    for row in targets:
        user = users.get(row.user_id)
        if not user:
            continue
        signers.append(
            {
                "user_id": user.id,
                "signer_name": user.real_name,
                "signer_unit": user.department or "",
                "sign_type": "leader_review" if row.is_leader else "participant_sign",
            }
        )
    return signers


def _normalize_required_signers(
    db: Session,
    meeting_id: int,
    required_signers: Optional[List[dict]] = None,
) -> List[dict]:
    signers = required_signers or _build_default_signers(db, meeting_id)
    normalized: List[dict] = []
    seen = set()
    for signer in signers:
        signer_name = (signer.get("signer_name") or "").strip()
        signer_unit = (signer.get("signer_unit") or "").strip()
        user_id = signer.get("user_id")
        sign_type = signer.get("sign_type") or "participant_sign"
        if not signer_name and user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                signer_name = user.real_name
                signer_unit = signer_unit or (user.department or "")
        if not signer_name:
            continue
        key = (user_id or signer_name.lower(), signer_name)
        if key in seen:
            continue
        seen.add(key)
        normalized.append(
            {
                "user_id": user_id,
                "signer_name": signer_name,
                "signer_unit": signer_unit,
                "sign_type": sign_type,
            }
        )
    return normalized


def _minutes_to_payload(db: Session, minutes: Optional[MeetingMinutes], meeting_id: int) -> dict:
    if not minutes:
        return {
            "content": None,
            "status": "none",
            "signatures": [],
            "participant_count": 0,
            "review_conclusion": "",
            "minutes": None,
            "minutes_list": [],
            "required_signers": [],
        }

    signatures = (
        db.query(MinutesSignature)
        .filter(MinutesSignature.minutes_id == minutes.id)
        .order_by(MinutesSignature.signed_at.asc(), MinutesSignature.id.asc())
        .all()
    )
    participant_count = db.execute(
        sa.select(sa.func.count()).select_from(meeting_participants).where(meeting_participants.c.meeting_id == meeting_id)
    ).scalar() or 0

    minutes_list = (
        db.query(MeetingMinutes)
        .filter(MeetingMinutes.meeting_id == meeting_id)
        .order_by(MeetingMinutes.is_primary.desc(), MeetingMinutes.updated_at.desc(), MeetingMinutes.id.desc())
        .all()
    )
    required_signers = []
    if minutes.required_signers:
        try:
            required_signers = json.loads(minutes.required_signers)
        except json.JSONDecodeError:
            required_signers = []

    return {
        "minutes_id": minutes.id,
        "content": minutes.content,
        "status": minutes.status,
        "signatures": [
            {
                "id": item.id,
                "sign_step": item.sign_step,
                "sign_type": item.sign_type,
                "signer_id": item.signer_id,
                "signer_name": item.signer_name or (item.signer.real_name if item.signer else ""),
                "signer_unit": item.signer_unit,
                "opinion": item.opinion or "",
                "signed_at": item.signed_at.isoformat() if item.signed_at else "",
                "signature_image": item.signature_image,
            }
            for item in signatures
        ],
        "participant_count": participant_count,
        "review_conclusion": minutes.review_conclusion or "",
        "reject_reason": minutes.reject_reason or "",
        "minutes": MinutesInfo.model_validate(minutes).model_dump(),
        "minutes_list": [MinutesInfo.model_validate(item).model_dump() for item in minutes_list],
        "required_signers": required_signers,
    }


def _record_version(db: Session, minutes: MeetingMinutes, content: str, editor_id: Optional[int]) -> None:
    db.add(
        MinutesVersion(
            minutes_id=minutes.id,
            content=content,
            version=minutes.version,
            editor_id=editor_id,
        )
    )


async def _generate_minutes_html(meeting: Meeting, current_user: User, transcripts: List[Transcript]) -> str:
    transcript_text = "\n".join(
        f"[{item.speaker_name or '未知发言人'}] {item.text}"
        for item in transcripts
        if item.text
    ) or "（暂无转写记录）"

    system_prompt = (
        "你是专业会议纪要助手。"
        "请基于会议基本信息和转写内容生成结构清晰、正式规范的 HTML 会议纪要。"
        "输出中至少包含会议概况、讨论纪要、结论决议、待办事项。"
    )
    user_prompt = (
        f"会议标题：{meeting.title}\n"
        f"会议时间：{meeting.start_time.strftime('%Y-%m-%d %H:%M')} - "
        f"{meeting.end_time.strftime('%H:%M') if meeting.end_time else '进行中'}\n"
        f"会议地点：{meeting.location or '线上'}\n"
        f"会议主持：{current_user.real_name}\n\n"
        f"转写内容如下：\n{transcript_text}"
    )

    try:
        return await generate_text(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=4096,
        )
    except Exception as exc:
        return (
            f"<h1>{meeting.title} - 会议纪要</h1>"
            f"<h2>一、会议概况</h2>"
            f"<p><strong>时间：</strong>{meeting.start_time.strftime('%Y-%m-%d %H:%M')}</p>"
            f"<p><strong>地点：</strong>{meeting.location or '线上'}</p>"
            f"<p><strong>主持：</strong>{current_user.real_name}</p>"
            f"<p><em>AI 暂时不可用，请手动完善纪要内容。错误：{exc}</em></p>"
        )


@router.post("/api/meeting/{meeting_id}/minutes", response_model=MinutesInfo)
async def create_minutes(
    meeting_id: int,
    data: MinutesCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_meeting(db, meeting_id)
    if data.make_primary:
        db.query(MeetingMinutes).filter(MeetingMinutes.meeting_id == meeting_id).update({"is_primary": False})
    minutes = MeetingMinutes(
        meeting_id=meeting_id,
        title=(data.title or "新增纪要").strip() or "新增纪要",
        content="",
        status="draft",
        version=1,
        is_primary=data.make_primary or db.query(MeetingMinutes).filter(MeetingMinutes.meeting_id == meeting_id).count() == 0,
    )
    db.add(minutes)
    db.commit()
    db.refresh(minutes)
    return MinutesInfo.model_validate(minutes)


@router.get("/api/meeting/{meeting_id}/minutes/list", response_model=List[MinutesInfo])
async def list_minutes(
    meeting_id: int,
    db: Session = Depends(get_db),
):
    _get_meeting(db, meeting_id)
    minutes_list = (
        db.query(MeetingMinutes)
        .filter(MeetingMinutes.meeting_id == meeting_id)
        .order_by(MeetingMinutes.is_primary.desc(), MeetingMinutes.updated_at.desc(), MeetingMinutes.id.desc())
        .all()
    )
    return [MinutesInfo.model_validate(item) for item in minutes_list]


@router.post("/api/meeting/{meeting_id}/minutes/{minutes_id}/set-primary", response_model=ResponseBase)
async def set_primary_minutes(
    meeting_id: int,
    minutes_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_meeting(db, meeting_id)
    minutes = _get_minutes(db, meeting_id, minutes_id=minutes_id)
    if not minutes:
        raise HTTPException(status_code=404, detail="纪要不存在")
    db.query(MeetingMinutes).filter(MeetingMinutes.meeting_id == meeting_id).update({"is_primary": False})
    minutes.is_primary = True
    db.commit()
    return ResponseBase(message="已设置为主纪要")


@router.post("/api/meeting/{meeting_id}/minutes/generate", response_model=MinutesInfo)
async def generate_minutes(
    meeting_id: int,
    minutes_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _get_meeting(db, meeting_id)
    minutes = _get_minutes(db, meeting_id, minutes_id=minutes_id, create_if_missing=True)
    transcripts = (
        db.query(Transcript)
        .filter(Transcript.meeting_id == meeting_id)
        .order_by(Transcript.start_time.asc(), Transcript.id.asc())
        .all()
    )
    minutes.content = await _generate_minutes_html(meeting, current_user, transcripts)
    minutes.status = "draft" if minutes.status in ("none", "rejected") else minutes.status
    minutes.version = (minutes.version or 0) + 1
    minutes.updated_at = datetime.utcnow()
    _record_version(db, minutes, minutes.content or "", current_user.id)
    db.commit()
    db.refresh(minutes)
    return MinutesInfo.model_validate(minutes)


@router.put("/api/meeting/{meeting_id}/minutes", response_model=MinutesInfo)
async def update_minutes(
    meeting_id: int,
    data: MinutesUpdate,
    minutes_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_meeting(db, meeting_id)
    minutes = _get_minutes(db, meeting_id, minutes_id=minutes_id, create_if_missing=True)
    if minutes.status in ("published", "reviewing", "signed"):
        raise HTTPException(status_code=400, detail="当前纪要已发布，不可修改")

    if minutes.status == "rejected":
        minutes.status = "draft"
        minutes.reject_reason = None
    if data.title is not None:
        minutes.title = data.title.strip() or minutes.title
    minutes.content = data.content
    minutes.review_conclusion = data.review_conclusion
    minutes.version = (minutes.version or 0) + 1
    minutes.updated_at = datetime.utcnow()
    _record_version(db, minutes, data.content, current_user.id)
    db.commit()
    db.refresh(minutes)
    return MinutesInfo.model_validate(minutes)


@router.post("/api/meeting/{meeting_id}/minutes/publish", response_model=ResponseBase)
async def publish_minutes(
    meeting_id: int,
    data: Optional[MinutesPublishRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _get_meeting(db, meeting_id)
    payload = data or MinutesPublishRequest()
    minutes = _get_minutes(db, meeting_id, minutes_id=payload.minutes_id)
    if not minutes:
        raise HTTPException(status_code=404, detail="纪要不存在，请先保存纪要")
    if not (minutes.content or "").strip():
        raise HTTPException(status_code=400, detail="纪要内容为空，无法发布")
    if minutes.status == "signed":
        raise HTTPException(status_code=400, detail="纪要已完成签署")

    required_signers = _normalize_required_signers(db, meeting_id, payload.required_signers)
    if not required_signers:
        raise HTTPException(status_code=400, detail="未配置可用签字人")

    minutes.required_signers = json.dumps(required_signers, ensure_ascii=False)
    minutes.status = "published"
    minutes.reject_reason = None
    minutes.updated_at = datetime.utcnow()
    _sync_post_process_status(db, meeting)
    db.commit()
    return ResponseBase(message="纪要已发布，等待指定人员审签")


@router.post("/api/meeting/{meeting_id}/minutes/reject", response_model=ResponseBase)
async def reject_minutes(
    meeting_id: int,
    data: Optional[RejectMinutesRequest] = None,
    minutes_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
):
    meeting = _get_meeting(db, meeting_id)
    minutes = _get_minutes(db, meeting_id, minutes_id=minutes_id)
    if not minutes:
        raise HTTPException(status_code=404, detail="纪要不存在")
    if minutes.status not in ("published", "reviewing"):
        raise HTTPException(status_code=400, detail="当前纪要状态不支持驳回")

    db.query(MinutesSignature).filter(MinutesSignature.minutes_id == minutes.id).delete()
    minutes.status = "rejected"
    minutes.reject_reason = data.reason if data else None
    minutes.updated_at = datetime.utcnow()
    _sync_post_process_status(db, meeting)
    db.commit()
    return ResponseBase(message="纪要已驳回，等待修改后重新发布")


@router.post("/api/meeting/{meeting_id}/minutes/sign", response_model=ResponseBase)
async def sign_minutes(
    meeting_id: int,
    data: SignatureSubmit,
    minutes_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _get_meeting(db, meeting_id)
    minutes = _get_minutes(db, meeting_id, minutes_id=minutes_id)
    if not minutes:
        raise HTTPException(status_code=404, detail="纪要不存在")

    hash_value = hashlib.sha256(
        f"{current_user.id}:{datetime.utcnow().isoformat()}:{data.signature_image[:100]}".encode("utf-8")
    ).hexdigest()
    db.add(
        MinutesSignature(
            minutes_id=minutes.id,
            signer_id=current_user.id,
            signer_name=current_user.real_name,
            signer_unit=current_user.department,
            signature_image=data.signature_image,
            sign_step=data.sign_step,
            sign_type="draft_sign",
            hash_value=hash_value,
        )
    )
    if data.sign_step == "draft":
        minutes.status = "reviewing"
    _sync_post_process_status(db, meeting)
    db.commit()
    return ResponseBase(message="签署成功")


@router.post("/api/meeting/{meeting_id}/minutes/public-sign", response_model=ResponseBase)
async def public_sign_minutes(
    meeting_id: int,
    data: PublicSignRequest,
    minutes_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
):
    meeting = _get_meeting(db, meeting_id)
    minutes = _get_minutes(db, meeting_id, minutes_id=minutes_id)
    if not minutes:
        raise HTTPException(status_code=404, detail="纪要不存在")
    if minutes.status not in ("published", "reviewing"):
        raise HTTPException(status_code=400, detail="纪要尚未发布，不能审签")

    required_signers = _normalize_required_signers(
        db,
        meeting_id,
        json.loads(minutes.required_signers) if minutes.required_signers else None,
    )
    matched_signer = next(
        (item for item in required_signers if item.get("signer_name") == data.signer_name.strip()),
        None,
    )
    if not matched_signer:
        raise HTTPException(status_code=403, detail="当前人员不在本纪要指定审签范围内")

    existing = (
        db.query(MinutesSignature)
        .filter(
            MinutesSignature.minutes_id == minutes.id,
            MinutesSignature.sign_step == "review",
            MinutesSignature.signer_name == data.signer_name.strip(),
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="该人员已完成审签")

    hash_value = hashlib.sha256(
        f"{data.signer_name}:{datetime.utcnow().isoformat()}:{data.signature_image[:100]}".encode("utf-8")
    ).hexdigest()
    db.add(
        MinutesSignature(
            minutes_id=minutes.id,
            signer_id=matched_signer.get("user_id"),
            signer_name=data.signer_name.strip(),
            signer_unit=(data.signer_unit or matched_signer.get("signer_unit") or "").strip() or None,
            signature_image=data.signature_image,
            sign_step="review",
            sign_type=matched_signer.get("sign_type"),
            opinion=data.opinion or None,
            hash_value=hash_value,
        )
    )
    db.flush()

    if minutes.status == "published":
        minutes.status = "reviewing"

    signed_names = {
        item.signer_name
        for item in db.query(MinutesSignature)
        .filter(MinutesSignature.minutes_id == minutes.id, MinutesSignature.sign_step == "review")
        .all()
    }
    required_names = {item["signer_name"] for item in required_signers}
    if required_names and required_names.issubset(signed_names):
        minutes.status = "signed"
    _sync_post_process_status(db, meeting)

    db.commit()
    return ResponseBase(message="审签成功")


@router.post("/api/meeting/{meeting_id}/minutes/force-complete", response_model=ResponseBase)
async def force_complete_sign(
    meeting_id: int,
    minutes_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _get_meeting(db, meeting_id)
    minutes = _get_minutes(db, meeting_id, minutes_id=minutes_id)
    if not minutes:
        raise HTTPException(status_code=404, detail="纪要不存在")
    if minutes.status not in ("published", "reviewing"):
        raise HTTPException(status_code=400, detail="当前纪要状态不支持强制结束")

    minutes.status = "signed"
    minutes.updated_at = datetime.utcnow()
    # 强制结束审签后，直接将会议状态设为已结束（不经过 _sync_post_process_status）
    issue_status = (meeting.issue_review_status or "pending").strip() or "pending"
    if issue_status in ("completed", "skipped"):
        meeting.status = MeetingStatus.ARCHIVED
    else:
        meeting.status = MeetingStatus.FINISHED
    db.commit()
    return ResponseBase(message="已强制结束审签流程")


@router.delete("/api/meeting/{meeting_id}/minutes/{minutes_id}", response_model=ResponseBase)
async def delete_minutes_record(
    meeting_id: int,
    minutes_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    minutes = db.query(MeetingMinutes).filter(
        MeetingMinutes.meeting_id == meeting_id,
        MeetingMinutes.id == minutes_id,
    ).first()
    if not minutes:
        raise HTTPException(status_code=404, detail="纪要不存在")
    if minutes.status not in ("draft", "rejected"):
        raise HTTPException(status_code=400, detail="仅草稿或被驳回状态的纪要可删除")
    db.delete(minutes)
    db.commit()
    return ResponseBase(message="纪要已删除")


@router.get("/api/meeting/{meeting_id}/minutes/info")
async def get_minutes_info(
    meeting_id: int,
    minutes_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
):
    minutes = _get_minutes(db, meeting_id, minutes_id=minutes_id)
    return _minutes_to_payload(db, minutes, meeting_id)


@router.get("/api/meeting/{meeting_id}/minutes/versions", response_model=List[MinutesVersionInfo])
async def get_minutes_versions(
    meeting_id: int,
    minutes_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    minutes = _get_minutes(db, meeting_id, minutes_id=minutes_id)
    if not minutes:
        raise HTTPException(status_code=404, detail="纪要不存在")
    versions = (
        db.query(MinutesVersion)
        .filter(MinutesVersion.minutes_id == minutes.id)
        .order_by(MinutesVersion.version.desc(), MinutesVersion.id.desc())
        .all()
    )
    return [MinutesVersionInfo.model_validate(item) for item in versions]


@router.get("/api/meeting/{meeting_id}/minutes/export")
async def export_minutes(
    meeting_id: int,
    minutes_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    minutes = _get_minutes(db, meeting_id, minutes_id=minutes_id)
    if not minutes:
        raise HTTPException(status_code=404, detail="纪要不存在")
    return {
        "code": 200,
        "message": "导出功能开发中",
        "data": {
            "minutes_id": minutes.id,
            "title": minutes.title,
            "content": minutes.content,
        },
    }


@router.post("/api/ai/polish")
async def polish_text(
    data: PolishRequest,
    current_user: User = Depends(get_current_user),
):
    system_prompt = "请在保留原意的前提下，把文本润色为更正式、清晰、适合作为会议材料的表达。"
    try:
        polished = await generate_text(
            prompt=f"请润色以下文本：\n\n{data.text}",
            system_prompt=system_prompt,
            temperature=0.3,
        )
        return {"code": 200, "data": {"original": data.text, "polished": polished}}
    except Exception as exc:
        return {"code": 500, "data": {"original": data.text, "polished": data.text, "error": str(exc)}}


@router.post("/api/tts/synthesize")
async def synthesize_speech(
    data: TTSRequest,
    current_user: User = Depends(get_current_user),
):
    return {"code": 200, "message": "TTS 功能开发中", "data": {"audio_url": "", "text": data.text}}
