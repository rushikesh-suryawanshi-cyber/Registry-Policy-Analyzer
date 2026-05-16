import os
from jinja2 import Environment, FileSystemLoader
from typing import List, Dict
from admx_parser.models import Policy
from .strategies import (
    ScriptGenerationStrategy,
    DetectionScriptStrategy,
    RemediationScriptStrategy,
    RollbackScriptStrategy,
    ValidationScriptStrategy,
    RegFileStrategy,
    AIGeneratedScriptStrategy,
    IntuneOMAURIStrategy
)

class ScriptGenerator:
    """Generates PowerShell and REG scripts from Policy models."""
    
    def __init__(self, templates_dir: str = None):
        if not templates_dir:
            # Default to the templates folder relative to this file
            templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
            
        self.env = Environment(loader=FileSystemLoader(templates_dir))

    def generate(self, policy: Policy, strategy: ScriptGenerationStrategy) -> str:
        """Generates a script using the provided strategy."""
        return strategy.generate(policy, self.env)

    def generate_detection_script(self, policy: Policy) -> str:
        return self.generate(policy, DetectionScriptStrategy())

    def generate_remediation_script(self, policy: Policy) -> str:
        return self.generate(policy, RemediationScriptStrategy())

    def generate_rollback_script(self, policy: Policy) -> str:
        return self.generate(policy, RollbackScriptStrategy())

    def generate_validation_script(self, policy: Policy) -> str:
        return self.generate(policy, ValidationScriptStrategy())

    def generate_reg_file(self, policy: Policy) -> str:
        return self.generate(policy, RegFileStrategy())

    def generate_ai_remediation_script(self, policy: Policy, model_name: str = "llama3") -> str:
        return self.generate(policy, AIGeneratedScriptStrategy(model_name=model_name))

    def generate_intune_omauri(self, policy: Policy) -> str:
        return self.generate(policy, IntuneOMAURIStrategy())
