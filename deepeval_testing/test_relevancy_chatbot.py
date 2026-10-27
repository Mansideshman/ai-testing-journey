import json
import sys
import time
from pathlib import Path
import pytest
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from groq_judge import GroqJudge

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.append(str(ROOT / "chatbot"))
from chatbot import ask_bot

with open(ROOT / "chatbot_testing" / "Data" / "goldentestdata.json") as file:
    DATASET = json.load(file)

ANSWERABLE = [case for case in DATASET if not case["should_refuse"]]
FIRST_TEN = ANSWERABLE[:10]

judge = GroqJudge("openai/gpt-oss-120b")

@pytest.mark.parametrize("case",FIRST_TEN,ids=[c["id"] for c in FIRST_TEN])
def test_answer_relevancy(case):
    time.sleep(3)

    history = []
    for earlier_question in case.get("history",[]):
        ask_bot(earlier_question, history)
    answer = ask_bot(case["question"],history)

    test_case = LLMTestCase(input=case["question"],actual_output=answer)
    metric = AnswerRelevancyMetric(threshold=0.7, model=judge)
    metric.measure(test_case)

    print("\nQuestion:",case["question"])
    print("Answer:",answer)
    print("score:",metric.score)
    print("Reason:",metric.reason)

    assert metric.score >=0.7, f"Low relevancy ({metric.score}):{metric.reason}"