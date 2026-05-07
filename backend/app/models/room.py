"""
会议室模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.core.database import Base


class MeetingRoom(Base):
    __tablename__ = "meeting_rooms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    room_width = Column(Integer, default=700)
    room_height = Column(Integer, default=440)
    tables_data = Column(Text, nullable=True)   # JSON: [{x,y,w,h,rx,label}]
    seats_data = Column(Text, nullable=True)     # JSON: [{id,label,x,y,ip}]
    screen_data = Column(Text, nullable=True)    # JSON: {x,y,w,h}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
