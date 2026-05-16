import argparse
import json
import logging
from pathlib import Path

from admx_parser.parser import AdmlParser, AdmxParser
from admx_parser.utils import setup_logger
from admx_parser.db.connection import DatabaseContext, init_db
from admx_parser.db.repository import PolicyRepository
from admx_parser.models import Policy

logger = setup_logger()

DB_PATH = "policies.db"
SCHEMA_PATH = "admx_parser/db/schema.sql"
CHROMA_DIR = "./chroma_db"
EMBED_MODEL = "nomic-embed-text"


def parse_admx(admx_path: Path, adml_path: Path, output_path: Path) -> list:
    """Step 1: Parse ADMX/ADML to structured policy list and export JSON."""
    logger.info("━" * 50)
    logger.info("STEP 1 — Parsing ADMX/ADML files...")

    adml_parser = AdmlParser(str(adml_path))
    string_table = adml_parser.parse()
    logger.info(f"  Loaded {len(string_table)} localization strings.")

    admx_parser = AdmxParser(str(admx_path), string_table)
    policies = admx_parser.parse()
    logger.info(f"  Parsed {len(policies)} policies.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_data = {
        "metadata": {
            "source_admx": admx_path.name,
            "source_adml": adml_path.name,
            "policy_count": len(policies)
        },
        "policies": [p.to_dict() for p in policies]
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)

    logger.info(f"  JSON exported → {output_path}")
    return policies


def ingest_to_sqlite(policies: list):
    """Step 2: Insert all parsed policies into SQLite FTS5 database."""
    logger.info("━" * 50)
    logger.info("STEP 2 — Ingesting into SQLite (FTS5)...")

    # Init schema (idempotent — safe to run multiple times)
    schema_path = Path(SCHEMA_PATH)
    if schema_path.exists():
        init_db(DB_PATH, SCHEMA_PATH)

    inserted = 0
    skipped = 0
    with DatabaseContext(DB_PATH) as conn:
        repo = PolicyRepository(conn)
        for policy in policies:
            try:
                repo.insert_policy(policy)
                inserted += 1
            except Exception as e:
                skipped += 1
                logger.debug(f"  Skipped {getattr(policy, 'name', '?')}: {e}")

    logger.info(f"  Inserted {inserted} policies into SQLite, skipped {skipped}.")


def ingest_to_vectordb(output_json: Path, skip_if_exists: bool = False):
    """Step 3: Embed policies and insert into ChromaDB via Ollama."""
    logger.info("━" * 50)
    logger.info("STEP 3 — Embedding policies into ChromaDB (Ollama)...")

    chroma_path = Path(CHROMA_DIR)
    if skip_if_exists and chroma_path.exists() and any(chroma_path.iterdir()):
        logger.info("  ChromaDB already populated. Use --reindex to force re-indexing.")
        return

    try:
        from admx_parser.rag.indexer import PolicyIndexer
        indexer = PolicyIndexer(persist_directory=CHROMA_DIR, model_name=EMBED_MODEL)
        indexer.index_from_json(str(output_json), batch_size=100)
        logger.info("  ChromaDB indexing complete.")
    except Exception as e:
        logger.warning(f"  ChromaDB indexing failed (is Ollama running?): {e}")
        logger.warning("  Tip: Run `ollama pull nomic-embed-text` then retry.")


def main():
    parser = argparse.ArgumentParser(
        description="Windows Policy Intelligence Engine — Full Ingestion Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse + ingest into SQLite + embed into ChromaDB (full pipeline):
  python main.py

  # Custom ADMX path:
  python main.py --admx_dir C:\\Windows\\PolicyDefinitions --adml_dir C:\\Windows\\PolicyDefinitions\\en-US

  # Skip vector DB embedding (SQLite only):
  python main.py --no-embed

  # Force re-indexing even if ChromaDB already has data:
  python main.py --reindex
        """
    )
    parser.add_argument("--admx_dir", default=r"C:\Windows\PolicyDefinitions",
                        help="Path to the ADMX directory (default: C:\\Windows\\PolicyDefinitions)")
    parser.add_argument("--adml_dir", default=r"C:\Windows\PolicyDefinitions\en-US",
                        help="Path to the ADML directory (default: ...\\en-US)")
    parser.add_argument("-o", "--output", default="examples/output.json",
                        help="Output JSON file path (default: examples/output.json)")
    parser.add_argument("--no-embed", action="store_true",
                        help="Skip embedding into ChromaDB vector DB")
    parser.add_argument("--reindex", action="store_true",
                        help="Force re-indexing ChromaDB even if it already has data")
    parser.add_argument("--no-db", action="store_true",
                        help="Skip SQLite ingestion")

    args = parser.parse_args()

    admx_path = Path(args.admx_dir)
    adml_path = Path(args.adml_dir)
    output_path = Path(args.output)

    if not admx_path.exists():
        logger.error(f"ADMX directory not found: {admx_path}")
        return
    if not adml_path.exists():
        logger.error(f"ADML directory not found: {adml_path}")
        return

    logger.info("=" * 50)
    logger.info(" Windows Policy Intelligence Engine")
    logger.info("=" * 50)

    # Step 1: Parse
    policies = parse_admx(admx_path, adml_path, output_path)

    # Step 2: SQLite
    if not args.no_db:
        ingest_to_sqlite(policies)
    else:
        logger.info("Skipping SQLite ingestion (--no-db).")

    # Step 3: ChromaDB / Ollama
    if not args.no_embed:
        ingest_to_vectordb(output_path, skip_if_exists=not args.reindex)
    else:
        logger.info("Skipping ChromaDB embedding (--no-embed).")

    logger.info("━" * 50)
    logger.info("Pipeline complete!")
    logger.info(f"  JSON:     {output_path}")
    logger.info(f"  SQLite:   {DB_PATH}")
    logger.info(f"  ChromaDB: {CHROMA_DIR}/")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
