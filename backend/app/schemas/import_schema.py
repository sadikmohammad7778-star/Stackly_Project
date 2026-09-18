from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================================
# Validation Error
# ============================================================

class ImportErrorResponse(BaseModel):
    row_number: int
    error_type: str
    error_message: str


# ============================================================
# Upload Response
# ============================================================

class ImportUploadResponse(BaseModel):
    import_id: int
    import_type: str
    filename: str
    columns: List[str]
    preview: List[Dict[str, Any]]
    total_records: int


# ============================================================
# Validation Request
# ============================================================

class ImportValidateRequest(BaseModel):
    import_id: int


# ============================================================
# Validation Response
# ============================================================

class ImportValidationResponse(BaseModel):
    import_id: int
    total_records: int
    valid_records: int
    invalid_records: int
    duplicate_records: int
    columns: List[str]
    errors: List[ImportErrorResponse] = Field(default_factory=list)


# ============================================================
# Process Request
# ============================================================

class ImportProcessRequest(BaseModel):
    import_id: int


# ============================================================
# Import Result
# ============================================================

class ImportResultResponse(BaseModel):
    import_id: int
    status: str
    total_records: int
    successful_records: int
    failed_records: int
    duplicate_records: int
    validation_failures: int


# ============================================================
# Import History
# ============================================================

class ImportHistoryResponse(BaseModel):
    id: int
    company_id: int
    import_type: str
    filename: str
    uploaded_by: int
    total_records: int
    successful_records: int
    failed_records: int
    duplicate_records: int
    status: str
    created_at: Any
    completed_at: Optional[Any] = None

    class Config:
        from_attributes = True