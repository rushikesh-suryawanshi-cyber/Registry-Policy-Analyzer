from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class RegistryOperation:
    hive: str  # e.g., 'HKLM', 'HKCU'
    key: str
    value_name: Optional[str]
    action: str  # 'set' or 'remove'
    value_type: Optional[str]  # 'DWORD', 'String', 'MultiString', 'Binary'
    value_data: Any
