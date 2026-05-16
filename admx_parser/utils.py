import logging
import re
import difflib

def setup_logger(name: str = "admx_parser", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger

def enhanced_lookup(token, adml_resources, threshold=0.4):
    token_lower = token.lower()
    substring_candidates = [key for key in adml_resources if token_lower in key.lower()]
    if substring_candidates:
        if len(substring_candidates) == 1:
            return adml_resources[substring_candidates[0]]
        best_match = None
        best_ratio = 0.0
        for key in substring_candidates:
            ratio = difflib.SequenceMatcher(None, token_lower, key.lower()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = key
        if best_ratio >= threshold:
            return adml_resources[best_match]
    best_match = None
    best_ratio = 0.0
    for key in adml_resources:
        ratio = difflib.SequenceMatcher(None, token_lower, key.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = key
    if best_match and best_ratio >= threshold:
        return adml_resources[best_match]
    return None

def resolve_references(text, adml_resources):
    if not text:
        return text
    pattern = r'\$\(\s*string\.([^)]+)\s*\)'

    def replacer(match):
        token = match.group(1).strip()
        resolved = adml_resources.get(token)
        if resolved:
            return resolved
        enhanced = enhanced_lookup(token, adml_resources)
        if enhanced:
            return enhanced
        return match.group(0)

    return re.sub(pattern, replacer, text)

def get_decimal_value(element):
    if element is not None and element.get("value"):
        try:
            return int(element.get("value"))
        except ValueError:
            return None
    return None

def normalize_category(cat_str):
    if cat_str and ":" in cat_str:
        return cat_str.split(":", 1)[1]
    return cat_str

def build_complete_gpo_path(policy, policy_data, categories, max_depth=10):
    parent_cat_elem = policy.find(policy.tag.replace("policy", "parentCategory"))
    starting_cat = None
    if parent_cat_elem is not None:
        starting_cat = parent_cat_elem.get("ref")
    else:
        starting_cat = policy.get("category")

    if starting_cat:
        starting_cat = normalize_category(starting_cat)
        chain = []
        visited = set()
        current = starting_cat
        depth = 0
        while current and current in categories and depth < max_depth:
            if current in visited:
                break
            visited.add(current)
            chain.insert(0, categories[current]["displayName"])
            parent_ref = categories[current].get("parent")
            if parent_ref:
                current = normalize_category(parent_ref)
            else:
                break
            depth += 1
            
        virtual_root = ""
        if policy.get("class") and policy.get("class").lower() == "machine":
            virtual_root = "Computer Configuration"
        elif policy.get("class") and policy.get("class").lower() == "user":
            virtual_root = "User Configuration"
            
        if virtual_root and (not chain or chain[0] != virtual_root):
            chain.insert(0, virtual_root)
            
        full_path = " > ".join(chain + [policy_data["displayName"]])
        return full_path
    else:
        if policy.get("class") and policy.get("class").lower() == "machine":
            return "Computer Configuration > " + policy_data["displayName"]
        elif policy.get("class") and policy.get("class").lower() == "user":
            return "User Configuration > " + policy_data["displayName"]
        else:
            return policy_data["displayName"]
