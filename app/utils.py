import re
from typing import Pattern


# Simple PII redaction: emails, phone numbers, credit cards (very naive)
EMAIL_RE: Pattern[str] = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE: Pattern[str] = re.compile(r"(?<!\d)(?:\+?\d[\s-]?)?(?:\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4}(?!\d)")
CARD_RE: Pattern[str] = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")


def redact_pii(text: str) -> str:
	if not text:
		return text
	redacted = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
	redacted = PHONE_RE.sub("[REDACTED_PHONE]", redacted)
	redacted = CARD_RE.sub("[REDACTED_CARD]", redacted)
	return redacted
