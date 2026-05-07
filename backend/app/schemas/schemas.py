"""
Pydantic schemas for request and response payloads.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ResponseBase(BaseModel):
    code: int = 200
    message: str = "success"


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class PaginatedResponse(ResponseBase):
    total: int = 0
    page: int = 1
    page_size: int = 20


class UserBase(BaseModel):
    username: str
    real_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    professional_title: Optional[str] = None
    id_card_number: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserInfo(UserBase):
    id: int
    avatar: Optional[str] = None
    is_active: bool = True
    is_participant_only: bool = False
    is_expert: bool = False

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = None
    meeting_type: str = "regular"
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    has_review_fee: bool = False
    welcome_message: Optional[str] = None
    welcome_theme: str = "aurora"


class MeetingCreate(MeetingBase):
    participant_ids: List[int] = []
    seat_layout: Optional[str] = None


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    meeting_type: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    participant_ids: Optional[List[int]] = None
    agenda: Optional[str] = None
    seat_layout: Optional[str] = None
    has_review_fee: Optional[bool] = None
    welcome_message: Optional[str] = None
    welcome_theme: Optional[str] = None
    expert_ids: Optional[List[int]] = None
    leader_id: Optional[int] = None


class ParticipantWithStatus(UserInfo):
    checked_in: bool = False
    check_in_time: Optional[datetime] = None
    signature_image: Optional[str] = None
    signature_status: str = "none"
    fee_signature_image: Optional[str] = None
    fee_id_card: Optional[str] = None
    fee_bank_card: Optional[str] = None
    role: str = "participant"
    sort_order: int = 0
    is_expert_in_meeting: bool = False
    is_leader: bool = False


class AttachmentInfo(BaseModel):
    id: int
    meeting_id: int
    filename: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    is_archived: bool = False
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AttachmentPermissionUpdate(BaseModel):
    user_ids: List[int] = []


class SeatLayoutUpdate(BaseModel):
    seat_layout: str


class AttachmentArchiveUpdate(BaseModel):
    attachment_ids: List[int] = []


class MeetingInfo(MeetingBase):
    id: int
    meeting_code: Optional[str] = None
    status: str
    creator_id: int
    issue_review_status: str = "pending"
    issue_review_require_sign: bool = False
    agenda: Optional[str] = None
    seat_layout: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime
    participants: List[UserInfo] = []

    class Config:
        from_attributes = True


class MeetingListResponse(PaginatedResponse):
    data: List[MeetingInfo] = []
    status_counts: dict = {}


class ConflictCheckRequest(BaseModel):
    participant_ids: List[int]
    start_time: datetime
    end_time: datetime
    exclude_meeting_id: Optional[int] = None


class ConflictInfo(BaseModel):
    user_id: int
    user_name: str
    conflict_meeting: str
    conflict_time: str


class TranscriptInfo(BaseModel):
    id: int
    segment_id: str
    speaker_id: Optional[int] = None
    speaker_name: Optional[str] = None
    text: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_interrupted: bool = False
    category: Optional[str] = None
    has_sensitive: bool = False

    class Config:
        from_attributes = True


class TranscriptCreate(BaseModel):
    segment_id: str
    speaker_name: Optional[str] = "未识别"
    text: str
    category: Optional[str] = None
    start_time: Optional[str] = None  # ISO format string


class TranscriptUpdate(BaseModel):
    text: Optional[str] = None
    category: Optional[str] = None


class KeypointInfo(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    importance: str = "normal"
    source_segment_ids: Optional[str] = None
    sort_order: int = 0

    class Config:
        from_attributes = True


class KeypointGenerateRequest(BaseModel):
    strategy: str = "by_topic"


class MinutesInfo(BaseModel):
    id: int
    meeting_id: int
    title: str = "默认纪要"
    content: Optional[str] = None
    review_conclusion: Optional[str] = None
    status: str = "draft"
    reject_reason: Optional[str] = None
    version: int = 1
    is_primary: bool = True
    required_signers: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MinutesUpdate(BaseModel):
    title: Optional[str] = None
    content: str
    review_conclusion: Optional[str] = None


class MinutesCreateRequest(BaseModel):
    title: Optional[str] = None
    make_primary: bool = False


class MinutesPublishRequest(BaseModel):
    minutes_id: Optional[int] = None
    required_signers: Optional[List[dict]] = None


class MinutesVersionInfo(BaseModel):
    id: int
    version: int
    editor_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SignatureSubmit(BaseModel):
    signature_image: str
    sign_step: str = "draft"


class PublicSignRequest(BaseModel):
    signature_image: str
    signer_name: str
    signer_unit: Optional[str] = None
    opinion: Optional[str] = None


class RejectMinutesRequest(BaseModel):
    reason: Optional[str] = None


class SignatureInfo(BaseModel):
    id: int
    sign_step: str
    sign_type: Optional[str] = None
    signer_id: Optional[int] = None
    signer_name: Optional[str] = None
    signer_unit: Optional[str] = None
    opinion: Optional[str] = None
    signed_at: datetime

    class Config:
        from_attributes = True


class MinutesFullInfo(MinutesInfo):
    signatures: List[SignatureInfo] = []

    class Config:
        from_attributes = True


class PolishRequest(BaseModel):
    text: str
    style: str = "formal"


class TTSRequest(BaseModel):
    text: str
    voice: str = "default"


class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_id: int
    priority: str = "medium"
    due_date: Optional[datetime] = None
    meeting_id: Optional[int] = None


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None


class TodoInfo(TodoBase):
    id: int
    status: str
    creator_id: int
    completed_at: Optional[datetime] = None
    flow_binding_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TodoListResponse(PaginatedResponse):
    data: List[TodoInfo] = []


class BindFlowRequest(BaseModel):
    flow_node_id: str
    flow_type: str


class TrackStats(BaseModel):
    total: int = 0
    completed: int = 0
    in_progress: int = 0
    overdue: int = 0
    completion_rate: float = 0.0


class GanttItem(BaseModel):
    id: int
    title: str
    assignee: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    progress: float = 0.0
    status: str


class ArchiveSearchRequest(BaseModel):
    keyword: str = ""
    search_mode: str = "keyword"
    meeting_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    participant_ids: Optional[List[int]] = None
    page: int = 1
    page_size: int = 20


class ArchiveInfo(BaseModel):
    id: int
    title: str
    meeting_type: str
    start_time: datetime
    end_time: datetime
    summary: Optional[str] = None
    participants: List[UserInfo] = []

    class Config:
        from_attributes = True


class BatchExportRequest(BaseModel):
    meeting_ids: List[int]
    include_minutes: bool = True
    include_recordings: bool = False
    include_transcripts: bool = True


class MeetingIssueCreate(BaseModel):
    content: str
    reporter_name: Optional[str] = None
    submitted: bool = False


class MeetingIssueUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None
    response: Optional[str] = None
    proofread: Optional[bool] = None
    archived: Optional[bool] = None


class IssueReviewFlowUpdate(BaseModel):
    issue_review_status: str
    issue_review_require_sign: Optional[bool] = None


class MeetingIssueInfo(BaseModel):
    id: int
    meeting_id: int
    content: str
    reporter_name: Optional[str] = None
    status: str = "open"
    response: Optional[str] = None
    proofread: bool = False
    archived: bool = False
    submitted: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostOpinionCreate(BaseModel):
    author_id: Optional[int] = None
    author_name: str
    author_unit: Optional[str] = None
    author_role: str = "participant"
    content: str


class PostOpinionInfo(BaseModel):
    id: int
    meeting_id: int
    author_id: Optional[int] = None
    author_name: str
    author_unit: Optional[str] = None
    author_role: str = "participant"
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
