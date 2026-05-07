"""
用户模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    real_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    department = Column(String(100))          # 单位
    position = Column(String(100))            # 职位
    professional_title = Column(String(100))  # 职称
    id_card_number = Column(String(30))       # 身份证号（评审费签署用）
    avatar = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_participant_only = Column(Boolean, default=False)  # 保留兼容
    is_expert = Column(Boolean, default=False)            # 是否专家
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    created_meetings = relationship("Meeting", back_populates="creator", foreign_keys="Meeting.creator_id")
    todo_items = relationship("TodoItem", back_populates="assignee", foreign_keys="TodoItem.assignee_id")
