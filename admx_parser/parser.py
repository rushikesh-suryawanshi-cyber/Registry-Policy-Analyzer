import os
import chardet
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List

from .models import Policy
from .utils import setup_logger, resolve_references, normalize_category, build_complete_gpo_path, get_decimal_value

logger = setup_logger()

class AdmlParser:
    def __init__(self, path: str):
        self.path = Path(path)
        self.resources = {}

    def parse(self) -> Dict[str, str]:
        if self.path.is_file():
            self._parse_file(self.path)
        elif self.path.is_dir():
            for f in self.path.glob('*.adml'):
                self._parse_file(f)
        else:
            logger.error(f"Path not found: {self.path}")
        return self.resources
        
    def _parse_file(self, file_path: Path):
        try:
            with open(file_path, "rb") as f:
                raw_data = f.read(2048)
                encoding = chardet.detect(raw_data).get("encoding", "utf-8")
            with open(file_path, "r", encoding=encoding, errors="replace") as file:
                xml_content = file.read().strip()
            root = ET.fromstring(xml_content)
            ns = {}
            if root.tag.startswith("{"):
                ns_uri = root.tag.split("}")[0][1:]
                ns = {'ns': ns_uri}
                string_table = root.find(".//ns:stringTable", ns)
                strings = string_table.findall("ns:string", ns) if string_table is not None else []
            else:
                string_table = root.find(".//stringTable")
                strings = string_table.findall("string") if string_table is not None else []
                
            if string_table is not None:
                for string_elem in strings:
                    res_id = string_elem.get("id")
                    text = string_elem.text or ""
                    if res_id:
                        self.resources[res_id] = text.strip()
        except Exception as e:
            logger.error(f"Error processing ADML file {file_path}: {e}")

class AdmxParser:
    def __init__(self, path: str, adml_resources: Dict[str, str]):
        self.path = Path(path)
        self.adml_resources = adml_resources
        self.policies = []

    def parse(self) -> List[Policy]:
        if self.path.is_file():
            self._parse_file(self.path)
        elif self.path.is_dir():
            for f in self.path.glob('*.admx'):
                self._parse_file(f)
        else:
            logger.error(f"Path not found: {self.path}")
        return self.policies
        
    def _load_categories(self, root, namespace):
        categories = {}
        cat_root = root.find(f".//{namespace}categories")
        if cat_root is not None:
            for cat in cat_root.findall(f"{namespace}category"):
                name = cat.get("name")
                norm_name = normalize_category(name)
                disp = cat.get("displayName")
                resolved_disp = resolve_references(disp, self.adml_resources) if disp else norm_name
                parent_elem = cat.find(f"{namespace}parentCategory")
                parent_ref = parent_elem.get("ref") if parent_elem is not None else None
                if parent_ref:
                    parent_ref = normalize_category(parent_ref)
                categories[norm_name] = {"displayName": resolved_disp, "parent": parent_ref}
        return categories

    def _parse_file(self, file_path: Path):
        try:
            with open(file_path, "rb") as f:
                raw_data = f.read(1024)
                encoding = chardet.detect(raw_data).get("encoding", "utf-8")
            with open(file_path, "r", encoding=encoding, errors="replace") as file:
                xml_content = file.read().strip()
                
            root = ET.fromstring(xml_content)
            namespace = ""
            if root.tag.startswith("{"):
                namespace = root.tag.split("}")[0] + "}"
                
            categories = self._load_categories(root, namespace)
            
            policies = root.findall(f".//{namespace}policy")
            if not policies:
                return

            for policy in policies:
                policy_data = {
                    "name": policy.get("name"),
                    "class_type": policy.get("class"),
                    "key": policy.get("key"),
                    "value_name": policy.get("valueName"),
                    "display_name": None,
                    "explain_text": None,
                    "gpo_path": None,
                    "enabled_value": get_decimal_value(policy.find(f".//{namespace}enabledValue//{namespace}decimal")),
                    "disabled_value": get_decimal_value(policy.find(f".//{namespace}disabledValue//{namespace}decimal")),
                    "min_value": None,
                    "max_value": None,
                    "enum_data": None,
                    "enabled_list": None,
                    "disabled_list": None,
                    "elements_data": []
                }

                disp = policy.get("displayName")
                expl = policy.get("explainText")
                if disp:
                    policy_data["display_name"] = resolve_references(disp, self.adml_resources)
                else:
                    policy_data["display_name"] = resolve_references(f"$(string.{policy_data['name']})", self.adml_resources)

                if expl:
                    policy_data["explain_text"] = resolve_references(expl, self.adml_resources)
                else:
                    policy_data["explain_text"] = resolve_references(f"$(string.{policy_data['name']}_Explain)", self.adml_resources)

                policy_data["gpo_path"] = build_complete_gpo_path(policy, {"displayName": policy_data["display_name"]}, categories)

                elements = policy.find(f".//{namespace}elements")
                if elements is not None:
                    decimal_elem = elements.find(f".//{namespace}decimal")
                    if decimal_elem is not None:
                        policy_data["min_value"] = int(decimal_elem.get("minValue")) if decimal_elem.get("minValue") else None
                        policy_data["max_value"] = int(decimal_elem.get("maxValue")) if decimal_elem.get("maxValue") else None
                        if not policy_data["value_name"]:
                            policy_data["value_name"] = decimal_elem.get("valueName")
                            
                    text_elem = elements.find(f".//{namespace}text")
                    if text_elem is not None and not policy_data["value_name"]:
                        policy_data["value_name"] = text_elem.get("valueName")

                    enum_elements = elements.findall(f".//{namespace}enum")
                    if enum_elements:
                        enum_data = []
                        for enum in enum_elements:
                            enum_value_name = enum.get("valueName")
                            items = enum.findall(f"{namespace}item")
                            for item in items:
                                display_name = item.get("displayName")
                                resolved_display_name = resolve_references(display_name, self.adml_resources)
                                value = None
                                value_container = item.find(f".//{namespace}value")
                                if value_container is not None:
                                    decimal_element = value_container.find(f".//{namespace}decimal")
                                    if decimal_element is not None:
                                        value = get_decimal_value(decimal_element)
                                enum_entry = {
                                    "displayName": resolved_display_name,
                                    "class": policy_data["class_type"],
                                    "key": policy_data["key"],
                                    "valueName": enum_value_name,
                                    "value": value
                                }
                                enum_data.append(enum_entry)
                        policy_data["enum_data"] = enum_data

                    for element in elements:
                        element_data = {
                            "id": element.get("id"),
                            "type": element.tag.split("}")[-1],
                            "valueName": element.get("valueName"),
                            "required": element.get("required"),
                            "minValue": element.get("minValue"),
                            "maxValue": element.get("maxValue"),
                            "class": policy_data["class_type"],
                            "key": policy_data["key"],
                        }
                        policy_data["elements_data"].append(element_data)
                        
                if not policy_data["elements_data"]:
                    policy_data["elements_data"] = None

                enabled_list = policy.find(f".//{namespace}enabledList")
                if enabled_list is not None:
                    enabled_list_data = []
                    for item in enabled_list.findall(f"{namespace}item"):
                        item_key = item.get("key") or policy_data["key"]
                        item_value_name = item.get("valueName") or policy_data["value_name"]
                        value = None
                        value_container = item.find(f".//{namespace}value")
                        if value_container is not None:
                            decimal_element = value_container.find(f".//{namespace}decimal")
                            if decimal_element is not None:
                                value = get_decimal_value(decimal_element)
                        enabled_list_data.append({
                            "key": item_key,
                            "valueName": item_value_name,
                            "value": value
                        })
                    policy_data["enabled_list"] = enabled_list_data

                disabled_list = policy.find(f".//{namespace}disabledList")
                if disabled_list is not None:
                    disabled_list_data = []
                    for item in disabled_list.findall(f"{namespace}item"):
                        item_key = item.get("key") or policy_data["key"]
                        item_value_name = item.get("valueName") or policy_data["value_name"]
                        value = None
                        value_container = item.find(f".//{namespace}value")
                        if value_container is not None:
                            decimal_element = value_container.find(f".//{namespace}decimal")
                            if decimal_element is not None:
                                value = get_decimal_value(decimal_element)
                        disabled_list_data.append({
                            "key": item_key,
                            "valueName": item_value_name,
                            "value": value
                        })
                    policy_data["disabled_list"] = disabled_list_data

                self.policies.append(Policy(**policy_data))
                
        except ET.ParseError as e:
            logger.error(f"Error parsing XML from {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
