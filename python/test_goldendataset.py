from checks import check_answer
import json
import pytest

with open("/home/mansideshman/Documents/MansiData/GitRepo/AITester/ai-testing-journey/JSON/testcases.json") as f:
     TEST_CASES = json.load(f)

with open("/home/mansideshman/Documents/MansiData/GitRepo/AITester/ai-testing-journey/JSON/fake_answers.json") as f:
    ANSWERS = json.load(f)

@pytest.mark.parametrize("case", TEST_CASES, ids=[c["id"] for c in TEST_CASES])
def test_golden_dataset(case):
    answer = ANSWERS[case["id"]]
    assert check_answer(answer, case["expected_keyword"]) == "PASS"