from typing import List, Dict, Any
import networkx as nx

class PolicyGraph:
    """Generates a dependency and relationship graph for policies."""

    def __init__(self, policies: List[Dict[str, Any]]):
        self.policies = policies
        self.graph = nx.Graph()
        self._build_graph()

    def _build_graph(self):
        """Constructs the graph with Policies, Categories, and Registry Keys as nodes."""
        for p in self.policies:
            policy_node = f"Policy:{p.get('name')}"
            self.graph.add_node(policy_node, type="policy", data=p)

            # Link to Registry Key
            key = p.get('key')
            if key:
                key_node = f"Key:{key}"
                self.graph.add_node(key_node, type="registry_key")
                self.graph.add_edge(policy_node, key_node, relation="modifies")

            # Link to Category (GPO Path)
            gpo_path = p.get('gpoPath')
            if gpo_path:
                # To simplify, link to the immediate parent category
                category = gpo_path.split('\\')[-1] if '\\' in gpo_path else gpo_path
                cat_node = f"Category:{category}"
                self.graph.add_node(cat_node, type="category")
                self.graph.add_edge(policy_node, cat_node, relation="belongs_to")

    def get_related_policies(self, policy_name: str) -> List[str]:
        """Finds related policies that share the same registry key or category."""
        target_node = f"Policy:{policy_name}"
        if target_node not in self.graph:
            return []

        related = set()
        # Find neighbors (keys and categories)
        for neighbor in self.graph.neighbors(target_node):
            # Find policies connected to those neighbors
            for second_degree in self.graph.neighbors(neighbor):
                if second_degree.startswith("Policy:") and second_degree != target_node:
                    related.add(second_degree.replace("Policy:", ""))
                    
        return list(related)
        
    def get_graph_summary(self) -> Dict[str, int]:
        """Returns basic stats about the generated graph."""
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "policy_nodes": sum(1 for n, d in self.graph.nodes(data=True) if d.get('type') == 'policy'),
            "registry_key_nodes": sum(1 for n, d in self.graph.nodes(data=True) if d.get('type') == 'registry_key'),
            "category_nodes": sum(1 for n, d in self.graph.nodes(data=True) if d.get('type') == 'category')
        }
