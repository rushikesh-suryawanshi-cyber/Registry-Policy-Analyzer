import os
from typing import List, Dict
from admx_parser.models import Policy
from admx_parser.scripting.models import RegistryOperation

class PolicyMapper:
    """Translates a Policy object into an internal Action Model."""

    @staticmethod
    def convert_policy_to_operations(policy: Policy) -> List[RegistryOperation]:
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

    @staticmethod
    def get_grouped_operations(operations: List[RegistryOperation]) -> Dict[str, List[RegistryOperation]]:
        grouped = {}
        for op in operations:
            hive_full = "HKEY_LOCAL_MACHINE" if op.hive == "HKLM" else "HKEY_CURRENT_USER"
            key_group = f"{hive_full}\\{op.key}"
            if key_group not in grouped:
                grouped[key_group] = []
            grouped[key_group].append(op)
        return grouped
