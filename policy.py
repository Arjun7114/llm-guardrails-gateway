# policy.py
# Loads policy.yaml and exposes the settings to the rest of the gateway.

import yaml

def load_policy(path: str = "policy.yaml") -> dict:
    """Read the YAML policy file into a Python dictionary."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    policy = load_policy()
    print("Loaded policy:\n")
    print(f"  Block PII?         {policy['input']['block_pii']}")
    print(f"  PII threshold:     {policy['input']['pii_threshold']}")
    print(f"  Block injection?   {policy['input']['block_injection']}")
    print(f"  Banned phrases:    {policy['input']['banned_phrases']}")
    print(f"  Banned topics:     {policy['banned_topics']}")
    print(f"  Refusal message:   {policy['refusal_message']}")