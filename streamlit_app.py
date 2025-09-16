import os
import csv
import streamlit as st
from dotenv import load_dotenv

from app.groq_client import analyze_transcript
from app.utils import redact_pii


load_dotenv()

# Load secrets from Streamlit Cloud if present
try:
	if "GROQ_API_KEY" in st.secrets and not os.getenv("GROQ_API_KEY"):
		os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"].strip()
	except_key = None
except Exception as except_key:
	pass

if "GROQ_MODEL" in st.secrets and not os.getenv("GROQ_MODEL"):
	os.environ["GROQ_MODEL"] = str(st.secrets["GROQ_MODEL"]).strip()

st.set_page_config(page_title="Call Transcript Analyzer", page_icon="📞", layout="centered")

# Sidebar: GROQ key management
with st.sidebar:
	st.header("Settings")
	current_key = os.getenv("GROQ_API_KEY")
	if not current_key:
		st.warning("GROQ_API_KEY not set. Paste your key to proceed.")
		entered = st.text_input("GROQ API Key", type="password")
		if entered:
			os.environ["GROQ_API_KEY"] = entered.strip()
			current_key = os.environ["GROQ_API_KEY"]
			st.success("API key set for this session.")
	else:
		masked = f"***{current_key[-4:]}" if len(current_key) >= 4 else "(short)"
		st.caption(f"GROQ_API_KEY detected: {masked}")

	# Connectivity test (does not save CSV)
	if st.button("Test Groq connection"):
		try:
			_ = analyze_transcript("Hello. Please return a tiny JSON.")
			st.success("Groq connection OK.")
		except Exception as e:
			st.error(f"Groq auth/test failed: {e}")

st.title("📞 Call Transcript Analyzer")
st.caption("Summarize a customer call and classify sentiment using Groq")

transcript = st.text_area("Transcript", height=200, placeholder="Paste a short customer call transcript…")
redact = st.checkbox("Redact PII (emails, phones, cards)", value=True)

csv_path = os.path.join(os.getcwd(), "call_analysis.csv")

analyze = st.button("Analyze")

if analyze:
	if not transcript or not transcript.strip():
		st.error("Please paste a transcript.")
		st.stop()

	# Re-check key before calling API
	if not os.getenv("GROQ_API_KEY"):
		st.error("GROQ_API_KEY is not set. Open the sidebar or set Streamlit Secrets.")
		st.stop()

	original_text = transcript.strip()
	processed_text = redact_pii(original_text) if redact else original_text

	with st.spinner("Contacting Groq and analyzing…"):
		try:
			result = analyze_transcript(processed_text)
		except Exception as e:
			st.error(f"Analysis failed: {e}")
			st.stop()

	summary = result.get("summary", "")
	sentiment = result.get("sentiment", "neutral")
	insights = result.get("insights", [])

	st.subheader("Summary")
	st.write(summary)

	st.subheader("Sentiment")
	st.write(sentiment.capitalize())

	if insights:
		st.subheader("Key insights")
		for i in insights:
			st.markdown(f"- {i}")

	# Save to CSV
	file_exists = os.path.isfile(csv_path)
	try:
		with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
			writer = csv.writer(f)
			if not file_exists:
				writer.writerow(["Transcript", "Summary", "Sentiment"])  # header
			writer.writerow([original_text, summary, sentiment])
		st.success("Saved to call_analysis.csv")
		st.code(csv_path)
	except Exception as e:
		st.warning(f"Could not save to CSV: {e}")
