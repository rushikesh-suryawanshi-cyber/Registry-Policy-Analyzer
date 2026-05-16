from typing import Dict, Any
from abc import ABC, abstractmethod
from admx_parser.models import Policy
from admx_parser.scripting.mapper import PolicyMapper
from admx_parser.scripting.exceptions import PolicyValidationError, TemplateNotFoundError, ScriptGenerationError
from jinja2 import Environment
from jinja2.exceptions import TemplateNotFound
from langchain_community.llms import Ollama

class ScriptGenerationStrategy(ABC):

    def _validate_policy(self, policy: Policy):
        if not policy:
            raise PolicyValidationError("Policy object cannot be None.")
        if not policy.name:
            raise PolicyValidationError("Policy must have a 'name' attribute.")

    def _get_template(self, env: Environment, template_name: str):
        try:
            return env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFoundError(f"Template '{template_name}' not found in the configured templates directory.")
        except Exception as e:
            raise ScriptGenerationError(f"Error loading template '{template_name}': {e}")

    @abstractmethod
    def generate(self, policy: Policy, env: Environment) -> str:
        pass

class DetectionScriptStrategy(ScriptGenerationStrategy):
    def generate(self, policy: Policy, env: Environment) -> str:
        self._validate_policy(policy)
        template = self._get_template(env, 'detection.ps1.j2')
        ops = PolicyMapper.convert_policy_to_operations(policy)
        return template.render(policy_name=policy.name, operations=ops)

class RemediationScriptStrategy(ScriptGenerationStrategy):
    def generate(self, policy: Policy, env: Environment) -> str:
        self._validate_policy(policy)
        template = self._get_template(env, 'remediation.ps1.j2')
        ops = PolicyMapper.convert_policy_to_operations(policy)
        return template.render(policy_name=policy.name, operations=ops)

class RollbackScriptStrategy(ScriptGenerationStrategy):
    def generate(self, policy: Policy, env: Environment) -> str:
        self._validate_policy(policy)
        template = self._get_template(env, 'rollback.ps1.j2')
        return template.render(policy_name=policy.name)

class ValidationScriptStrategy(ScriptGenerationStrategy):
    def generate(self, policy: Policy, env: Environment) -> str:
        self._validate_policy(policy)
        template = self._get_template(env, 'validation.ps1.j2')
        ops = PolicyMapper.convert_policy_to_operations(policy)
        return template.render(policy_name=policy.name, operations=ops)

class RegFileStrategy(ScriptGenerationStrategy):
    def generate(self, policy: Policy, env: Environment) -> str:
        self._validate_policy(policy)
        template = self._get_template(env, 'reg_file.reg.j2')
        ops = PolicyMapper.convert_policy_to_operations(policy)
        grouped = PolicyMapper.get_grouped_operations(ops)
        return template.render(grouped_operations=grouped)

class IntuneOMAURIStrategy(ScriptGenerationStrategy):
    def generate(self, policy: Policy, env: Environment) -> str:
        self._validate_policy(policy)
        ops = PolicyMapper.convert_policy_to_operations(policy)

        output = [
            f"Intune Custom Configuration Profile (OMA-URI) for: {policy.name}",
            f"Description: {policy.display_name or policy.name}",
            "-" * 60
        ]

        if not ops:
            output.append("No registry operations found to map to OMA-URI.")
            return "\n".join(output)

        for idx, op in enumerate(ops, 1):
            # A rough mapping to ADMX-backed OMA-URI formats for demonstration
            # The actual OMA-URI path depends heavily on the specific ADMX ingestion,
            # but this provides the structured data an admin needs to build the profile.
            data_type = op.value_type if op.value_type else 'Integer'
            if data_type.upper() == 'DWORD':
                data_type = 'Integer'

            output.extend([
                f"Row {idx}:",
                f"  Name: {op.value_name or op.key.split(r'\\')[-1]}",
                f"  OMA-URI Path: ./Device/Vendor/MSFT/Policy/Config/Operations/{op.key.replace(r'\\', '/')}/{op.value_name or 'default'}",
                f"  Data Type: {data_type}",
                f"  Value: {op.value_data}",
                ""
            ])

        return "\n".join(output)

class AIGeneratedScriptStrategy(ScriptGenerationStrategy):
    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name

    def generate(self, policy: Policy, env: Environment) -> str:
        self._validate_policy(policy)
        ops = PolicyMapper.convert_policy_to_operations(policy)

        operations_desc = []
        for op in ops:
            hive_str = "HKEY_LOCAL_MACHINE" if op.hive == "HKLM" else "HKEY_CURRENT_USER"
            operations_desc.append(
                f"- Set value '{op.value_name}' in key '{hive_str}\\{op.key}' to {op.value_data} (Type: {op.value_type})"
            )

        ops_str = "\n".join(operations_desc)

        prompt = f"""You are an expert Windows systems administrator and PowerShell scripter.
Write a production-ready PowerShell remediation script to enforce the following Group Policy.

Policy Name: {policy.name}
Display Name: {policy.display_name}
Description: {policy.explain_text}

The script MUST perform the following registry operations:
{ops_str}

Requirements:
1. Ensure the registry keys exist before attempting to set values. Create them if necessary.
2. Use standard PowerShell cmdlets (e.g., Test-Path, New-Item, Set-ItemProperty).
3. Include brief comments explaining the actions.
4. Output ONLY the raw PowerShell script code, no markdown wrapping, no explanations before or after.
"""

        llm = Ollama(model=self.model_name)
        try:
            return llm.invoke(prompt).strip()
        except Exception as e:
            raise ScriptGenerationError(f"Failed to generate script using Ollama model '{self.model_name}': {e}")
