"""
WebSocket 实时语音转写
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, List
import json
import uuid
from datetime import datetime

from app.core.database import get_db, SessionLocal

router = APIRouter(tags=["WebSocket"])

# 活跃的 WebSocket 连接管理
active_connections: Dict[int, List[WebSocket]] = {}


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, meeting_id: int, websocket: WebSocket):
        await websocket.accept()
        if meeting_id not in self.active_connections:
            self.active_connections[meeting_id] = []
        self.active_connections[meeting_id].append(websocket)

    def disconnect(self, meeting_id: int, websocket: WebSocket):
        if meeting_id in self.active_connections:
            self.active_connections[meeting_id].remove(websocket)
            if not self.active_connections[meeting_id]:
                del self.active_connections[meeting_id]

    async def broadcast(self, meeting_id: int, message: dict):
        """向指定会议的所有连接广播消息"""
        if meeting_id in self.active_connections:
            for connection in self.active_connections[meeting_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


manager = ConnectionManager()


@router.websocket("/ws/meeting/{meeting_id}/transcribe")
async def websocket_transcribe(websocket: WebSocket, meeting_id: int):
    """
    实时语音转写 WebSocket 端点

    前端通过 Web Audio API 采集麦克风音频流，
    以 PCM 16kHz 采样率分帧(每帧200ms)发送至后端。
    后端进行 ASR 识别后将结果推送回前端。
    """
    await manager.connect(meeting_id, websocket)

    try:
        while True:
            data = await websocket.receive()

            if "bytes" in data:
                # 接收音频二进制数据
                audio_data = data["bytes"]

                # TODO: 发送至 ASR 引擎进行流式识别
                # 以下为模拟的转写结果
                segment_id = f"seg_{uuid.uuid4().hex[:8]}"
                result = {
                    "type": "transcript",
                    "segment_id": segment_id,
                    "speaker_id": None,
                    "speaker_name": "未识别",
                    "timestamp": datetime.utcnow().isoformat(),
                    "text": "[实时转写文本]",
                    "is_final": False,
                    "is_interrupted": False,
                    "has_sensitive": False,
                }

                await manager.broadcast(meeting_id, result)

            elif "text" in data:
                # 接收文本控制命令
                try:
                    command = json.loads(data["text"])
                    cmd_type = command.get("type")

                    if cmd_type == "start":
                        await manager.broadcast(meeting_id, {
                            "type": "status",
                            "status": "recording",
                            "message": "录音已开始",
                        })

                    elif cmd_type == "pause":
                        await manager.broadcast(meeting_id, {
                            "type": "status",
                            "status": "paused",
                            "message": "录音已暂停",
                        })

                    elif cmd_type == "stop":
                        await manager.broadcast(meeting_id, {
                            "type": "status",
                            "status": "stopped",
                            "message": "录音已停止",
                        })

                    elif cmd_type == "ping":
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": datetime.utcnow().isoformat(),
                        })

                except json.JSONDecodeError:
                    pass

    except WebSocketDisconnect:
        manager.disconnect(meeting_id, websocket)
    except Exception as e:
        manager.disconnect(meeting_id, websocket)


@router.websocket("/ws/meeting/{meeting_id}/ai-qa")
async def websocket_ai_qa(websocket: WebSocket, meeting_id: int):
    """
    AI 问答 WebSocket 端点
    支持 SSE 风格的流式回答（调用 DeepSeek API）
    """
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            question = json.loads(data)
            question_text = question.get("question", question.get("content", ""))
            question_id = question.get("id", "")

            system_prompt = (
                "你是智能会议助手AI，请根据用户的问题给出专业、简洁、有条理的回答。"
                "如果问题与会议相关，请结合会议管理的专业知识回答。"
            )

            try:
                from app.services.llm_service import chat_completion_stream

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question_text},
                ]

                async for chunk in chat_completion_stream(messages, temperature=0.7):
                    await websocket.send_json({
                        "type": "qa_stream",
                        "question_id": question_id,
                        "content": chunk,
                        "is_final": False,
                        "sources": [],
                    })

                # 发送结束标志
                await websocket.send_json({
                    "type": "qa_stream",
                    "question_id": question_id,
                    "content": "",
                    "is_final": True,
                    "sources": [
                        {"type": "meeting", "id": meeting_id, "title": "AI 回答完成"},
                    ],
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "qa_stream",
                    "question_id": question_id,
                    "content": f"AI 服务暂时不可用：{str(e)}",
                    "is_final": True,
                    "sources": [],
                })

    except WebSocketDisconnect:
        pass
