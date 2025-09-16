# Call Transcript Analyzer (Streamlit + Groq)

Accepts a customer call transcript, summarizes it (2–3 sentences), classifies sentiment (positive/neutral/negative), shows results, and saves to `call_analysis.csv`.

## Setup

1) Python 3.10+
2) Install deps:

```bash
pip install -r requirements.txt
```

3) Environment:
- Get an API key from the Groq Console (`https://console.groq.com/`).
- Set env var `GROQ_API_KEY` and optionally `GROQ_MODEL` (default `llama-3.1-8b-instant`).

On Windows PowerShell:
```powershell
$env:GROQ_API_KEY = "YOUR_KEY_HERE"
```

## Run (Streamlit)

```bash
streamlit run streamlit_app.py
```

Then open the local URL shown in the terminal.

## Example
Use this transcript in the UI:

"""
Agent: Hi! How can I help today?
Customer: I tried booking a slot yesterday but payment failed twice.
Agent: Sorry about that. Let me check your order and retry with a different method.
"""

The app will show summary, sentiment, and save a row to `call_analysis.csv`.

## Extras
- PII redaction (emails/phones/cards) toggle
- Key insights (bullets) for highlights or next actions

## Optional: FastAPI API (already present)
If you also want an API server, you can still run:

```bash
uvicorn app.main:app --reload
```

- UI docs: `http://127.0.0.1:8000/docs`

## Recording checklist (4–5 min)
- Approach and architecture
- Walk through code: `streamlit_app.py`, `app/groq_client.py`, `app/utils.py`
- Run Streamlit and analyze a sample
- Open `call_analysis.csv` and show the saved result
