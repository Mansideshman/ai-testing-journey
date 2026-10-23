# simple chatbot

- Same question gave different wording each time. At temperature 0, answers were almost identical.
- At temperature 1, wording and order changed, and the meaning shifted slightly: “can’t withdraw without a penalty” became “may incur penalties”. - - This shows why exact-match tests don’t work for AI, and why testers must check meaning, not just keywords.


## Multi-turn conversation (memory)
- Before: the bot answered each question alone, so follow-ups like "And for self-employed?" failed.
- Fix: stored every message in a history list and sent the full conversation each time.
- After: follow-up questions worked. [write your results]
- Memory trap: [what happened when you asked "What is my name?"]