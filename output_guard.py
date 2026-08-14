# output_guard.py
# OUTPUT GUARDRAILS: screen the LLM's REPLY before it reaches the user.
# Catches empty responses, PII the model may have leaked, and (optionally)
# toxic content. Runs AFTER generation, as the last line of defense.

from policy import load_policy
from pii_detector import scan as pii_scan

POLICY = load_policy()

# A small toxic-term denylist. Like the injection detector, this is a
# pattern-based layer: catches obvious cases, not a complete solution.
TOXIC_TERMS = ["idiot", "stupid", "hate you", "kill yourself", "shut up"]


def check_output(text: str):
    """Run enabled OUTPUT guardrails against the LLM's reply.
    Returns (allowed: bool, reasons: list)."""
    reasons = []

    # 1. Non-empty check.
    if POLICY["output"].get("require_non_empty"):
        if not text or not text.strip():
            reasons.append("Empty response")

    # 2. Leaked-PII check — did the MODEL output sensitive data?
    threshold = POLICY["input"].get("pii_threshold", 0.5)
    pii_hits = [f for f in pii_scan(text) if f["score"] >= threshold]
    if pii_hits:
        types = ", ".join(sorted({f["type"] for f in pii_hits}))
        reasons.append(f"Response leaked PII ({types})")

    # 3. Toxicity check (if enabled).
    if POLICY["output"].get("block_toxicity"):
        low = text.lower()
        hits = [t for t in TOXIC_TERMS if t in low]
        if hits:
            reasons.append(f"Toxic content: {hits}")

    return (len(reasons) == 0, reasons)


# --- Standalone test ---
if __name__ == "__main__":
    tests = [
        "The home office stipend is $500.",                     # clean
        "",                                                     # empty
        "You can reach the CEO at ceo@acme.com.",               # leaked PII
        "That's a stupid question, you idiot.",                 # toxic
    ]

    for t in tests:
        allowed, reasons = check_output(t)
        status = "ALLOWED" if allowed else "BLOCKED"
        print(f"\nOUTPUT: {t!r}")
        print(f"  -> {status}  {reasons}")