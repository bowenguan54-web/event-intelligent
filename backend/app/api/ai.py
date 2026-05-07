"""
AI 问答路由
"""
import os
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from app.core.security import get_current_user
from app.models.user import User
from app.services.llm_service import generate_text, generate_text_stream

router = APIRouter(prefix="/api/ai", tags=["AI服务"])


@router.post("/qa")
async def ai_qa(
    data: dict,
    current_user: User = Depends(get_current_user),
):
    """AI 问答（非流式版本）"""
    question = data.get("question", "")
    meeting_id = data.get("meeting_id")

    system_prompt = (
        "你是智能会议助手AI，请根据用户的问题给出专业、简洁、有条理的回答。"
        "如果问题与会议相关，请结合会议管理的专业知识回答。"
    )

    try:
        answer = await generate_text(
            prompt=question,
            system_prompt=system_prompt,
            temperature=0.7,
        )
        return {
            "code": 200,
            "data": {
                "answer": answer,
                "sources": [],
            },
        }
    except Exception as e:
        return {
            "code": 500,
            "data": {
                "answer": f"AI 服务暂时不可用：{str(e)}",
                "sources": [],
            },
        }


@router.post("/stream")
async def ai_stream(
    data: dict,
    current_user: User = Depends(get_current_user),
):
    """AI 问答（SSE 流式版本）"""
    question = data.get("question", "")
    system_prompt = data.get("system_prompt",
        "你是智能会议助手AI，请根据用户的问题给出专业、简洁、有条理的回答。"
    )

    async def event_generator():
        try:
            async for chunk in generate_text_stream(
                prompt=question,
                system_prompt=system_prompt,
                temperature=0.7,
            ):
                # SSE 规范: data 字段内不允许裸换行符
                # 将换行符替换为特殊标记，前端再还原
                safe_chunk = chunk.replace("\n", "\\n")
                yield f"data: {safe_chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/meeting-record-text")
async def get_meeting_record_text():
    """读取演示用会议记录文本文件（无需登录）"""
    # __file__ = .../backend/app/api/ai.py → 4 层 dirname → 项目根目录
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    file_path = os.path.join(base_dir, "frontend", "会议记录.txt")
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except FileNotFoundError:
        return {"content": "【提示】未找到会议记录文件，请在 frontend/ 目录下放置「会议记录.txt」文件。\n\n您可以在该文件中写入任意会议记录内容，系统将按行逐字输出。"}
    except Exception as e:
        return {"content": f"读取文件失败：{str(e)}"}
