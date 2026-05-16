from pydantic import BaseModel
from typing import List, Optional

class PolicyResponse(BaseModel):
    id: int
    name: str
    display_name: Optional[str] = None
    explain_text: Optional[str] = None
    gpo_path: Optional[str] = None
    key: Optional[str] = None
    value_name: Optional[str] = None

class PaginatedResponse(BaseModel):
    total_count: int
    page: int
    page_size: int
    items: List[PolicyResponse]
