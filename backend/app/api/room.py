"""
会议室管理路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.room import MeetingRoom

router = APIRouter(prefix="/api/room", tags=["会议室管理"])


# ========== Schemas ==========
class RoomCreate(BaseModel):
    name: str
    description: Optional[str] = None
    room_width: int = 700
    room_height: int = 440
    tables_data: Optional[str] = None
    seats_data: Optional[str] = None
    screen_data: Optional[str] = None


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    room_width: Optional[int] = None
    room_height: Optional[int] = None
    tables_data: Optional[str] = None
    seats_data: Optional[str] = None
    screen_data: Optional[str] = None


class RoomInfo(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    room_width: int
    room_height: int
    tables_data: Optional[str] = None
    seats_data: Optional[str] = None
    screen_data: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== API ==========
@router.get("/list", response_model=List[RoomInfo])
async def list_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取所有会议室"""
    rooms = db.query(MeetingRoom).order_by(MeetingRoom.name).all()
    return [RoomInfo.model_validate(r) for r in rooms]


@router.post("/create", response_model=RoomInfo)
async def create_room(
    data: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建会议室"""
    existing = db.query(MeetingRoom).filter(MeetingRoom.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="会议室名称已存在")
    room = MeetingRoom(
        name=data.name,
        description=data.description,
        room_width=data.room_width,
        room_height=data.room_height,
        tables_data=data.tables_data,
        seats_data=data.seats_data,
        screen_data=data.screen_data,
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return RoomInfo.model_validate(room)


@router.get("/{room_id}", response_model=RoomInfo)
async def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取单个会议室"""
    room = db.query(MeetingRoom).filter(MeetingRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="会议室不存在")
    return RoomInfo.model_validate(room)


@router.put("/{room_id}", response_model=RoomInfo)
async def update_room(
    room_id: int,
    data: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新会议室"""
    room = db.query(MeetingRoom).filter(MeetingRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="会议室不存在")
    update_data = data.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] != room.name:
        dup = db.query(MeetingRoom).filter(MeetingRoom.name == update_data["name"]).first()
        if dup:
            raise HTTPException(status_code=400, detail="会议室名称已存在")
    for key, value in update_data.items():
        setattr(room, key, value)
    db.commit()
    db.refresh(room)
    return RoomInfo.model_validate(room)


@router.delete("/{room_id}")
async def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除会议室"""
    room = db.query(MeetingRoom).filter(MeetingRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="会议室不存在")
    db.delete(room)
    db.commit()
    return {"message": "会议室已删除"}


@router.get("/by-name/{name}", response_model=RoomInfo)
async def get_room_by_name(
    name: str,
    db: Session = Depends(get_db),
):
    """通过名称查询会议室（公开接口，会议端使用）"""
    room = db.query(MeetingRoom).filter(MeetingRoom.name == name).first()
    if not room:
        raise HTTPException(status_code=404, detail="会议室不存在")
    return RoomInfo.model_validate(room)


@router.get("/public/all", response_model=List[RoomInfo])
async def list_rooms_public(
    db: Session = Depends(get_db),
):
    """获取所有会议室列表（公开接口，新建会议选择地点使用）"""
    rooms = db.query(MeetingRoom).order_by(MeetingRoom.name).all()
    return [RoomInfo.model_validate(r) for r in rooms]
