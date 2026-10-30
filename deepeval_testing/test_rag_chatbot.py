import json
import sys
import time
from pathlib import Path
import pytest
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric, ContextualRecallMetric
from groq_judge import GroqJudge
from custom_metrics import make_groundedness

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.append(str(ROOT / "chatbot"))

from ragchatbot import ask_rag_bot

with open(ROOT /"chatbot_testing" / "Data" / "goldentestdata.json") as file:
    DATASET = json.load(file)

WITH_EXPECTED = [case for case in DATASET if "expected_output" in case]

judge = GroqJudge("openai/gpt-oss-120b")

RESULTS_FILE = HERE / "results" / "rag_results.jsonl"
RESULTS_FILE.parent.mkdir(exist_ok=True)

@pytest.mark.parametrize("case", WITH_EXPECTED, ids=[c["id"] for c in WITH_EXPECTED])
def test_rag(case):
    time.sleep(3)
  
    history = []
    for earlier_question in case.get("history",[]):
        ask_rag_bot(earlier_question, history)
    answer, retrieved = ask_rag_bot(case["question"],history)

    test_case = LLMTestCase(
        input = case["question"],
        actual_output=answer,
        expected_output=case["expected_output"],
        retrieval_context=retrieved
    )

    faithfulness = FaithfulnessMetric(threshold=0.7, model=judge)
    recall = ContextualRecallMetric(threshold=0.7, model=judge)
    groundedness = make_groundedness(judge)

    faithfulness.measure(test_case)
    recall.measure(test_case)
    groundedness.measure(test_case)

    headings = [chunk.split("\n")[1] for chunk in retrieved]

    with open(RESULTS_FILE, "a") as file:
        record = {
            "id": case["id"],
            "question": case["question"],
            "retrieved": headings,
            "answer": answer,
            "faithfulness": faithfulness.score,
            "faithfulness_reason":faithfulness.reason,
            "recall": recall.score,
            "recall_reason": recall.reason,
            "groundedness": groundedness.score,
            "groundedness_reason": groundedness.reason
        }
        file.write(json.dumps(record)+ "\n")

    print("\nQuestion:", case["question"])
    print("Retrieved:", headings)
    print("Answer:",answer)
    print("Faithfulness:", faithfulness.score, "| Recall:",recall.score, "| Groundedness:", groundedness.score)
    assert recall.score >= 0.7, f"Retrieval problem ({recall.score}): {recall.reason}"
    assert groundedness.score >= 0.7, f"Not grounded ({groundedness.score}): {groundedness.reason}"
    assert faithfulness.score >= 0.7, f"Not faithful ({faithfulness.score}):{faithfulness.reason}"
