"""
待办事项路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.todo import TodoItem, TodoLog, TodoStatus
from app.models.meeting import Meeting
from app.schemas.schemas import (
    TodoCreate, TodoUpdate, TodoInfo, TodoListResponse,
    BindFlowRequest, ResponseBase,
)

router = APIRouter(prefix="/api/todo", tags=["待办事项"])


@router.get("/list", response_model=TodoListResponse)
async def list_todos(
    meeting_id: Optional[int] = None,
    assignee_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分页查询待办事项"""
    query = db.query(TodoItem)

    if meeting_id:
        query = query.filter(TodoItem.meeting_id == meeting_id)
    if assignee_id:
        query = query.filter(TodoItem.assignee_id == assignee_id)
    if status:
        query = query.filter(TodoItem.status == status)
    if priority:
        query = query.filter(TodoItem.priority == priority)

    # 自动标记逾期
    now = datetime.utcnow()
    overdue_items = (
        db.query(TodoItem)
        .filter(
            TodoItem.status.in_([TodoStatus.PENDING, TodoStatus.IN_PROGRESS]),
            TodoItem.due_date < now,
        )
        .all()
    )
    for item in overdue_items:
        item.status = TodoStatus.OVERDUE
    if overdue_items:
        db.commit()

    total = query.count()
    todos = query.order_by(TodoItem.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return TodoListResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=[TodoInfo.model_validate(t) for t in todos],
    )


@router.post("/create", response_model=TodoInfo)
async def create_todo(
    data: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建待办事项"""
    todo = TodoItem(
        title=data.title,
        description=data.description,
        meeting_id=data.meeting_id,
        assignee_id=data.assignee_id,
        creator_id=current_user.id,
        priority=data.priority,
        due_date=data.due_date,
    )
    db.add(todo)
    db.flush()

    # 记录日志
    log = TodoLog(
        todo_id=todo.id,
        operator_id=current_user.id,
        action="create",
        content=f"创建待办事项: {data.title}",
    )
    db.add(log)
    db.commit()
    db.refresh(todo)

    return TodoInfo.model_validate(todo)


@router.put("/{todo_id}", response_model=TodoInfo)
async def update_todo(
    todo_id: int,
    data: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新待办事项"""
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="待办事项不存在")

    update_data = data.model_dump(exclude_unset=True)
    old_status = todo.status

    for key, value in update_data.items():
        setattr(todo, key, value)

    # 记录完成时间
    if data.status == TodoStatus.COMPLETED and old_status != TodoStatus.COMPLETED:
        todo.completed_at = datetime.utcnow()

    # 记录日志
    log = TodoLog(
        todo_id=todo.id,
        operator_id=current_user.id,
        action="status_change" if "status" in update_data else "update",
        content=f"更新待办: {', '.join(f'{k}={v}' for k, v in update_data.items())}",
    )
    db.add(log)
    db.commit()
    db.refresh(todo)

    return TodoInfo.model_validate(todo)


@router.post("/{todo_id}/bindflow", response_model=ResponseBase)
async def bind_flow(
    todo_id: int,
    data: BindFlowRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """将待办绑定至 OA 工作流"""
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="待办事项不存在")

    todo.flow_binding_id = data.flow_node_id
    db.commit()

    return ResponseBase(message="绑定成功")


@router.get("/{todo_id}/flowstatus")
async def get_flow_status(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查询关联工作流状态"""
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="待办事项不存在")

    if not todo.flow_binding_id:
        return {"code": 200, "data": {"bound": False}}

    # TODO: 查询外部工作流引擎
    return {
        "code": 200,
        "data": {
            "bound": True,
            "flow_node_id": todo.flow_binding_id,
            "flow_status": "processing",
        },
    }


@router.get("/reminders/pending")
async def get_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的待办提醒（待处理、即将到期、已逾期）"""
    now = datetime.utcnow()
    from datetime import timedelta
    soon = now + timedelta(days=3)

    # 自动标记逾期
    overdue_items = (
        db.query(TodoItem)
        .filter(
            TodoItem.status.in_([TodoStatus.PENDING, TodoStatus.IN_PROGRESS]),
            TodoItem.due_date < now,
        )
        .all()
    )
    for item in overdue_items:
        item.status = TodoStatus.OVERDUE
    if overdue_items:
        db.commit()

    # 查询该用户的逾期待办
    overdue = (
        db.query(TodoItem)
        .filter(TodoItem.assignee_id == current_user.id, TodoItem.status == TodoStatus.OVERDUE)
        .order_by(TodoItem.due_date.asc())
        .limit(10)
        .all()
    )

    # 查询即将到期（3天内）
    upcoming = (
        db.query(TodoItem)
        .filter(
            TodoItem.assignee_id == current_user.id,
            TodoItem.status.in_([TodoStatus.PENDING, TodoStatus.IN_PROGRESS]),
            TodoItem.due_date != None,
            TodoItem.due_date <= soon,
            TodoItem.due_date >= now,
        )
        .order_by(TodoItem.due_date.asc())
        .limit(10)
        .all()
    )

    # 查询待处理
    pending = (
        db.query(TodoItem)
        .filter(
            TodoItem.assignee_id == current_user.id,
            TodoItem.status.in_([TodoStatus.PENDING, TodoStatus.IN_PROGRESS]),
        )
        .order_by(TodoItem.created_at.desc())
        .limit(10)
        .all()
    )

    reminders = []
    for item in overdue:
        meeting_title = ""
        if item.meeting_id:
            m = db.query(Meeting).filter(Meeting.id == item.meeting_id).first()
            meeting_title = m.title if m else ""
        reminders.append({
            "id": item.id,
            "type": "overdue",
            "title": f"已逾期：{item.title}",
            "meeting_title": meeting_title,
            "due_date": item.due_date.strftime("%Y-%m-%d") if item.due_date else "",
            "priority": item.priority,
        })

    for item in upcoming:
        meeting_title = ""
        if item.meeting_id:
            m = db.query(Meeting).filter(Meeting.id == item.meeting_id).first()
            meeting_title = m.title if m else ""
        reminders.append({
            "id": item.id,
            "type": "upcoming",
            "title": f"即将到期：{item.title}",
            "meeting_title": meeting_title,
            "due_date": item.due_date.strftime("%Y-%m-%d") if item.due_date else "",
            "priority": item.priority,
        })

    # 添加待处理中不在上面列表的
    existing_ids = {r["id"] for r in reminders}
    for item in pending:
        if item.id not in existing_ids:
            meeting_title = ""
            if item.meeting_id:
                m = db.query(Meeting).filter(Meeting.id == item.meeting_id).first()
                meeting_title = m.title if m else ""
            reminders.append({
                "id": item.id,
                "type": "pending",
                "title": f"待办：{item.title}",
                "meeting_title": meeting_title,
                "due_date": item.due_date.strftime("%Y-%m-%d") if item.due_date else "",
                "priority": item.priority,
            })

    return {"total": len(reminders), "reminders": reminders}
