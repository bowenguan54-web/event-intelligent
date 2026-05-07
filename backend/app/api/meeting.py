"""
Meeting management APIs.
"""

from datetime import datetime
import json
import os
import random
import string
import uuid
from typing import List, Optional

import sqlalchemy as sa
from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.meeting import (
    Meeting,
    MeetingAttachment,
    MeetingAttachmentPermission,
    MeetingIssue,
    MeetingMinutes,
    MeetingPostOpinion,
    MeetingStatus,
    MeetingType,
    meeting_participants,
)
from app.models.user import User
from app.schemas.schemas import (
    AttachmentArchiveUpdate,
    AttachmentInfo,
    AttachmentPermissionUpdate,
    ConflictCheckRequest,
    ConflictInfo,
    IssueReviewFlowUpdate,
    MeetingCreate,
    MeetingInfo,
    MeetingIssueCreate,
    MeetingIssueInfo,
    MeetingIssueUpdate,
    MeetingListResponse,
    MeetingUpdate,
    ParticipantWithStatus,
    PostOpinionCreate,
    PostOpinionInfo,
    ResponseBase,
    SeatLayoutUpdate,
)
from app.services.llm_service import generate_text
from app.api.websocket import manager as ws_manager

router = APIRouter(prefix="/api/meeting", tags=["meeting"])


class MeetingCreateExtended(MeetingCreate):
    expert_ids: List[int] = []
    leader_id: Optional[int] = None


def _auto_update_status(meeting: Meeting, db: Session) -> bool:
    now = datetime.utcnow()
    if meeting.status == MeetingStatus.PENDING and meeting.start_time and meeting.start_time <= now:
        meeting.status = MeetingStatus.IN_PROGRESS
        db.add(meeting)
        db.flush()
        return True
    return False


def _ensure_meeting(db: Session, meeting_id: int) -> Meeting:
    meeting = db.query(Meeting).options(joinedload(Meeting.participants)).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    return meeting


def _ensure_creator(meeting: Meeting, current_user: User) -> None:
    if meeting.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有会议发起人可以执行该操作")


def _sync_post_process_status(db: Session, meeting: Meeting) -> bool:
    primary_minutes = (
        db.query(MeetingMinutes)
        .filter(MeetingMinutes.meeting_id == meeting.id)
        .order_by(MeetingMinutes.is_primary.desc(), MeetingMinutes.updated_at.desc(), MeetingMinutes.id.desc())
        .first()
    )
    primary_status = primary_minutes.status if primary_minutes else "none"
    issue_status = (meeting.issue_review_status or "pending").strip() or "pending"
    next_status = meeting.status

    if primary_status == "signed" and issue_status in ("completed", "skipped"):
        next_status = MeetingStatus.ARCHIVED  # 问题审查与纪要审签均完成 → 自动归档到会后事项管理
    elif primary_status in ("published", "reviewing", "signed"):
        next_status = MeetingStatus.SIGNING   # 纪要审签流程进行中
    elif meeting.status in (MeetingStatus.PROCESSING, MeetingStatus.SIGNING):
        next_status = MeetingStatus.PROCESSING  # 仍在会后处理中
    elif meeting.status in (MeetingStatus.FINISHED, MeetingStatus.ARCHIVED):
        next_status = meeting.status  # 已结束/已归档，不回退

    if next_status != meeting.status:
        meeting.status = next_status
        db.add(meeting)
        return True
    return False


def _participant_roles_map(db: Session, meeting_id: int) -> dict:
    rows = db.execute(
        sa.select(
            meeting_participants.c.user_id,
            meeting_participants.c.checked_in,
            meeting_participants.c.check_in_time,
            meeting_participants.c.role,
            meeting_participants.c.sort_order,
            meeting_participants.c.signature_image,
            meeting_participants.c.signature_status,
            meeting_participants.c.is_expert,
            meeting_participants.c.is_leader,
            meeting_participants.c.fee_signature_image,
            meeting_participants.c.fee_id_card,
            meeting_participants.c.fee_bank_card,
        ).where(meeting_participants.c.meeting_id == meeting_id)
    ).fetchall()
    return {row.user_id: row for row in rows}


def _sync_participants(
    db: Session,
    meeting_id: int,
    participant_ids: List[int],
    expert_ids: Optional[List[int]] = None,
    leader_id: Optional[int] = None,
) -> None:
    expert_set = set(expert_ids or [])
    existing_rows = db.execute(
        sa.select(meeting_participants.c.user_id).where(meeting_participants.c.meeting_id == meeting_id)
    ).fetchall()
    existing_ids = {row.user_id for row in existing_rows}
    new_ids = set(participant_ids)

    for removed_id in existing_ids - new_ids:
        db.execute(
            sa.delete(meeting_participants).where(
                meeting_participants.c.meeting_id == meeting_id,
                meeting_participants.c.user_id == removed_id,
            )
        )

    for idx, user_id in enumerate(participant_ids):
        values = {
            "meeting_id": meeting_id,
            "user_id": user_id,
            "sort_order": idx,
            "is_expert": user_id in expert_set or user_id == leader_id,
            "is_leader": user_id == leader_id if leader_id else False,
        }
        if user_id in existing_ids:
            db.execute(
                sa.update(meeting_participants)
                .where(
                    meeting_participants.c.meeting_id == meeting_id,
                    meeting_participants.c.user_id == user_id,
                )
                .values(
                    sort_order=idx,
                    is_expert=values["is_expert"],
                    is_leader=values["is_leader"],
                )
            )
        else:
            db.execute(sa.insert(meeting_participants).values(**values))


def _generate_meeting_code(db: Session) -> str:
    while True:
        code = "".join(random.choices(string.digits, k=6))
        if not db.query(Meeting).filter(Meeting.meeting_code == code).first():
            return code


def _parse_seat_layout(meeting: Meeting) -> dict:
    if not meeting.seat_layout:
        return {"seats": []}
    if isinstance(meeting.seat_layout, dict):
        return meeting.seat_layout
    try:
        return json.loads(meeting.seat_layout)
    except (TypeError, json.JSONDecodeError):
        raise HTTPException(status_code=500, detail="座位数据解析失败")


def _build_participant_info(user: User, row) -> ParticipantWithStatus:
    return ParticipantWithStatus(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        email=user.email,
        phone=user.phone,
        department=user.department,
        position=user.position,
        professional_title=user.professional_title,
        id_card_number=user.id_card_number,
        avatar=user.avatar,
        is_active=user.is_active,
        is_expert=user.is_expert,
        checked_in=bool(row.checked_in) if row else False,
        check_in_time=row.check_in_time if row else None,
        signature_image=row.signature_image if row else None,
        signature_status=(row.signature_status or "none") if row else "none",
        fee_signature_image=row.fee_signature_image if row else None,
        fee_id_card=row.fee_id_card if row else None,
        fee_bank_card=row.fee_bank_card if row else None,
        role=(row.role or "participant") if row else "participant",
        sort_order=row.sort_order if row else 0,
        is_expert_in_meeting=bool(row.is_expert) if row else False,
        is_leader=bool(row.is_leader) if row else False,
    )


def _filter_public_attachments(db: Session, meeting_id: int, user_id: Optional[int]) -> List[MeetingAttachment]:
    attachments = (
        db.query(MeetingAttachment)
        .options(joinedload(MeetingAttachment.permissions))
        .filter(MeetingAttachment.meeting_id == meeting_id)
        .order_by(MeetingAttachment.uploaded_at.asc(), MeetingAttachment.id.asc())
        .all()
    )
    if user_id is None:
        return attachments

    row = db.execute(
        sa.select(meeting_participants.c.checked_in).where(
            meeting_participants.c.meeting_id == meeting_id,
            meeting_participants.c.user_id == user_id,
        )
    ).first()
    if not row:
        raise HTTPException(status_code=403, detail="当前人员不在本次会议参会名单中")
    if not row.checked_in:
        raise HTTPException(status_code=403, detail="请先签到，再查看会议内容")

    visible = []
    for item in attachments:
        permission_user_ids = {permission.user_id for permission in item.permissions}
        if not permission_user_ids or user_id in permission_user_ids:
            visible.append(item)
    return visible


@router.get("/list", response_model=MeetingListResponse)
async def list_meetings(
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Meeting).options(joinedload(Meeting.participants)).filter(Meeting.status != MeetingStatus.ARCHIVED)
    if status:
        # 'processing' 过滤同时包含 PROCESSING（会后处理中）和 SIGNING（已合并）
        if status == 'processing':
            query = query.filter(Meeting.status.in_([MeetingStatus.PROCESSING, MeetingStatus.SIGNING]))
        else:
            query = query.filter(Meeting.status == status)
    if keyword:
        query = query.filter(Meeting.title.contains(keyword))
    if start_date:
        query = query.filter(Meeting.start_time >= start_date)
    if end_date:
        query = query.filter(Meeting.end_time <= end_date)

    total = query.count()
    meetings = query.order_by(Meeting.start_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    any_changed = False
    for item in meetings:
        any_changed = _auto_update_status(item, db) or any_changed
    if any_changed:
        db.commit()

    all_meetings = db.query(Meeting).all()
    for item in all_meetings:
        _auto_update_status(item, db)
    db.commit()
    status_counts = {
        "pending": sum(1 for item in all_meetings if item.status == MeetingStatus.PENDING),
        "preparing": sum(1 for item in all_meetings if item.status == MeetingStatus.PREPARING),
        "in_progress": sum(1 for item in all_meetings if item.status == MeetingStatus.IN_PROGRESS),
        "processing": sum(1 for item in all_meetings if item.status == MeetingStatus.PROCESSING),
        "finished": sum(1 for item in all_meetings if item.status == MeetingStatus.FINISHED),
        "signing": sum(1 for item in all_meetings if item.status == MeetingStatus.SIGNING),
    }
    return MeetingListResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=[MeetingInfo.model_validate(item) for item in meetings],
        status_counts=status_counts,
    )


@router.post("/create", response_model=MeetingInfo)
async def create_meeting(
    data: MeetingCreateExtended,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = Meeting(
        meeting_code=_generate_meeting_code(db),
        title=data.title,
        description=data.description,
        meeting_type=data.meeting_type or MeetingType.REGULAR,
        location=data.location,
        start_time=data.start_time,
        end_time=data.end_time,
        creator_id=current_user.id,
        seat_layout=data.seat_layout,
        has_review_fee=data.has_review_fee,
        welcome_message=data.welcome_message,
        welcome_theme=data.welcome_theme,
    )
    db.add(meeting)
    db.flush()
    _sync_participants(db, meeting.id, data.participant_ids, data.expert_ids, data.leader_id)
    db.commit()
    db.refresh(meeting)
    return MeetingInfo.model_validate(meeting)


@router.get("/current", response_model=MeetingInfo)
async def get_current_meeting(db: Session = Depends(get_db)):
    meeting = (
        db.query(Meeting)
        .options(joinedload(Meeting.participants))
        .filter(Meeting.status.in_([MeetingStatus.PENDING, MeetingStatus.PREPARING, MeetingStatus.IN_PROGRESS]))
        .order_by(Meeting.start_time.desc())
        .first()
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="当前没有可进入的会议")
    return MeetingInfo.model_validate(meeting)


@router.get("/room-conflict-check")
async def check_room_conflict(
    start_time: datetime,
    end_time: datetime,
    exclude_meeting_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Meeting).filter(
        Meeting.status.in_([MeetingStatus.PENDING, MeetingStatus.PREPARING, MeetingStatus.IN_PROGRESS]),
        Meeting.start_time < end_time,
        Meeting.end_time > start_time,
    )
    if exclude_meeting_id:
        query = query.filter(Meeting.id != exclude_meeting_id)
    conflicts = query.all()
    return [
        {
            "meeting_id": item.id,
            "title": item.title,
            "start_time": item.start_time.strftime("%Y-%m-%d %H:%M"),
            "end_time": item.end_time.strftime("%H:%M"),
        }
        for item in conflicts
    ]


@router.get("/{meeting_id}", response_model=MeetingInfo)
async def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    if _auto_update_status(meeting, db):
        db.commit()
        db.refresh(meeting)
    return MeetingInfo.model_validate(meeting)


@router.get("/{meeting_id}/participants-status", response_model=List[ParticipantWithStatus])
async def get_participants_status(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    role_map = _participant_roles_map(db, meeting_id)
    users = db.query(User).filter(User.id.in_([item.id for item in meeting.participants] or [-1])).all()
    result = [_build_participant_info(user, role_map.get(user.id)) for user in users]
    result.sort(key=lambda item: (item.sort_order, item.id))
    return result


@router.put("/{meeting_id}/participants-order")
async def update_participants_order(
    meeting_id: int,
    user_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    _ensure_creator(meeting, current_user)
    for idx, user_id in enumerate(user_ids):
        db.execute(
            sa.update(meeting_participants)
            .where(
                meeting_participants.c.meeting_id == meeting_id,
                meeting_participants.c.user_id == user_id,
            )
            .values(sort_order=idx)
        )
    db.commit()
    return {"detail": "排序已更新"}


@router.get("/{meeting_id}/attachments", response_model=List[AttachmentInfo])
async def list_attachments(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_meeting(db, meeting_id)
    attachments = (
        db.query(MeetingAttachment)
        .filter(MeetingAttachment.meeting_id == meeting_id)
        .order_by(MeetingAttachment.uploaded_at.asc(), MeetingAttachment.id.asc())
        .all()
    )
    return [AttachmentInfo.model_validate(item) for item in attachments]


@router.put("/{meeting_id}/attachments/{attachment_id}/permissions", response_model=ResponseBase)
async def update_attachment_permissions(
    meeting_id: int,
    attachment_id: int,
    data: AttachmentPermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    _ensure_creator(meeting, current_user)
    attachment = (
        db.query(MeetingAttachment)
        .options(joinedload(MeetingAttachment.permissions))
        .filter(MeetingAttachment.id == attachment_id, MeetingAttachment.meeting_id == meeting_id)
        .first()
    )
    if not attachment:
        raise HTTPException(status_code=404, detail="会议材料不存在")

    db.query(MeetingAttachmentPermission).filter(MeetingAttachmentPermission.attachment_id == attachment_id).delete()
    for user_id in set(data.user_ids or []):
        db.add(MeetingAttachmentPermission(attachment_id=attachment_id, user_id=user_id))
    db.commit()
    return ResponseBase(message="材料查看权限已更新")


@router.put("/{meeting_id}/attachments/archive", response_model=ResponseBase)
async def update_attachment_archive_selection(
    meeting_id: int,
    data: AttachmentArchiveUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    _ensure_creator(meeting, current_user)
    selected_ids = set(data.attachment_ids or [])
    attachments = db.query(MeetingAttachment).filter(MeetingAttachment.meeting_id == meeting_id).all()
    for item in attachments:
        item.is_archived = item.id in selected_ids
    db.commit()
    return ResponseBase(message="归档材料范围已更新")


@router.get("/attachment/{attachment_id}/download")
async def download_attachment(attachment_id: int, db: Session = Depends(get_db)):
    attachment = db.query(MeetingAttachment).filter(MeetingAttachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="附件不存在")
    if not os.path.exists(attachment.file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(
        attachment.file_path,
        filename=attachment.filename,
        media_type=attachment.file_type or "application/octet-stream",
    )


@router.post("/{meeting_id}/start", response_model=MeetingInfo)
async def start_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    _ensure_creator(meeting, current_user)
    if meeting.status not in [MeetingStatus.PENDING, MeetingStatus.PREPARING]:
        raise HTTPException(status_code=400, detail="当前会议状态不允许开始")
    meeting.status = MeetingStatus.IN_PROGRESS
    db.commit()
    db.refresh(meeting)
    return MeetingInfo.model_validate(meeting)


@router.post("/{meeting_id}/prepare", response_model=MeetingInfo)
async def prepare_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    _ensure_creator(meeting, current_user)
    if meeting.status != MeetingStatus.PENDING:
        raise HTTPException(status_code=400, detail="只有待开始会议才能进入准备阶段")
    meeting.status = MeetingStatus.PREPARING
    db.commit()
    db.refresh(meeting)
    return MeetingInfo.model_validate(meeting)


@router.post("/{meeting_id}/end", response_model=MeetingInfo)
async def end_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    _ensure_creator(meeting, current_user)
    if meeting.status not in [MeetingStatus.PENDING, MeetingStatus.PREPARING, MeetingStatus.IN_PROGRESS]:
        raise HTTPException(status_code=400, detail="当前会议状态不能结束")
    # 进入会后处理阶段，等待问题审查与纪要审签均完成后才标记为已结束
    meeting.status = MeetingStatus.PROCESSING
    db.commit()
    db.refresh(meeting)
    return MeetingInfo.model_validate(meeting)


@router.get("/by-code/{code}", response_model=MeetingInfo)
async def get_meeting_by_code(code: str, db: Session = Depends(get_db)):
    meeting = db.query(Meeting).options(joinedload(Meeting.participants)).filter(Meeting.meeting_code == code).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="未找到对应会议，请检查会议号")
    return MeetingInfo.model_validate(meeting)


@router.get("/{meeting_id}/seat/{seat_id}")
async def get_seat_person(meeting_id: int, seat_id: int, db: Session = Depends(get_db)):
    meeting = _ensure_meeting(db, meeting_id)
    layout = _parse_seat_layout(meeting)
    target = next((seat for seat in layout.get("seats", []) if seat.get("id") == seat_id and seat.get("userId")), None)
    if not target:
        raise HTTPException(status_code=404, detail="该座位未安排人员")
    user = db.query(User).filter(User.id == target["userId"]).first()
    row = db.execute(
        sa.select(meeting_participants).where(
            meeting_participants.c.meeting_id == meeting_id,
            meeting_participants.c.user_id == target["userId"],
        )
    ).first()
    return {
        "seatId": seat_id,
        "seatLabel": target.get("label", str(seat_id)),
        "userId": target["userId"],
        "userName": user.real_name if user else target.get("userName", ""),
        "department": user.department if user else "",
        "professionalTitle": user.professional_title if user else "",
        "position": user.position if user else "",
        "isExpert": bool(row.is_expert) if row else False,
        "isLeader": bool(row.is_leader) if row else False,
    }


@router.put("/{meeting_id}/seat-layout", response_model=ResponseBase)
async def update_seat_layout(
    meeting_id: int,
    data: SeatLayoutUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    _ensure_creator(meeting, current_user)
    if meeting.status not in [MeetingStatus.PENDING, MeetingStatus.PREPARING]:
        raise HTTPException(status_code=400, detail="仅待开始或准备中的会议支持调整座位")
    meeting.seat_layout = data.seat_layout
    db.commit()
    return ResponseBase(message="座位安排已更新")


@router.get("/{meeting_id}/public", response_model=MeetingInfo)
async def get_meeting_public(meeting_id: int, db: Session = Depends(get_db)):
    meeting = _ensure_meeting(db, meeting_id)
    return MeetingInfo.model_validate(meeting)


@router.get("/{meeting_id}/public-participants")
async def get_public_participants(meeting_id: int, db: Session = Depends(get_db)):
    meeting = _ensure_meeting(db, meeting_id)
    role_map = _participant_roles_map(db, meeting_id)
    users = db.query(User).filter(User.id.in_([item.id for item in meeting.participants] or [-1])).all()
    result = []
    for user in users:
        row = role_map.get(user.id)
        result.append(
            {
                "id": user.id,
                "real_name": user.real_name,
                "department": user.department,
                "position": user.position,
                "professional_title": user.professional_title,
                "id_card_number": user.id_card_number,
                "checked_in": bool(row.checked_in) if row else False,
                "check_in_time": row.check_in_time.isoformat() if row and row.check_in_time else None,
                "role": (row.role or "participant") if row else "participant",
                "signature_image": row.signature_image if row else None,
                "signature_status": (row.signature_status or "none") if row else "none",
                "fee_signature_image": row.fee_signature_image if row else None,
                "fee_id_card": row.fee_id_card if row else None,
                "fee_bank_card": row.fee_bank_card if row else None,
                "is_expert": bool(row.is_expert) if row else False,
                "is_leader": bool(row.is_leader) if row else False,
            }
        )
    result.sort(key=lambda item: role_map.get(item["id"]).sort_order if role_map.get(item["id"]) else 0)
    return result


@router.post("/{meeting_id}/terminal-checkin")
async def terminal_checkin(meeting_id: int, user_id: int, db: Session = Depends(get_db)):
    row = db.execute(
        sa.select(meeting_participants).where(
            meeting_participants.c.meeting_id == meeting_id,
            meeting_participants.c.user_id == user_id,
        )
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="未找到该参会人员")
    db.execute(
        sa.update(meeting_participants)
        .where(
            meeting_participants.c.meeting_id == meeting_id,
            meeting_participants.c.user_id == user_id,
        )
        .values(checked_in=True, check_in_time=datetime.utcnow())
    )
    db.commit()
    # 通过 WebSocket 实时通知会议室签到状态变化
    await ws_manager.broadcast(meeting_id, {
        "type": "checkin",
        "user_id": user_id,
        "checked_in": True,
    })
    return {"message": "签到成功"}


@router.post("/{meeting_id}/fee-sign")
async def terminal_fee_sign(
    meeting_id: int,
    user_id: int = Body(..., embed=True),
    fee_signature_image: str = Body(..., embed=True),
    fee_id_card: str = Body("", embed=True),
    fee_bank_card: str = Body("", embed=True),
    db: Session = Depends(get_db),
):
    row = db.execute(
        sa.select(meeting_participants).where(
            meeting_participants.c.meeting_id == meeting_id,
            meeting_participants.c.user_id == user_id,
        )
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="未找到该参会人员")
    db.execute(
        sa.update(meeting_participants)
        .where(
            meeting_participants.c.meeting_id == meeting_id,
            meeting_participants.c.user_id == user_id,
        )
        .values(
            fee_signature_image=fee_signature_image,
            fee_id_card=fee_id_card,
            fee_bank_card=fee_bank_card,
        )
    )
    db.commit()
    return {"message": "评审费签名成功"}


@router.get("/{meeting_id}/public-attachments")
async def get_public_attachments(
    meeting_id: int,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    _ensure_meeting(db, meeting_id)
    attachments = _filter_public_attachments(db, meeting_id, user_id)
    return [AttachmentInfo.model_validate(item) for item in attachments]


@router.put("/{meeting_id}", response_model=MeetingInfo)
async def update_meeting(
    meeting_id: int,
    data: MeetingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    _ensure_creator(meeting, current_user)
    if meeting.status != MeetingStatus.PENDING:
        raise HTTPException(status_code=400, detail="仅未开始会议可编辑")

    update_data = data.model_dump(exclude_unset=True)
    participant_ids = update_data.pop("participant_ids", None)
    expert_ids = update_data.pop("expert_ids", None)
    leader_id = update_data.pop("leader_id", None)
    for key, value in update_data.items():
        setattr(meeting, key, value)

    if participant_ids is not None:
        _sync_participants(db, meeting_id, participant_ids, expert_ids, leader_id)
    elif expert_ids is not None or leader_id is not None:
        current_ids = [item.id for item in meeting.participants]
        _sync_participants(db, meeting_id, current_ids, expert_ids, leader_id)

    db.commit()
    db.refresh(meeting)
    return MeetingInfo.model_validate(meeting)


@router.delete("/{meeting_id}", response_model=ResponseBase)
async def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    _ensure_creator(meeting, current_user)
    if meeting.status in [MeetingStatus.IN_PROGRESS, MeetingStatus.SIGNING]:
        raise HTTPException(status_code=400, detail="进行中的会议不可删除")
    db.delete(meeting)
    db.commit()
    return ResponseBase(message="删除成功")


@router.post("/conflict-check", response_model=List[ConflictInfo])
async def check_conflicts(
    data: ConflictCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conflicts = []
    for user_id in data.participant_ids:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            continue
        query = (
            db.query(Meeting)
            .join(meeting_participants, meeting_participants.c.meeting_id == Meeting.id)
            .filter(
                meeting_participants.c.user_id == user_id,
                Meeting.status.in_([MeetingStatus.PENDING, MeetingStatus.PREPARING, MeetingStatus.IN_PROGRESS]),
                Meeting.start_time < data.end_time,
                Meeting.end_time > data.start_time,
            )
        )
        if data.exclude_meeting_id:
            query = query.filter(Meeting.id != data.exclude_meeting_id)
        for item in query.all():
            conflicts.append(
                ConflictInfo(
                    user_id=user_id,
                    user_name=user.real_name,
                    conflict_meeting=item.title,
                    conflict_time=f"{item.start_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')}",
                )
            )
    return conflicts


@router.post("/{meeting_id}/upload")
async def upload_attachment(
    meeting_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    _ensure_creator(meeting, current_user)
    file_ext = os.path.splitext(file.filename)[1]
    file_name = f"{uuid.uuid4().hex}{file_ext}"
    file_dir = os.path.join(settings.UPLOAD_DIR, str(meeting_id))
    os.makedirs(file_dir, exist_ok=True)
    file_path = os.path.join(file_dir, file_name)
    content = await file.read()
    with open(file_path, "wb") as file_handle:
        file_handle.write(content)

    attachment = MeetingAttachment(
        meeting_id=meeting_id,
        filename=file.filename,
        file_path=file_path,
        file_size=len(content),
        file_type=file.content_type,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return {
        "code": 200,
        "message": "上传成功",
        "data": AttachmentInfo.model_validate(attachment).model_dump(),
    }


@router.post("/{meeting_id}/agenda/generate", response_model=ResponseBase)
async def generate_agenda(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    start_str = meeting.start_time.strftime("%Y-%m-%d %H:%M") if meeting.start_time else ""
    end_str = meeting.end_time.strftime("%H:%M") if meeting.end_time else ""
    prompt = (
        f"会议标题：{meeting.title}\n"
        f"会议时间：{start_str} - {end_str}\n"
        f"会议地点：{meeting.location or '线上'}\n"
        f"会议简介：{meeting.description or '无'}\n"
        "请生成一份结构清晰的 HTML 会议议程。"
    )
    try:
        meeting.agenda = await generate_text(
            prompt=prompt,
            system_prompt="你是会议议程助手，请输出正式、简洁的 HTML 议程。",
            temperature=0.4,
        )
    except Exception:
        meeting.agenda = (
            f"<h2>{meeting.title} - 会议议程</h2>"
            "<ol><li>会议签到与准备</li><li>议题汇报</li><li>集中讨论</li><li>形成结论</li><li>布置会后事项</li></ol>"
        )
    db.commit()
    return ResponseBase(message="议程生成成功")


@router.post("/{meeting_id}/checkin-sheet/generate")
async def generate_checkin_sheet(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    rows = "".join(
        f"<tr><td>{idx}</td><td>{participant.real_name}</td><td>{participant.department or ''}</td><td></td><td></td></tr>"
        for idx, participant in enumerate(meeting.participants, 1)
    )
    html = (
        f"<h2>{meeting.title} - 签到表</h2>"
        f"<p>时间：{meeting.start_time.strftime('%Y-%m-%d %H:%M')}</p>"
        f"<p>地点：{meeting.location or '待定'}</p>"
        "<table border='1' cellpadding='8' cellspacing='0' style='width:100%;border-collapse:collapse;'>"
        "<thead><tr><th>序号</th><th>姓名</th><th>单位</th><th>签到时间</th><th>签名</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )
    return {"code": 200, "message": "签到表生成成功", "data": {"html": html}}


@router.get("/{meeting_id}/issues", response_model=List[MeetingIssueInfo])
async def list_issues(meeting_id: int, db: Session = Depends(get_db)):
    """管理端：只返回已提交的问题记录"""
    issues = (
        db.query(MeetingIssue)
        .filter(MeetingIssue.meeting_id == meeting_id, MeetingIssue.submitted == True)  # noqa: E712
        .order_by(MeetingIssue.created_at.asc(), MeetingIssue.id.asc())
        .all()
    )
    return [MeetingIssueInfo.model_validate(item) for item in issues]


@router.get("/{meeting_id}/terminal-issues", response_model=List[MeetingIssueInfo])
async def list_terminal_issues(meeting_id: int, reporter_name: Optional[str] = None, db: Session = Depends(get_db)):
    """会议终端：返回当前专家自己录入的所有问题（含未提交）"""
    query = db.query(MeetingIssue).filter(MeetingIssue.meeting_id == meeting_id)
    if reporter_name:
        query = query.filter(MeetingIssue.reporter_name == reporter_name)
    issues = query.order_by(MeetingIssue.created_at.asc(), MeetingIssue.id.asc()).all()
    return [MeetingIssueInfo.model_validate(item) for item in issues]


@router.post("/{meeting_id}/issues", response_model=MeetingIssueInfo)
async def create_issue(meeting_id: int, data: MeetingIssueCreate, db: Session = Depends(get_db)):
    _ensure_meeting(db, meeting_id)
    issue = MeetingIssue(
        meeting_id=meeting_id,
        content=data.content,
        reporter_name=data.reporter_name,
        submitted=bool(data.submitted),
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return MeetingIssueInfo.model_validate(issue)


@router.put("/{meeting_id}/issues/{issue_id}", response_model=MeetingIssueInfo)
async def update_issue(
    meeting_id: int,
    issue_id: int,
    data: MeetingIssueUpdate,
    db: Session = Depends(get_db),
):
    issue = db.query(MeetingIssue).filter(MeetingIssue.id == issue_id, MeetingIssue.meeting_id == meeting_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="问题不存在")
    if data.content is not None:
        issue.content = data.content
    if data.status is not None:
        issue.status = data.status
    if data.response is not None:
        issue.response = data.response
    if data.proofread is not None:
        issue.proofread = data.proofread
    if data.archived is not None:
        issue.archived = data.archived
    issue.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(issue)
    return MeetingIssueInfo.model_validate(issue)


@router.post("/{meeting_id}/issue-review/status", response_model=MeetingInfo)
async def update_issue_review_status(
    meeting_id: int,
    data: IssueReviewFlowUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    _ensure_creator(meeting, current_user)

    next_status = (data.issue_review_status or "").strip()
    if next_status not in {"pending", "completed", "skipped"}:
        raise HTTPException(status_code=400, detail="问题审查状态无效")

    if next_status == "completed":
        remaining = (
            db.query(MeetingIssue)
            .filter(MeetingIssue.meeting_id == meeting_id, MeetingIssue.archived != True)  # noqa: E712
            .count()
        )
        if remaining > 0:
            raise HTTPException(status_code=400, detail="仍有未归档的问题，请先归档或选择跳过问题审查")

    meeting.issue_review_status = next_status
    if data.issue_review_require_sign is not None:
        meeting.issue_review_require_sign = bool(data.issue_review_require_sign)
    _sync_post_process_status(db, meeting)
    db.commit()
    db.refresh(meeting)
    return MeetingInfo.model_validate(meeting)


@router.post("/{meeting_id}/issues/{issue_id}/submit")
async def submit_issue(meeting_id: int, issue_id: int, db: Session = Depends(get_db)):
    """会议终端：提交问题记录到管理端。提交后不可删除，且问题审查完成后不再接受提交。"""
    meeting = _ensure_meeting(db, meeting_id)
    if meeting.issue_review_status in ("completed", "skipped"):
        raise HTTPException(status_code=400, detail="问题审查已结束，不支持提交新问题")
    issue = db.query(MeetingIssue).filter(MeetingIssue.id == issue_id, MeetingIssue.meeting_id == meeting_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="问题不存在")
    if issue.submitted:
        return {"detail": "已提交"}
    issue.submitted = True
    issue.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(issue)
    return MeetingIssueInfo.model_validate(issue)


@router.delete("/{meeting_id}/issues/{issue_id}")
async def delete_issue(meeting_id: int, issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(MeetingIssue).filter(MeetingIssue.id == issue_id, MeetingIssue.meeting_id == meeting_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="问题不存在")
    if issue.submitted:
        raise HTTPException(status_code=400, detail="已提交的问题不可删除")
    db.delete(issue)
    db.commit()
    return {"detail": "删除成功"}


@router.get("/{meeting_id}/post-opinions", response_model=List[PostOpinionInfo])
async def list_post_opinions(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_meeting(db, meeting_id)
    opinions = (
        db.query(MeetingPostOpinion)
        .filter(MeetingPostOpinion.meeting_id == meeting_id)
        .order_by(MeetingPostOpinion.created_at.desc(), MeetingPostOpinion.id.desc())
        .all()
    )
    return [PostOpinionInfo.model_validate(item) for item in opinions]


@router.post("/{meeting_id}/post-opinions", response_model=PostOpinionInfo)
async def create_post_opinion(
    meeting_id: int,
    data: PostOpinionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_meeting(db, meeting_id)
    opinion = MeetingPostOpinion(meeting_id=meeting_id, **data.model_dump())
    db.add(opinion)
    db.commit()
    db.refresh(opinion)
    return PostOpinionInfo.model_validate(opinion)


@router.post("/{meeting_id}/public-post-opinions", response_model=PostOpinionInfo)
async def create_public_post_opinion(
    meeting_id: int,
    data: PostOpinionCreate,
    db: Session = Depends(get_db),
):
    _ensure_meeting(db, meeting_id)
    opinion = MeetingPostOpinion(meeting_id=meeting_id, **data.model_dump())
    db.add(opinion)
    db.commit()
    db.refresh(opinion)
    return PostOpinionInfo.model_validate(opinion)


@router.post("/{meeting_id}/public-ai-qa")
async def public_ai_qa(meeting_id: int, data: dict, db: Session = Depends(get_db)):
    meeting = _ensure_meeting(db, meeting_id)
    question = (data.get("question") or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")
    prompt = (
        f"会议名称：{meeting.title}\n"
        f"会议类型：{meeting.meeting_type}\n"
        f"会议地点：{meeting.location or '线上'}\n"
        f"会议说明：{meeting.description or '无'}\n"
        f"欢迎词：{meeting.welcome_message or '无'}\n\n"
        f"用户问题：{question}"
    )
    try:
        answer = await generate_text(
            prompt=prompt,
            system_prompt="你是会议智能问答助手，请基于给定的会议信息进行回答，不确定时明确说明。",
            temperature=0.4,
        )
    except Exception as exc:
        answer = f"智能问答暂时不可用：{exc}"
    return {"code": 200, "data": {"answer": answer, "sources": []}}


@router.post("/{meeting_id}/terminal-sign")
async def terminal_sign(
    meeting_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    signature_image: str = Body("", embed=True),
):
    row = db.execute(
        sa.select(meeting_participants).where(
            meeting_participants.c.meeting_id == meeting_id,
            meeting_participants.c.user_id == user_id,
        )
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="未找到该参会人员")
    db.execute(
        sa.update(meeting_participants)
        .where(
            meeting_participants.c.meeting_id == meeting_id,
            meeting_participants.c.user_id == user_id,
        )
        .values(
            checked_in=True,
            check_in_time=datetime.utcnow(),
            signature_image=signature_image,
            signature_status="signed",
        )
    )
    db.commit()
    return {"message": "签到签名成功"}


@router.post("/{meeting_id}/signature-rollback")
async def signature_rollback(
    meeting_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    _ensure_creator(meeting, current_user)
    db.execute(
        sa.update(meeting_participants)
        .where(
            meeting_participants.c.meeting_id == meeting_id,
            meeting_participants.c.user_id == user_id,
        )
        .values(
            signature_image=None,
            signature_status="rejected",
            checked_in=False,
            check_in_time=None,
        )
    )
    db.commit()
    return {"message": "已退回，等待重新签到"}


@router.put("/{meeting_id}/participants-roles")
async def update_participants_roles(
    meeting_id: int,
    expert_ids: List[int] = [],
    leader_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    _ensure_creator(meeting, current_user)
    participant_ids = [item.id for item in meeting.participants]
    _sync_participants(db, meeting_id, participant_ids, expert_ids, leader_id)
    db.commit()
    return {"detail": "角色更新成功"}
