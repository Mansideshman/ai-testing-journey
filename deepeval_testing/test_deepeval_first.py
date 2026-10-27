# pyrefly: ignore[missing-import]
from deepeval import assert_test
# pyrefly: ignore[missing-import]
from deepeval.test_case import LLMTestCase
# pyrefly: ignore[missing-import]
from deepeval.metrics import AnswerRelevancyMetric
from groq_judge import GroqJudge

judge = GroqJudge("openai/gpt-oss-120b")

def test_relevant_answer():
    test_case = LLMTestCase(
        input="What is the home loan interest rate?",
        actual_output="The home loan interest rate is 8.5% per year"

    )
    metric = AnswerRelevancyMetric(threshold=0.7, model=judge)
    assert_test(test_case, [metric])

def test_irrelevant_answer_score():
    test_case = LLMTestCase(
        input="What is the home loan interest rate?",
        actual_output="Our bank has branches in Pune and Mumbai, open 10 am to 5 pm."
    )
    metric = AnswerRelevancyMetric(threshold=0.7, model=judge)
    metric.measure(test_case)
    print("\nScore:",metric.score)
    print("Reason:",metric.reason)
    assert metric.score < 0.7, f"Irrelevant answer scored {metric.score}:{metric.reason}"

