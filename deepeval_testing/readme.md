# DeepEval Testing

First steps with [DeepEval](https://deepeval.com): using an LLM as a judge to score chatbot answers by meaning, not by exact keywords.

## Files

| File | What it does |
|------|--------------|
| [groq_judge.py](groq_judge.py) | `GroqJudge`: a custom DeepEval judge model that sends DeepEval's scoring prompts to Groq (`openai/gpt-oss-120b`, `temperature=0`). Loads the API key from `chatbot/.env` |
| [test_deepeval_first.py](test_deepeval_first.py) | Two `AnswerRelevancyMetric` tests: a relevant answer must score at least 0.7, and an irrelevant answer must score below 0.7 |
| [test_relevancy_chatbot.py](test_relevancy_chatbot.py) | Runs the first 10 answerable golden dataset questions against the real chatbot (replaying `history` for multi-turn cases) and checks each answer with `AnswerRelevancyMetric` (threshold 0.7) |
| [test_correctness_chatbot.py](test_correctness_chatbot.py) | GEval "Correctness" test: asks the real chatbot every golden dataset case that has an `expected_output` and checks that the facts match. Saves each result to `results/correctness_results.jsonl` |
| [results/correctness_results.jsonl](results/correctness_results.jsonl) | Saved results of the correctness run: one JSON record per line with the question, answer, expected output, score and the judge's reason |
| [pytest.ini](pytest.ini) | Sets `asyncio_default_fixture_loop_scope` to silence a `pytest-asyncio` deprecation warning |

## How to run

DeepEval needs Python 3.9 or newer (this project uses 3.11). From inside this folder, with the venv active:

```bash
cd deepeval_testing
pytest test_deepeval_first.py -v -s
```

Test the real chatbot (calls both the chatbot and the judge, about 1.5 minutes):

```bash
pytest test_relevancy_chatbot.py -v -s --reruns 1
```

Check the facts in real chatbot answers with GEval:

```bash
pytest test_correctness_chatbot.py -v -s
```

`-s` prints the judge's score and reason. `--reruns 1` retries a failed case once (from `pytest-rerunfailures`), because LLM results can be flaky.

## How the judge works

DeepEval does not score answers itself. It asks an LLM (the judge) to do it. `GroqJudge` subclasses `DeepEvalBaseLLM` and implements four methods:

- `load_model`: returns the Groq client
- `generate`: sends the prompt to Groq and returns the text reply
- `a_generate`: the async version (here it calls `generate`)
- `get_model_name`: the model name shown in reports

## Experiment: what does Answer Relevancy really measure?

Question: "What is the home loan interest rate?" (the correct answer from the bank policies is 8.5% per year)

| Answer | Score | Passes 0.7? |
|--------|-------|-------------|
| "The home loan interest rate is 8.5% per year" (correct and short) | 1.00 | Yes |
| "Our bank has branches in Pune and Mumbai, open 10 am to 5 pm." (off topic) | 0.00 | No |
| The correct 8.5% answer wrapped in greetings, branch hours, other products and a goodbye | 0.17 | No |
| "The home loan interest rate is 15% per year." (wrong but on topic) | 1.00 | Yes |

The judge's reason for the long answer: "the response was filled with unrelated greetings, appreciation, branch hours, mentions of other products, and a closing remark, none of which answered the home loan interest rate question."

The judge's reason for the wrong answer: "the response directly answered the question about the home loan interest rate with no irrelevant statements, achieving perfect relevance."

## Real chatbot run: relevancy of 10 golden dataset answers

The first 10 answerable cases from [goldentestdata.json](../chatbot_testing/Data/goldentestdata.json), asked to the real chatbot and scored by `GroqJudge`.

**Result: 9 passed, 1 failed** (TS03).

| Run | TS03 score | Judge's reason |
|-----|------------|----------------|
| 1 | 0.67 (failed) | "the response merely restated that the product is a fixed deposit without providing the senior citizen rate for a 4-year term" |
| 2 (rerun) | 1.00 (passed) | Bot answered "A senior citizen receives **7.75% per year** for a 4-year fixed deposit." |

The same test failed and then passed. Both the chatbot's wording and the judge's scoring change between runs, so an LLM-judged test can be flaky. Retrying once (`--reruns 1`) separates flakiness from real problems: a real problem fails every time.

### Bugs fixed before the first run

- A wrong auto-added import (`from chatbot_testing.check_dataset import file`)
- `with open(...)` without `as file:` (a `SyntaxError`), and the old folder name `chatbot-testing`
- `time.leep` instead of `time.sleep`
- `"hostory"` instead of `"history"`: this never crashed, because `.get()` quietly returned `[]`, so multi-turn cases silently lost their earlier questions
- The `assert` was outside the test function, so it ran at import time

## Answer relevancy on real chatbot answers (10 cases)

- **Passed:** 9 / 10
- **Lowest score:** TS03, 0.67. Judge's reason: "the response merely restated that the product is a fixed deposit without providing the senior citizen rate for a 4-year term, leaving the core question unanswered."
- **Did I agree with the judge?** Not sure, and that is the lesson. The bot's answer from the failed run was not saved, so I can't check whether it really left out the rate. On the rerun, the bot gave the correct rate ("**7.75% per year** for a 4-year fixed deposit") and scored 1.00. To judge the judge, the failure message must include the bot's answer, not only the score and reason.
- **TS06 observation:** the question "What's the rate?" is unclear. The bot asked a clarifying question: "Could you please let me know which product you're interested in: personal loan, home loan, credit card, or fixed deposit?" It scored **1.00**. Asking for clarification is the right behaviour, so I agree with the score. But the judge's reason ("the response directly answered the question") is not accurate: the bot did not answer, it asked back. A correct score can come with a wrong reason, so read the reasons, not only the numbers.

## Correctness with GEval (10 cases)

Answer Relevancy gave a wrong answer a perfect score, so this test checks the facts. `GEval` is a metric where you write the grading rules (the criteria) in plain English, and the judge scores the answer against them. Each case compares the bot's answer with an `expected_output` added to [goldentestdata.json](../chatbot_testing/Data/goldentestdata.json) (TS01 to TS04, TS06, TS07, TS09 to TS12).

The criteria:

> Check whether the actual output gives the same facts as the expected output. Numbers, rates and amounts must match exactly. Different wording is fine if the meaning is the same. If the expected output describes a behaviour, check that the actual output shows that behaviour.

The last sentence is for TS06 and TS10, where the expected output describes a behaviour ("should ask which product's rate the customer means", "a polite greeting that offers to help") instead of giving an answer.

**Result: 10 / 10 passed.** Nine cases scored 1.0. TS03 scored 0.9 because the bot left out the breakdown "(7.25% plus 0.5%)".

### The wrong 15% answer: Relevancy vs GEval

The same wrong answer from the relevancy experiment, scored with this `Correctness` metric (expected output: "The home loan interest rate is 8.5% per year."):

| Answer | Answer Relevancy | GEval Correctness |
|--------|------------------|-------------------|
| "The home loan interest rate is **15%** per year." (wrong) | **1.00** (passed) | **0.0** (failed) |
| "The home loan interest rate is **8.5%** per year." (correct) | 1.00 (passed) | 1.0 (passed) |

The judge's reason for the wrong answer: "The Actual Output states a home loan interest rate of 15%, which does not match the Expected Output of 8.5%; the factual detail is incorrect, so the response fails the evaluation."

Answer Relevancy only sees the question and the answer, so it can't know 15% is wrong. GEval also sees the `expected_output`, and the criteria say numbers must match exactly. A metric can only catch wrong facts when it is given the right facts.

### Finding: the judge was too lenient on TS09

| | Wording | Meaning |
|---|---|---|
| Policy | "penalty of 1% **on the interest rate**" | the FD rate drops by 1% |
| Bot | "1 % **of the interest earned**" | you lose 1% of your interest |

These are different amounts of money, but the judge gave 1.0 ("the meaning is equivalent"). The number matched, but what it applies to did not. A stricter criteria line would be: "What the number applies to (rate, amount, interest) must also match."

### Bugs fixed before the first run

- The same wrong auto-added import as before (`from chatbot_testing import file`)
- `with open(...)` without `as file:`, and the old folder name `chatbot-testing`
- `LLMTestCaseParams.input` no longer exists in DeepEval 4.3.1: the names are upper case and the class is now `SingleTurnParams` (`SingleTurnParams.INPUT`)
- `.json1` instead of `.jsonl` (JSON Lines: one JSON record per line)
- `paraterize` instead of `parametrize`

## What I learned

- **Relevancy is not correctness.** Answer Relevancy only checks whether the answer stays on topic. A wrong answer (15% instead of 8.5%) got a perfect 1.00. For a bank chatbot, that is a dangerous gap.
- **Extra chatter is punished.** The metric splits the answer into statements and counts how many address the question. A correct answer buried in small talk scored only 0.17.
- **One metric is not enough.** To catch wrong facts, use a metric that knows the truth: `FaithfulnessMetric` (checks the answer against the policy text given as `retrieval_context`) or `GEval` with an `expected_output`.
- **Every test needs an assert.** A test that only prints a score can never fail.
- **Small typos break LLM tests.** A leading space in the model name (`" openai/gpt-oss-120b"`) gave a 404 error, and `threashold` instead of `threshold` gave a `TypeError`.
- **The judge is non-deterministic too.** The same correct answer can score 0.67 on one run and 1.00 on the next. Use retries, and note which tests needed one.
- **Silent typos are the worst bugs.** A misspelt dictionary key with `.get()` gives no error, it just tests the wrong thing.
- **Relevancy and correctness answer different questions.** Relevancy asks "is it on topic?", correctness asks "are the facts right?". A real suite needs both.
- **A passing score is only as strict as the criteria.** TS09 passed with a misleading answer because the criteria only checked that numbers match, not what they apply to.
- **Save every result.** Writing each answer, score and reason to a JSON Lines file means every judgement can be checked later.
