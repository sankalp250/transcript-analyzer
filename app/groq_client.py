from typing import Dict, Any
from groq import Groq
import os
import json


SYSTEM_PROMPT = (
	"You are an assistant that summarizes customer support call transcripts and "
	"classifies customer sentiment. Return concise, business-usable outputs."
)

# Prefer a fast, cost-effective model for latency-sensitive endpoints
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def analyze_transcript(transcript_text: str) -> Dict[str, Any]:
	"""Call Groq once and return structured JSON: {summary, sentiment, insights[]}"""
	api_key = os.getenv("GROQ_API_KEY")
	if not api_key:
		raise RuntimeError("GROQ_API_KEY is not set. Please configure your environment.")

	client = Groq(api_key=api_key)

	user_prompt = (
		"Analyze the following call transcript.\n\n"
		"1) Summarize in 2–3 sentences. Be specific and concise.\n"
		"2) Sentiment: choose exactly one of [positive, neutral, negative].\n"
		"3) Provide up to 3 bullet insights highlighting key issues or next steps.\n\n"
		"Return a strict JSON object with keys: summary, sentiment, insights (array of strings). No prose.\n\n"
		f"Transcript:\n{transcript_text}\n"
	)

	completion = client.chat.completions.create(
		model=DEFAULT_MODEL,
		messages=[
			{"role": "system", "content": SYSTEM_PROMPT},
			{"role": "user", "content": user_prompt},
		],
		temperature=0.2,
	)

	content = completion.choices[0].message.content
	try:
		data = json.loads(content)
	except json.JSONDecodeError:
		# Fallback: try to extract the JSON block if model added extra text
		start = content.find("{")
		end = content.rfind("}")
		if start != -1 and end != -1 and end > start:
			data = json.loads(content[start : end + 1])
		else:
			raise

	# Normalize fields
	summary = str(data.get("summary", "")).strip()
	sentiment = str(data.get("sentiment", "")).strip().lower()
	if sentiment not in {"positive", "neutral", "negative"}:
		sentiment = "neutral"
	insights = [str(x).strip() for x in (data.get("insights") or []) if str(x).strip()]

	return {"summary": summary, "sentiment": sentiment, "insights": insights}
