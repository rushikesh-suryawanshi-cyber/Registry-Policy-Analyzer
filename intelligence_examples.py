import json
import pprint
from admx_parser.intelligence.correlation import RegistryCorrelator
from admx_parser.intelligence.scoring import RiskScorer
from admx_parser.intelligence.graph import PolicyGraph
from admx_parser.intelligence.recommendations import IntelligenceAgent

def load_data():
    try:
        with open("examples/output.json", "r", encoding="utf-8") as f:
            return json.load(f).get("policies", [])
    except FileNotFoundError:
        print("No output.json found. Please run main.py to parse ADMX files first.")
        return []

def run_intelligence():
    policies = load_data()
    if not policies:
        return
    print(f"--- Loaded {len(policies)} policies ---\n")

    print("--- 1. Registry Correlation ---")
    correlator = RegistryCorrelator(policies)
    duplicates = correlator.find_duplicate_mappings()
    conflicts = correlator.find_conflicting_policies()
    deprecated = correlator.find_deprecated_settings()
    
    print(f"Found {len(duplicates)} duplicate registry mappings.")
    print(f"Found {len(conflicts)} conflicting scope mappings.")
    print(f"Found {len(deprecated)} deprecated policies.")
    if deprecated:
        print("Example Deprecated:")
        pprint.pprint(deprecated[0])
    print()

    print("--- 2. Security Risk Scoring & Tagging ---")
    scorer = RiskScorer(policies)
    scored = scorer.evaluate_all()
    print(f"Evaluated {len(scored)} high-risk or tagged policies.")
    if scored:
        print("Top Risk Policy:")
        pprint.pprint(scored[0])
    print()

    print("--- 3. Policy Dependency Graph ---")
    graph = PolicyGraph(policies)
    stats = graph.get_graph_summary()
    print(f"Graph generated: {stats['policy_nodes']} Policies, {stats['registry_key_nodes']} Keys, {stats['category_nodes']} Categories.")
    print(f"Total Edges (Relationships): {stats['total_edges']}")
    print()

    print("--- 4. AI Insights (Requires Ollama running) ---")
    print("Initialize IntelligenceAgent to run AI tasks like browser hardening recommendations.")

if __name__ == "__main__":
    run_intelligence()
