import json
import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - depends on local tooling
    PdfReader = None


ROOT = Path(__file__).resolve().parents[1]
EXTRACTED_PATH = ROOT / "data" / "seed" / "extracted-sat-practice-test-4.json"
OUTPUT_PATH = ROOT / "data" / "seed" / "questionBank.json"
EXPLANATIONS_PDF = Path("/private/tmp/sat-practice-test-4-answers-digital.pdf")

ANSWER_KEYS = {
    ("Reading and Writing", 1): [
        "B", "A", "A", "C", "A", "B", "D", "B", "B", "D", "C", "D", "A", "B",
        "C", "A", "A", "A", "A", "D", "D", "D", "B", "C", "B", "A", "C", "D",
        "A", "A", "D", "D", "C",
    ],
    ("Reading and Writing", 2): [
        "D", "D", "B", "B", "B", "B", "A", "C", "C", "A", "A", "B", "D", "C",
        "C", "A", "B", "D", "C", "A", "B", "D", "D", "A", "B", "B", "A", "A",
        "C", "C", "A", "A", "B",
    ],
    ("Math", 1): [
        "B", "A", "B", "D", "A", "9", "10", "A", "B", "D", "A", "C",
        "1/5; .2", "80", "D", "B", "B", "A", "C", "100", "361/8; 45.12; 45.13",
        "B", "D", "C", "C", "D", "5",
    ],
    ("Math", 2): [
        "B", "B", "C", "A", "A", "15; -5", "50", "B", "D", "A", "A", "B",
        ".3; 3/10", "2", "A", "C", "B", "D", "A", "15/17; .8824; .8823", "51",
        "A", "C", "C", "D", "B", "600",
    ],
}

SECTION_PAGES = {
    ("Reading and Writing", 1): range(4, 18),
    ("Reading and Writing", 2): range(18, 31),
    ("Math", 1): range(34, 40),
    ("Math", 2): range(42, 49),
}

RW_CONCEPTS = [
    (range(1, 5), "Words in context", "Choose the most logical and precise word or phrase"),
    (range(5, 13), "Craft and structure", "Analyze main ideas, purpose, structure, and paired texts"),
    (range(13, 19), "Command of evidence", "Use textual or quantitative evidence to support a claim"),
    (range(19, 27), "Standard English conventions", "Apply grammar, usage, and punctuation conventions"),
    (range(27, 29), "Transitions", "Select the most logical transition"),
    (range(29, 34), "Rhetorical synthesis", "Use notes to accomplish a writing goal"),
]

MATH_CONCEPTS = {
    1: "Problem-solving and data analysis",
    2: "Problem-solving and data analysis",
    3: "Algebra",
    4: "Algebra",
    5: "Functions",
    6: "Algebra",
    7: "Algebra",
    8: "Functions",
    9: "Geometry and trigonometry",
    10: "Problem-solving and data analysis",
    11: "Algebra",
    12: "Algebra",
    13: "Algebra",
    14: "Algebra",
    15: "Algebra",
    16: "Functions",
    17: "Problem-solving and data analysis",
    18: "Advanced math",
    19: "Algebra",
    20: "Geometry and trigonometry",
    21: "Advanced math",
    22: "Geometry and trigonometry",
    23: "Advanced math",
    24: "Advanced math",
    25: "Geometry and trigonometry",
    26: "Advanced math",
    27: "Advanced math",
}

MATH_OVERRIDES = {
    (1, 1): {
        "image": "/assets/sat-pt4/math-m1-q01.png",
        "visualRequired": True,
    },
    (1, 3): {
        "prompt": "x^2 / 25 = 36\n\nWhat is a solution to the given equation?",
        "choices": ["A) 6", "B) 30", "C) 450", "D) 900"],
    },
    (1, 4): {
        "choices": ["A) (3)(8)x = 83", "B) 8x = 83 + 3", "C) 3x + 8 = 83", "D) 8x + 3 = 83"],
    },
    (1, 8): {
        "prompt": "For the linear function f, the table shows three values of x and their corresponding values of f(x).\n\nx | f(x)\n0 | 29\n1 | 32\n2 | 35\n\nWhich equation defines f(x)?",
        "choices": ["A) f(x) = 3x + 29", "B) f(x) = 29x + 32", "C) f(x) = 35x + 29", "D) f(x) = 32x + 35"],
    },
    (1, 9): {
        "image": "/assets/sat-pt4/math-m1-q09.png",
        "visualRequired": True,
    },
    (1, 10): {
        "image": "/assets/sat-pt4/math-m1-q10.png",
        "visualRequired": True,
    },
    (1, 12): {
        "image": "/assets/sat-pt4/math-m1-q12.png",
        "visualRequired": True,
    },
    (1, 13): {
        "prompt": "If x/8 = 5, what is the value of 8/x?",
    },
    (1, 14): {
        "prompt": "24x + y = 48\n6x + y = 72\n\nThe solution to the given system of equations is (x, y). What is the value of y?",
    },
    (1, 15): {
        "prompt": "Line t in the xy-plane has a slope of -1/3 and passes through the point (9, 10). Which equation defines line t?",
        "choices": ["A) y = (1/3)x - 3", "B) y = 9x + 10", "C) y = -x + 103", "D) y = (-1/3)x + 13"],
    },
    (1, 18): {
        "choices": ["A) f(x) = (x + 44)^2", "B) f(x) = (x + 176)^2", "C) f(x) = (176x + 44)^2", "D) f(x) = (176x + 176)^2"],
    },
    (1, 19): {
        "prompt": "14x/(7y) = 2√(w + 19)\n\nThe given equation relates the distinct positive real numbers w, x, and y. Which equation correctly expresses w in terms of x and y?",
        "choices": ["A) w = √(x/y) - 19", "B) w = √(28x/(14y)) - 19", "C) w = (x/y)^2 - 19", "D) w = (28x/(14y))^2 - 19"],
    },
    (1, 21): {
        "prompt": "The expression 6 fifth-root(3^5 x^45) · eighth-root(2^8 x) is equivalent to ax^b, where a and b are positive constants and x > 1.\n\nWhat is the value of a + b?",
    },
    (1, 22): {
        "prompt": "A right triangle has sides of length 2√2, 6√2, and √80 units. What is the area of the triangle, in square units?",
        "choices": ["A) 8√2 + √80", "B) 12", "C) 24√80", "D) 24"],
    },
    (1, 23): {
        "prompt": "The expression 4x^2 + bx - 45, where b is a constant, can be rewritten as (hx + k)(x + j), where h, k, and j are integer constants. Which of the following must be an integer?",
        "choices": ["A) b/h", "B) b/k", "C) 45/h", "D) 45/k"],
    },
    (1, 24): {
        "prompt": "y = 2x^2 - 21x + 64\ny = 3x + a\n\nIn the given system of equations, a is a constant. The graphs of the equations in the given system intersect at exactly one point, (x, y), in the xy-plane. What is the value of x?",
    },
    (1, 26): {
        "prompt": "In the xy-plane, a parabola has vertex (9, -14) and intersects the x-axis at two points. If the equation of the parabola is written in the form y = ax^2 + bx + c, where a, b, and c are constants, which of the following could be the value of a + b + c?",
    },
    (1, 27): {
        "prompt": "Function f is defined by f(x) = -ax + b, where a and b are constants. In the xy-plane, the graph of y = f(x) - 15 has a y-intercept at (0, -99/7). The product of a and b is 65/7. What is the value of a?",
    },
    (2, 4): {
        "prompt": "x + y = 18\nx = 5y\n\nWhat is the solution (x, y) to the given system of equations?",
    },
    (2, 6): {
        "prompt": "|x - 5| = 10\n\nWhat is one possible solution to the given equation?",
    },
    (2, 7): {
        "prompt": "f(x) = 7x + 1\n\nThe function gives the total number of people on a company retreat with x managers. What is the total number of people on a company retreat with 7 managers?",
    },
    (2, 9): {
        "prompt": "The function f is defined by f(x) = 270(0.1)^x. What is the value of f(0)?",
    },
    (2, 12): {
        "prompt": "-4x^2 - 7x = -36\n\nWhat is the positive solution to the given equation?",
        "choices": ["A) 7/4", "B) 9/4", "C) 4", "D) 7"],
    },
    (2, 14): {
        "prompt": "f(x) = 2x + 3\n\nFor the given function f, the graph of y = f(x) in the xy-plane is parallel to line j. What is the slope of line j?",
    },
    (2, 17): {
        "choices": ["A) 0", "B) 1/7", "C) 4/3", "D) 4"],
    },
    (2, 18): {
        "prompt": "f(x) = (x - 10)(x + 13)\n\nThe function f is defined by the given equation. For what value of x does f(x) reach its minimum?",
        "choices": ["A) -130", "B) -13", "C) -23/2", "D) -3/2"],
    },
    (2, 19): {
        "prompt": "The function f(x) = 1/9(x - 7)^2 + 3 gives a metal ball's height above the ground f(x), in inches, x seconds after it started moving on a track, where 0 <= x <= 10. Which of the following is the best interpretation of the vertex of the graph of y = f(x) in the xy-plane?",
    },
    (2, 20): {
        "prompt": "In triangle JKL, cos(K) = 24/51 and angle J is a right angle. What is the value of cos(L)?",
    },
    (2, 21): {
        "prompt": "-x^2 + bx - 676 = 0\n\nIn the given equation, b is a positive integer. The equation has no real solution. What is the greatest possible value of b?",
    },
    (2, 22): {
        "prompt": "If a new graph of three linear equations is created using the system of equations shown and the equation x + 4y = -16, how many solutions (x, y) will the resulting system of three equations have?",
        "choices": ["A) Zero", "B) Exactly one", "C) Exactly two", "D) Infinitely many"],
        "image": "/assets/sat-pt4/math-m2-q22.png",
        "visualRequired": True,
    },
    (2, 23): {
        "prompt": "f(x) = 5,470(0.64)^(x/12)\n\nThe function f gives the value, in dollars, of a certain piece of equipment after x months of use. If the value of the equipment decreases each year by p% of its value the preceding year, what is the value of p?",
    },
    (2, 25): {
        "prompt": "The equation x^2 + (y - 1)^2 = 49 represents circle A. Circle B is obtained by shifting circle A down 2 units in the xy-plane. Which of the following equations represents circle B?",
        "choices": ["A) (x - 2)^2 + (y - 1)^2 = 49", "B) x^2 + (y - 3)^2 = 49", "C) (x + 2)^2 + (y - 1)^2 = 49", "D) x^2 + (y + 1)^2 = 49"],
    },
    (2, 26): {
        "prompt": "Two identical rectangular prisms each have a height of 90 centimeters (cm). The base of each prism is a square, and the surface area of each prism is K cm^2. If the prisms are glued together along a square base, the resulting prism has a surface area of (92/47)K cm^2. What is the side length, in cm, of each square base?",
    },
}

CHOICE_OVERRIDES = {
    ("Reading and Writing", 1, 14): [
        "A) The feathers located on the wings of the migratory fork-tailed flycatchers have a narrower shape than those of the nonmigratory birds, which allows them to fly long distances.",
        "B) Over several generations, the sound made by the feathers of migratory male fork-tailed flycatchers grows progressively higher pitched relative to that made by the feathers of nonmigratory males.",
        "C) Fork-tailed flycatchers communicate different messages to each other depending on whether their feathers create high-pitched or low-pitched sounds.",
        "D) The breeding habits of the migratory and nonmigratory fork-tailed flycatchers remained generally the same over several generations.",
    ],
    ("Reading and Writing", 2, 2): ["A) conceptualize", "B) neglect", "C) illustrate", "D) overcome"],
    ("Reading and Writing", 2, 8): ["A) reciprocate", "B) annotate", "C) buttress", "D) disengage"],
    ("Math", 2, 4): ["A) (15, 3)", "B) (16, 2)", "C) (17, 1)", "D) (18, 0)"],
    ("Math", 2, 9): ["A) 0", "B) 1", "C) 27", "D) 270"],
    ("Math", 2, 24): [
        "A) The median of data set B is equal to the median of data set A, and the range of data set B is equal to the range of data set A.",
        "B) The median of data set B is equal to the median of data set A, and the range of data set B is greater than the range of data set A.",
        "C) The median of data set B is greater than the median of data set A, and the range of data set B is equal to the range of data set A.",
        "D) The median of data set B is greater than the median of data set A, and the range of data set B is greater than the range of data set A.",
    ],
}

EXPLANATION_SECTIONS = [
    ("Reading and Writing", 1, "READING AND WRITING: MODULE 1", "READING AND WRITING: MODULE 2"),
    ("Reading and Writing", 2, "READING AND WRITING: MODULE 2", "MATH: MODULE 1"),
    ("Math", 1, "MATH: MODULE 1", "MATH: MODULE 2"),
    ("Math", 2, "MATH: MODULE 2", None),
]


def clean_spaces(text):
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def one_line(text):
    return re.sub(r"\s+", " ", text).strip()


def load_page_texts():
    data = json.loads(EXTRACTED_PATH.read_text(encoding="utf-8"))
    return {page["page"]: page["text"] for page in data["pages"]}


def is_bad_marker(section, number, text, start):
    before = text[max(0, start - 40):start]
    after = text[start:start + 350]
    if re.search(r"Module\s*$", before):
        return True
    bad_after = [
        "Reading and Writing",
        "Math\n27 QUESTIONS",
        "For multiple-choice questions",
        "The number of degrees",
        "REFERENCE",
        "DIRECTIONS",
    ]
    if any(phrase in after for phrase in bad_after):
        return True
    return False


def question_markers(section, text, total):
    markers = []
    position = 0
    for number in range(1, total + 1):
        candidates = [
            match for match in re.finditer(rf"(?m)^\s*{number}\s*$", text[position:])
            if not is_bad_marker(section, number, text, position + match.start())
        ]
        if not candidates:
            raise ValueError(f"Could not find marker for {section} question {number}")
        match = candidates[0]
        absolute_start = position + match.start()
        absolute_end = position + match.end()
        markers.append((number, absolute_start, absolute_end))
        position = absolute_end
    return markers


def strip_boilerplate(text):
    text = re.sub(r"Unauthorized copying or reuse of any part of this page is illegal\.", " ", text, flags=re.I)
    text = re.sub(r"\b\d+\s+CO\s*N\s*T\s*I\s*N\s*U\s*E\b", " ", text, flags=re.I)
    text = re.sub(r"\bSTOP\b.*$", " ", text, flags=re.I | re.S)
    text = re.sub(r"^Module\s+\d\s+", " ", text)
    text = re.sub(r"^\s*Reading and Writing\s+33 QUESTIONS.*?single best answer\.", " ", text, flags=re.S)
    text = re.sub(r"^\s*Math\s+27 QUESTIONS.*?(?=\n\s*1\s*\n)", " ", text, flags=re.S)
    return clean_spaces(text)


def clean_question_block(text):
    text = re.sub(r"\n\s*Module\s*\n\s*[12]\s*\n", "\n", text)
    text = re.sub(r"\n\s*Module\s*\n", "\n", text)
    return clean_spaces(text)


def clean_artifacts(text):
    lines = []
    for line in str(text or "").splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if re.fullmatch(r"[-~_\s]{4,}", stripped):
            continue
        if re.search(r"</l|\.{3,}|___|I I I|CO N T I N U E", stripped):
            continue
        if len(stripped) > 8:
            graph_chars = sum(stripped.count(char) for char in "-~_+|")
            if graph_chars / max(1, len(stripped)) > 0.35:
                continue
        lines.append(line)
    return clean_spaces("\n".join(lines))


def parse_choices(block):
    matches = list(re.finditer(r"(?m)^\s*([A-D])\)\s*", block))
    if len(matches) < 4:
        return block, []
    prompt = block[:matches[0].start()]
    choices = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(block)
        label = match.group(1)
        body = block[match.end():end]
        choices.append(f"{label}) {one_line(body)}")
    return prompt, choices


def parse_section(section, module, pages):
    total = len(ANSWER_KEYS[(section, module)])
    raw_text = "\n".join(pages[page] for page in SECTION_PAGES[(section, module)])
    raw_text = strip_boilerplate(raw_text)
    markers = question_markers(section, raw_text, total)
    questions = []
    for index, (number, _, marker_end) in enumerate(markers):
        end = markers[index + 1][1] if index + 1 < len(markers) else len(raw_text)
        block = clean_question_block(raw_text[marker_end:end])
        prompt, choices = parse_choices(block)
        prompt = clean_artifacts(prompt)
        choices = [clean_artifacts(choice) for choice in choices]
        questions.append((number, clean_spaces(prompt), choices))
    return questions


def explanation_text():
    if not EXPLANATIONS_PDF.exists() or PdfReader is None:
        return ""
    reader = PdfReader(str(EXPLANATIONS_PDF))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def parse_explanations():
    text = explanation_text()
    if not text:
        return {}
    explanations = {}
    for section, module, start_token, end_token in EXPLANATION_SECTIONS:
        start = text.find(start_token)
        end = text.find(end_token, start + len(start_token)) if end_token else len(text)
        if start == -1:
            continue
        chunk = text[start:end if end != -1 else len(text)]
        matches = list(re.finditer(r"QUESTION\s+(\d+)", chunk))
        for index, match in enumerate(matches):
            number = int(match.group(1))
            block_end = matches[index + 1].start() if index + 1 < len(matches) else len(chunk)
            block = one_line(chunk[match.end():block_end])
            block = re.sub(r"^Choice ([A-D]) is the best answer because\s+", r"Choice \1 is correct because ", block)
            block = re.sub(r"^Choice ([A-D]) is correct\.\s*", r"Choice \1 is correct. ", block)
            block = re.split(r"\s+Choice [A-D] is incorrect", block)[0]
            explanations[(section, module, number)] = block.strip()
    return explanations


def rw_metadata(number):
    for numbers, concept, skill in RW_CONCEPTS:
        if number in numbers:
            return concept, skill
    return "Reading and writing", "Answer the SAT Reading and Writing question"


def math_metadata(number):
    concept = MATH_CONCEPTS.get(number, "Math")
    return concept, "Solve the SAT Math question"


def difficulty(number, total):
    if number <= max(1, total // 3):
        return "Easy"
    if number <= max(1, (2 * total) // 3):
        return "Medium"
    return "Hard"


def build_bank():
    pages = load_page_texts()
    explanations = parse_explanations()
    bank = []
    for section, module in SECTION_PAGES:
        parsed = parse_section(section, module, pages)
        total = len(parsed)
        for number, prompt, choices in parsed:
            answer = ANSWER_KEYS[(section, module)][number - 1]
            if section == "Reading and Writing":
                concept, skill = rw_metadata(number)
                prefix = "rw"
                choices = CHOICE_OVERRIDES.get((section, module, number), choices)
            else:
                concept, skill = math_metadata(number)
                prefix = "math"
                override = MATH_OVERRIDES.get((module, number), {})
                prompt = override.get("prompt", prompt)
                choices = override.get("choices", choices)
                choices = CHOICE_OVERRIDES.get((section, module, number), choices)
            item_type = "multiple-choice" if choices else "student-produced-response"
            metadata = {
                "practiceTest": 4,
                "moduleNumber": module,
                "questionNumber": number,
            }
            if section == "Math":
                override = MATH_OVERRIDES.get((module, number), {})
                if override.get("image"):
                    metadata["image"] = override["image"]
                if override.get("visualRequired"):
                    metadata["visualRequired"] = True
            bank.append({
                "id": f"pt4-{prefix}-m{module}-{number:02d}",
                "section": section,
                "module": f"Practice Test 4 Module {module}",
                "type": item_type,
                "difficulty": difficulty(number, total),
                "concept": concept,
                "skill": skill,
                "prompt": prompt,
                "choices": choices,
                "answer": answer,
                "explanation": explanations.get((section, module, number), "Official answer key imported from College Board Practice Test 4 scoring guide."),
                "logic": "Imported from College Board SAT Practice Test 4. For items with graphs or figures, review the source PDF page if the extracted text omits visual detail.",
                "tutorial": "Identify the tested skill, restate the question in your own words, and eliminate choices or compute carefully before answering.",
                "source": "College Board SAT Practice Test 4 Digital PDF",
                "metadata": metadata,
            })
    return bank


def main():
    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else OUTPUT_PATH
    bank = build_bank()
    output_path.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    counts = {}
    for item in bank:
        key = (item["section"], item["module"], item["type"])
        counts[key] = counts.get(key, 0) + 1
    print(f"Wrote {len(bank)} questions to {output_path}")
    for key, count in sorted(counts.items()):
        print(f"{key}: {count}")


if __name__ == "__main__":
    main()
