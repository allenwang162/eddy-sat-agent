import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BANK = ROOT / "data" / "seed" / "questionBank.json"
VALID_SECTIONS = {"Reading and Writing", "Math"}
VALID_DIFFICULTIES = {"Easy", "Medium", "Hard"}
REQUIRED_FIELDS = {
    "id",
    "section",
    "module",
    "type",
    "difficulty",
    "concept",
    "skill",
    "prompt",
    "choices",
    "answer",
    "explanation",
}


def load_questions(path):
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"Could not read {path}: {exc}") from exc
    if not isinstance(payload, list):
        raise SystemExit(f"{path} must contain a JSON array of questions.")
    return payload


def normalized_answer(value):
    return (
        str(value or "")
        .strip()
        .lower()
        .replace(" ", "")
        .replace("\n", "")
        .lstrip("0")
        .removeprefix(".")
    )


def split_answers(value):
    return [normalized_answer(part) for part in str(value or "").split(";") if normalized_answer(part)]


def artifact_score(text):
    text = str(text or "")
    if not text:
        return 0
    markers = [
        r"-{5,}",
        r"~{3,}",
        r"_{3,}",
        r"\.{3,}",
        r"</l",
        r"\bCO\s*N\s*T\s*I\s*N\s*U\s*E\b",
        r"\bModule\s+[12]\b",
        r"\bUnauthorized copying\b",
        r"\bU\s*12345678910\b",
    ]
    score = sum(len(re.findall(pattern, text, flags=re.I)) for pattern in markers)
    graph_chars = sum(text.count(char) for char in "-~_+|")
    if len(text) > 80 and graph_chars / len(text) > 0.20:
        score += 2
    return score


def looks_like_embedded_choices(prompt):
    return len(re.findall(r"(?m)^\s*[A-D]\)", str(prompt or ""))) >= 2


def image_path_from_metadata(question):
    metadata = question.get("metadata") or {}
    image = metadata.get("image")
    if not image:
        return None
    if image.startswith("/assets/"):
        return ROOT / "public" / image.lstrip("/")
    return ROOT / image.lstrip("/")


def validate_question(question, index, seen_ids):
    errors = []
    warnings = []
    label = question.get("id") or f"item #{index + 1}"

    missing = sorted(REQUIRED_FIELDS - set(question))
    if missing:
        errors.append(f"{label}: missing required fields: {', '.join(missing)}")
        return errors, warnings

    qid = question["id"]
    if qid in seen_ids:
        errors.append(f"{label}: duplicate id")
    seen_ids.add(qid)

    if question.get("section") not in VALID_SECTIONS:
        errors.append(f"{label}: invalid section {question.get('section')!r}")
    if question.get("difficulty") not in VALID_DIFFICULTIES:
        warnings.append(f"{label}: unusual difficulty {question.get('difficulty')!r}")

    prompt = question.get("prompt")
    choices = question.get("choices")
    answer = question.get("answer")
    qtype = question.get("type")

    if not str(prompt or "").strip():
        errors.append(f"{label}: empty prompt")
    if not isinstance(choices, list):
        errors.append(f"{label}: choices must be a list")
        choices = []

    if qtype == "multiple-choice":
        if len(choices) != 4:
            errors.append(f"{label}: multiple-choice question has {len(choices)} choices, expected 4")
        if str(answer).strip() not in {"A", "B", "C", "D"}:
            errors.append(f"{label}: multiple-choice answer must be A, B, C, or D")
        for expected, choice in zip("ABCD", choices):
            if not str(choice).strip():
                errors.append(f"{label}: choice {expected} is blank")
                continue
            if not str(choice).startswith(f"{expected}) "):
                errors.append(f"{label}: choice {expected} must start with '{expected}) '")
    elif qtype == "student-produced-response":
        if choices:
            errors.append(f"{label}: free-response question should not have choices")
        if not split_answers(answer):
            errors.append(f"{label}: free-response question needs at least one accepted answer")
        if str(answer).strip() in {"A", "B", "C", "D"}:
            errors.append(f"{label}: free-response answer looks like a multiple-choice key")
        if looks_like_embedded_choices(prompt):
            errors.append(f"{label}: prompt contains embedded choices but choices[] is empty")
    else:
        errors.append(f"{label}: unsupported type {qtype!r}")

    if artifact_score(prompt) >= 2:
        warnings.append(f"{label}: prompt contains likely PDF graph/header artifacts")
    for choice in choices:
        if artifact_score(choice) >= 2:
            warnings.append(f"{label}: choice contains likely PDF graph/header artifacts")

    image_path = image_path_from_metadata(question)
    if image_path and not image_path.exists():
        errors.append(f"{label}: metadata.image points to missing file {image_path}")
    if (question.get("metadata") or {}).get("visualRequired") and not image_path:
        warnings.append(f"{label}: visualRequired is true but no metadata.image is set")

    if not str(question.get("explanation") or "").strip():
        warnings.append(f"{label}: missing explanation text")

    return errors, warnings


def parse_expected_counts(values):
    expected = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Invalid --expect-count value {value!r}; use 'Name=Number'.")
        name, raw_count = value.split("=", 1)
        expected[name.strip()] = int(raw_count)
    return expected


def count_key(question, key):
    if key == "total":
        return "total"
    if key == "free-response":
        return "free-response" if question.get("type") == "student-produced-response" else None
    if key == "multiple-choice":
        return "multiple-choice" if question.get("type") == "multiple-choice" else None
    if question.get("section") == key:
        return key
    if question.get("module") == key:
        return key
    return None


def validate_counts(questions, expected):
    errors = []
    for name, expected_count in expected.items():
        if name == "total":
            actual = len(questions)
        else:
            actual = sum(1 for question in questions if count_key(question, name) == name)
        if actual != expected_count:
            errors.append(f"count {name!r}: expected {expected_count}, found {actual}")
    return errors


def print_summary(questions):
    by_section = Counter(question.get("section") for question in questions)
    by_type = Counter(question.get("type") for question in questions)
    by_module = Counter(question.get("module") for question in questions)
    print(f"Validated {len(questions)} questions")
    print("Sections:", ", ".join(f"{key}={value}" for key, value in sorted(by_section.items())))
    print("Types:", ", ".join(f"{key}={value}" for key, value in sorted(by_type.items())))
    print("Modules:")
    for module, count in sorted(by_module.items()):
        print(f"  {module}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Validate an Eddy SAT question bank import.")
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_BANK)
    parser.add_argument(
        "--expect-count",
        action="append",
        default=[],
        help="Expected count, e.g. total=120, Math=54, 'Reading and Writing=66', free-response=14.",
    )
    parser.add_argument("--warnings-as-errors", action="store_true")
    args = parser.parse_args()

    questions = load_questions(args.path)
    errors = []
    warnings = []
    seen_ids = set()
    for index, question in enumerate(questions):
        item_errors, item_warnings = validate_question(question, index, seen_ids)
        errors.extend(item_errors)
        warnings.extend(item_warnings)
    errors.extend(validate_counts(questions, parse_expected_counts(args.expect_count)))

    print_summary(questions)
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")
    if args.warnings_as_errors:
        errors.extend(warnings)
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("\nQuestion bank harness passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
