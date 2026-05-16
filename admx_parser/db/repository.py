import logging
from typing import List, Dict, Any, Optional
from ..models import Policy

logger = logging.getLogger("admx_parser")

class PolicyRepository:
    """Repository for managing Policy records in SQLite."""
    
    def __init__(self, connection):
        self.conn = connection

    def insert_policy(self, policy: Policy) -> int:
        """Inserts a new Policy into the database and returns its primary key ID."""
        cursor = self.conn.cursor()
        
        # Insert main policy
        cursor.execute("""
            INSERT INTO policies (
                name, class_type, key, value_name, display_name, 
                explain_text, gpo_path, enabled_value, disabled_value, 
                min_value, max_value
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            policy.name, policy.class_type, policy.key, policy.value_name,
            policy.display_name, policy.explain_text, policy.gpo_path,
            policy.enabled_value, policy.disabled_value, policy.min_value, policy.max_value
        ))
        
        policy_id = cursor.lastrowid
        
        # Insert enumData
        if policy.enum_data:
            for enum_item in policy.enum_data:
                cursor.execute("""
                    INSERT INTO policy_values (
                        policy_id, type, display_name, value_name, value
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    policy_id, 'enum', enum_item.get('displayName'), 
                    enum_item.get('valueName'), enum_item.get('value')
                ))
                
        # Insert enabledList
        if policy.enabled_list:
            for item in policy.enabled_list:
                cursor.execute("""
                    INSERT INTO policy_values (
                        policy_id, type, value_name, value
                    ) VALUES (?, ?, ?, ?)
                """, (
                    policy_id, 'enabled_list', item.get('valueName'), item.get('value')
                ))
                
        # Insert disabledList
        if policy.disabled_list:
            for item in policy.disabled_list:
                cursor.execute("""
                    INSERT INTO policy_values (
                        policy_id, type, value_name, value
                    ) VALUES (?, ?, ?, ?)
                """, (
                    policy_id, 'disabled_list', item.get('valueName'), item.get('value')
                ))
                
        # Insert elementsData
        if policy.elements_data:
            for el in policy.elements_data:
                cursor.execute("""
                    INSERT INTO policy_values (
                        policy_id, type, element_id, value_name, required, min_value, max_value
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    policy_id, f"element_{el.get('type')}", el.get('id'), el.get('valueName'),
                    el.get('required'), el.get('minValue'), el.get('maxValue')
                ))
                
        # Add primary registry entry if present
        if policy.key and policy.value_name:
            cursor.execute("""
                INSERT INTO registry_entries (policy_id, key, value_name)
                VALUES (?, ?, ?)
            """, (policy_id, policy.key, policy.value_name))

        return policy_id

    def search_policy(self, query: str) -> List[Dict[str, Any]]:
        """Searches for policies using the FTS5 virtual table."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.id, p.name, p.display_name, p.explain_text, p.gpo_path,
                   snippet(policies_fts, -1, '<b>', '</b>', '...', 64) as snippet
            FROM policies_fts fts
            JOIN policies p ON p.id = fts.rowid
            WHERE policies_fts MATCH ?
            ORDER BY rank
        """, (query,))
        
        return [dict(row) for row in cursor.fetchall()]

    def get_policy(self, policy_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a single policy by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM policies WHERE id = ?", (policy_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_policy(self, policy_id: int, updates: Dict[str, Any]) -> bool:
        """Updates specific fields of a policy."""
        if not updates:
            return False
            
        fields = []
        values = []
        for k, v in updates.items():
            fields.append(f"{k} = ?")
            values.append(v)
            
        values.append(policy_id)
        
        query = f"UPDATE policies SET {', '.join(fields)} WHERE id = ?"
        
        cursor = self.conn.cursor()
        cursor.execute(query, values)
        return cursor.rowcount > 0

    def advanced_search(
        self, 
        keyword: Optional[str] = None, 
        registry_key: Optional[str] = None,
        registry_value: Optional[str] = None,
        category: Optional[str] = None,
        vendor: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "rank",
        sort_order: str = "ASC"
    ) -> Dict[str, Any]:
        """Advanced search supporting FTS5, exact/partial filtering, pagination, and sorting."""
        cursor = self.conn.cursor()
        
        base_query = """
            SELECT p.id, p.name, p.display_name, p.explain_text, p.gpo_path, p.key, p.value_name
            FROM policies p
        """
        
        where_clauses = []
        params = []
        
        if keyword:
            base_query += " JOIN policies_fts fts ON p.id = fts.rowid"
            where_clauses.append("policies_fts MATCH ?")
            params.append(keyword)
            
        if registry_key:
            where_clauses.append("p.key LIKE ?")
            params.append(f"%{registry_key}%")
            
        if registry_value:
            where_clauses.append("p.value_name LIKE ?")
            params.append(f"%{registry_value}%")
            
        if category:
            where_clauses.append("p.gpo_path LIKE ?")
            params.append(f"%{category}%")
            
        if vendor:
            # We don't have a strict 'vendor' column, but vendor is often the root of the gpo_path
            where_clauses.append("p.gpo_path LIKE ?")
            params.append(f"%{vendor}%")
            
        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)
            
        # Count total records for pagination
        count_query = f"SELECT COUNT(*) as total FROM ({base_query})"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()['total']
        
        # Determine sorting
        allowed_sorts = ["name", "display_name", "gpo_path", "key", "rank"]
        if sort_by not in allowed_sorts:
            sort_by = "name"
        if sort_order.upper() not in ["ASC", "DESC"]:
            sort_order = "ASC"
            
        if sort_by == "rank" and not keyword:
            sort_by = "name"
            
        # For rank, order is usually ascending (lower rank = better match in FTS5)
        # But we let the user control it. FTS5 'rank' works automatically.
        base_query += f" ORDER BY {sort_by} {sort_order}"
        
        # Pagination
        offset = (page - 1) * page_size
        base_query += " LIMIT ? OFFSET ?"
        params.extend([page_size, offset])
        
        cursor.execute(base_query, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        return {
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "items": results
        }
        """Deletes a policy. Associated values/tags are deleted via CASCADE."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM policies WHERE id = ?", (policy_id,))
        return cursor.rowcount > 0
