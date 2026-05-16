import os
import json
from pathlib import Path

from admx_parser.db.connection import init_db, DatabaseContext
from admx_parser.db.repository import PolicyRepository
from admx_parser.models import Policy

def main():
    db_path = "policies.db"
    schema_path = "admx_parser/db/schema.sql"
    json_path = "examples/output.json"
    
    # 1. Initialize the database
    if os.path.exists(db_path):
        os.remove(db_path)
    print("Initializing Database...")
    init_db(db_path, schema_path)
    
    # 2. Insert Policies from JSON output
    print(f"Loading data from {json_path}...")
    if not os.path.exists(json_path):
        print(f"JSON file not found. Make sure {json_path} exists.")
        return
        
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    policies_data = data.get("policies", [])
    print(f"Found {len(policies_data)} policies. Inserting into SQLite...")
    
    with DatabaseContext(db_path) as conn:
        repo = PolicyRepository(conn)
        
        for p_dict in policies_data:
            # Map JSON camelCase keys to our Policy dataclass snake_case attributes
            policy = Policy(
                name=p_dict.get("name"),
                class_type=p_dict.get("class"),
                key=p_dict.get("key"),
                value_name=p_dict.get("valueName"),
                display_name=p_dict.get("displayName"),
                explain_text=p_dict.get("explainText"),
                gpo_path=p_dict.get("gpoPath"),
                enabled_value=p_dict.get("enabledValue"),
                disabled_value=p_dict.get("disabledValue"),
                min_value=p_dict.get("minValue"),
                max_value=p_dict.get("maxValue"),
                enum_data=p_dict.get("enumData"),
                enabled_list=p_dict.get("enabledList"),
                disabled_list=p_dict.get("disabledList"),
                elements_data=p_dict.get("elementsData")
            )
            repo.insert_policy(policy)
            
    print("Insertion complete!")
    
    # 3. Perform FTS5 searches
    print("\n--- Testing FTS5 Search ---")
    with DatabaseContext(db_path) as conn:
        repo = PolicyRepository(conn)
        
        # Example 1: Search for CD-ROM policies
        query = '"CD-ROM"'
        print(f"\nSearching for {query}:")
        results = repo.search_policy(query)
        print(f"Found {len(results)} results.")
        for i, res in enumerate(results[:3]): # Print top 3
            print(f" {i+1}. [{res['name']}] {res['display_name']}")
            print(f"    Snippet: {res['snippet']}")
            
        # Example 2: Search for password length
        query = '"password length"'
        print(f"\nSearching for {query}:")
        results = repo.search_policy(query)
        print(f"Found {len(results)} results.")
        for i, res in enumerate(results[:3]):
            print(f" {i+1}. [{res['name']}] {res['display_name']}")
            print(f"    Snippet: {res['snippet']}")

if __name__ == "__main__":
    main()
