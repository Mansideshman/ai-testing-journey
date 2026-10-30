from deepeval.metrics import GEval
from deepeval.test_case import SingleTurnParams

# Faithfulness only fails claims that contradict the context.
# Groundedness also fails claims the context does not support.
GROUNDEDNESS_CRITERIA = (
    "Check whether every factual claim in the actual output is directly supported by the retrieval context. "
    "A claim that is not mentioned in the retrieval context counts as unsupported, even if it does not contradict it. "
    "If the actual output makes no factual claims (for example, it only says it does not have the information), it is grounded."
)


def make_groundedness(judge, threshold=0.7):
    return GEval(
        name="Groundedness",
        criteria=GROUNDEDNESS_CRITERIA,
        evaluation_params=[
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.RETRIEVAL_CONTEXT
        ],
        threshold=threshold,
        model=judge
    )
