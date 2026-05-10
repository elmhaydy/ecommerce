import json
from urllib import error, request

from django.conf import settings


SUPPORT_SYSTEM_PROMPT = (
    "You are the customer support assistant for M&Y Shop, an ecommerce store. "
    "Reply in the same language as the user, either French or English. "
    "Be concise, practical, and support-focused. Help with products, cart, checkout, "
    "orders, delivery, returns, warranty, coupons, and account questions. "
    "If you are unsure of a store-specific policy, say so clearly and recommend contacting support."
)


def _extract_output_text(payload):
    output_text = payload.get("output_text")
    if output_text:
        return output_text.strip()

    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                return content["text"].strip()

    return ""


def generate_support_reply(messages):
    api_key = getattr(settings, "OPENAI_API_KEY", "")
    model = getattr(settings, "OPENAI_SUPPORT_MODEL", "gpt-5.2")

    if not api_key:
        return {
            "ok": False,
            "message": "OPENAI_API_KEY is not configured."
        }

    payload = {
        "model": model,
        "instructions": SUPPORT_SYSTEM_PROMPT,
        "input": messages,
    }

    req = request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=40) as response:
            body = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        return {
            "ok": False,
            "message": detail or f"OpenAI HTTP error: {exc.code}",
        }
    except Exception as exc:
        return {
            "ok": False,
            "message": str(exc),
        }

    payload = json.loads(body)
    text = _extract_output_text(payload)

    if not text:
        return {
            "ok": False,
            "message": "No support response returned by OpenAI.",
        }

    return {
        "ok": True,
        "message": text,
    }
