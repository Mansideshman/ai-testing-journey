import json
import sys
import time
from pathlib import Path
# pyrefly: ignore[missing-import]
import pytest
# pyrefly: ignore[missing-import]
from deepeval.test_case import LLMTestCase, SingleTurnParams
# pyrefly: ignore[missing-import]
from deepeval.metrics import GEval
from groq_judge import GroqJudge

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.append(str(ROOT/"chatbot"))
from chatbot import ask_bot

with open(ROOT / "chatbot_testing" / "Data" / "goldentestdata.json") as file:
    DATASET = json.load(file)

WITH_EXPECTED = [case for case in DATASET if "expected_output" in case]

judge = GroqJudge("openai/gpt-oss-120b")

correctness = GEval(
    name="Correctness",
    criteria=(
        "Check whether the actual output gives the same facts as the expected output. "
        "Numbers, rates and amounts must match exactly. "
        "Different wording is fine if the meaning is the same. "
        "If the expected output describes a behaviour, check that the actual output shows that behaviour."
    ),
    evaluation_params=[
        SingleTurnParams.INPUT,
        SingleTurnParams.ACTUAL_OUTPUT,
        SingleTurnParams.EXPECTED_OUTPUT
    ],
    threshold=0.7,
    model=judge
    )
RESULTS_FILE = HERE / "results" / "correctness_results.jsonl"
RESULTS_FILE.parent.mkdir(exist_ok=True)

@pytest.mark.parametrize("case",WITH_EXPECTED,ids=[c["id"] for c in WITH_EXPECTED])
def test_correctness(case):
    time.sleep(3)

    history = []
    for earlier_question in case.get("history",[]):
        ask_bot(earlier_question,history)
    answer = ask_bot(case["question"],history)

    test_case = LLMTestCase(
        input=case["question"],
        actual_output=answer,
        expected_output=case["expected_output"]
    )
    correctness.measure(test_case)

    with open(RESULTS_FILE,"a")as file:
        record = {
            "id":case["id"],
            "question":case["question"],
            "answer":answer,
            "expected":case["expected_output"],
            "score":correctness.score,
            "reason":correctness.reason
        }
        file.write(json.dumps(record)+"\n")

    print("\nAnswer:",answer)
    print("Score:",correctness.score)
    print("Reason:",correctness.reason)

    assert correctness.score >= 0.7, f"Incorrect ({correctness.score}):{correctness.reason}\nAnswer: {answer}"

        