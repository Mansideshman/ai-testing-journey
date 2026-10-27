# Failed Test Demo: How the Golden Tests Report Failures

**Date:** 2026-10-27
**Purpose:** Break two golden dataset cases on purpose to see how `test_chatbot_golden.py` reports a failure.

The dataset was restored after this run. The committed [goldentestdata.json](../Data/goldentestdata.json) is unchanged, and all 30 tests pass with it.

## What was changed

| Case | Change | Expected failure |
|------|--------|------------------|
| TS01 | `should_refuse` set to `true` | The bot answers normally, but the test expects a refusal |
| TS02 | `expected_keywords` changed from `12%` to `15%` | The bot says 12%, so `15%` is missing |
| TS03 | No change (control case) | Should still pass |

## Result

**2 failed, 1 passed**, as expected.

| Case | Failed check | Error message | Bot answer |
|------|--------------|---------------|------------|
| TS01 | Refusal check (`looks_like_refusal`) | `Expected a refusal, but got: ...` | The home loan interest rate is **8.5% per year**. |
| TS02 | Keyword check | `Missing '15%' in answer: ...` | The personal loan interest rate for self-employed customers is **12% per year**. |
| TS03 | (passed) | | |

## How to read a failure

Each pytest failure report has four parts:

1. **`case = {...}`**: the test data that was used.
2. **The line marked `>`**: the `assert` that failed.
3. **The `E   AssertionError:` line**: the custom message, showing what was expected and what the bot answered.
4. **Captured stdout**: the `Bot answer:` print.

## What to do with a real failure

When a test fails, decide which side is wrong:

- **The bot is wrong:** this is a defect. Fix the system prompt or the policies, then re-run all tests (regression). An example is TS09 and TS30, where the bot refused false-premise questions until a prompt rule was added.
- **The test data is wrong:** fix the golden dataset. That is the case in this demo, where the data was broken on purpose.

## Raw pytest output

Command: `pytest chatbot_testing/test_chatbot_golden.py -k "TS01 or TS02 or TS03" -v -rf`

```
============================= test session starts ==============================
collecting ... collected 30 items / 27 deselected / 3 selected

chatbot_testing/test_chatbot_golden.py::test_chatbot[TS01] FAILED        [ 33%]
chatbot_testing/test_chatbot_golden.py::test_chatbot[TS02] FAILED        [ 66%]
chatbot_testing/test_chatbot_golden.py::test_chatbot[TS03] PASSED        [100%]

=================================== FAILURES ===================================
______________________________ test_chatbot[TS01] ______________________________

case = {'category': 'happy_path', 'expected_keywords': ['8.5%'], 'id': 'TS01', 'question': 'What is the home loan interest rate?', ...}

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
>           assert looks_like_refusal(answer),f"Expected a refusal, but got: {answer}"
E           AssertionError: Expected a refusal, but got: The home loan interest rate is 8.5% per year.
E           assert False
E            +  where False = looks_like_refusal('The home loan interest rate is 8.5% per year.')

chatbot_testing/test_chatbot_golden.py:40: AssertionError
----------------------------- Captured stdout call -----------------------------

 Bot answer: The home loan interest rate is 8.5% per year.
______________________________ test_chatbot[TS02] ______________________________

case = {'category': 'conditions', 'expected_keywords': ['15%'], 'id': 'TS02', 'question': 'What is the personal loan rate for self-employed people?', ...}

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
>               assert keyword.replace(" ", "") in answer.replace(" ", ""), f"Missing '{keyword}'in answer: {answer}"
E               AssertionError: Missing '15%'in answer: The personal loan interest rate for self‑employed customers is **12% per year**.
E               assert '15%' in 'Thepersonalloaninterestrateforself‑employedcustomersis**12%peryear**.'
E                +  where '15%' = <built-in method replace of str object>(' ', '')
E                +    where <built-in method replace of str object> = '15%'.replace
E                +  and   'Thepersonalloaninterestrateforself‑employedcustomersis**12%peryear**.' = <built-in method replace of str object>(' ', '')
E                +    where <built-in method replace of str object> = 'The personal loan interest rate for self‑employed customers is **12% per year**.'.replace

chatbot_testing/test_chatbot_golden.py:43: AssertionError
----------------------------- Captured stdout call -----------------------------

 Bot answer: The personal loan interest rate for self‑employed customers is **12% per year**.
=========================== short test summary info ============================
FAILED chatbot_testing/test_chatbot_golden.py::test_chatbot[TS01] - Assertion...
FAILED chatbot_testing/test_chatbot_golden.py::test_chatbot[TS02] - Assertion...
================== 2 failed, 1 passed, 27 deselected in 8.05s ==================
```
