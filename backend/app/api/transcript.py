"""
会议记录与转写路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.meeting import Meeting, Transcript, MeetingKeypoint
from app.schemas.schemas import (
    TranscriptInfo, TranscriptCreate, TranscriptUpdate, KeypointInfo,
    KeypointGenerateRequest, ResponseBase,
)
from app.services.llm_service import generate_text

router = APIRouter(prefix="/api/meeting", tags=["会议记录"])


@router.get("/{meeting_id}/transcripts", response_model=List[TranscriptInfo])
async def get_transcripts(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取转写全文记录"""
    transcripts = (
        db.query(Transcript)
        .filter(Transcript.meeting_id == meeting_id)
        .order_by(Transcript.start_time.asc())
        .all()
    )
    return [TranscriptInfo.model_validate(t) for t in transcripts]


@router.post("/{meeting_id}/transcript", response_model=TranscriptInfo)
async def create_transcript(
    meeting_id: int,
    data: TranscriptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """保存一条转写记录（前端模拟录音时使用）"""
    # 若 segment_id 已存在则直接返回
    existing = db.query(Transcript).filter(
        Transcript.meeting_id == meeting_id,
        Transcript.segment_id == data.segment_id,
    ).first()
    if existing:
        return TranscriptInfo.model_validate(existing)

    from datetime import datetime as _dt
    start_time = None
    if data.start_time:
        try:
            start_time = _dt.fromisoformat(data.start_time)
        except ValueError:
            pass

    transcript = Transcript(
        meeting_id=meeting_id,
        segment_id=data.segment_id,
        speaker_name=data.speaker_name or "未识别",
        text=data.text,
        category=data.category,
        start_time=start_time or _dt.utcnow(),
    )
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    return TranscriptInfo.model_validate(transcript)


@router.put("/{meeting_id}/transcript/{seg_id}", response_model=TranscriptInfo)
async def update_transcript(
    meeting_id: int,
    seg_id: str,
    data: TranscriptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """修正单条转写记录"""
    transcript = (
        db.query(Transcript)
        .filter(Transcript.meeting_id == meeting_id, Transcript.segment_id == seg_id)
        .first()
    )
    if not transcript:
        raise HTTPException(status_code=404, detail="转写记录不存在")

    if data.text is not None:
        transcript.text = data.text
    if data.category is not None:
        transcript.category = data.category
    db.commit()
    db.refresh(transcript)
    return TranscriptInfo.model_validate(transcript)


@router.get("/{meeting_id}/audio/{seg_id}")
async def get_audio_segment(
    meeting_id: int,
    seg_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取指定片段音频"""
    transcript = (
        db.query(Transcript)
        .filter(Transcript.meeting_id == meeting_id, Transcript.segment_id == seg_id)
        .first()
    )
    if not transcript or not transcript.audio_path:
        raise HTTPException(status_code=404, detail="音频文件不存在")

    from fastapi.responses import FileResponse
    return FileResponse(transcript.audio_path, media_type="audio/wav")


from pydantic import BaseModel as _BaseModel
class BatchDeleteRequest(_BaseModel):
    segment_ids: List[str]

@router.delete("/{meeting_id}/transcripts/batch", response_model=ResponseBase)
async def batch_delete_transcripts(
    meeting_id: int,
    data: BatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """批量删除转写记录（裁剪归档用）"""
    if not data.segment_ids:
        return ResponseBase(success=True, message="无需删除")
    deleted = (
        db.query(Transcript)
        .filter(
            Transcript.meeting_id == meeting_id,
            Transcript.segment_id.in_(data.segment_ids),
        )
        .all()
    )
    for t in deleted:
        db.delete(t)
    db.commit()
    return ResponseBase(success=True, message=f"已删除 {len(deleted)} 条记录")


@router.post("/{meeting_id}/keypoints", response_model=List[KeypointInfo])
async def generate_keypoints(
    meeting_id: int,
    data: KeypointGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI 提取会议要点"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")

    transcripts = (
        db.query(Transcript)
        .filter(Transcript.meeting_id == meeting_id)
        .order_by(Transcript.start_time.asc())
        .all()
    )

    # 拼接转写文本
    transcript_text = "\n".join(
        [f"[{t.speaker_name or '未知'}] {t.text}" for t in transcripts if t.text]
    ) if transcripts else "（暂无转写记录）"

    # 调用 DeepSeek AI 提取要点
    system_prompt = (
        "你是专业的会议要点提取助手。请从会议转写记录中提取关键要点。"
        "以 JSON 数组格式返回，每个要点包含以下字段：\n"
        '- title: 要点标题（简短）\n'
        '- content: 要点详细内容\n'
        '- importance: 重要程度（"high", "medium", "low"）\n'
        "只输出 JSON 数组，不要添加其他说明或 markdown 标记。"
    )

    try:
        result = await generate_text(
            prompt=f"会议标题：{meeting.title}\n\n转写记录：\n{transcript_text}\n\n请提取会议要点。",
            system_prompt=system_prompt,
            temperature=0.3,
        )

        # 解析 AI 返回的 JSON
        # 尝试清理可能的 markdown 包裹
        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

        keypoints_data = json.loads(cleaned)
        sample_keypoints = []
        for i, kp in enumerate(keypoints_data, 1):
            sample_keypoints.append(MeetingKeypoint(
                meeting_id=meeting_id,
                title=kp.get("title", f"要点{i}"),
                content=kp.get("content", ""),
                importance=kp.get("importance", "medium"),
                sort_order=i,
            ))
    except Exception:
        # AI 调用或解析失败时使用默认要点
        sample_keypoints = [
            MeetingKeypoint(
                meeting_id=meeting_id,
                title="待提取",
                content="AI 要点提取暂时不可用，请手动添加会议要点",
                importance="medium",
                sort_order=1,
            ),
        ]

    # 清除旧要点并保存新要点
    db.query(MeetingKeypoint).filter(MeetingKeypoint.meeting_id == meeting_id).delete()
    for kp in sample_keypoints:
        db.add(kp)
    db.commit()

    keypoints = db.query(MeetingKeypoint).filter(MeetingKeypoint.meeting_id == meeting_id).order_by(MeetingKeypoint.sort_order).all()
    return [KeypointInfo.model_validate(k) for k in keypoints]


@router.post("/{meeting_id}/validate")
async def validate_transcripts(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """触发智能校验并返回建议列表"""
    transcripts = (
        db.query(Transcript)
        .filter(Transcript.meeting_id == meeting_id)
        .all()
    )

    # 拼接转写文本用于 AI 校验
    transcript_text = "\n".join(
        [f"[{t.segment_id}] {t.text}" for t in transcripts if t.text]
    ) if transcripts else ""

    if not transcript_text:
        return {"code": 200, "data": []}

    # 调用 DeepSeek AI 执行智能校验
    system_prompt = (
        "你是专业的语音转写校验助手。请检查以下转写文本中可能存在的错误，"
        "包括同音字误识别、语序不通顺、语义矛盾等问题。\n"
        "以 JSON 数组格式返回校验建议，每条建议包含：\n"
        '- segment_id: 对应的片段ID（方括号中的内容）\n'
        '- original_text: 原始文本\n'
        '- suggested_text: 建议修正后的文本\n'
        '- reason: 修正原因\n'
        '- confidence: 置信度（0-1 的浮点数）\n'
        "只输出 JSON 数组，不要添加其他说明或 markdown 标记。"
        "如果没有发现错误，返回空数组 []。"
    )

    try:
        result = await generate_text(
            prompt=f"请校验以下转写文本：\n{transcript_text}",
            system_prompt=system_prompt,
            temperature=0.2,
        )

        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

        suggestions_raw = json.loads(cleaned)
        suggestions = []
        for i, s in enumerate(suggestions_raw, 1):
            suggestions.append({
                "id": i,
                "segment_id": s.get("segment_id", ""),
                "original_text": s.get("original_text", ""),
                "suggested_text": s.get("suggested_text", ""),
                "reason": s.get("reason", ""),
                "confidence": s.get("confidence", 0.8),
            })
    except Exception:
        suggestions = []

    return {"code": 200, "data": suggestions}
