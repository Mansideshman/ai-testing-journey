import json
import sys
import time
from pathlib import Path
import pytest

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.append(str(ROOT / "chatbot"))
# pyrefly: ignore[missing-import]
from ragchatbot import ask_rag_bot

with open(ROOT / "chatbot_testing" / "Data" / "metamorphic_cases.json") as file:
    GROUPS = json.load(file)

CASES = []
for group in GROUPS:
    for number, question in enumerate(group["paraphrases"], start=1):
        CASES.append((group["id"] + "-" + str(number), question, group["keyword"]))

RESULTS_FILE = HERE / "results" / "metamorphic_results.jsonl"
RESULTS_FILE.parent.mkdir(exist_ok=True)


@pytest.mark.parametrize("case_id, question, keyword", CASES, ids=[c[0] for c in CASES])
def test_paraphrase_gives_same_fact(case_id, question, keyword):
    time.sleep(2)
    answer, retrieved = ask_rag_bot(question, [])
    headings = [chunk.split("\n")[1] for chunk in retrieved]
    clean_answer = " ".join(answer.split())

    with open(RESULTS_FILE,"a") as file:
        record = {
            "case_id": case_id,
            "question": question,
            "retrieved": headings,
            "answer": clean_answer,
            "has_keyword": keyword in clean_answer
        }
        file.write(json.dumps(record) + "\n")

    print("\n", case_id, "|", question)
    print("Retrieved:", headings)
    print("Answer:", clean_answer)

    assert keyword in clean_answer, f"Expected '{keyword}' but got:{clean_answer}"

