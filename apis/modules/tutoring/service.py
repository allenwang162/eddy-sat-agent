import json
from urllib.request import Request, urlopen

from apis.config import env
from apis.modules.oauth.service import choose_codex_model, get_codex_access_token


def tutor_system_prompt():
    return " ".join([
        "You are Eddy, a calm SAT tutor inside a practice app.",
        "Your audience is high school students. Sound friendly, direct, and encouraging without being childish.",
        "Coach with hints first. Do not reveal the final answer unless the student explicitly asks.",
        "When the student asks for a hint, start the response with 'Hint: ...' as the first line.",
        "When the student asks for the concept, start the response with 'Concept: ...' as the first line.",
        "When the student asks to eliminate choices, start the response with 'Eliminate: ...' as the first line.",
        "When the student explicitly asks for the answer, start the response with 'Correct answer: ...' as the first line, then explain why it is correct.",
        "Explain the tested concept, the trap answer pattern, and one next step.",
        "Keep replies concise and age-appropriate.",
        "Do not repeat the full SAT question. If context is useful, quote only a short key phrase.",
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


def extract_token_usage(data):
    usage = data.get("usage") or (data.get("response") or {}).get("usage") or {}
    if not isinstance(usage, dict):
        return None
    input_tokens = usage.get("input_tokens") or usage.get("prompt_tokens")
    output_tokens = usage.get("output_tokens") or usage.get("completion_tokens")
    total_tokens = usage.get("total_tokens")
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens
    if input_tokens is None and output_tokens is None and total_tokens is None:
        return None
    result = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }
    details = usage.get("input_tokens_details") or usage.get("prompt_tokens_details")
    if isinstance(details, dict) and details.get("cached_tokens") is not None:
        result["cached_input_tokens"] = details.get("cached_tokens")
    return {key: value for key, value in result.items() if value is not None}


def estimate_token_count(value):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    return max(1, round(len(text) / 4)) if text else 0


def tutor_input_payload(payload):
    return {
        "studentQuestion": payload.get("userMessage"),
        "satQuestion": payload.get("question"),
        "concept": payload.get("concept"),
        "pageContext": payload.get("pageContext"),
        "latestAttempt": payload.get("latestAttempt"),
        "selectedAnswer": payload.get("selectedAnswer"),
    }


def estimated_usage(input_payload, reply):
    input_tokens = estimate_token_count(tutor_system_prompt()) + estimate_token_count(input_payload)
    output_tokens = estimate_token_count(reply)
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "usage_source": "estimated",
    }


def clean_tutor_text(text):
    return (text or "").strip()


def local_tutor_reply(payload):
    concept = payload.get("concept")
    question = payload.get("question") or {}
    latest_attempt = payload.get("latestAttempt") or {}
    page_context = payload.get("pageContext")
    user_message = payload.get("userMessage")
    lowered_message = (user_message or "").lower()
    answer_request = "answer" in (user_message or "").lower()
    if page_context == "reviewView":
        focus = latest_attempt.get("focusConcept") or "your lowest-scoring skill"
        score = latest_attempt.get("scoreRange") or f"{latest_attempt.get('score', 0)}%"
        accuracy = f"{latest_attempt.get('correct', 0)} of {latest_attempt.get('total', 0)} correct"
        return "\n\n".join([
            "Let's turn the result into a practical study plan.",
            f"Latest result: {score}, with {accuracy}.",
            f"Main focus: {focus}. Start by reviewing missed questions in that area, then complete a short targeted set and explain each miss in one sentence.",
            "Next steps: 1) redo two missed questions, 2) ask for the concept pattern, 3) practice three similar questions, 4) check whether the same mistake repeats.",
            f'Your question was: "{user_message}".' if user_message else "",
        ]).strip()
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
    if "hint" in lowered_message:
        return "\n\n".join(part for part in [
            f"Hint: Focus on {concept or 'the tested skill'} before looking at the choices.",
            base,
            f"Key clue: {prompt[:80]}{'...' if len(prompt) > 80 else ''}" if prompt else "",
        ] if part)
    if "concept" in lowered_message:
        return "\n\n".join(part for part in [
            f"Concept: {concept or 'SAT reasoning'}.",
            base,
            "Next step: name what the question is asking before comparing choices.",
        ] if part)
    if "eliminate" in lowered_message:
        return "\n\n".join(part for part in [
            "Eliminate: Cross out choices that do not match the exact task.",
            f"Use this concept check: {base}",
            "Then compare the remaining choices against the wording of the question.",
        ] if part)
    if answer_request and question.get("answer"):
        answer = question.get("answer")
        choices = question.get("choices") or []
        matching_choice = next((choice for choice in choices if str(choice).startswith(f"{answer})")), None)
        answer_line = f"Correct answer: {answer}"
        if matching_choice:
            answer_line = f"Correct answer: {matching_choice}"
        return "\n\n".join(part for part in [
            answer_line,
            f"Why: {question.get('explanation') or question.get('logic') or base}",
            f"Concept focus: {concept or 'SAT reasoning'}. {base}",
            "Next step: compare the correct choice with the wording of the question, then identify why one tempting wrong choice fails.",
        ] if part)
    return "\n\n".join(part for part in [
        "Let's work this without giving away the answer too quickly.",
        f"Concept focus: {concept or 'SAT reasoning'}. {base}",
        f"For this item, restate the target in your own words. Key clue: {prompt[:90]}{'...' if len(prompt) > 90 else ''}" if prompt else "",
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
    input_payload = tutor_input_payload(payload)
    body = {
        "model": model,
        "store": False,
        "stream": True,
        "instructions": tutor_system_prompt(),
        "input": [{
            "role": "user",
            "content": [{
                "type": "input_text",
                "text": json.dumps(input_payload),
            }],
        }],
    }
    text = _post_json(f"{env.CODEX_BASE_URL}/responses", body, {
        "authorization": f"Bearer {access_token}",
        "content-type": "application/json",
        "accept": "application/json, text/event-stream",
    })
    chunks = []
    usage = None
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
            response_data = event.get("response") or event
            event_usage = extract_token_usage(response_data)
            if event_usage:
                event_usage["usage_source"] = "provider"
                usage = event_usage
            full = extract_response_text(response_data)
            if full:
                chunks.append(full)
        except Exception:
            pass
    reply = clean_tutor_text("".join(chunks))
    if reply and not usage:
        usage = estimated_usage(input_payload, reply)
    return {"reply": reply, "model": model, "usage": usage} if reply else None


def openai_tutor_reply(payload):
    if not env.OPENAI_API_KEY:
        return None
    input_payload = tutor_input_payload(payload)
    body = {
        "model": env.OPENAI_MODEL,
        "input": [
            {"role": "system", "content": tutor_system_prompt()},
            {"role": "user", "content": json.dumps(input_payload)},
        ],
    }
    text = _post_json("https://api.openai.com/v1/responses", body, {
        "authorization": f"Bearer {env.OPENAI_API_KEY}",
        "content-type": "application/json",
    })
    data = json.loads(text)
    reply = extract_response_text(data)
    usage = extract_token_usage(data)
    if reply and usage:
        usage["usage_source"] = "provider"
    if reply and not usage:
        usage = estimated_usage(input_payload, reply)
    return {"reply": reply, "model": env.OPENAI_MODEL, "usage": usage} if reply else None
