from typing import Optional, Literal, Any, List
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from typing import Literal
from pydantic import BaseModel



class IntegrationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)

    source_type: Literal["csv", "postgresql", "rest_api"]

    connection_config: dict[str, Any] = Field(default_factory=dict)

    target_module: Literal["products", "customers", "sales", "inventory"]

    sync_strategy: Literal["insert", "update", "skip", "reject"] = "insert"

    credentials: Optional[dict[str, str]] = None


class IntegrationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)

    connection_config: Optional[dict[str, Any]] = None

    target_module: Optional[
        Literal["products", "customers", "sales", "inventory"]
    ] = None

    sync_strategy: Optional[
        Literal["insert", "update", "skip", "reject"]
    ] = None

    is_enabled: Optional[bool] = None

    credentials: Optional[dict[str, str]] = None


class IntegrationResponse(BaseModel):
    id: int
    company_id: int
    created_by: int
    name: str
    source_type: str
    connection_config: dict[str, Any]
    target_module: str
    sync_strategy: str
    status: str
    is_enabled: bool
    last_sync_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class IntegrationUploadResponse(BaseModel):
    integration_id: int
    filename: str
    total_rows: int
    columns: List[str]
    preview: List[dict[str, Any]]
    message: str


class IntegrationPreviewResponse(BaseModel):
    integration_id: int
    filename: str
    total_rows: int
    columns: List[str]
    preview: List[dict[str, Any]]


class IntegrationTestResponse(BaseModel):
    integration_id: int
    status: str
    message: str


class IntegrationMappingItem(BaseModel):
    source_field: str = Field(..., min_length=1, max_length=150)
    target_field: str = Field(..., min_length=1, max_length=150)
    is_required: bool = False
    transformation_config: Optional[dict[str, Any]] = None


class IntegrationMappingUpdate(BaseModel):
    mappings: List[IntegrationMappingItem]


class IntegrationMappingResponse(BaseModel):
    id: int
    integration_id: int
    source_field: str
    target_field: str
    source_type: Optional[str] = None
    target_type: str
    is_required: bool
    is_active: bool
    transformation_config: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class IntegrationSyncResponse(BaseModel):
    message: str
    sync_id: int
    status: str
    total_records: int
    processed_records: int
    inserted_records: int
    updated_records: int
    skipped_records: int
    failed_records: int
    duration_ms: Optional[int] = None


class IntegrationSyncHistoryItem(BaseModel):
    id: int
    integration_id: int
    company_id: int
    triggered_by: Optional[int] = None
    trigger_type: str
    status: str
    total_records: int
    processed_records: int
    inserted_records: int
    updated_records: int
    skipped_records: int
    failed_records: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    error_summary: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class IntegrationSyncHistoryResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[IntegrationSyncHistoryItem]


class IntegrationSyncDetailResponse(IntegrationSyncHistoryItem):
    execution_metadata: Optional[str] = None


class IntegrationSyncErrorResponse(BaseModel):
    id: int
    sync_id: int
    source_record_id: Optional[str] = None
    row_number: Optional[int] = None
    error_category: str
    error_message: str
    source_data: Optional[dict] = None
    retry_status: str
    retry_count: int
    is_retryable: bool
    last_retry_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class IntegrationSyncErrorListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[IntegrationSyncErrorResponse]


from datetime import datetime, time
from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict, Field


class IntegrationScheduleCreate(BaseModel):
    frequency: Literal["daily", "weekly"]
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    scheduled_time: time
    timezone: str = "Asia/Kolkata"
    is_active: bool = True


class IntegrationScheduleUpdate(BaseModel):
    frequency: Optional[Literal["daily", "weekly"]] = None
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    scheduled_time: Optional[time] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None


class IntegrationScheduleResponse(BaseModel):
    id: int
    integration_id: int
    frequency: str
    day_of_week: Optional[int] = None
    scheduled_time: Optional[time] = None
    timezone: str
    cron_expression: Optional[str] = None
    is_active: bool
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    last_run_status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class IntegrationSyncRequest(BaseModel):
    trigger_type: Literal[
        "manual",
        "scheduled",
        "initial",
        "incremental"
    ] = "manual"