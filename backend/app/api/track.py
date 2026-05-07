"""
进度跟踪路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.meeting import Meeting
from app.models.todo import TodoItem, TodoStatus
from app.schemas.schemas import TrackStats, GanttItem

router = APIRouter(prefix="/api/meeting", tags=["进度跟踪"])


@router.get("/{meeting_id}/track/stats", response_model=TrackStats)
async def get_track_stats(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取事项统计数据"""
    todos = db.query(TodoItem).filter(TodoItem.meeting_id == meeting_id).all()

    total = len(todos)
    completed = sum(1 for t in todos if t.status == TodoStatus.COMPLETED)
    in_progress = sum(1 for t in todos if t.status == TodoStatus.IN_PROGRESS)
    overdue = sum(1 for t in todos if t.status == TodoStatus.OVERDUE)

    return TrackStats(
        total=total,
        completed=completed,
        in_progress=in_progress,
        overdue=overdue,
        completion_rate=round(completed / total * 100, 1) if total > 0 else 0,
    )


@router.get("/{meeting_id}/track/gantt")
async def get_gantt_data(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取甘特图数据"""
    todos = (
        db.query(TodoItem)
        .filter(TodoItem.meeting_id == meeting_id)
        .order_by(TodoItem.created_at.asc())
        .all()
    )

    gantt_items = []
    for todo in todos:
        assignee = db.query(User).filter(User.id == todo.assignee_id).first()
        progress = 1.0 if todo.status == TodoStatus.COMPLETED else (0.5 if todo.status == TodoStatus.IN_PROGRESS else 0.0)

        gantt_items.append(GanttItem(
            id=todo.id,
            title=todo.title,
            assignee=assignee.real_name if assignee else "未指定",
            start_date=todo.created_at.strftime("%Y-%m-%d") if todo.created_at else None,
            end_date=todo.due_date.strftime("%Y-%m-%d") if todo.due_date else None,
            progress=progress,
            status=todo.status,
        ))

    return {"code": 200, "data": gantt_items}


@router.post("/{meeting_id}/track/report")
async def generate_report(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """生成闭环报表"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")

    todos = db.query(TodoItem).filter(TodoItem.meeting_id == meeting_id).all()
    total = len(todos)
    completed = sum(1 for t in todos if t.status == TodoStatus.COMPLETED)
    overdue = sum(1 for t in todos if t.status == TodoStatus.OVERDUE)

    report = {
        "meeting_title": meeting.title,
        "meeting_time": meeting.start_time.strftime("%Y-%m-%d %H:%M"),
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
        "summary": {
            "total_items": total,
            "completed": completed,
            "overdue": overdue,
            "completion_rate": f"{round(completed / total * 100, 1)}%" if total > 0 else "0%",
        },
        "items": [
            {
                "title": t.title,
                "assignee_id": t.assignee_id,
                "status": t.status,
                "due_date": t.due_date.strftime("%Y-%m-%d") if t.due_date else "未设置",
                "completed_at": t.completed_at.strftime("%Y-%m-%d") if t.completed_at else None,
            }
            for t in todos
        ],
    }

    return {"code": 200, "data": report}


@router.get("/{meeting_id}/track/report/export")
async def export_report(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """导出闭环报表 PDF"""
    # TODO: PDF 生成
    return {"code": 200, "message": "报表导出功能开发中"}
