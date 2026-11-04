import json
import sys
import time
from pathlib import Path
import pytest

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.append(str(ROOT / "chatbot"))
from ragchatbot import ask_rag_bot

with open(ROOT / "chatbot_testing" / "Data" / "bias_cases.json") as file:
    GROUPS = json.load(file)

RESULTS_FILE = HERE / "results" / "bias_results.jsonl"
RESULTS_FILE.parent.mkdir(exist_ok=True)


@pytest.mark.parametrize("group", GROUPS, ids=[g["id"] for g in GROUPS])
def test_equal_treatment(group):
    problems = []

    for value in group["variants"]:
        time.sleep(2)
        question = group["template"].replace("{value}",value).strip()
        answer, retrieved = ask_rag_bot(question, [])
        answer = " ".join(answer.split())

        if "expected_by_variant" in group:
            expected = group["expected_by_variant"][value]
        else:
            expected = group["expected_keyword"]

        correct = expected in answer

        with open(RESULTS_FILE, "a") as file:
            record = {
                "group": group["id"],
                "attribute": group["attribute"],
                "variant": value,
                "question": question,
                "answer": answer,
                "expected": expected,
                "correct": correct,
                "answer_length": len(answer)
            }
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

        print(f"\n[{group['attribute']}: {value or '(none)'}] {answer}")

        if not correct:
            problems.append(f"'{value}' -> expected '{expected}', got: {answer}")

    assert not problems, "unequal treatment found:\n" + "\n".join(problems)
