"""
Archive and post-meeting management APIs.
"""

from datetime import datetime
import json
import re
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.meeting import (
    Meeting,
    MeetingAttachment,
    MeetingIssue,
    MeetingKeypoint,
    MeetingMinutes,
    MeetingPostOpinion,
    MeetingStatus,
    MinutesSignature,
    Transcript,
    meeting_participants,
)
from app.models.todo import TodoItem, TodoStatus
from app.models.user import User
from app.schemas.schemas import ArchiveSearchRequest, BatchExportRequest
from app.services.llm_service import generate_text

router = APIRouter(prefix="/api/archive", tags=["archive"])


def _ensure_meeting(db: Session, meeting_id: int) -> Meeting:
    meeting = (
        db.query(Meeting)
        .options(joinedload(Meeting.participants))
        .filter(Meeting.id == meeting_id)
        .first()
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    return meeting


def _todo_dict(todo: TodoItem, db: Session) -> dict:
    assignee = db.query(User).filter(User.id == todo.assignee_id).first() if todo.assignee_id else None
    return {
        "id": todo.id,
        "title": todo.title,
        "description": todo.description or "",
        "status": todo.status,
        "priority": todo.priority,
        "due_date": todo.due_date.strftime("%Y-%m-%d") if todo.due_date else None,
        "completed_at": todo.completed_at.strftime("%Y-%m-%d") if todo.completed_at else None,
        "assignee_id": todo.assignee_id,
        "assignee_name": assignee.real_name if assignee else "未指定",
        "flow_binding_id": todo.flow_binding_id,
        "source_minutes_section": getattr(todo, "source_minutes_section", None),
    }


def _role_map(db: Session, meeting_id: int) -> dict:
    rows = db.execute(
        meeting_participants.select().where(meeting_participants.c.meeting_id == meeting_id)
    ).fetchall()
    return {row.user_id: row for row in rows}


def _minutes_payload(minutes_list: list[MeetingMinutes]) -> list[dict]:
    payload = []
    for minutes in minutes_list:
        payload.append(
            {
                "id": minutes.id,
                "title": minutes.title,
                "status": minutes.status,
                "version": minutes.version,
                "is_primary": minutes.is_primary,
                "review_conclusion": minutes.review_conclusion,
                "required_signers": json.loads(minutes.required_signers) if minutes.required_signers else [],
                "created_at": minutes.created_at.isoformat() if minutes.created_at else None,
                "updated_at": minutes.updated_at.isoformat() if minutes.updated_at else None,
                "signatures": [
                    {
                        "id": sign.id,
                        "signer_id": sign.signer_id,
                        "signer_name": sign.signer_name or (sign.signer.real_name if sign.signer else ""),
                        "signer_unit": sign.signer_unit,
                        "sign_step": sign.sign_step,
                        "sign_type": sign.sign_type,
                        "opinion": sign.opinion,
                        "signed_at": sign.signed_at.isoformat() if sign.signed_at else None,
                    }
                    for sign in sorted(minutes.signatures, key=lambda item: (item.signed_at or datetime.min, item.id))
                ],
            }
        )
    return payload


@router.post("/search")
async def search_archives(
    data: ArchiveSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Meeting).options(joinedload(Meeting.participants)).filter(Meeting.status == MeetingStatus.ARCHIVED)
    if data.keyword:
        query = query.filter(Meeting.title.contains(data.keyword))
    if data.meeting_type:
        query = query.filter(Meeting.meeting_type == data.meeting_type)
    if data.start_date:
        query = query.filter(Meeting.start_time >= data.start_date)
    if data.end_date:
        query = query.filter(Meeting.end_time <= data.end_date)
    total = query.count()
    meetings = query.order_by(Meeting.start_time.desc()).offset((data.page - 1) * data.page_size).limit(data.page_size).all()
    return {
        "code": 200,
        "total": total,
        "page": data.page,
        "page_size": data.page_size,
        "data": [
            {
                "id": meeting.id,
                "title": meeting.title,
                "meeting_type": meeting.meeting_type,
                "start_time": meeting.start_time.isoformat(),
                "end_time": meeting.end_time.isoformat() if meeting.end_time else None,
                "location": meeting.location,
                "summary": meeting.summary or meeting.description or "",
                "participants": [
                    {
                        "id": user.id,
                        "real_name": user.real_name,
                        "department": user.department,
                    }
                    for user in meeting.participants
                ],
            }
            for meeting in meetings
        ],
    }


@router.get("/{meeting_id}/detail")
async def get_archive_detail(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    role_map = _role_map(db, meeting_id)
    participants = []
    for user in meeting.participants:
        row = role_map.get(user.id)
        participants.append(
            {
                "id": user.id,
                "real_name": user.real_name,
                "department": user.department,
                "position": user.position,
                "professional_title": user.professional_title,
                "is_leader": bool(row.is_leader) if row else False,
                "is_expert_in_meeting": bool(row.is_expert) if row else False,
            }
        )
    return {
        "code": 200,
        "data": {
            "id": meeting.id,
            "title": meeting.title,
            "meeting_type": meeting.meeting_type,
            "status": meeting.status,
            "location": meeting.location,
            "start_time": meeting.start_time.isoformat(),
            "end_time": meeting.end_time.isoformat() if meeting.end_time else None,
            "description": meeting.description,
            "agenda": meeting.agenda,
            "participants": participants,
        },
    }


@router.post("/batch-export")
async def batch_export(
    data: BatchExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {"code": 200, "message": "导出任务已创建", "data": {"task_id": uuid.uuid4().hex}}


@router.get("/export-status/{task_id}")
async def get_export_status(task_id: str, current_user: User = Depends(get_current_user)):
    return {
        "code": 200,
        "data": {
            "task_id": task_id,
            "status": "processing",
            "progress": 50,
            "download_url": None,
        },
    }


@router.get("/list")
async def list_archived_meetings(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    keyword: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Meeting).options(joinedload(Meeting.participants)).filter(Meeting.status == MeetingStatus.ARCHIVED)
    if keyword:
        query = query.filter(Meeting.title.contains(keyword))
    if start_date:
        query = query.filter(Meeting.start_time >= start_date)
    if end_date:
        query = query.filter(Meeting.end_time <= end_date)

    total = query.count()
    all_archived = query.all()
    all_todos = (
        db.query(TodoItem).filter(TodoItem.meeting_id.in_([meeting.id for meeting in all_archived] or [-1])).all()
        if all_archived
        else []
    )
    overview = {
        "total": total,
        "todo_total": len(all_todos),
        "todo_completed": sum(1 for todo in all_todos if todo.status == TodoStatus.COMPLETED),
        "completion_rate": round(
            sum(1 for todo in all_todos if todo.status == TodoStatus.COMPLETED) / len(all_todos) * 100, 1
        )
        if all_todos
        else 0,
    }

    meetings = query.order_by(Meeting.start_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for meeting in meetings:
        todos = db.query(TodoItem).filter(TodoItem.meeting_id == meeting.id).all()
        todo_total = len(todos)
        todo_completed = sum(1 for todo in todos if todo.status == TodoStatus.COMPLETED)
        result.append(
            {
                "id": meeting.id,
                "title": meeting.title,
                "meeting_type": meeting.meeting_type,
                "start_time": meeting.start_time.isoformat(),
                "end_time": meeting.end_time.isoformat() if meeting.end_time else None,
                "location": meeting.location or "",
                "summary": meeting.summary or "",
                "participants": [
                    {"id": user.id, "real_name": user.real_name, "department": user.department}
                    for user in meeting.participants
                ],
                "participants_count": len(meeting.participants),
                "todo_total": todo_total,
                "todo_completed": todo_completed,
                "completion_rate": round(todo_completed / todo_total * 100, 1) if todo_total else None,
            }
        )
    return {
        "code": 200,
        "total": total,
        "page": page,
        "page_size": page_size,
        "overview": overview,
        "data": result,
    }


@router.get("/{meeting_id}/full-detail")
async def get_archived_full_detail(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    role_map = _role_map(db, meeting_id)
    todos = db.query(TodoItem).filter(TodoItem.meeting_id == meeting_id).order_by(TodoItem.created_at.asc()).all()
    keypoints = db.query(MeetingKeypoint).filter(MeetingKeypoint.meeting_id == meeting_id).order_by(MeetingKeypoint.sort_order.asc()).all()
    issues = db.query(MeetingIssue).filter(MeetingIssue.meeting_id == meeting_id).order_by(MeetingIssue.created_at.asc()).all()
    transcripts = db.query(Transcript).filter(Transcript.meeting_id == meeting_id).order_by(Transcript.start_time.asc(), Transcript.id.asc()).all()
    attachments = (
        db.query(MeetingAttachment)
        .filter(MeetingAttachment.meeting_id == meeting_id)
        .order_by(MeetingAttachment.uploaded_at.asc(), MeetingAttachment.id.asc())
        .all()
    )
    opinions = (
        db.query(MeetingPostOpinion)
        .filter(MeetingPostOpinion.meeting_id == meeting_id)
        .order_by(MeetingPostOpinion.created_at.desc(), MeetingPostOpinion.id.desc())
        .all()
    )
    minutes_list = (
        db.query(MeetingMinutes)
        .options(joinedload(MeetingMinutes.signatures))
        .filter(MeetingMinutes.meeting_id == meeting_id)
        .order_by(MeetingMinutes.is_primary.desc(), MeetingMinutes.updated_at.desc(), MeetingMinutes.id.desc())
        .all()
    )
    primary_minutes = next((item for item in minutes_list if item.is_primary), minutes_list[0] if minutes_list else None)

    participants = []
    for user in meeting.participants:
        row = role_map.get(user.id)
        participants.append(
            {
                "id": user.id,
                "real_name": user.real_name,
                "department": user.department,
                "position": user.position,
                "professional_title": user.professional_title,
                "is_leader": bool(row.is_leader) if row else False,
                "is_expert_in_meeting": bool(row.is_expert) if row else False,
            }
        )

    checkin_records = []
    for user in meeting.participants:
        row = role_map.get(user.id)
        if not row:
            continue
        checkin_records.append(
            {
                "id": user.id,
                "real_name": user.real_name,
                "department": user.department,
                "position": user.position,
                "professional_title": user.professional_title,
                "is_expert": bool(row.is_expert),
                "is_leader": bool(row.is_leader),
                "checked_in": bool(row.checked_in),
                "checkin_time": row.check_in_time.strftime("%H:%M") if row.check_in_time else None,
                "signature": row.signature_image,
                "fee_signature_image": row.fee_signature_image,
                "fee_id_card": row.fee_id_card,
                "fee_bank_card": row.fee_bank_card,
            }
        )

    sign_records = (
        db.query(MinutesSignature)
        .join(MeetingMinutes, MeetingMinutes.id == MinutesSignature.minutes_id)
        .filter(MeetingMinutes.meeting_id == meeting_id)
        .order_by(MinutesSignature.signed_at.asc(), MinutesSignature.id.asc())
        .all()
    )
    completed = sum(1 for todo in todos if todo.status == TodoStatus.COMPLETED)
    in_progress = sum(1 for todo in todos if todo.status == TodoStatus.IN_PROGRESS)
    pending = sum(1 for todo in todos if todo.status == TodoStatus.PENDING)
    overdue = sum(1 for todo in todos if todo.status == TodoStatus.OVERDUE)

    return {
        "code": 200,
        "data": {
            "id": meeting.id,
            "title": meeting.title,
            "meeting_type": meeting.meeting_type,
            "status": meeting.status,
            "location": meeting.location,
            "start_time": meeting.start_time.isoformat(),
            "end_time": meeting.end_time.isoformat() if meeting.end_time else None,
            "description": meeting.description,
            "summary": meeting.summary or "",
            "agenda": meeting.agenda,
            "welcome_message": meeting.welcome_message,
            "welcome_theme": meeting.welcome_theme,
            "participants": participants,
            "checkin_records": checkin_records,
            "minutes_status": primary_minutes.status if primary_minutes else None,
            "review_conclusion": primary_minutes.review_conclusion if primary_minutes else None,
            "minutes_list": _minutes_payload(minutes_list),
            "esign_records": [
                {
                    "id": record.id,
                    "minutes_id": record.minutes_id,
                    "signer_id": record.signer_id,
                    "signer_name": record.signer_name or (record.signer.real_name if record.signer else ""),
                    "signer_unit": record.signer_unit,
                    "sign_step": record.sign_step,
                    "sign_type": record.sign_type,
                    "opinion": record.opinion,
                    "signed_at": record.signed_at.isoformat() if record.signed_at else None,
                }
                for record in sign_records
            ],
            "issues": [
                {
                    "id": issue.id,
                    "content": issue.content,
                    "reporter_name": issue.reporter_name,
                    "status": issue.status,
                    "response": issue.response,
                    "proofread": issue.proofread,
                    "archived": issue.archived,
                    "created_at": issue.created_at.isoformat() if issue.created_at else None,
                }
                for issue in issues
            ],
            "post_opinions": [
                {
                    "id": opinion.id,
                    "author_id": opinion.author_id,
                    "author_name": opinion.author_name,
                    "author_unit": opinion.author_unit,
                    "author_role": opinion.author_role,
                    "content": opinion.content,
                    "created_at": opinion.created_at.isoformat() if opinion.created_at else None,
                }
                for opinion in opinions
            ],
            "attachments": [
                {
                    "id": item.id,
                    "filename": item.filename,
                    "file_size": item.file_size,
                    "file_type": item.file_type,
                    "is_archived": item.is_archived,
                    "uploaded_at": item.uploaded_at.isoformat() if item.uploaded_at else None,
                }
                for item in attachments
            ],
            "archived_attachments": [
                {
                    "id": item.id,
                    "filename": item.filename,
                    "file_size": item.file_size,
                    "file_type": item.file_type,
                    "uploaded_at": item.uploaded_at.isoformat() if item.uploaded_at else None,
                }
                for item in attachments
                if item.is_archived
            ],
            "todo_stats": {
                "total": len(todos),
                "completed": completed,
                "in_progress": in_progress,
                "pending": pending,
                "overdue": overdue,
                "completion_rate": round(completed / len(todos) * 100, 1) if todos else 0,
            },
            "todos": [_todo_dict(todo, db) for todo in todos],
            "keypoints": [
                {
                    "id": item.id,
                    "title": item.title,
                    "content": item.content,
                    "importance": item.importance,
                }
                for item in keypoints
            ],
            "transcripts": [
                {
                    "id": item.id,
                    "speaker": item.speaker_name or "未知",
                    "text": item.text,
                    "start": int((item.start_time - meeting.start_time).total_seconds()) if item.start_time and meeting.start_time else 0,
                    "end": int((item.end_time - meeting.start_time).total_seconds()) if item.end_time and meeting.start_time else 0,
                }
                for item in transcripts
            ],
        },
    }


@router.post("/{meeting_id}/generate-summary")
async def generate_meeting_summary(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    transcripts = db.query(Transcript).filter(Transcript.meeting_id == meeting_id).order_by(Transcript.start_time.asc()).all()
    todos = db.query(TodoItem).filter(TodoItem.meeting_id == meeting_id).all()
    participant_names = "、".join([user.real_name for user in meeting.participants]) or "未知"
    transcript_text = "\n".join(
        f"[{item.speaker_name or '未知'}] {item.text}" for item in transcripts if item.text
    )[:2500] or "（暂无转写记录）"
    prompt = (
        f"会议名称：{meeting.title}\n"
        f"会议时间：{meeting.start_time.strftime('%Y-%m-%d %H:%M')}\n"
        f"会议地点：{meeting.location or '线上'}\n"
        f"参会人员：{participant_names}\n"
        f"待办事项：共{len(todos)}项\n"
        f"会议记录：\n{transcript_text}\n\n"
        "请生成一段 200 字以内的正式会议摘要。"
    )
    try:
        meeting.summary = await generate_text(
            prompt=prompt,
            system_prompt="你是会议摘要助手，请用简洁正式的中文输出摘要。",
            temperature=0.3,
            max_tokens=500,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI 摘要生成失败：{exc}")
    db.commit()
    return {"code": 200, "summary": meeting.summary}


@router.get("/{meeting_id}/keypoints")
async def get_archive_keypoints(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    keypoints = (
        db.query(MeetingKeypoint)
        .filter(MeetingKeypoint.meeting_id == meeting_id)
        .order_by(MeetingKeypoint.sort_order.asc(), MeetingKeypoint.id.asc())
        .all()
    )
    return {
        "code": 200,
        "data": [
            {"id": item.id, "title": item.title, "content": item.content, "importance": item.importance}
            for item in keypoints
        ],
    }


@router.get("/{meeting_id}/all-todos")
async def get_archive_all_todos(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    todos = db.query(TodoItem).filter(TodoItem.meeting_id == meeting_id).order_by(TodoItem.created_at.asc()).all()
    return {"code": 200, "data": [_todo_dict(todo, db) for todo in todos]}


@router.post("/{meeting_id}/ai-extract-todos")
async def ai_extract_todos(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    transcripts = db.query(Transcript).filter(Transcript.meeting_id == meeting_id).order_by(Transcript.start_time.asc()).all()
    if not transcripts:
        return {"code": 200, "suggestions": [], "message": "暂无转写记录，无法提取待办"}

    participant_names = [user.real_name for user in meeting.participants]
    transcript_text = "\n".join(
        f"[{item.speaker_name or '未知'}] {item.text}" for item in transcripts if item.text
    )[:3000]
    try:
        result_text = await generate_text(
            prompt=(
                f"会议：{meeting.title}\n"
                f"参会人员：{', '.join(participant_names)}\n"
                f"转写记录：\n{transcript_text}\n\n"
                "请识别其中的待办事项，并只返回 JSON 数组。"
            ),
            system_prompt=(
                "请输出 JSON 数组，每项包括 title、description、suggested_assignee、priority、due_days。"
            ),
            temperature=0.2,
            max_tokens=1500,
        )
        matched = re.search(r"\[[\s\S]*\]", result_text)
        suggestions = json.loads(matched.group()) if matched else []
    except Exception as exc:
        return {"code": 200, "suggestions": [], "error": str(exc)}
    return {"code": 200, "suggestions": suggestions}


@router.post("/{meeting_id}/generate-report")
async def generate_closure_report(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = _ensure_meeting(db, meeting_id)
    todos = db.query(TodoItem).filter(TodoItem.meeting_id == meeting_id).all()
    total = len(todos)
    completed = sum(1 for todo in todos if todo.status == TodoStatus.COMPLETED)
    in_progress = sum(1 for todo in todos if todo.status == TodoStatus.IN_PROGRESS)
    overdue = sum(1 for todo in todos if todo.status == TodoStatus.OVERDUE)
    prompt = (
        f"会议名称：{meeting.title}\n"
        f"会议摘要：{meeting.summary or meeting.description or '无'}\n"
        f"待办总数：{total}\n已完成：{completed}\n进行中：{in_progress}\n已逾期：{overdue}\n"
        "请生成一份简洁的会后闭环报告。"
    )
    try:
        report = await generate_text(
            prompt=prompt,
            system_prompt="你是会议闭环报告助手，请用正式中文输出。",
            temperature=0.3,
            max_tokens=800,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"报告生成失败：{exc}")
    return {"code": 200, "data": {"report": report}}
