from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


@dataclass
class FieldChange:
    """Represents a single field-level change within a policy."""
    field: str
    old_value: Any
    new_value: Any

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }


@dataclass
class PolicyDiff:
    """Represents the diff state for a single policy."""
    policy_name: str
    change_type: str  # 'added', 'removed', 'modified'
    display_name: Optional[str] = None
    gpo_path: Optional[str] = None
    field_changes: List[FieldChange] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "policy_name": self.policy_name,
            "change_type": self.change_type,
            "display_name": self.display_name,
            "gpo_path": self.gpo_path,
        }
        if self.field_changes:
            d["changes"] = [c.to_dict() for c in self.field_changes]
        return d


@dataclass
class DatasetDiff:
    """Top-level diff result between two policy datasets."""
    old_source: str
    new_source: str
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    added: List[PolicyDiff] = field(default_factory=list)
    removed: List[PolicyDiff] = field(default_factory=list)
    modified: List[PolicyDiff] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.removed) + len(self.modified)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "old_source": self.old_source,
            "new_source": self.new_source,
            "generated_at": self.generated_at,
            "summary": {
                "total_changes": self.total_changes,
                "added_count": len(self.added),
                "removed_count": len(self.removed),
                "modified_count": len(self.modified),
            },
            "added": [p.to_dict() for p in self.added],
            "removed": [p.to_dict() for p in self.removed],
            "modified": [p.to_dict() for p in self.modified],
        }
