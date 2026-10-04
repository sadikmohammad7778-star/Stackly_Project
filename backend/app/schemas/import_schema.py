from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ImportErrorResponse(BaseModel):
    row_number: int
    error_type: str
    error_message: str
    record_data: Optional[str] = None
    status: str = "Failed"


class ImportUploadResponse(BaseModel):
    import_id: int
    import_type: str
    filename: str
    columns: List[str]
    preview: List[Dict[str, Any]]
    total_records: int
    status: str = "Uploaded"


class ImportValidateRequest(BaseModel):
    import_id: int


class ImportValidationResponse(BaseModel):
    import_id: int
    status: str
    total_records: int
    valid_records: int
    invalid_records: int
    duplicate_records: int
    skipped_records: int = 0
    columns: List[str]
    errors: List[ImportErrorResponse] = Field(default_factory=list)


class ImportProcessRequest(BaseModel):
    import_id: int


class ImportResultResponse(BaseModel):
    import_id: int
    status: str
    total_records: int
    valid_records: int
    successful_records: int
    failed_records: int
    duplicate_records: int
    skipped_records: int
    processed_records: int
    progress_percentage: int
    validation_failures: int


class ImportHistoryResponse(BaseModel):
    id: int
    company_id: int
    import_type: str
    filename: str
    uploaded_by: int
    total_records: int
    valid_records: int
    successful_records: int
    failed_records: int
    duplicate_records: int
    skipped_records: int
    processed_records: int
    progress_percentage: int
    status: str
    created_at: Any
    started_at: Optional[Any] = None
    completed_at: Optional[Any] = None
    processing_duration: Optional[int] = None

    class Config:
        from_attributes = True


class ImportStatusResponse(BaseModel):
    import_id: int
    status: str
    total_records: int
    valid_records: int
    successful_records: int
    failed_records: int
    duplicate_records: int
    skipped_records: int
    processed_records: int
    progress_percentage: int
    started_at: Optional[Any] = None
    completed_at: Optional[Any] = None
    processing_duration: Optional[int] = None


class ImportDetailResponse(BaseModel):
    import_id: int
    company_id: int
    import_type: str
    filename: str
    uploaded_by: int
    total_records: int
    valid_records: int
    successful_records: int
    failed_records: int
    duplicate_records: int
    skipped_records: int
    processed_records: int
    progress_percentage: int
    status: str
    created_at: Any
    started_at: Optional[Any] = None
    completed_at: Optional[Any] = None
    processing_duration: Optional[int] = None
    errors: List[ImportErrorResponse] = Field(default_factory=list)

class ImportCancelResponse(BaseModel):
    import_id: int
    status: str
    message: str    