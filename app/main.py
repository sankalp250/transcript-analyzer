from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import os
import csv
from dotenv import load_dotenv

from .groq_client import analyze_transcript
from .utils import redact_pii


load_dotenv()

app = FastAPI(title="Call Transcript Analyzer", version="1.0.0")

# Static files and templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(os.path.dirname(BASE_DIR), "templates")
STATIC_DIR = os.path.join(os.path.dirname(BASE_DIR), "static")

if os.path.isdir(STATIC_DIR):
	app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


CSV_PATH = os.path.join(os.path.dirname(BASE_DIR), "call_analysis.csv")


class AnalyzeRequest(BaseModel):
	transcript: str
	redact: Optional[bool] = True


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
	return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
async def analyze(transcript: Optional[str] = Form(None), redact: Optional[bool] = Form(True), body: Optional[AnalyzeRequest] = None):
	# Accept either form-data (UI) or JSON body
	input_text = transcript if transcript is not None else (body.transcript if body else None)
	if not input_text or not input_text.strip():
		raise HTTPException(status_code=400, detail="Transcript is required")

	should_redact = redact if transcript is not None else (body.redact if body is not None and body.redact is not None else True)
	original_text = input_text.strip()
	processed_text = redact_pii(original_text) if should_redact else original_text

	try:
		analysis = analyze_transcript(processed_text)
		summary = analysis["summary"]
		sentiment = analysis["sentiment"]
		insights = analysis.get("insights", [])
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

	# Persist to CSV
	file_exists = os.path.isfile(CSV_PATH)
	with open(CSV_PATH, mode="a", newline="", encoding="utf-8") as f:
		writer = csv.writer(f)
		if not file_exists:
			writer.writerow(["Transcript", "Summary", "Sentiment"])  # header
		writer.writerow([original_text, summary, sentiment])

	response_payload = {
		"transcript": original_text,
		"summary": summary,
		"sentiment": sentiment,
		"insights": insights,
		"csv_path": CSV_PATH,
	}

	# Return JSON for programmatic calls; UI expects JSON and renders client-side
	return JSONResponse(response_payload)
