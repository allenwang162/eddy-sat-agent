import json
from urllib.request import Request, urlopen

from backend.config import env
from backend.modules.oauth.service import choose_codex_model, get_codex_access_token


def tutor_system_prompt():
    return " ".join([
        "You are Eddy, a calm SAT tutor inside a practice app.",
        "Your audience is high school students. Sound friendly, direct, and encouraging without being childish.",
        "Coach with hints first. Do not reveal the final answer unless the student explicitly asks.",
        "Explain the tested concept, the trap answer pattern, and one next step.",
        "Keep replies concise and age-appropriate.",
        "Use plain paragraphs and short bullet lists. Do not use Markdown heading syntax such as #, ##, or ###.",
    ])


def extract_response_text(data):
    if data.get("output_text"):
        return data["output_text"]
    parts = []
    for item in data.get("output", []) or []:
        for content in item.get("content", []) or []:
            if content.get("text"):
                parts.append(content["text"])
            if content.get("output_text"):
                parts.append(content["output_text"])
    return "\n".join(parts)


def clean_tutor_text(text):
    return (text or "").strip()


def local_tutor_reply(payload):
    concept = payload.get("concept")
    question = payload.get("question") or {}
    user_message = payload.get("userMessage")
    hints = {
        "Linear equations": "Isolate the variable one operation at a time. Keep both sides balanced and check the result in the original equation.",
        "Systems of equations": "Look for a way to eliminate one variable. If the coefficients line up, add or subtract equations before substituting.",
        "Quadratics": "Identify whether factoring, completing the square, or the vertex form gives the fastest route.",
        "Function notation": "Treat the input like a replacement value. Substitute carefully before simplifying.",
        "Data analysis": "Separate what the graph or table literally says from what the question asks you to compute.",
        "Words in context": "Read the sentence before and after the blank. The right word must match both meaning and tone.",
        "Command of evidence": "Find the claim first, then choose the option that directly supports it rather than merely sounding related.",
        "Transitions": "Name the relationship between the two ideas: contrast, cause, example, sequence, or continuation.",
    }
    base = hints.get(concept, "Start by identifying the tested concept, then remove answer choices that do not match the exact wording of the question.")
    prompt = question.get("prompt", "")
    return "\n\n".join(part for part in [
        "Let's work this without giving away the answer too quickly.",
        f"Concept focus: {concept or 'SAT reasoning'}. {base}",
        f"For this item, restate the target in your own words: {prompt[:180]}{'...' if len(prompt) > 180 else ''}" if prompt else "",
        f'Your question was: "{user_message}". Try one small next step, then ask me to check it.' if user_message else "",
    ] if part)


def _post_json(url, payload, headers):
    req = Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    with urlopen(req, timeout=60) as response:
        return response.read().decode("utf-8")


def codex_tutor_reply(payload, user_id):
    if not user_id:
        return None
    access_token = get_codex_access_token(user_id)
    if not access_token:
        return None
    model = choose_codex_model(access_token)
    body = {
        "model": model,
        "store": False,
        "stream": True,
        "instructions": tutor_system_prompt(),
        "input": [{
            "role": "user",
            "content": [{
                "type": "input_text",
                "text": json.dumps({
                    "studentQuestion": payload.get("userMessage"),
                    "satQuestion": payload.get("question"),
                    "concept": payload.get("concept"),
                    "selectedAnswer": payload.get("selectedAnswer"),
                }),
            }],
        }],
    }
    text = _post_json(f"{env.CODEX_BASE_URL}/responses", body, {
        "authorization": f"Bearer {access_token}",
        "content-type": "application/json",
        "accept": "application/json, text/event-stream",
    })
    chunks = []
    for line in text.splitlines():
        if not line.startswith("data:"):
            continue
        raw = line[5:].strip()
        if not raw or raw == "[DONE]":
            continue
        try:
            event = json.loads(raw)
            delta = event.get("delta") or event.get("output_text_delta") or (event.get("response") or {}).get("output_text")
            if isinstance(delta, str):
                chunks.append(delta)
            full = extract_response_text(event.get("response") or event)
            if full:
                chunks.append(full)
        except Exception:
            pass
    reply = clean_tutor_text("".join(chunks))
    return {"reply": reply, "model": model} if reply else None


def openai_tutor_reply(payload):
    if not env.OPENAI_API_KEY:
        return None
    body = {
        "model": env.OPENAI_MODEL,
        "input": [
            {"role": "system", "content": tutor_system_prompt()},
            {"role": "user", "content": json.dumps({
                "studentQuestion": payload.get("userMessage"),
                "satQuestion": payload.get("question"),
                "concept": payload.get("concept"),
                "selectedAnswer": payload.get("selectedAnswer"),
            })},
        ],
    }
    text = _post_json("https://api.openai.com/v1/responses", body, {
        "authorization": f"Bearer {env.OPENAI_API_KEY}",
        "content-type": "application/json",
    })
    return extract_response_text(json.loads(text))
