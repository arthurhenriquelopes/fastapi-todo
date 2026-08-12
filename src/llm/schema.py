from pydantic import BaseModel, Field
from enum import Enum

class CategoryEnum(str, Enum):
    billing = "billing"
    bug = "bug"
    feature = "feature"
    other = "other"

class UrgencyEnum(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"

class JobStatusEnum(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class TriageInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    idempotency_key: str | None = None

class TriageOutput(BaseModel):
    category: CategoryEnum
    urgency: UrgencyEnum
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str = Field(..., min_length=1)

class TriageJobResponse(BaseModel):
    job_id: str
    status: JobStatusEnum
    result: TriageOutput | None = None
    error: str | None = None
