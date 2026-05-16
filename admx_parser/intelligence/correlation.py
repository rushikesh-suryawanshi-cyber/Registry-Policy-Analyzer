from typing import List, Dict, Any, Tuple
from collections import defaultdict

class RegistryCorrelator:
    """Engine to detect registry duplicates, conflicts, and deprecations."""

    def __init__(self, policies: List[Dict[str, Any]]):
        self.policies = policies

    def find_duplicate_mappings(self) -> List[Dict[str, Any]]:
        """Finds multiple policies mapping to the exact same registry key and value name."""
        # mapping: (key, valueName) -> list of policies
        registry_map = defaultdict(list)
        
        for p in self.policies:
            key = p.get('key')
            val = p.get('valueName')
            if key and val:
                registry_map[(key, val)].append(p)

        duplicates = []
        for (key, val), pols in registry_map.items():
            if len(pols) > 1:
                duplicates.append({
                    "registry_path": f"{key}\\{val}",
                    "policies": [p.get('name') for p in pols],
                    "count": len(pols)
                })
        return duplicates

    def find_conflicting_policies(self) -> List[Dict[str, Any]]:
        """Identifies conflicting scopes (e.g. Machine vs User) for the same key."""
        registry_map = defaultdict(list)
        
        for p in self.policies:
            key = p.get('key')
            val = p.get('valueName')
            if key and val:
                registry_map[(key, val)].append(p)

        conflicts = []
        for (key, val), pols in registry_map.items():
            if len(pols) > 1:
                classes = set(p.get('class', '') for p in pols)
                if 'Machine' in classes and 'User' in classes:
                    conflicts.append({
                        "registry_path": f"{key}\\{val}",
                        "issue": "Scope Conflict: Configured in both Machine and User contexts.",
                        "policies": [p.get('name') for p in pols]
                    })
        return conflicts

    def find_deprecated_settings(self) -> List[Dict[str, Any]]:
        """Uses heuristics on the `supportedOn` text to flag older policies."""
        deprecated = []
        for p in self.policies:
            supported = p.get('supportedOn', '')
            if not supported:
                continue
            supported_lower = supported.lower()
            if ('windows 7' in supported_lower or 'windows xp' in supported_lower) and \
               ('windows 10' not in supported_lower and 'windows 11' not in supported_lower):
                 deprecated.append({
                     "policy_name": p.get('name'),
                     "supported_on": supported,
                     "reason": "Only supports older legacy Windows versions."
                 })
        return deprecated
