from backend.config import env
from backend.repositories.sqlite_repositories import list_questions
from backend.shared.json_store import read_json


def _normalize_answer(value):
    text = str(value or "").strip().lower().replace(" ", "").replace("\n", "")
    while len(text) > 1 and text.startswith("0") and text[1].isdigit():
        text = text[1:]
    if text.startswith("."):
        text = f"0{text}"
    return text


def _accepted_answers(answer):
    return [_normalize_answer(part) for part in str(answer or "").split(";") if _normalize_answer(part)]


def _is_correct(selected, answer):
    return _normalize_answer(selected) in _accepted_answers(answer)


def _score_range(scoring_table, raw_score, section):
    row = scoring_table.get(str(raw_score)) or scoring_table.get(raw_score) or {}
    section_range = row.get(section)
    return section_range if isinstance(section_range, list) and len(section_range) == 2 else None


def score_practice_attempt(payload):
    question_ids = payload.get("questionIds") or []
    answers = payload.get("answers") or {}
    question_by_id = {question["id"]: question for question in list_questions()}
    scoring_tables = read_json(env.SEED_DATA_DIR / "scoringTables.json", {"tests": {}})

    results = []
    sections = {}
    practice_tests = set()
    for question_id in question_ids:
        question = question_by_id.get(question_id)
        if not question:
            continue
        selected = answers.get(question_id, "")
        correct = _is_correct(selected, question.get("answer"))
        metadata = question.get("metadata") or {}
        practice_test = metadata.get("practiceTest")
        if practice_test:
            practice_tests.add(str(practice_test))
        section_name = question.get("section")
        module_number = metadata.get("moduleNumber")
        section = sections.setdefault(section_name, {"raw": 0, "total": 0, "modules": {}})
        section["total"] += 1
        if correct:
            section["raw"] += 1
        if module_number is not None:
            module = section["modules"].setdefault(str(module_number), {"raw": 0, "total": 0})
            module["total"] += 1
            if correct:
                module["raw"] += 1
        results.append({
            "id": question_id,
            "selected": selected,
            "answer": question.get("answer"),
            "correct": correct,
        })

    total = len(results)
    correct = sum(1 for result in results if result["correct"])
    percentage = round((correct / total) * 100) if total else 0

    scoring_test = next(iter(practice_tests)) if len(practice_tests) == 1 else None
    scoring_table = (scoring_tables.get("tests") or {}).get(scoring_test or "", {}).get("table", {})
    section_ranges = {}
    for section_name, section in sections.items():
        score_range = _score_range(scoring_table, section["raw"], section_name)
        section["scoreRange"] = score_range
        section_ranges[section_name] = score_range

    total_range = None
    if section_ranges.get("Reading and Writing") and section_ranges.get("Math"):
        total_range = [
            section_ranges["Reading and Writing"][0] + section_ranges["Math"][0],
            section_ranges["Reading and Writing"][1] + section_ranges["Math"][1],
        ]

    return {
        "practiceTest": int(scoring_test) if scoring_test and scoring_test.isdigit() else scoring_test,
        "scoreType": "range" if scoring_table else "percent",
        "score": percentage,
        "correct": correct,
        "total": total,
        "sections": sections,
        "totalScoreRange": total_range,
        "results": results,
    }
