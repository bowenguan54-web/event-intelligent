"""
会议相关模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class MeetingStatus(str, enum.Enum):
    PENDING = "pending"           # 未召开
    PREPARING = "preparing"       # 准备中（发起人已开放大屏，参会者可选座位）
    IN_PROGRESS = "in_progress"   # 进行中
    PROCESSING = "processing"     # 会后处理中（录音已停止，等待问题审查与纪要审签）
    FINISHED = "finished"         # 已结束（问题审查与纪要审签均完成）
    SIGNING = "signing"           # 审签中（纪要审签进行中）
    ARCHIVED = "archived"         # 已归档


class MeetingType(str, enum.Enum):
    REGULAR = "regular"           # 例会
    SPECIAL = "special"           # 专题会议
    DECISION = "decision"         # 决策会议
    REVIEW = "review"             # 评审会议
    OTHER = "other"               # 其他


# 会议与参会人员多对多关联表
meeting_participants = Table(
    "meeting_participants",
    Base.metadata,
    Column("meeting_id", Integer, ForeignKey("meetings.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role", String(20), default="participant"),  # organizer/participant/recorder
    Column("checked_in", Boolean, default=False),
    Column("check_in_time", DateTime, nullable=True),
    Column("signature_image", Text, nullable=True),     # 手写签名 Base64
    Column("signature_status", String(20), default="none"),  # none/signed/rejected
    Column("is_late", Boolean, default=False),
    Column("is_early_leave", Boolean, default=False),
    Column("sort_order", Integer, default=0),
    Column("is_expert", Boolean, default=False),         # 本次会议是否作为专家
    Column("is_leader", Boolean, default=False),         # 是否专家组组长
    Column("fee_signature_image", Text, nullable=True),  # 评审费签名 Base64
    Column("fee_id_card", Text, nullable=True),          # 评审费：身份证号
    Column("fee_bank_card", Text, nullable=True),        # 评审费：银行卡号
)


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_code = Column(String(20), unique=True, index=True, nullable=True)  # 6位会议号
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    meeting_type = Column(String(20), default=MeetingType.REGULAR)
    status = Column(String(20), default=MeetingStatus.PENDING, index=True)
    location = Column(String(200))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agenda = Column(Text)  # 会议议程 (HTML/JSON)
    seat_layout = Column(Text, nullable=True)  # 座位排布JSON
    summary = Column(Text, nullable=True)  # 会议摘要
    has_review_fee = Column(Boolean, default=False)  # 是否设置评审费
    welcome_message = Column(Text, nullable=True)  # 会议准备欢迎词
    welcome_theme = Column(String(50), default="aurora")  # 欢迎屏主题
    issue_review_status = Column(String(20), default="pending")  # pending/completed/skipped
    issue_review_require_sign = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    creator = relationship("User", back_populates="created_meetings", foreign_keys=[creator_id])
    participants = relationship("User", secondary=meeting_participants, backref="meetings")
    transcripts = relationship("Transcript", back_populates="meeting", cascade="all, delete-orphan")
    attachments = relationship("MeetingAttachment", back_populates="meeting", cascade="all, delete-orphan")
    minutes = relationship("MeetingMinutes", back_populates="meeting", cascade="all, delete-orphan")
    keypoints = relationship("MeetingKeypoint", back_populates="meeting", cascade="all, delete-orphan")
    todo_items = relationship("TodoItem", back_populates="meeting", cascade="all, delete-orphan")
    issues = relationship("MeetingIssue", back_populates="meeting", cascade="all, delete-orphan")
    post_opinions = relationship("MeetingPostOpinion", back_populates="meeting", cascade="all, delete-orphan")


class MeetingAttachment(Base):
    __tablename__ = "meeting_attachments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))
    is_archived = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    meeting = relationship("Meeting", back_populates="attachments")
    permissions = relationship("MeetingAttachmentPermission", back_populates="attachment", cascade="all, delete-orphan")


class MeetingAttachmentPermission(Base):
    __tablename__ = "meeting_attachment_permissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    attachment_id = Column(Integer, ForeignKey("meeting_attachments.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    attachment = relationship("MeetingAttachment", back_populates="permissions")
    user = relationship("User", foreign_keys=[user_id])


class Transcript(Base):
    """会议转写记录"""
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    segment_id = Column(String(50), unique=True, index=True)
    speaker_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    speaker_name = Column(String(50))
    text = Column(Text, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    audio_path = Column(String(500))
    is_interrupted = Column(Boolean, default=False)  # 是否被打断
    category = Column(String(50))  # 分类标注：决策/讨论/通报
    is_filtered = Column(Boolean, default=False)     # 语气词是否已过滤
    has_sensitive = Column(Boolean, default=False)    # 是否包含敏感词
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    meeting = relationship("Meeting", back_populates="transcripts")
    speaker = relationship("User", foreign_keys=[speaker_id])


class MeetingKeypoint(Base):
    """会议要点"""
    __tablename__ = "meeting_keypoints"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    importance = Column(String(20), default="normal")  # high/medium/low
    source_segment_ids = Column(Text)  # 关联的转写片段ID列表(JSON)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    meeting = relationship("Meeting", back_populates="keypoints")


class MeetingMinutes(Base):
    """会议纪要"""
    __tablename__ = "meeting_minutes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False, index=True)
    title = Column(String(200), default="默认纪要")
    content = Column(Text)  # 纪要内容 (HTML)
    review_conclusion = Column(Text, nullable=True)  # 评审结论
    status = Column(String(20), default="draft")  # draft/reviewing/signed/participant_signing
    reject_reason = Column(Text, nullable=True)  # 驳回原因
    version = Column(Integer, default=1)
    is_primary = Column(Boolean, default=True)
    required_signers = Column(Text, nullable=True)  # 审签人员配置JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    meeting = relationship("Meeting", back_populates="minutes")
    versions = relationship("MinutesVersion", back_populates="minutes", cascade="all, delete-orphan")
    signatures = relationship("MinutesSignature", back_populates="minutes", cascade="all, delete-orphan")


class MinutesVersion(Base):
    """纪要版本历史"""
    __tablename__ = "minutes_versions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    minutes_id = Column(Integer, ForeignKey("meeting_minutes.id"), nullable=False)
    content = Column(Text)
    version = Column(Integer)
    editor_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    minutes = relationship("MeetingMinutes", back_populates="versions")
    editor = relationship("User", foreign_keys=[editor_id])


class MinutesSignature(Base):
    """纪要电子签名"""
    __tablename__ = "minutes_signatures"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    minutes_id = Column(Integer, ForeignKey("meeting_minutes.id"), nullable=False)
    signer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    signer_name = Column(String(100), nullable=True)
    signature_image = Column(Text)  # Base64 签名图片
    sign_step = Column(String(20))  # draft / review / participant_sign
    sign_type = Column(String(20), nullable=True)  # leader_review / participant_sign
    signer_unit = Column(String(200), nullable=True)
    opinion = Column(Text, nullable=True)
    signed_at = Column(DateTime, default=datetime.utcnow)
    hash_value = Column(String(256))

    minutes = relationship("MeetingMinutes", back_populates="signatures")
    signer = relationship("User", foreign_keys=[signer_id])


class MeetingIssue(Base):
    """会议问题记录"""
    __tablename__ = "meeting_issues"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    content = Column(Text, nullable=False)
    reporter_name = Column(String(100))
    # 状态: open/explained/adopted/adopted_resolved/adopted_unresolved
    status = Column(String(30), default="open")
    response = Column(Text, nullable=True)  # 回复/说明内容
    proofread = Column(Boolean, default=False)
    archived = Column(Boolean, default=False)
    submitted = Column(Boolean, default=False)  # 是否已提交到管理端
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    meeting = relationship("Meeting", back_populates="issues")



class MeetingPostOpinion(Base):
    """会后意见录入"""
    __tablename__ = "meeting_post_opinions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    author_name = Column(String(100), nullable=False)
    author_unit = Column(String(200), nullable=True)
    author_role = Column(String(30), default="participant")  # expert/participant/other
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    meeting = relationship("Meeting", back_populates="post_opinions")
    author = relationship("User", foreign_keys=[author_id])
