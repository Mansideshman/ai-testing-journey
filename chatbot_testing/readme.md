# Week 3: Chatbot Testing

## What I built
- 30 test scenarios across 11 categories (happy path, conditions, calculations, exceptions, out of scope, unclear, multi-turn, spelling, safety, tricky, greetings)
- A golden dataset (JSON) with expected keywords and refusal flags
- A dataset check script that counts categories and finds missing fields
- A pytest suite that sends every question to the real chatbot and checks the answers

## Results
- First full run: 26/30 passed. The 4 failures were:
  - TS09 and TS30: real defects. The bot refused false-premise questions (for example, "Since the FD penalty is 5%...") instead of correcting them. Fixed by adding a prompt rule to correct wrong information.
  - TS19: test issue. The bot's answer was correct, but it used an unusual space character ("7\u202fdays"). Fixed by normalizing whitespace before checking keywords.
  - TS25: API rate limit. Fixed by adding a 2-second pause between tests.
- After the fixes: 30/30 passed on the full run
- Stability across 3 runs: 30/30 passed each time
- Eye check findings: the 4 cases with no expected keywords (TS06, TS10, TS23, TS24) always pass automatically, so I read the bot's answers myself. All 4 were correct.
- Testing the tests: I broke TS01 and TS02 on purpose, and both failed with clear messages ([failure record](reports/failed_tests_demo.md))

## How to run
```bash
source .venv/bin/activate
pytest chatbot_testing/test_chatbot_golden.py -v -s
