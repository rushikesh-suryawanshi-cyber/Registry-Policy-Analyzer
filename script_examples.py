import os
import json
from admx_parser.models import Policy
from admx_parser.scripting.generator import ScriptGenerator

def main():
    json_path = "examples/output.json"
    output_dir = "generated_scripts"
    
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return
        
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    policies_data = data.get("policies", [])
    if not policies_data:
        print("No policies found in JSON.")
        return
        
    # Find an interesting policy, e.g., one with enums or values, or just the first one
    policy_dict = next((p for p in policies_data if p.get('enumData')), policies_data[0])
    
    policy = Policy(
        name=policy_dict.get("name"),
        class_type=policy_dict.get("class"),
        key=policy_dict.get("key"),
        value_name=policy_dict.get("valueName"),
        display_name=policy_dict.get("displayName"),
        explain_text=policy_dict.get("explainText"),
        gpo_path=policy_dict.get("gpoPath"),
        enabled_value=policy_dict.get("enabledValue"),
        disabled_value=policy_dict.get("disabledValue"),
        min_value=policy_dict.get("minValue"),
        max_value=policy_dict.get("maxValue"),
        enum_data=policy_dict.get("enumData"),
        enabled_list=policy_dict.get("enabledList"),
        disabled_list=policy_dict.get("disabledList"),
        elements_data=policy_dict.get("elementsData")
    )

    print(f"Generating scripts for Policy: {policy.name}")
    
    os.makedirs(output_dir, exist_ok=True)
    generator = ScriptGenerator()
    
    # 1. Detection
    detect_script = generator.generate_detection_script(policy)
    with open(os.path.join(output_dir, f"{policy.name}_detect.ps1"), 'w') as f:
        f.write(detect_script)
        
    # 2. Remediation
    remediate_script = generator.generate_remediation_script(policy)
    with open(os.path.join(output_dir, f"{policy.name}_remediate.ps1"), 'w') as f:
        f.write(remediate_script)
        
    # 3. Rollback
    rollback_script = generator.generate_rollback_script(policy)
    with open(os.path.join(output_dir, f"{policy.name}_rollback.ps1"), 'w') as f:
        f.write(rollback_script)
        
    # 4. Validation
    validate_script = generator.generate_validation_script(policy)
    with open(os.path.join(output_dir, f"{policy.name}_validate.ps1"), 'w') as f:
        f.write(validate_script)
        
    # 5. REG file
    reg_file = generator.generate_reg_file(policy)
    with open(os.path.join(output_dir, f"{policy.name}.reg"), 'w') as f:
        f.write(reg_file)
        
    print(f"Scripts successfully generated in '{output_dir}' directory.")

if __name__ == "__main__":
    main()
