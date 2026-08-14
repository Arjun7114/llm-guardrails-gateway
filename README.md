\# LLM Guardrails Gateway



A security middleware layer that sits between users and any LLM. It screens

incoming requests for prompt injections, jailbreaks, and PII, enforces

configurable policies, and validates outgoing responses before they reach the

user — all driven by a human-editable YAML policy file.



\*\*Never trust input. Never trust output. Enforce policy at the boundary.\*\*



Built with Python, Presidio, and a local LLM via Ollama.



\## The Problem



Putting an LLM directly in front of users is risky. Users attempt prompt

injections and jailbreaks to override instructions; they paste sensitive data

(credit cards, SSNs) that shouldn't leave the system; and the model itself can

return toxic content, leak PII, or drift off-policy. A single application has no

consistent place to enforce these rules.



This gateway is that place — a reusable boundary any LLM app can sit behind. It

applies \*\*defense in depth\*\*: layered, independent checks on both the way in and

the way out, configured by policy rather than hardcoded.



\## Architecture



```

User message

&#x20;    │

&#x20;    ▼

┌─────────────────────┐

│  INPUT GUARDRAILS   │  PII detection · injection/jailbreak

│                     │  detection · banned topics \& phrases

└─────────────────────┘

&#x20;    │ (blocked → refuse, LLM never called)

&#x20;    ▼

┌─────────────────────┐

│        LLM          │  (only reached if input is safe)

└─────────────────────┘

&#x20;    │

&#x20;    ▼

┌─────────────────────┐

│  OUTPUT GUARDRAILS  │  empty check · leaked-PII check ·

│                     │  toxicity check

└─────────────────────┘

&#x20;    │ (blocked → refuse)

&#x20;    ▼

Safe response to user

```



All behaviour is controlled by `policy.yaml`, so a non-engineer (compliance,

legal, product) can change rules without touching code.



\## Features



\- \*\*PII detection\*\* (Presidio) — catches credit cards, emails, phone numbers,

&#x20; SSNs, and IPs, with checksum/format validation and a tunable confidence

&#x20; threshold.

\- \*\*Prompt injection \& jailbreak detection\*\* — pattern-based screening for known

&#x20; attack phrasings ("ignore previous instructions", "DAN", "developer mode").

\- \*\*YAML policy engine\*\* — toggle guardrails, set thresholds, and define banned

&#x20; topics/phrases in a readable config file. Loaded with `yaml.safe\_load`.

\- \*\*Output guardrails\*\* — screen the model's reply for emptiness, leaked PII, and

&#x20; toxic content before the user sees it.

\- \*\*Full gateway\*\* — a single `ask()` entry point wrapping any LLM; blocked input

&#x20; never reaches the model, saving cost and eliminating risk.

\- \*\*Automated tests\*\* — a deterministic suite (`test\_gateway.py`) proving each

&#x20; guardrail's behaviour; CI-ready.



\## Design Notes \& Honest Limitations



Good security engineering means knowing where the controls end:



\- \*\*Prompt injection is an open problem.\*\* The detector uses a denylist of known

&#x20; patterns — it raises the attacker's cost but can be bypassed by novel phrasings

&#x20; (e.g. leetspeak like "1gnore"). It is one layer, not a complete solution.

\- \*\*PII detection trades recall for precision.\*\* Presidio validates formats

&#x20; (e.g. the Luhn checksum for cards), so structurally-invalid or textbook-fake

&#x20; values — like the example SSN `123-45-6789` — fall below the confidence

&#x20; threshold and pass through. Realistic values are caught. Production systems add

&#x20; dedicated recognizers for high-stakes formats rather than only lowering the

&#x20; threshold, which would raise false positives.

\- \*\*Toxicity uses a keyword denylist\*\*; a production system would use a trained

&#x20; classifier.



Stating these limits is deliberate: the goal is honest, layered defense, not a

false claim of completeness.



\## Tech Stack



\- \*\*PII detection:\*\* Microsoft Presidio (+ spaCy `en\_core\_web\_sm`)

\- \*\*Policy config:\*\* PyYAML

\- \*\*LLM:\*\* Llama 3 via Ollama (local)

\- \*\*Language:\*\* Python



\## Project Structure



```

llm-guardrails-gateway/

├── policy.yaml            # human-editable rules (the policy engine)

├── policy.py             # loads policy.yaml

├── pii\_detector.py       # PII input/output guardrail

├── injection\_detector.py # prompt-injection guardrail

├── gateway.py            # input gateway (combines guardrails + policy)

├── output\_guard.py       # output guardrails

├── app.py                # full end-to-end gateway wrapping the LLM

├── test\_gateway.py       # automated guardrail tests

├── requirements.txt

└── README.md

```



\## Running It Locally



\*\*Prerequisites:\*\* Python 3.10+, and \[Ollama](https://ollama.com/download)

installed and running.



```bash

git clone https://github.com/Arjun7114/llm-guardrails-gateway.git

cd llm-guardrails-gateway



python -m venv venv

venv\\Scripts\\activate         # Windows

\# source venv/bin/activate    # Mac/Linux



pip install -r requirements.txt

python -m spacy download en\_core\_web\_sm

ollama pull llama3



\# Run the full gateway demo

python app.py



\# Run the guardrail tests

python test\_gateway.py

```



\## Related Projects



Part of a series on building trustworthy LLM systems:

\- \*\*\[Self-Healing RAG](https://github.com/Arjun7114/Self-healing-rag)\*\* — a RAG

&#x20; system that critiques and retries its own answers to avoid hallucination. This

&#x20; gateway can sit in front of it to add a security boundary.

