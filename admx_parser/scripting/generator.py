import os
from jinja2 import Environment, FileSystemLoader
from typing import List, Dict
from admx_parser.models import Policy
from .models import RegistryOperation

class ScriptGenerator:
    """Generates PowerShell and REG scripts from Policy models."""
    
    def __init__(self, templates_dir: str = None):
        if not templates_dir:
            # Default to the templates folder relative to this file
            templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
            
        self.env = Environment(loader=FileSystemLoader(templates_dir))

    def _convert_policy_to_operations(self, policy: Policy) -> List[RegistryOperation]:
        """Translates a Policy object into an internal Action Model."""
        operations = []
        
        hive = "HKLM" if policy.class_type and policy.class_type.lower() == "machine" else "HKCU"
        key = policy.key
        
        if policy.enabled_value is not None and policy.value_name:
            operations.append(RegistryOperation(
                hive=hive,
                key=key,
                value_name=policy.value_name,
                action='set',
                value_type='DWORD',
                value_data=policy.enabled_value
            ))
            
        if policy.enum_data:
            for item in policy.enum_data:
                # Naive typing: if value is integer, assume DWORD, else String
                v_type = 'DWORD' if isinstance(item.get("value"), int) else 'String'
                operations.append(RegistryOperation(
                    hive=hive,
                    key=item.get("key") or key,
                    value_name=item.get("valueName"),
                    action='set',
                    value_type=v_type,
                    value_data=item.get("value")
                ))
                
        # If no explicit enabled values are found, attempt to use the key/valueName if set
        if not operations and key and policy.value_name:
            # Assume 1 for enabled if not specified (common default for ADMX policies)
            operations.append(RegistryOperation(
                hive=hive,
                key=key,
                value_name=policy.value_name,
                action='set',
                value_type='DWORD',
                value_data=1
            ))
            
        return operations

    def _get_grouped_operations(self, operations: List[RegistryOperation]) -> Dict[str, List[RegistryOperation]]:
        grouped = {}
        for op in operations:
            hive_full = "HKEY_LOCAL_MACHINE" if op.hive == "HKLM" else "HKEY_CURRENT_USER"
            key_group = f"{hive_full}\\{op.key}"
            if key_group not in grouped:
                grouped[key_group] = []
            grouped[key_group].append(op)
        return grouped

    def generate_detection_script(self, policy: Policy) -> str:
        template = self.env.get_template('detection.ps1.j2')
        ops = self._convert_policy_to_operations(policy)
        return template.render(policy_name=policy.name, operations=ops)

    def generate_remediation_script(self, policy: Policy) -> str:
        template = self.env.get_template('remediation.ps1.j2')
        ops = self._convert_policy_to_operations(policy)
        return template.render(policy_name=policy.name, operations=ops)

    def generate_rollback_script(self, policy: Policy) -> str:
        template = self.env.get_template('rollback.ps1.j2')
        return template.render(policy_name=policy.name)

    def generate_validation_script(self, policy: Policy) -> str:
        template = self.env.get_template('validation.ps1.j2')
        ops = self._convert_policy_to_operations(policy)
        return template.render(policy_name=policy.name, operations=ops)

    def generate_reg_file(self, policy: Policy) -> str:
        template = self.env.get_template('reg_file.reg.j2')
        ops = self._convert_policy_to_operations(policy)
        grouped = self._get_grouped_operations(ops)
        return template.render(grouped_operations=grouped)
