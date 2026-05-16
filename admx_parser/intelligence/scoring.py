import re
from typing import List, Dict, Any

class RiskScorer:
    """Calculates Security Risk Scores and Auto-Tags policies."""

    SECURITY_KEYWORDS = ['password', 'credential', 'lsa', 'defender', 'firewall', 'encryption', 'bitlocker']
    PRIVACY_KEYWORDS = ['telemetry', 'camera', 'microphone', 'location', 'diagnostic']
    NETWORK_KEYWORDS = ['wifi', 'wlan', 'lan', 'proxy', 'dns', 'ipsec', 'rdp']
    BROWSER_KEYWORDS = ['edge', 'chrome', 'firefox', 'cookie', 'phishing', 'smartscreen']

    def __init__(self, policies: List[Dict[str, Any]]):
        self.policies = policies

    def evaluate_all(self) -> List[Dict[str, Any]]:
        results = []
        for p in self.policies:
            score, tags = self._evaluate_policy(p)
            if score > 0 or tags:
                results.append({
                    "policy_name": p.get('name'),
                    "display_name": p.get('displayName'),
                    "risk_score": score,
                    "tags": tags
                })
        # Sort by risk score descending
        results.sort(key=lambda x: x['risk_score'], reverse=True)
        return results

    def _evaluate_policy(self, policy: Dict[str, Any]) -> tuple[int, List[str]]:
        score = 0
        tags = set()
        
        text = f"{policy.get('name', '')} {policy.get('displayName', '')} {policy.get('explainText', '')}".lower()
        key = (policy.get('key') or '').lower()

        # Check Security
        if any(kw in text or kw in key for kw in self.SECURITY_KEYWORDS):
            tags.add("Security")
            score += 40

        # Check Privacy
        if any(kw in text or kw in key for kw in self.PRIVACY_KEYWORDS):
            tags.add("Privacy")
            score += 30

        # Check Network
        if any(kw in text or kw in key for kw in self.NETWORK_KEYWORDS):
            tags.add("Network")
            score += 20

        # Check Browser
        if any(kw in text or kw in key for kw in self.BROWSER_KEYWORDS):
            tags.add("Browser")

        # Additional Risk Heuristics
        if 'system' in key or 'hklm' in key:
            score += 10 # System-wide changes are slightly higher risk

        if 'disable' in text and ('antivirus' in text or 'defender' in text):
            score = 100 # Critical risk

        # Cap score at 100
        score = min(score, 100)
        return score, list(tags)
