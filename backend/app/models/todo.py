"""
待办事项模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class TodoStatus(str, enum.Enum):
    PENDING = "pending"         # 待处理
    IN_PROGRESS = "in_progress" # 进行中
    COMPLETED = "completed"     # 已完成
    OVERDUE = "overdue"         # 已逾期


class TodoPriority(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TodoItem(Base):
    __tablename__ = "todo_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default=TodoStatus.PENDING, index=True)
    priority = Column(String(20), default=TodoPriority.MEDIUM)
    due_date = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)
    source_minutes_section = Column(Text)  # 来源纪要段落
    flow_binding_id = Column(String(100), nullable=True)  # OA工作流绑定ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    meeting = relationship("Meeting", back_populates="todo_items")
    assignee = relationship("User", back_populates="todo_items", foreign_keys=[assignee_id])
    creator = relationship("User", foreign_keys=[creator_id])
    logs = relationship("TodoLog", back_populates="todo_item", cascade="all, delete-orphan")


class TodoLog(Base):
    """待办执行日志"""
    __tablename__ = "todo_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    todo_id = Column(Integer, ForeignKey("todo_items.id"), nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # status_change/comment/update
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    todo_item = relationship("TodoItem", back_populates="logs")
    operator = relationship("User", foreign_keys=[operator_id])
