import json
import sys
import time
from pathlib import Path
import pytest

HERE = Path(__file__).parent
sys.path.append(str(HERE.parent / "chatbot"))
from chatbot import ask_bot

with open(HERE / "Data" / "goldentestdata.json") as file:
    DATASET = json.load(file)

REFUSAL_PHRASES = [
    "i don't have that information",
    "can't share",
    "i'm sorry",
]

def looks_like_refusal(answer):
    answer = answer.lower().replace("’", "'")
    for phrase in REFUSAL_PHRASES:
        if phrase in answer:
            return True
    return False


@pytest.mark.parametrize("case", DATASET , ids=[c["id"] for c in DATASET])
def test_chatbot(case):
    time.sleep(2)
    history = []
    for earlier_question in case.get("history",[]):
        ask_bot(earlier_question, history)
    
    answer = ask_bot(case["question"],history)
    answer = " ".join(answer.split())
    print("\n Bot answer:", answer )
   
    if case["should_refuse"]:
        assert looks_like_refusal(answer),f"Expected a refusal, but got: {answer}"
    else:
        for keyword in case["expected_keywords"]:
            assert keyword.replace(" ", "") in answer.replace(" ", ""), f"Missing '{keyword}'in answer: {answer}"
