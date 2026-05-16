from typing import Dict, Any
from abc import ABC, abstractmethod
from admx_parser.models import Policy
from admx_parser.scripting.mapper import PolicyMapper
from admx_parser.scripting.exceptions import PolicyValidationError, TemplateNotFoundError, ScriptGenerationError
from jinja2 import Environment
from jinja2.exceptions import TemplateNotFound

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
