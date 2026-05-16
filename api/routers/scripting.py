from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from typing import Optional

from admx_parser.db.repository import PolicyRepository
from admx_parser.scripting.generator import ScriptGenerator
from api.dependencies import get_repository

router = APIRouter(
    prefix="/scripts",
    tags=["Scripting"]
)

generator = ScriptGenerator()

@router.get("/generate/{policy_name}", response_class=PlainTextResponse)
def generate_script(
    policy_name: str,
    script_type: str = "remediation",  # can be detection, remediation, rollback, validation, reg, ai_remediation, intune
    model: str = "llama3", # Only used if script_type is ai_remediation
    db: PolicyRepository = Depends(get_repository)
):
    """
    Generates a script for a specific policy.

    Valid script_type values: detection, remediation, rollback, validation, reg, ai_remediation, intune
    """
    policy = db.get_policy_by_name(policy_name)
    if not policy:
        raise HTTPException(status_code=404, detail=f"Policy '{policy_name}' not found.")

    try:
        if script_type == "detection":
            return generator.generate_detection_script(policy)
        elif script_type == "remediation":
            return generator.generate_remediation_script(policy)
        elif script_type == "rollback":
            return generator.generate_rollback_script(policy)
        elif script_type == "validation":
            return generator.generate_validation_script(policy)
        elif script_type == "reg":
            return generator.generate_reg_file(policy)
        elif script_type == "ai_remediation":
            return generator.generate_ai_remediation_script(policy, model_name=model)
        elif script_type == "intune":
            return generator.generate_intune_omauri(policy)
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid script_type. Must be one of: detection, remediation, rollback, validation, reg, ai_remediation, intune"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating script: {str(e)}")
