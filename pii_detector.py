# pii_detector.py
# INPUT GUARDRAIL: scans a user's message for personally identifiable
# information (PII) BEFORE it is sent to the LLM. Pure Python, no LLM,
# deterministic — fast and reliable security logic.

from presidio_analyzer import AnalyzerEngine

# The analyzer loads once (it's a bit heavy), then can scan many texts.
_analyzer = AnalyzerEngine()

# Which PII types we care about. Presidio supports many; these are the
# common sensitive ones for an LLM gateway.
ENTITIES = [
    "CREDIT_CARD",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "US_SSN",
    "IP_ADDRESS",
   
]

def scan(text: str):
    """Return a list of PII findings in the text."""
    results = _analyzer.analyze(text=text, entities=ENTITIES, language="en")
    findings = []
    for r in results:
        findings.append({
            "type": r.entity_type,
            "text": text[r.start:r.end],   # the actual matched substring
            "score": round(r.score, 2),     # Presidio's confidence 0..1
        })
    return findings

def contains_pii(text: str, threshold: float = 0.5) -> bool:
    """True if any PII is found above the confidence threshold."""
    return any(f["score"] >= threshold for f in scan(text))


# --- Standalone test ---
if __name__ == "__main__":
    samples = [
        "My credit card is 4111-1111-1111-1111 and expires soon.",
        "Email me at john.doe@example.com or call 415-555-0198.",
        "What is the company's remote work policy?",  # clean, no PII
    ]

    for s in samples:
        print(f"\nTEXT: {s}")
        findings = scan(s)
        if findings:
            for f in findings:
                print(f"  FOUND {f['type']:15} -> '{f['text']}'  (score {f['score']})")
        else:
            print("  clean - no PII detected")