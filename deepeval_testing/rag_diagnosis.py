import json
import sys
import time
from pathlib import Path
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric, ContextualRecallMetric
from groq_judge import GroqJudge

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.append(str(ROOT / "chatbot"))
from ragchatbot import retrieve

RESULTS_FILE = HERE / "results" / "rag_diagnosis.jsonl"
RESULTS_FILE.parent.mkdir(exist_ok=True)
PASS_MARK = 0.7

judge = GroqJudge("openai/gpt-oss-120b")

# One case for each corner of the diagnosis table.
# The sections come from the real retrieve(); some answers are written by hand
# to force a hallucination, because the real bot never made one.
CASES = [
    {
        "expect": "Working well",
        "question": "What is the home loan interest rate?",
        "answer": "The home loan interest rate is 8.5% per year.",
        "expected_output": "The home loan interest rate is 8.5% per year.",
    },
    {
        "expect": "Retrieval problem",
        "question": "What FD rate does a senior citizen get for 4 years?",
        "answer": "I'm sorry, I don't have that information.",
        "expected_output": "A senior citizen gets 7.75% per year for a 4-year FD (7.25% plus 0.5%).",
    },
    {
        "expect": "Hallucination",
        "question": "What is the home loan interest rate?",
        "answer": "The home loan interest rate is 8.5% per year, there is no processing fee, and every home loan comes with a free credit card.",
        "expected_output": "The home loan interest rate is 8.5% per year.",
    },
    {
        "expect": "Both broken",
        "question": "Can I withdraw my FD on the 3rd day?",
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


for case in CASES:
    time.sleep(3)
    retrieved = retrieve(case["question"])
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

    print("=" * 60)
    print("Expected diagnosis:", case["expect"], "| Got:", result)
    print("Retrieved:", headings)
    print("Recall:", recall.score, "| Faithfulness:", faithfulness.score)
    print("Recall reason:", recall.reason)
    print("Faithfulness reason:", faithfulness.reason)
