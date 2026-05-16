#!/usr/bin/env python3
"""
ADMX Policy Diff CLI
====================
Compare two ADMX policy snapshots (JSON files or live ADMX directories).

Usage examples:
  # Compare two pre-parsed JSON snapshots
  python diff_report_example.py --old examples/output_v1.json --new examples/output.json

  # Compare two live ADMX directories
  python diff_report_example.py \
      --old-admx-dir C:/admx_v1 --old-adml-dir C:/admx_v1/en-US \
      --new-admx-dir C:/admx_v2 --new-adml-dir C:/admx_v2/en-US

  # Save JSON report
  python diff_report_example.py --old a.json --new b.json --output reports/diff.json
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

from admx_parser.diff.engine import (
    PolicyComparator,
    _load_dataset_from_admx_dir,
    _load_dataset_from_json,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("admx_parser")


def _make_synthetic_diff_datasets(json_path: str):
    """
    Creates two datasets from a single JSON file to demonstrate the diff engine
    when no second file is available. Tweaks a handful of policies to simulate
    additions, removals, and field modifications.
    """
    dataset = _load_dataset_from_json(json_path)
    names = list(dataset.keys())

    if len(names) < 5:
        logger.error("Need at least 5 policies in the JSON file to create a demo.")
        sys.exit(1)

    old_ds = dict(dataset)
    new_ds = dict(dataset)

    # Simulate a removal — drop the first policy from "new"
    removed_name = names[0]
    del new_ds[removed_name]

    # Simulate an addition — clone the second policy under a new name
    added_name = names[1] + "_V2"
    new_ds[added_name] = dict(dataset[names[1]])
    new_ds[added_name]["name"] = added_name

    # Simulate a modification — change explainText of the third policy
    modified_name = names[2]
    new_ds[modified_name] = dict(dataset[modified_name])
    new_ds[modified_name]["explainText"] = (
        "[Updated in v2] " + (dataset[modified_name].get("explainText") or "")
    )

    # Simulate a registry key change on the fourth policy
    modified_name2 = names[3]
    new_ds[modified_name2] = dict(dataset[modified_name2])
    new_ds[modified_name2]["key"] = dataset[modified_name2].get("key", "") + "\\Updated"

    return old_ds, new_ds


def main():
    parser = argparse.ArgumentParser(
        description="ADMX Policy Version Comparison Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # JSON-based comparison
    parser.add_argument("--old", dest="old_json", help="Path to OLD policy JSON snapshot")
    parser.add_argument("--new", dest="new_json", help="Path to NEW policy JSON snapshot")

    # Directory-based comparison
    parser.add_argument("--old-admx-dir", dest="old_admx_dir")
    parser.add_argument("--old-adml-dir", dest="old_adml_dir")
    parser.add_argument("--new-admx-dir", dest="new_admx_dir")
    parser.add_argument("--new-adml-dir", dest="new_adml_dir")

    # Output
    parser.add_argument(
        "--output", "-o",
        dest="output_path",
        default="reports/diff_report.json",
        help="Path to write the JSON diff report (default: reports/diff_report.json)",
    )
    parser.add_argument(
        "--no-summary", action="store_true",
        help="Skip printing the human-readable summary to stdout",
    )

    args = parser.parse_args()

    # --- Load datasets ---
    if args.old_json and args.new_json:
        if not Path(args.old_json).exists():
            logger.error(f"Old JSON not found: {args.old_json}")
            sys.exit(1)
        if not Path(args.new_json).exists():
            logger.error(f"New JSON not found: {args.new_json}")
            sys.exit(1)
        logger.info("Loading old dataset from JSON...")
        old_ds = _load_dataset_from_json(args.old_json)
        logger.info("Loading new dataset from JSON...")
        new_ds = _load_dataset_from_json(args.new_json)
        old_label = args.old_json
        new_label = args.new_json

    elif args.old_admx_dir and args.new_admx_dir:
        old_adml = args.old_adml_dir or os.path.join(args.old_admx_dir, "en-US")
        new_adml = args.new_adml_dir or os.path.join(args.new_admx_dir, "en-US")
        logger.info("Loading old dataset from ADMX directory...")
        old_ds = _load_dataset_from_admx_dir(args.old_admx_dir, old_adml)
        logger.info("Loading new dataset from ADMX directory...")
        new_ds = _load_dataset_from_admx_dir(args.new_admx_dir, new_adml)
        old_label = args.old_admx_dir
        new_label = args.new_admx_dir

    else:
        # Demo mode — synthesise changes from the existing output.json
        demo_json = "examples/output.json"
        if not Path(demo_json).exists():
            logger.error(
                "No --old/--new arguments provided and examples/output.json not found.\n"
                "Run: python main.py   to generate it first."
            )
            sys.exit(1)
        logger.info(f"Demo mode: generating synthetic diff from {demo_json}...")
        old_ds, new_ds = _make_synthetic_diff_datasets(demo_json)
        old_label = f"{demo_json} (v1 snapshot)"
        new_label = f"{demo_json} (v2 snapshot)"

    # --- Run comparison ---
    comparator = PolicyComparator(old_label=old_label, new_label=new_label)
    logger.info("Running comparison...")
    diff = comparator.compare(old_ds, new_ds)

    # --- Output ---
    comparator.to_json_report(diff, output_path=args.output_path)
    print(f"\nJSON report saved to: {args.output_path}")

    if not args.no_summary:
        print()
        print(comparator.to_human_summary(diff))


if __name__ == "__main__":
    main()
