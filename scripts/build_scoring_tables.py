import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_practice_test_5_bank import SCORING_TABLE as TEST_5_SCORING_TABLE


OUTPUT_PATH = ROOT / "data" / "seed" / "scoringTables.json"

TEST_4_SCORING_TABLE = {
    0: {"Reading and Writing": [200, 200], "Math": [200, 200]},
    1: {"Reading and Writing": [200, 200], "Math": [200, 200]},
    2: {"Reading and Writing": [200, 200], "Math": [200, 200]},
    3: {"Reading and Writing": [200, 200], "Math": [200, 200]},
    4: {"Reading and Writing": [200, 200], "Math": [200, 200]},
    5: {"Reading and Writing": [200, 200], "Math": [200, 200]},
    6: {"Reading and Writing": [200, 200], "Math": [200, 200]},
    7: {"Reading and Writing": [200, 210], "Math": [200, 220]},
    8: {"Reading and Writing": [200, 220], "Math": [200, 230]},
    9: {"Reading and Writing": [210, 230], "Math": [220, 250]},
    10: {"Reading and Writing": [230, 250], "Math": [250, 280]},
    11: {"Reading and Writing": [240, 260], "Math": [280, 310]},
    12: {"Reading and Writing": [250, 270], "Math": [290, 320]},
    13: {"Reading and Writing": [260, 280], "Math": [300, 330]},
    14: {"Reading and Writing": [280, 300], "Math": [310, 340]},
    15: {"Reading and Writing": [290, 310], "Math": [320, 350]},
    16: {"Reading and Writing": [320, 340], "Math": [330, 360]},
    17: {"Reading and Writing": [340, 360], "Math": [330, 360]},
    18: {"Reading and Writing": [350, 370], "Math": [340, 370]},
    19: {"Reading and Writing": [360, 380], "Math": [350, 380]},
    20: {"Reading and Writing": [370, 390], "Math": [360, 390]},
    21: {"Reading and Writing": [370, 390], "Math": [370, 400]},
    22: {"Reading and Writing": [380, 400], "Math": [370, 400]},
    23: {"Reading and Writing": [390, 410], "Math": [380, 410]},
    24: {"Reading and Writing": [400, 420], "Math": [390, 420]},
    25: {"Reading and Writing": [410, 430], "Math": [400, 430]},
    26: {"Reading and Writing": [420, 440], "Math": [420, 450]},
    27: {"Reading and Writing": [420, 440], "Math": [430, 460]},
    28: {"Reading and Writing": [430, 450], "Math": [440, 470]},
    29: {"Reading and Writing": [440, 460], "Math": [460, 490]},
    30: {"Reading and Writing": [450, 470], "Math": [470, 500]},
    31: {"Reading and Writing": [460, 480], "Math": [480, 510]},
    32: {"Reading and Writing": [460, 480], "Math": [500, 530]},
    33: {"Reading and Writing": [470, 490], "Math": [510, 540]},
    34: {"Reading and Writing": [480, 500], "Math": [520, 550]},
    35: {"Reading and Writing": [490, 510], "Math": [530, 560]},
    36: {"Reading and Writing": [490, 510], "Math": [550, 580]},
    37: {"Reading and Writing": [500, 520], "Math": [560, 590]},
    38: {"Reading and Writing": [510, 530], "Math": [570, 600]},
    39: {"Reading and Writing": [520, 540], "Math": [580, 610]},
    40: {"Reading and Writing": [530, 550], "Math": [590, 620]},
    41: {"Reading and Writing": [540, 560], "Math": [600, 630]},
    42: {"Reading and Writing": [540, 560], "Math": [620, 650]},
    43: {"Reading and Writing": [550, 570], "Math": [630, 660]},
    44: {"Reading and Writing": [560, 580], "Math": [650, 680]},
    45: {"Reading and Writing": [570, 590], "Math": [670, 700]},
    46: {"Reading and Writing": [580, 600], "Math": [690, 720]},
    47: {"Reading and Writing": [590, 610], "Math": [710, 740]},
    48: {"Reading and Writing": [590, 610], "Math": [730, 760]},
    49: {"Reading and Writing": [600, 620], "Math": [740, 770]},
    50: {"Reading and Writing": [610, 630], "Math": [750, 780]},
    51: {"Reading and Writing": [620, 640], "Math": [760, 790]},
    52: {"Reading and Writing": [630, 650], "Math": [770, 800]},
    53: {"Reading and Writing": [630, 650], "Math": [780, 800]},
    54: {"Reading and Writing": [640, 660], "Math": [790, 800]},
    55: {"Reading and Writing": [650, 670]},
    56: {"Reading and Writing": [660, 680]},
    57: {"Reading and Writing": [670, 690]},
    58: {"Reading and Writing": [680, 700]},
    59: {"Reading and Writing": [690, 710]},
    60: {"Reading and Writing": [700, 720]},
    61: {"Reading and Writing": [710, 730]},
    62: {"Reading and Writing": [720, 740]},
    63: {"Reading and Writing": [730, 750]},
    64: {"Reading and Writing": [750, 770]},
    65: {"Reading and Writing": [770, 790]},
    66: {"Reading and Writing": [790, 800]},
}


def main():
    payload = {
        "tests": {
            "4": {
                "title": "SAT Practice Test 4",
                "scoreType": "range",
                "table": TEST_4_SCORING_TABLE,
            },
            "5": {
                "title": "SAT Practice Test 5",
                "scoreType": "range",
                "table": TEST_5_SCORING_TABLE,
            },
        }
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote scoring tables for tests 4 and 5 to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
