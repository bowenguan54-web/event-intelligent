"""
认证路由
"""
import secrets
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user
from app.models.user import User
from app.schemas.schemas import UserCreate, UserLogin, UserInfo, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")

    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        real_name=user_data.real_name,
        email=user_data.email,
        phone=user_data.phone,
        department=user_data.department,
        position=user_data.position,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user=UserInfo.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user=UserInfo.model_validate(user),
    )


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserInfo.model_validate(current_user)


@router.get("/users", response_model=List[UserInfo])
async def list_users(
    department: str = None,
    keyword: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查询用户列表（用于人员选择）"""
    query = db.query(User).filter(User.is_active == True)
    if department:
        query = query.filter(User.department == department)
    if keyword:
        query = query.filter(
            (User.real_name.contains(keyword)) | (User.username.contains(keyword))
        )
    return [UserInfo.model_validate(u) for u in query.all()]


class ParticipantCreate(BaseModel):
    real_name: str
    department: Optional[str] = None
    position: Optional[str] = None
    professional_title: Optional[str] = None
    id_card_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_expert: bool = False


@router.post("/participants", response_model=UserInfo)
async def create_participant(
    data: ParticipantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建参会人员（无登录账号），支持指定专家/其他人员类别"""
    username = f"p_{secrets.token_hex(6)}"
    user = User(
        username=username,
        password_hash=get_password_hash(secrets.token_hex(16)),
        real_name=data.real_name,
        department=data.department,
        position=data.position,
        professional_title=data.professional_title,
        id_card_number=data.id_card_number,
        phone=data.phone,
        email=data.email if data.email else None,
        is_participant_only=True,
        is_expert=data.is_expert,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserInfo.model_validate(user)


@router.delete("/participants/{user_id}")
async def delete_participant(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除参会人员（仅限 is_participant_only=True 的外部参会者）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not user.is_participant_only:
        raise HTTPException(status_code=403, detail="只能删除外部参会人员，系统账号无法删除")
    db.delete(user)
    db.commit()
    return {"detail": "删除成功"}
