# simple chatbot

- Same question gave different wording each time. At temperature 0, answers were almost identical.
- At temperature 1, wording and order changed, and the meaning shifted slightly: “can’t withdraw without a penalty” became “may incur penalties”. - - This shows why exact-match tests don’t work for AI, and why testers must check meaning, not just keywords.

## Multi-turn conversation (memory)
- Before: each question was sent alone, so follow-ups failed.
- Fix: stored every message in a history list and sent the full conversation each time.
- After: [write whether "And for self-employed?" and "What if I am a senior citizen?" worked]

### Memory trap test
- Input sequence: "My name is Mansi" → "What is the credit card late fee?" → "What is my name?"
- Result: bot greeted me by name, answered the fee correctly, but then said "I don't have that information" when asked my name.
- Observation: memory works, but the "answer only from policies" rule overrides it.
- Risk: inconsistent behaviour – the bot used my name, then claimed not to know it.
- Discussion: refusing to repeat personal details may be safer for a bank, but the behaviour should be consistent and intentional. This needs a product decision.



## Testing the tests
- Deliberately changed TS01 to expect a refusal and TS02 to expect "15%".
- Both tests failed with clear messages showing the bot's actual answer.
- This confirmed the test suite can catch wrong answers and refusal failures.

## Automated test run (golden dataset)
- 30/30 passed on the first full run.
- Eye check of tests without keywords (TS06, TS10, TS23, TS24): passed
- Stability: ran the suite 3 times. Results:  30/30 each time passed
- Lesson: "all passed" doesn't mean "no problems". Tests without strong checks can hide defects.