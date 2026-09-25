from typing import Optional

from pydantic import BaseModel


class DataQualityIssueUpdate(BaseModel):
    status: str
    resolution_note: Optional[str] = None