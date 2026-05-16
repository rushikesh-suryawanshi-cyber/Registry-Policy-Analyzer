from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from admx_parser.db.repository import PolicyRepository
from ..schemas import PaginatedResponse
from ..dependencies import get_repository

router = APIRouter(
    prefix="/search",
    tags=["search"]
)

@router.get("/keyword", response_model=PaginatedResponse)
def search_by_keyword(
    q: str = Query(..., description='The keyword or phrase to search for. Wrap phrases in double quotes for exact match.', min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort_by: str = Query("rank", description="Field to sort by (rank, name, display_name, gpo_path, key)"),
    sort_order: str = Query("ASC", description="ASC or DESC"),
    repo: PolicyRepository = Depends(get_repository)
):
    """
    Search policies using Full-Text Search across name, display_name, explain_text, and gpo_path.
    """
    try:
        results = repo.advanced_search(
            keyword=q,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database search failed: {str(e)}")

@router.get("/registry", response_model=PaginatedResponse)
def search_by_registry(
    key: Optional[str] = Query(None, description="Partial or exact registry key path"),
    value: Optional[str] = Query(None, description="Partial or exact registry value name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort_by: str = Query("name"),
    sort_order: str = Query("ASC"),
    repo: PolicyRepository = Depends(get_repository)
):
    """
    Search policies that configure a specific registry key or registry value.
    """
    if not key and not value:
        raise HTTPException(status_code=400, detail="Must provide at least 'key' or 'value' parameter.")
        
    try:
        results = repo.advanced_search(
            registry_key=key,
            registry_value=value,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/category", response_model=PaginatedResponse)
def search_by_category(
    path: str = Query(..., description="Partial or exact category path (e.g. 'Windows Components')"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort_by: str = Query("name"),
    sort_order: str = Query("ASC"),
    repo: PolicyRepository = Depends(get_repository)
):
    """
    Search policies by their GPO Category path.
    """
    try:
        results = repo.advanced_search(
            category=path,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vendor", response_model=PaginatedResponse)
def search_by_vendor(
    name: str = Query(..., description="Vendor name or ADMX file origin (e.g. 'Chrome', 'Mozilla')"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort_by: str = Query("name"),
    sort_order: str = Query("ASC"),
    repo: PolicyRepository = Depends(get_repository)
):
    """
    Search policies by Vendor. (Matches against the root category / source context).
    """
    try:
        results = repo.advanced_search(
            vendor=name,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
