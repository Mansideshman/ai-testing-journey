import json
import sys
import time
import pytest
from pathlib import Path
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric, ContextualRecallMetric
from groq_judge import GroqJudge

HERE = Path(__file__).parent
ROOT = HERE.parent
RESULTS_FILE = HERE / "results" / "rag_diagnosis.jsonl"
RESULTS_FILE.parent.mkdir(exist_ok=True)
PASS_MARK = 0.7

HOME_LOAN_PAGE = """Sahyadri Bank – Loan Policy
## Home Loan
- Interest rate: 8.5% per year
- Maximum tenure: 30 years
- Down payment: at least 20% of the property value"""

CARD_FEES_PAGE = """Sahyadri Bank – Credit Card Policy
## Fees
- Annual fee: ₹500 (waived if you spend ₹50,000 or more in a year)
- Late payment fee: ₹750
- Cash withdrawal fee: 2.5% of the amount"""

judge = GroqJudge("openai/gpt-oss-120b")

# One case for each corner of the diagnosis table.
# The sections come from the real retrieve(); some answers are written by hand
# to force a hallucination, because the real bot never made one.
CASES = [
    {
        "expect": "Working well",
        "question": "What is the home loan interest rate?",
        "retrieved": [HOME_LOAN_PAGE],
        "answer": "The home loan interest rate is 8.5% per year.",
        "expected_output": "The home loan interest rate is 8.5% per year.",
    },
    {
        "expect": "Retrieval problem",
        "question": "What FD rate does a senior citizen get for 4 years?",
        "retrieved": [CARD_FEES_PAGE],
        "answer": "I'm sorry, I don't have that information.",
        "expected_output": "A senior citizen gets 7.75% per year for a 4-year FD (7.25% plus 0.5%).",
    },
    {
        "expect": "Hallucination",
        "question": "What is the home loan interest rate?",
        "retrieved": [HOME_LOAN_PAGE],
        "answer": "The home loan interest rate is 8.5% per year, there is no processing fee, and every home loan comes with a free credit card.",
        "expected_output": "The home loan interest rate is 8.5% per year.",
    },
    {
        "expect": "Both broken",
        "question": "Can I withdraw my FD on the 3rd day?",
        "retrieved": [CARD_FEES_PAGE],
        "answer": "Yes, you can withdraw your FD at any time with a 2% penalty on the amount.",
        "expected_output": "No. Withdrawal is not allowed in the first 7 days of a fixed deposit.",
    },
]


def diagnose(recall, faithfulness):
    if recall >= PASS_MARK and faithfulness >= PASS_MARK:
        return "Working well"
    if recall < PASS_MARK and faithfulness >= PASS_MARK:
        return "Retrieval problem"
    if recall >= PASS_MARK and faithfulness < PASS_MARK:
        return "Hallucination"
    return "Both broken"


@pytest.mark.parametrize("case", CASES, ids=[c["expect"] for c in CASES])
def test_diagnosis(case):
    time.sleep(3)
    retrieved = case["retrieved"]
    test_case = LLMTestCase(
        input=case["question"],
        actual_output=case["answer"],
        expected_output=case["expected_output"],
        retrieval_context=retrieved
    )
    recall = ContextualRecallMetric(threshold=PASS_MARK, model=judge)
    faithfulness = FaithfulnessMetric(threshold=PASS_MARK, model=judge)
    recall.measure(test_case)
    faithfulness.measure(test_case)

    result = diagnose(recall.score, faithfulness.score)
    headings = [chunk.split("\n")[1] for chunk in retrieved]

    with open(RESULTS_FILE, "a") as file:
        record = {
            "expect": case["expect"],
            "diagnosis": result,
            "question": case["question"],
            "retrieved": headings,
            "answer": case["answer"],
            "recall": recall.score,
            "recall_reason": recall.reason,
            "faithfulness": faithfulness.score,
            "faithfulness_reason": faithfulness.reason
        }
        file.write(json.dumps(record) + "\n")

    assert result == case["expect"], (
        f"Expected {case['expect']}, got {result}"
        f"\nRecall: {recall.score} | {recall.reason}"
        f"\nFaithfulness: {faithfulness.score} | {faithfulness.reason}"
    )
