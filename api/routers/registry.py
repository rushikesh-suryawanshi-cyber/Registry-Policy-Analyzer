from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from admx_parser.db.repository import PolicyRepository
from ..dependencies import get_repository

router = APIRouter(
    prefix="/registry",
    tags=["registry"]
)


@router.get("/hives")
def get_hives(repo: PolicyRepository = Depends(get_repository)):
    """
    Returns the top-level registry hives that have policies configured.
    e.g. ['HKEY_LOCAL_MACHINE', 'HKEY_CURRENT_USER']
    """
    cursor = repo.conn.cursor()
    cursor.execute("""
        SELECT DISTINCT
            CASE 
                WHEN key LIKE 'HKEY_LOCAL_MACHINE%' OR key LIKE 'Software\\%' OR key LIKE 'System\\%' THEN 'HKEY_LOCAL_MACHINE'
                WHEN key LIKE 'HKEY_CURRENT_USER%' THEN 'HKEY_CURRENT_USER'
                WHEN key LIKE 'HKEY_USERS%' THEN 'HKEY_USERS'
                WHEN key LIKE 'HKEY_CLASSES_ROOT%' THEN 'HKEY_CLASSES_ROOT'
                ELSE 'HKEY_LOCAL_MACHINE'
            END as hive
        FROM policies
        WHERE key IS NOT NULL AND key != ''
        ORDER BY hive
    """)
    hives = [row['hive'] for row in cursor.fetchall()]
    return {"hives": list(set(hives))}


@router.get("/children")
def get_children(
    path: str = Query(..., description="Registry key path to get children for (e.g. 'Software\\Policies')"),
    repo: PolicyRepository = Depends(get_repository)
):
    """
    Returns the immediate child segments of a registry key path.
    Used to lazily expand the registry tree.
    """
    cursor = repo.conn.cursor()

    HIVES = [
        "HKEY_LOCAL_MACHINE",
        "HKEY_CURRENT_USER",
        "HKEY_USERS",
        "HKEY_CLASSES_ROOT",
    ]

    # Normalize path — strip leading hive names so DB keys match
    normalized = path
    for hive in HIVES:
        # Handle both 'HIVE\\subkey' and just 'HIVE' (root)
        if normalized.upper() == hive.upper():
            normalized = ""  # at hive root — return top-level segments
            break
        if normalized.upper().startswith(hive.upper() + "\\"):
            normalized = normalized[len(hive) + 1:]  # +1 for the backslash
            break

    if normalized == "":
        # At hive root — get all distinct top-level key segments
        cursor.execute("""
            SELECT DISTINCT key FROM policies
            WHERE key IS NOT NULL AND key != ''
            ORDER BY key
            LIMIT 1000
        """)
        rows = cursor.fetchall()
        children = set()
        for row in rows:
            first_segment = row['key'].split("\\")[0]
            if first_segment:
                children.add(first_segment)
        return {
            "path": path,
            "children": sorted(list(children)),
            "has_policies": False
        }

    # Find all keys that start with this path prefix
    cursor.execute("""
        SELECT DISTINCT key FROM policies
        WHERE key IS NOT NULL AND key != ''
          AND (key LIKE ? OR key = ?)
        ORDER BY key
        LIMIT 2000
    """, (f"{normalized}\\%", normalized))

    rows = cursor.fetchall()
    children = set()

    prefix_len = len(normalized) + 1  # +1 for the backslash

    for row in rows:
        key = row['key']
        if key.upper() == normalized.upper():
            continue  # exact match — no child
        if not key.upper().startswith(normalized.upper() + "\\"):
            continue
        remainder = key[prefix_len:]
        # Take only the next segment
        next_segment = remainder.split("\\")[0]
        if next_segment:
            children.add(next_segment)

    # Also check if exact path match yields policies (leaf node)
    cursor.execute("""
        SELECT COUNT(*) as cnt FROM policies
        WHERE key LIKE ? OR key = ?
    """, (f"{normalized}\\%", normalized))
    has_policies = cursor.fetchone()['cnt'] > 0

    return {
        "path": path,
        "children": sorted(list(children)),
        "has_policies": has_policies
    }


@router.get("/policies")
def get_policies_for_key(
    key: str = Query(..., description="Exact or prefix registry key path to fetch policies for"),
    exact: bool = Query(False, description="If true, match only the exact key. If false, match key and all sub-keys."),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=200),
    repo: PolicyRepository = Depends(get_repository)
):
    """
    Returns all policies that configure a specific registry key path.
    """
    cursor = repo.conn.cursor()

    # Normalize — strip leading hive prefix
    normalized = key
    for hive in ["HKEY_LOCAL_MACHINE\\", "HKEY_CURRENT_USER\\", "HKEY_USERS\\", "HKEY_CLASSES_ROOT\\"]:
        if normalized.upper().startswith(hive.upper()):
            normalized = normalized[len(hive):]
            break

    if exact:
        cursor.execute("""
            SELECT id, name, display_name, explain_text, gpo_path, key, value_name, class_type
            FROM policies
            WHERE key = ?
            ORDER BY name
            LIMIT ? OFFSET ?
        """, (normalized, page_size, (page - 1) * page_size))
    else:
        cursor.execute("""
            SELECT id, name, display_name, explain_text, gpo_path, key, value_name, class_type
            FROM policies
            WHERE key = ? OR key LIKE ?
            ORDER BY name
            LIMIT ? OFFSET ?
        """, (normalized, f"{normalized}\\%", page_size, (page - 1) * page_size))

    rows = [dict(r) for r in cursor.fetchall()]

    # Count
    if exact:
        cursor.execute("SELECT COUNT(*) as cnt FROM policies WHERE key = ?", (normalized,))
    else:
        cursor.execute("SELECT COUNT(*) as cnt FROM policies WHERE key = ? OR key LIKE ?",
                       (normalized, f"{normalized}\\%"))
    total = cursor.fetchone()['cnt']

    return {
        "key": key,
        "total_count": total,
        "page": page,
        "page_size": page_size,
        "items": rows
    }


@router.get("/stats")
def get_registry_stats(repo: PolicyRepository = Depends(get_repository)):
    """Returns high-level registry statistics."""
    cursor = repo.conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT key) as unique_keys FROM policies WHERE key IS NOT NULL AND key != ''")
    unique_keys = cursor.fetchone()['unique_keys']
    cursor.execute("SELECT COUNT(*) as total FROM policies WHERE key IS NOT NULL AND key != ''")
    total_policies = cursor.fetchone()['total']
    return {"unique_keys": unique_keys, "total_policies": total_policies}
