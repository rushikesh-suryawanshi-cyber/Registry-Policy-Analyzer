from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

@dataclass
class Policy:
    name: Optional[str]
    class_type: Optional[str]
    key: Optional[str] = None
    value_name: Optional[str] = None
    display_name: Optional[str] = None
    explain_text: Optional[str] = None
    gpo_path: Optional[str] = None
    enabled_value: Optional[int] = None
    disabled_value: Optional[int] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    enum_data: Optional[List[Dict[str, Any]]] = None
    enabled_list: Optional[List[Dict[str, Any]]] = None
    disabled_list: Optional[List[Dict[str, Any]]] = None
    elements_data: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "class": self.class_type,
            "key": self.key,
            "valueName": self.value_name,
            "displayName": self.display_name,
            "explainText": self.explain_text,
            "gpoPath": self.gpo_path,
            "enabledValue": self.enabled_value,
            "disabledValue": self.disabled_value,
            "minValue": self.min_value,
            "maxValue": self.max_value,
            "enumData": self.enum_data,
            "enabledList": self.enabled_list,
            "disabledList": self.disabled_list,
            "elementsData": self.elements_data
        }
