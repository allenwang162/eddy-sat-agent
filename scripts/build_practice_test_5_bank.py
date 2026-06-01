import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import scripts.build_practice_test_4_bank as importer

EXTRACTED_PATH = ROOT / "data" / "seed" / "extracted-sat-practice-test-5.json"
OUTPUT_PATH = ROOT / "data" / "seed" / "questionBank.json"
EXPLANATIONS_PDF = Path("/Users/allenwang/Downloads/full-length-sat-paper-practice-test_-bundle-5/sat-practice-test-5-answers-digital.pdf")

ANSWER_KEYS = {
    ("Reading and Writing", 1): [
        "A", "B", "B", "D", "B", "D", "B", "C", "B", "B", "D", "A", "D", "B",
        "C", "B", "A", "B", "A", "C", "A", "D", "B", "D", "B", "B", "D", "D",
        "B", "D", "A", "C", "D",
    ],
    ("Reading and Writing", 2): [
        "C", "D", "A", "A", "C", "C", "B", "A", "A", "D", "A", "D", "D", "D",
        "D", "B", "A", "A", "B", "A", "C", "B", "A", "C", "C", "B", "C", "D",
        "D", "A", "D", "D", "A",
    ],
    ("Math", 1): [
        "C", "B", "D", "B", "B", "4", "29", "C", "B", "B", "C", "D", "6",
        "4.51; 451/100", "C", "D", "B", "D", "A", ".3928; .3929; 11/28", "336",
        "B", "D", "D", "A", "A", "25",
    ],
    ("Math", 2): [
        "B", "B", "B", "B", "D", "6", "30; -30", "D", "B", "A", "C", "D",
        "14.66; 14.67; 44/3", "4205", "A", "A", "B", "B", "D", "20", "66",
        "D", "D", "D", "A", "C", "4176",
    ],
}

SECTION_PAGES = {
    ("Reading and Writing", 1): range(4, 17),
    ("Reading and Writing", 2): range(18, 32),
    ("Math", 1): range(34, 42),
    ("Math", 2): range(44, 51),
}

MATH_OVERRIDES = {
    (1, 1): {
        "prompt": "The graph of a system of a linear equation and a nonlinear equation is shown. What is the solution (x, y) to this system?",
        "image": "/assets/sat-pt5/math-m1-q01.png",
        "visualRequired": True,
    },
    (1, 3): {
        "prompt": "The graph of the linear function f is shown, where y = f(x). What is the y-intercept of the graph of f?",
        "choices": ["A) (0, 0)", "B) (0, -16/11)", "C) (0, -8)", "D) (0, 8)"],
        "image": "/assets/sat-pt5/math-m1-q03.png",
        "visualRequired": True,
    },
    (1, 6): {
        "prompt": "The graph of a system of linear equations is shown. The solution to the system is (x, y). What is the value of x?",
        "image": "/assets/sat-pt5/math-m1-q06.png",
        "visualRequired": True,
    },
    (1, 8): {
        "prompt": "In the figure, line m is parallel to line n, and line k intersects both lines. Which of the following statements is true?",
        "image": "/assets/sat-pt5/math-m1-q08.png",
        "visualRequired": True,
    },
    (1, 11): {
        "choices": ["A) -24", "B) -22", "C) -6", "D) -1"],
    },
    (1, 13): {
        "prompt": "y = 4x\ny = x^2 - 12\n\nA solution to the given system of equations is (x, y), where x > 0. What is the value of x?",
    },
    (1, 14): {
        "prompt": "A store sells two different-sized containers of blueberries. The store's sales of these blueberries totaled 896.86 dollars last month. The equation 4.51x + 6.07y = 896.86 represents this situation, where x is the number of smaller containers sold and y is the number of larger containers sold. According to the equation, what is the price, in dollars, of each smaller container?",
    },
    (1, 16): {
        "prompt": "The graph of the rational function f is shown, where y = f(x) and x >= 0. Which of the following is the graph of y = f(x) + 5, where x >= 0?",
        "choices": ["A) Graph A", "B) Graph B", "C) Graph C", "D) Graph D"],
        "image": "/assets/sat-pt5/math-m1-q16.png",
        "visualRequired": True,
    },
    (1, 19): {
        "prompt": "What is (11/28)^2?",
        "choices": ["A) 121/784", "B) 121/56", "C) 11/56", "D) 22/28"],
    },
    (1, 20): {
        "prompt": "What is 11/28 expressed as a decimal?",
    },
    (1, 24): {
        "prompt": "Which of the following functions has(have) a minimum value at -3?\n\nI. f(x) = -3\nII. f(x) = (x + 3)^2\nIII. f(x) = (x - 3)^2",
        "choices": ["A) I only", "B) II only", "C) III only", "D) I and II only"],
    },
    (2, 2): {
        "prompt": "Argon is placed inside a container with a constant volume. The graph shows the estimated pressure y, in pounds per square inch (psi), of the argon when its temperature is x kelvins. What is the estimated pressure of the argon, in psi, when the temperature is 600 kelvins?",
        "image": "/assets/sat-pt5/math-m2-q02.png",
        "visualRequired": True,
    },
    (2, 5): {
        "choices": ["A) c = 25x", "B) c = 36x", "C) c = 11x + 25", "D) c = 25x + 11"],
    },
    (2, 9): {
        "prompt": "A competitive diver dives from a platform into the water. The graph shown gives the height above the water y, in meters, of the diver x seconds after diving from the platform. What is the best interpretation of the x-intercept of the graph?",
        "image": "/assets/sat-pt5/math-m2-q09.png",
        "visualRequired": True,
    },
    (2, 10): {
        "prompt": "The kinetic energy, in joules, of an object with mass 9 kilograms traveling at a speed of v meters per second is given by the function K, where K(v) = (9/2)v^2. Which of the following is the best interpretation of K(34) = 5,202 in this context?",
    },
    (2, 11): {
        "prompt": "The scatterplot shows the relationship between two variables x and y. A line of best fit for the data is also shown. For how many of the 10 data points is the actual y-value greater than the y-value predicted by the line of best fit?",
        "choices": ["A) 3", "B) 4", "C) 6", "D) 7"],
        "image": "/assets/sat-pt5/math-m2-q11.png",
        "visualRequired": True,
    },
    (2, 13): {
        "prompt": "What is the slope of the graph of y = (1/3)(29x + 10) + 5x in the xy-plane?",
    },
    (2, 15): {
        "prompt": "Five Eretmochelys imbricata, a type of sea turtle, each have a nest. The table shows an original data set of the number of eggs that each turtle laid in its nest.\n\nNest | Number of eggs\nA | 149\nB | 144\nC | 148\nD | 136\nE | 139\n\nA sixth nest with 121 eggs is added to create a new data set. Which of the following correctly compares the means of the two data sets?",
        "choices": [
            "A) The mean of the original data set is greater than the mean of the new data set.",
            "B) The mean of the original data set is less than the mean of the new data set.",
            "C) The means of both data sets are equal.",
            "D) There is not enough information to compare the means.",
        ],
    },
    (2, 16): {
        "choices": ["A) 116", "B) 118", "C) 126", "D) 180"],
    },
    (2, 21): {
        "prompt": "A rectangle is inscribed in a circle, such that each vertex of the rectangle lies on the circumference of the circle. The diagonal of the rectangle is twice the length of the shortest side of the rectangle. The area of the rectangle is 1,089√3 square units. What is the length, in units, of the diameter of the circle?",
    },
    (2, 23): {
        "prompt": "Which expression is equivalent to (42a/k) + 42ak, where k > 0?",
        "choices": ["A) 84a/k", "B) 84ak^2/k", "C) 42a(k + 1)/k", "D) 42a(k^2 + 1)/k"],
    },
    (2, 25): {
        "prompt": "P(t) = 260(1.04)^(4t/6)\n\nThe function P models the population, in thousands, of a certain city t years after 2003. According to the model, the population is predicted to increase by 4% every n months. What is the value of n?",
    },
    (2, 26): {
        "choices": ["A) (0, 6/5)", "B) (4, 7)", "C) (10, 2)", "D) (11, 1)"],
    },
}

RW_OVERRIDES = {
    (1, 2): {
        "prompt": "Many ancient sculptures of people's heads are missing their noses. This is because the nose is the most _______ part of a sculpture of a person's head. It is delicate and sticks out from the rest of the sculpture, making it especially easy to break.\n\nWhich choice completes the text with the most logical and precise word or phrase?",
        "choices": ["A) recognizable", "B) fragile", "C) common", "D) sophisticated"],
    },
    (1, 15): {
        "choices": [
            "A) \"This wallpaper has a kind of sub-pattern in a different shade, a particularly irritating one, for you can only see it in certain lights, and not clearly then.\"",
            "B) \"By moonlight--the moon shines in all night when there is a moon--I wouldn't know it was the same paper.\"",
            "C) \"I'm really getting quite fond of the big room, all but that horrid [wall]paper.\"",
            "D) \"The color is repellant, almost revolting; a smouldering, unclean yellow, strangely faded by the slow-turning sunlight.\"",
        ],
    },
    (1, 21): {
        "prompt": "In 1929, Edwin Herbert Land invented a polarizing filter that was featured in a number of products, from sunglasses to 3D movies. A decade later, Land _______ his technology to invent the world's first instant camera, the Polaroid Land camera.\n\nWhich choice completes the text so that it conforms to the conventions of Standard English?",
        "choices": ["A) used", "B) to have used", "C) to use", "D) using"],
    },
    (1, 31): {
        "choices": [
            "A) The real author of Adam Bede was Mary Ann Evans, who published the novel using the pseudonym George Eliot.",
            "B) George Eliot, which Adam Bede's title page indicated was the name of the novel's author, was widely assumed to be a pseudonym.",
            "C) The title page of the novel Adam Bede indicated that the author's name was George Eliot.",
            "D) A woman who had used a pseudonym to conceal her identity later revealed herself as the real author of Adam Bede.",
        ],
    },
    (2, 7): {
        "choices": [
            "A) It explains a discrepancy between what has been observed in study settings and what has been observed in real-world settings that the text goes on to assert is attributable to the studies not using real-world data.",
            "B) It identifies a conflict between research findings and recent events that the text goes on to suggest is a consequence of a complicating factor in the data used to generate those findings.",
            "C) It presents a long-standing divergence in research findings that the text goes on to say is due to different groups of researchers using data that derive from different electoral circumstances.",
            "D) It describes a recent exception to a general pattern in research findings that the text goes on to explain is a result of researchers underestimating the significance of inconsistencies in the data they've analyzed.",
        ],
    },
    (2, 11): {
        "choices": [
            "A) Literary theorist Mikhail Bakhtin argued that there are important characteristics of narratives that are not fully encompassed by two concepts that other theorists have used to analyze narratives.",
            "B) Literary theorist Mikhail Bakhtin claimed that meaning is not inherent in a narrative but is created when an audience encounters a narrative so that narratives are interpreted differently by different people.",
            "C) The storytelling methods used in The Godfather Part II may seem unusually complicated, but they can be easily understood when two concepts from literary theory are utilized.",
            "D) Narratives that are told out of chronological order are more difficult for audiences to understand than are narratives presented chronologically.",
        ],
    },
    (1, 16): {
        "image": "/assets/sat-pt5/rw-m1-q16.png",
        "visualRequired": True,
    },
    (2, 12): {
        "image": "/assets/sat-pt5/rw-m2-q12.png",
        "visualRequired": True,
    },
    (2, 14): {
        "image": "/assets/sat-pt5/rw-m2-q14.png",
        "visualRequired": True,
    },
    (2, 16): {
        "prompt": "Simulated Change in Annual Aquifer Input and Irrigation Output if Precipitation Concentration Increases as Climate Models Predict\n\nBaseline precipitation currently somewhat concentrated: water entering aquifers +4.9%, surface water used for irrigation +0.4%, groundwater used for irrigation +0.9%.\nBaseline precipitation currently evenly distributed: water entering aquifers +11.0%, surface water used for irrigation +9.0%, groundwater used for irrigation +7.9%.\n\nSome climate models for the western United States predict that while total annual precipitation may remain unchanged from the present level, precipitation will become concentrated into fewer but more intense rain and snow events. University of Michigan researchers simulated how this change would affect water resources in two places with different baseline precipitation patterns. Which choice most effectively uses data from the table to complete the statement?",
        "choices": [
            "A) If baseline precipitation is somewhat concentrated, the amount of water being used for irrigation will increase 0.4% for surface water and 0.9% for groundwater, whereas the amount of water entering aquifers will increase 11.0% if baseline precipitation is evenly distributed.",
            "B) If baseline precipitation is somewhat concentrated, water use for irrigation will increase only slightly, whereas it will increase 9.0% for surface water and 7.9% for groundwater if baseline precipitation is evenly distributed.",
            "C) If baseline precipitation is somewhat concentrated, the amount of water entering aquifers will increase 4.9%, while the amount being used for irrigation will increase 0.4% for surface water and 0.9% for groundwater.",
            "D) If baseline precipitation is somewhat concentrated, water use for irrigation will decline by a small amount, whereas it will increase 11.0% for surface water and 9.0% for groundwater if baseline precipitation is evenly distributed.",
        ],
    },
    (2, 25): {
        "choices": ["A) Serra is intending", "B) Serra, intends", "C) Serra, intending", "D) Serra intends"],
    },
}

SCORING_TABLE = {
    0: {"Reading and Writing": [200, 200], "Math": [200, 200]},
    1: {"Reading and Writing": [200, 200], "Math": [200, 200]},
    2: {"Reading and Writing": [200, 200], "Math": [200, 200]},
    3: {"Reading and Writing": [200, 200], "Math": [200, 210]},
    4: {"Reading and Writing": [200, 200], "Math": [200, 220]},
    5: {"Reading and Writing": [200, 210], "Math": [200, 240]},
    6: {"Reading and Writing": [200, 230], "Math": [210, 260]},
    7: {"Reading and Writing": [200, 240], "Math": [220, 270]},
    8: {"Reading and Writing": [200, 250], "Math": [230, 290]},
    9: {"Reading and Writing": [200, 260], "Math": [270, 330]},
    10: {"Reading and Writing": [220, 280], "Math": [290, 330]},
    11: {"Reading and Writing": [230, 290], "Math": [300, 340]},
    12: {"Reading and Writing": [240, 300], "Math": [310, 350]},
    13: {"Reading and Writing": [250, 310], "Math": [320, 360]},
    14: {"Reading and Writing": [260, 320], "Math": [330, 370]},
    15: {"Reading and Writing": [270, 330], "Math": [340, 380]},
    16: {"Reading and Writing": [290, 350], "Math": [340, 380]},
    17: {"Reading and Writing": [310, 370], "Math": [350, 390]},
    18: {"Reading and Writing": [330, 370], "Math": [350, 390]},
    19: {"Reading and Writing": [340, 380], "Math": [360, 400]},
    20: {"Reading and Writing": [350, 390], "Math": [370, 410]},
    21: {"Reading and Writing": [360, 400], "Math": [380, 420]},
    22: {"Reading and Writing": [360, 400], "Math": [380, 420]},
    23: {"Reading and Writing": [370, 410], "Math": [390, 430]},
    24: {"Reading and Writing": [380, 420], "Math": [400, 440]},
    25: {"Reading and Writing": [390, 430], "Math": [410, 450]},
    26: {"Reading and Writing": [390, 430], "Math": [420, 460]},
    27: {"Reading and Writing": [400, 440], "Math": [430, 470]},
    28: {"Reading and Writing": [410, 450], "Math": [440, 480]},
    29: {"Reading and Writing": [420, 460], "Math": [450, 510]},
    30: {"Reading and Writing": [430, 470], "Math": [460, 520]},
    31: {"Reading and Writing": [440, 480], "Math": [470, 530]},
    32: {"Reading and Writing": [450, 490], "Math": [480, 540]},
    33: {"Reading and Writing": [450, 490], "Math": [490, 550]},
    34: {"Reading and Writing": [460, 500], "Math": [510, 570]},
    35: {"Reading and Writing": [470, 510], "Math": [520, 580]},
    36: {"Reading and Writing": [480, 520], "Math": [530, 590]},
    37: {"Reading and Writing": [490, 530], "Math": [540, 600]},
    38: {"Reading and Writing": [500, 540], "Math": [550, 610]},
    39: {"Reading and Writing": [500, 540], "Math": [560, 620]},
    40: {"Reading and Writing": [510, 550], "Math": [570, 630]},
    41: {"Reading and Writing": [520, 560], "Math": [580, 640]},
    42: {"Reading and Writing": [530, 570], "Math": [600, 660]},
    43: {"Reading and Writing": [530, 590], "Math": [610, 670]},
    44: {"Reading and Writing": [540, 600], "Math": [630, 690]},
    45: {"Reading and Writing": [550, 610], "Math": [640, 700]},
    46: {"Reading and Writing": [560, 620], "Math": [660, 720]},
    47: {"Reading and Writing": [570, 630], "Math": [680, 740]},
    48: {"Reading and Writing": [580, 640], "Math": [700, 760]},
    49: {"Reading and Writing": [590, 650], "Math": [720, 780]},
    50: {"Reading and Writing": [600, 660], "Math": [750, 790]},
    51: {"Reading and Writing": [620, 660], "Math": [760, 800]},
    52: {"Reading and Writing": [630, 670], "Math": [780, 800]},
    53: {"Reading and Writing": [640, 680], "Math": [790, 800]},
    54: {"Reading and Writing": [650, 690], "Math": [790, 800]},
    55: {"Reading and Writing": [660, 700]},
    56: {"Reading and Writing": [680, 720]},
    57: {"Reading and Writing": [690, 730]},
    58: {"Reading and Writing": [700, 740]},
    59: {"Reading and Writing": [710, 750]},
    60: {"Reading and Writing": [720, 760]},
    61: {"Reading and Writing": [730, 770]},
    62: {"Reading and Writing": [750, 770]},
    63: {"Reading and Writing": [760, 780]},
    64: {"Reading and Writing": [770, 790]},
    65: {"Reading and Writing": [780, 800]},
    66: {"Reading and Writing": [790, 800]},
}


def with_test_5_config():
    importer.EXTRACTED_PATH = EXTRACTED_PATH
    importer.EXPLANATIONS_PDF = EXPLANATIONS_PDF
    importer.ANSWER_KEYS = ANSWER_KEYS
    importer.SECTION_PAGES = SECTION_PAGES


def build_bank():
    with_test_5_config()
    items = importer.build_bank()
    for item in items:
        module_number = item["metadata"]["moduleNumber"]
        question_number = item["metadata"]["questionNumber"]
        item["id"] = item["id"].replace("pt4-", "pt5-")
        item["module"] = item["module"].replace("Practice Test 4", "Practice Test 5")
        item["source"] = "College Board SAT Practice Test 5 Digital PDF"
        item["logic"] = item["logic"].replace("Practice Test 4", "Practice Test 5")
        item["metadata"]["practiceTest"] = 5

        if item["section"] == "Math":
            override = MATH_OVERRIDES.get((module_number, question_number), {})
        else:
            override = RW_OVERRIDES.get((module_number, question_number), {})
        if "prompt" in override:
            item["prompt"] = override["prompt"]
        if "choices" in override:
            item["choices"] = override["choices"]
            item["type"] = "multiple-choice" if item["choices"] else "student-produced-response"
        if override.get("image"):
            item["metadata"]["image"] = override["image"]
        if override.get("visualRequired"):
            item["metadata"]["visualRequired"] = True
    return items


def main():
    existing = json.loads(OUTPUT_PATH.read_text(encoding="utf-8")) if OUTPUT_PATH.exists() else []
    existing = [item for item in existing if (item.get("metadata") or {}).get("practiceTest") != 5]
    bank = existing + build_bank()
    OUTPUT_PATH.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    scoring_path = ROOT / "data" / "seed" / "scoringTables.json"
    scoring_payload = json.loads(scoring_path.read_text(encoding="utf-8")) if scoring_path.exists() else {"tests": {}}
    scoring_payload.setdefault("tests", {})["5"] = {
        "title": "SAT Practice Test 5",
        "scoreType": "range",
        "table": SCORING_TABLE,
    }
    scoring_path.write_text(json.dumps(scoring_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(bank)} total questions to {OUTPUT_PATH}")
    print(f"Added {len(bank) - len(existing)} Practice Test 5 questions")
    print(f"Wrote scoring table to {scoring_path}")


if __name__ == "__main__":
    main()
