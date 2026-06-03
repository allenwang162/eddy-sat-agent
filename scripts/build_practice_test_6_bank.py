import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import scripts.build_practice_test_4_bank as importer


EXTRACTED_PATH = ROOT / "data" / "seed" / "extracted-sat-practice-test-6.json"
SCORING_EXTRACTED_PATH = ROOT / "data" / "seed" / "extracted-sat-practice-test-6-scoring.json"
OUTPUT_PATH = ROOT / "data" / "seed" / "questionBank.json"
EXPLANATIONS_PDF = Path("/Users/allenwang/Downloads/full-length-sat-paper-practice-test_-bundle-6/sat-practice-test-6-answers-digital.pdf")

ANSWER_KEYS = {
    ("Reading and Writing", 1): [
        "D", "B", "B", "D", "D", "A", "B", "B", "D", "D", "A", "A", "A", "C",
        "B", "D", "D", "B", "A", "C", "D", "D", "D", "C", "B", "D", "D", "C",
        "C", "B", "A", "B", "C",
    ],
    ("Reading and Writing", 2): [
        "C", "D", "C", "B", "B", "C", "D", "C", "C", "C", "C", "C", "C", "D",
        "D", "B", "A", "D", "C", "A", "A", "C", "B", "A", "D", "B", "D", "A",
        "B", "C", "D", "B", "C",
    ],
    ("Math", 1): [
        "A", "D", "D", "D", "A", "31", "11", "D", "B", "B", "A", "B",
        ".5; 1/2", "7.5; 15/2", "B", "C", "D", "D", "D", "189/5; 37.8",
        "-24", "D", "A", "C", "D", "A", "54",
    ],
    ("Math", 2): [
        "B", "A", "B", "A", "B", "6", "10", "B", "A", "A", "D", "C",
        "774", "5", "B", "A", "D", "B", "A", ".2916; .2917; 7/24", "1677",
        "B", "A", "D", "A", "A", "-28",
    ],
}

SECTION_PAGES = {
    ("Reading and Writing", 1): range(4, 18),
    ("Reading and Writing", 2): range(18, 31),
    ("Math", 1): range(34, 43),
    ("Math", 2): range(46, 53),
}

RW_OVERRIDES = {
    (1, 1): {
        "prompt": "Though not closely related, the hedgehog tenrecs of Madagascar share many traits with true hedgehogs—including protective spines, pointed snouts, and small body size—traits the two groups of mammals independently developed in response to equivalent roles in their respective habitats.\n\nWhich choice completes the text with the most logical and precise word or phrase?",
    },
    (2, 10): {
        "choices": [
            "A) Although it may seem surprising that foreign investment declines in developing countries as natural-resource extraction makes up a larger share of those countries' economies, that decline happens because resource extraction requires initial investments too large for foreign investors to supply.",
            "B) Although developing countries tend to become less dependent on foreign investment as natural-resource industries make up a larger share of their economies, this change may not occur if the boom-bust cycle of those industries destabilizes local currencies or increases countries' vulnerability to external shocks.",
            "C) Although one might expect that foreign investment would increase as natural-resource extraction makes up a larger share of developing countries' economies, the opposite happens because heavy reliance on natural resources can lead to unattractive conditions for investors.",
            "D) Although foreign investors tend to avoid initial investments in natural-resource industries in developing countries, foreign investment may increase significantly as those industries stabilize and the risks associated with them decline.",
        ],
    },
}

MATH_OVERRIDES = {
    (1, 1): {
        "prompt": "p + 3 + 8 = 10\n\nWhat value of p is the solution to the given equation?",
        "choices": ["A) -1", "B) 5", "C) 15", "D) 21"],
    },
    (1, 2): {
        "prompt": "The scatterplot shows the relationship between two variables, x and y. Which of the following graphs shows the most appropriate model for the data?",
        "choices": ["A) Graph A", "B) Graph B", "C) Graph C", "D) Graph D"],
        "visualRequired": True,
    },
    (1, 6): {
        "prompt": "How many yards are equivalent to 1,116 inches?\n\n1 yard = 36 inches",
    },
    (1, 7): {
        "prompt": "f(x) = 14 + 4x\n\nThe function f represents the total cost, in dollars, of attending an arcade when x games are played. How many games can be played for a total cost of $58?",
    },
    (1, 9): {
        "prompt": "P(t) = 1,800(1.02)^t\n\nThe function P gives the estimated number of marine mammals in a certain area, where t is the number of years since a study began. What is the best interpretation of P(0) = 1,800 in this context?",
    },
    (1, 17): {
        "prompt": "P = N(19 - C)\n\nThe given equation relates the positive numbers P, N, and C. Which equation correctly expresses C in terms of P and N?",
        "choices": ["A) C = 19 + P/N", "B) C = 19 - P/N", "C) C = 19 + N/P", "D) C = 19 - N/P"],
    },
    (1, 18): {
        "prompt": "w^2 + 12w - 40 = 0\n\nWhich of the following is a solution to the given equation?",
        "choices": ["A) 6 - 2√19", "B) 2√19", "C) √19", "D) -6 + 2√19"],
    },
    (1, 19): {
        "prompt": "The table shown summarizes the number of employees at each of the 17 restaurants in a town.\n\nNumber of employees | Number of restaurants\n2 to 7 | 2\n8 to 13 | 4\n14 to 19 | 2\n20 to 25 | 7\n26 to 31 | 2\n\nWhich of the following could be the median number of employees for the restaurants in this town?",
        "choices": ["A) 2", "B) 9", "C) 15", "D) 21"],
    },
    (1, 22): {
        "choices": ["A) 0.5600", "B) 1.0056", "C) 1.1800", "D) 1.1856"],
    },
    (2, 1): {
        "prompt": "The function f is defined by f(x) = 8x. For what value of x does f(x) = 72?",
    },
    (2, 4): {
        "prompt": "The graph of function f is shown, where y = f(x). Which of the following describes function f?",
        "choices": ["A) Increasing linear", "B) Decreasing linear", "C) Increasing exponential", "D) Decreasing exponential"],
        "visualRequired": True,
    },
    (2, 5): {
        "prompt": "The graph of the function f is shown, where y = f(x). What is the y-intercept of the graph?",
        "visualRequired": True,
    },
    (2, 9): {
        "choices": ["A) 17", "B) 96", "C) 102", "D) 612"],
    },
    (2, 11): {
        "prompt": "The function f defined by f(t) = 14 + 9t gives the estimated length, in inches, of a vine plant t months after Tavon purchased it. Which of the following is the best interpretation of 9 in this context?",
    },
    (2, 18): {
        "prompt": "Line k is defined by y = 7x + 1/8. Line j is perpendicular to line k in the xy-plane. What is the slope of line j?",
        "choices": ["A) -8", "B) -1/7", "C) 1/8", "D) 7"],
    },
    (2, 22): {
        "prompt": "In triangle ABC, angle B is a right angle. The length of side AB is 10√37 and the length of side BC is 24√37. What is the length of side AC?",
        "choices": ["A) 14√37", "B) 26√37", "C) 34√37", "D) 34√74"],
    },
    (2, 24): {
        "prompt": "The function f is defined by f(x) = a(x + b), where a and b are constants. In the xy-plane, the graph of y = f(x) passes through the point (-24, 0), and f(24) < 0. Which of the following must be true?",
        "choices": ["A) f(0) = 24", "B) f(0) = -24", "C) a > b", "D) a < b"],
    },
    (2, 25): {
        "prompt": "In the xy-plane, a circle has center C with coordinates (h, k). Points A and B lie on the circle. Point A has coordinates (h + 1, k + √102), and angle ACB is a right angle. What is the length of AB?",
        "choices": ["A) √206", "B) 2√102", "C) 103√2", "D) 103√3"],
    },
}


def with_test_6_config():
    importer.EXTRACTED_PATH = EXTRACTED_PATH
    importer.EXPLANATIONS_PDF = EXPLANATIONS_PDF
    importer.ANSWER_KEYS = ANSWER_KEYS
    importer.SECTION_PAGES = SECTION_PAGES
    importer.MATH_OVERRIDES = {}
    importer.CHOICE_OVERRIDES = {}


def parse_scoring_table():
    payload = json.loads(SCORING_EXTRACTED_PATH.read_text(encoding="utf-8"))
    page_text = "\n".join(page["text"] for page in payload.get("pages", []) if page.get("page") == 5)
    table = {}
    for match in re.finditer(r"(?m)^(\d+)\s+(\d{3})\s+(\d{3})(?:\s+(\d{3})\s+(\d{3}))?$", page_text):
        raw = int(match.group(1))
        table[raw] = {"Reading and Writing": [int(match.group(2)), int(match.group(3))]}
        if match.group(4) and match.group(5):
            table[raw]["Math"] = [int(match.group(4)), int(match.group(5))]
    if len(table) < 67 or 54 not in table or "Math" not in table[54]:
        raise ValueError(f"Could not parse full Practice Test 6 scoring table; parsed {len(table)} rows")
    return table


def build_bank():
    with_test_6_config()
    items = importer.build_bank()
    for item in items:
        module_number = item["metadata"]["moduleNumber"]
        question_number = item["metadata"]["questionNumber"]
        item["id"] = item["id"].replace("pt4-", "pt6-")
        item["module"] = item["module"].replace("Practice Test 4", "Practice Test 6")
        item["source"] = "College Board SAT Practice Test 6 Digital PDF"
        item["logic"] = item["logic"].replace("Practice Test 4", "Practice Test 6")
        item["metadata"]["practiceTest"] = 6

        override = MATH_OVERRIDES.get((module_number, question_number), {}) if item["section"] == "Math" else RW_OVERRIDES.get((module_number, question_number), {})
        if "prompt" in override:
            item["prompt"] = override["prompt"]
        if "choices" in override:
            item["choices"] = override["choices"]
            item["type"] = "multiple-choice" if item["choices"] else "student-produced-response"
        if override.get("visualRequired"):
            item["metadata"]["visualRequired"] = True
    return items


def main():
    existing = json.loads(OUTPUT_PATH.read_text(encoding="utf-8")) if OUTPUT_PATH.exists() else []
    existing = [item for item in existing if (item.get("metadata") or {}).get("practiceTest") != 6]
    bank = existing + build_bank()
    OUTPUT_PATH.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    scoring_path = ROOT / "data" / "seed" / "scoringTables.json"
    scoring_payload = json.loads(scoring_path.read_text(encoding="utf-8")) if scoring_path.exists() else {"tests": {}}
    scoring_payload.setdefault("tests", {})["6"] = {
        "title": "SAT Practice Test 6",
        "scoreType": "range",
        "table": parse_scoring_table(),
    }
    scoring_path.write_text(json.dumps(scoring_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(bank)} total questions to {OUTPUT_PATH}")
    print(f"Added {len(bank) - len(existing)} Practice Test 6 questions")
    print(f"Wrote scoring table to {scoring_path}")


if __name__ == "__main__":
    main()
