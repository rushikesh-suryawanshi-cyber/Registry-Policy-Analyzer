import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

from deepdiff import DeepDiff

from .models import DatasetDiff, FieldChange, PolicyDiff
from ..parser import AdmlParser, AdmxParser

logger = logging.getLogger("admx_parser")

# Fields to compare for modifications
COMPARED_FIELDS = [
    "class",
    "key",
    "valueName",
    "displayName",
    "explainText",
    "gpoPath",
    "enabledValue",
    "disabledValue",
    "minValue",
    "maxValue",
    "enumData",
    "enabledList",
    "disabledList",
    "elementsData",
]


def _hash_policy(policy_dict: Dict[str, Any]) -> str:
    """Produces a stable SHA-256 hash from a policy dictionary for fast change detection."""
    stable_repr = json.dumps(policy_dict, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(stable_repr.encode("utf-8")).hexdigest()


def _load_dataset_from_json(json_path: str) -> Dict[str, Dict]:
    """Loads a parsed policy JSON file and indexes policies by name."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    policies = data.get("policies", [])
    return {p["name"]: p for p in policies if p.get("name")}


def _load_dataset_from_admx_dir(
    admx_dir: str, adml_dir: str
) -> Dict[str, Dict]:
    """Parses an ADMX/ADML directory on the fly and returns the indexed dataset."""
    logger.info(f"Parsing ADML from: {adml_dir}")
    adml_parser = AdmlParser(adml_dir)
    string_table = adml_parser.parse()

    logger.info(f"Parsing ADMX from: {admx_dir}")
    admx_parser = AdmxParser(admx_dir, string_table)
    policies = admx_parser.parse()

    return {p.name: p.to_dict() for p in policies if p.name}


class PolicyComparator:
    """Compares two policy datasets and generates structured diff reports."""

    def __init__(self, old_label: str = "old", new_label: str = "new"):
        self.old_label = old_label
        self.new_label = new_label

    def compare(
        self,
        old_dataset: Dict[str, Dict],
        new_dataset: Dict[str, Dict],
    ) -> DatasetDiff:
        """
        Runs the full comparison pipeline:
        1. Hash-based triage to identify changed/added/removed policies.
        2. Field-level deepdiff only for changed policies.
        """
        result = DatasetDiff(old_source=self.old_label, new_source=self.new_label)

        old_names = set(old_dataset.keys())
        new_names = set(new_dataset.keys())

        # --- Added policies ---
        for name in sorted(new_names - old_names):
            p = new_dataset[name]
            result.added.append(
                PolicyDiff(
                    policy_name=name,
                    change_type="added",
                    display_name=p.get("displayName"),
                    gpo_path=p.get("gpoPath"),
                )
            )

        # --- Removed policies ---
        for name in sorted(old_names - new_names):
            p = old_dataset[name]
            result.removed.append(
                PolicyDiff(
                    policy_name=name,
                    change_type="removed",
                    display_name=p.get("displayName"),
                    gpo_path=p.get("gpoPath"),
                )
            )

        # --- Modified policies (hash triage first) ---
        common_names = sorted(old_names & new_names)
        logger.info(
            f"Comparing {len(common_names)} common policies via hash triage..."
        )
        changed_count = 0
        for name in common_names:
            old_p = old_dataset[name]
            new_p = new_dataset[name]

            if _hash_policy(old_p) == _hash_policy(new_p):
                continue  # Identical — skip deepdiff entirely

            changed_count += 1
            field_changes = self._diff_policy(old_p, new_p)
            if field_changes:
                result.modified.append(
                    PolicyDiff(
                        policy_name=name,
                        change_type="modified",
                        display_name=new_p.get("displayName"),
                        gpo_path=new_p.get("gpoPath"),
                        field_changes=field_changes,
                    )
                )

        logger.info(
            f"Hash triage complete. {changed_count} policies had hash mismatches."
        )
        return result

    def _diff_policy(
        self, old_p: Dict[str, Any], new_p: Dict[str, Any]
    ) -> List[FieldChange]:
        """Runs deepdiff on the subset of tracked fields for a single policy pair."""
        changes: List[FieldChange] = []

        for field_name in COMPARED_FIELDS:
            old_val = old_p.get(field_name)
            new_val = new_p.get(field_name)

            if old_val == new_val:
                continue

            # For complex nested fields use deepdiff for a clean readable delta
            if isinstance(old_val, (dict, list)) or isinstance(new_val, (dict, list)):
                dd = DeepDiff(old_val, new_val, ignore_order=True, verbose_level=1)
                if dd:
                    changes.append(
                        FieldChange(
                            field=field_name,
                            old_value=old_val,
                            new_value=new_val,
                        )
                    )
            else:
                changes.append(
                    FieldChange(field=field_name, old_value=old_val, new_value=new_val)
                )

        return changes

    def to_json_report(self, diff: DatasetDiff, output_path: Optional[str] = None) -> str:
        """Serializes the DatasetDiff to a formatted JSON string (and optionally writes to file)."""
        payload = json.dumps(diff.to_dict(), indent=4, ensure_ascii=False, default=str)
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(payload)
            logger.info(f"JSON report written to: {output_path}")
        return payload

    def to_human_summary(self, diff: DatasetDiff) -> str:
        """Generates a concise, human-readable changelog text."""
        lines = [
            "=" * 60,
            f"  ADMX Policy Diff Report",
            f"  Old: {diff.old_source}",
            f"  New: {diff.new_source}",
            f"  Generated: {diff.generated_at}",
            "=" * 60,
            f"  Total Changes : {diff.total_changes}",
            f"  Added         : {len(diff.added)}",
            f"  Removed       : {len(diff.removed)}",
            f"  Modified      : {len(diff.modified)}",
            "=" * 60,
        ]

        if diff.added:
            lines.append("\n[+] ADDED POLICIES")
            for p in diff.added:
                lines.append(f"    + {p.policy_name}  ({p.display_name})")
                if p.gpo_path:
                    lines.append(f"      Path: {p.gpo_path}")

        if diff.removed:
            lines.append("\n[-] REMOVED POLICIES")
            for p in diff.removed:
                lines.append(f"    - {p.policy_name}  ({p.display_name})")
                if p.gpo_path:
                    lines.append(f"      Path: {p.gpo_path}")

        if diff.modified:
            lines.append("\n[~] MODIFIED POLICIES")
            for p in diff.modified:
                lines.append(f"\n  ~ {p.policy_name}  ({p.display_name})")
                for ch in p.field_changes:
                    old_str = str(ch.old_value)[:80] + "..." if len(str(ch.old_value)) > 80 else str(ch.old_value)
                    new_str = str(ch.new_value)[:80] + "..." if len(str(ch.new_value)) > 80 else str(ch.new_value)
                    lines.append(f"    Field : {ch.field}")
                    lines.append(f"    Before: {old_str}")
                    lines.append(f"    After : {new_str}")
                    lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)
