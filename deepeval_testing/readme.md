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
| [calibrate_judge.py](calibrate_judge.py) | Compares the judge's pass/fail verdicts (latest score per case from `results/correctness_results.jsonl`, pass mark 0.7) with human labels, and prints the agreement rate and every disagreement |
| [human_labels.json](human_labels.json) | My own pass/fail label for each of the 10 correctness cases, made without looking at the judge's scores |
| [test_rag_chatbot.py](test_rag_chatbot.py) | RAG chatbot test: asks `ragchatbot.py` every case with an `expected_output` and scores each answer with `ContextualRecallMetric` (did the search find the right sections?) and `FaithfulnessMetric` (did the answer stick to them?). Saves results to `results/rag_results.jsonl` |
| [rag_diagnosis.py](rag_diagnosis.py) | Checks the 4-corner RAG diagnosis table with one case per corner (two of them with hand-written answers), and saves results to `results/rag_diagnosis.jsonl` |
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
- **Calibrate the judge before trusting it.** Agreement with a human is the judge's own test score.
- **Fix the reference before the rubric.** A vague expected output let the judge explain a wrong answer away; a precise one stopped it.
- **Fix defects at the source.** The misleading TS09 answer came from ambiguous policy wording, so the real fix was the policy, not the test.
- **When the product changes, the tests must change too.** After the policy fix, the correct answer failed the old keyword (`1%`) and the old expected output, and the human label went out of date.
- **A judge can be too strict as well as too lenient.** GEval invented a "no-extra-facts rule" and failed a correct answer for a helpful follow-up question. Test a criteria change on both a right and a wrong answer.


## Judge calibration

An AI judge's scores can't be trusted until they are checked against a human. I labelled the 10 correctness answers myself as pass or fail, without looking at the judge's scores, and compared them with [calibrate_judge.py](calibrate_judge.py).

| Step | What changed | Agreement |
|------|--------------|-----------|
| 1 | Random human labels, to test that the script catches disagreements | 80% (8 / 10) |
| 2 | Human labels checked against the policy files | 90% (9 / 10) |
| 3 | Stricter rubric line added to the GEval criteria | 90% (9 / 10) |
| 4 | Precise `expected_output` for TS09 | **100% (10 / 10)** |

- **Human-labelled 10 answers** without looking at the judge's scores ([human_labels.json](human_labels.json)).
- **Agreement rate:** 90% (9 out of 10) at first, 100% (10 out of 10) after the fix. The 80% in step 1 came from random labels, used only to prove the script works.
- **Disagreements:** TS09, and the human was right. The bot said the penalty is "1% **of the interest earned**". The policy says "1% **on the interest rate**", which means the FD rate drops by 1 percentage point (for example, 7% becomes 6%). These are different amounts of money, but the judge gave 1.0 because the number 1% matched.
- **Change made to the rubric:**
  1. Added "What the number applies to (rate, amount, interest) must also match" to the criteria. **This did not help.** TS09 still scored 1.0, and the judge explained the gap away: "1% of the interest (i.e., 1% on the interest rate)".
  2. Made TS09's `expected_output` precise: "The FD early withdrawal penalty is 1%, not 5%. It lowers the FD interest rate by 1 percentage point (for example, 7% becomes 6%). It is not 1% of the interest earned." **This worked.** TS09 now scores 0.2 and fails, with the reason "incorrectly states that the penalty is 1% of the interest earned".
- **Root cause:** the policy wording "penalty of 1% on the interest rate" in [fixed_deposits.md](../chatbot/data/policies/fixed_deposits.md) is ambiguous. Both the bot and the judge read it the way a customer might. This is a defect in the policy text, not only in the bot.
- **Lesson:** an AI judge must be checked against human judgement before its scores can be trusted. All 10 tests passed while one answer could mislead a customer, and only human review found it. A judge is only as precise as the reference it compares against: a clear expected output worked where a stricter rubric did not.

## Policy fix: TS09 before and after

Calibration showed the real root cause was the policy text, so the defect was fixed there.

**Policy change** in [fixed_deposits.md](../chatbot/data/policies/fixed_deposits.md):

```diff
- Allowed, with a penalty of 1% on the interest rate
+ Allowed, with a penalty: the interest rate is reduced by 1 percentage point (for example, 7% becomes 6%). The penalty is not 1% of the interest earned.
```

| | Before | After |
|---|---|---|
| Bot's TS09 answer | "1 % **of the interest earned**, not 5 %" (misleading) | "the interest rate is simply reduced by 1 percentage point (e.g., a 7 % rate becomes 6 %)" (correct) |
| Golden keyword test | passed with `1%` | failed with `1%`, passed after updating the keyword to `1 percentage point` |
| GEval correctness | 1.0 with the vague expected output, 0.2 with the precise one | 0.3 (failed a correct answer), then **0.8** after the criteria fix |
| Judge calibration | 90%, then 100% | 100%, with TS09 relabelled `pass` |

**Updating the tests after the fix:**

1. **Golden dataset:** TS09's keyword changed from `1%` to `1 percentage point`, and the expected output now states the meaning: "The penalty is not 5%. The FD interest rate is reduced by 1 percentage point (for example, 7% becomes 6%). It is not 1% of the interest earned."
2. **GEval was now too strict.** The correct answer scored 0.3 because it didn't repeat "not 1% of the interest earned", and because the bot asked for the deposit amount (the judge called this a "no-extra-facts rule", which the criteria never contained). Two lines were added to the criteria:
   - "If the expected output says what something is not, the actual output must not contradict it, but it does not need to repeat it."
   - "Extra helpful details or follow-up questions are fine if they do not contradict the expected facts."
3. **Checked both ways before applying:** with the new criteria, the correct answer scored 0.8 and 0.7, and the old wrong answer still scored 0.0 both times. The judge got fairer without becoming lenient again.
4. **Human label updated:** TS09 changed from `fail` to `pass`, because the answer is now correct. The old label described the old answer.

**Result:** all 10 correctness cases pass, TS09 scores 0.8, and judge calibration is 100% (10 / 10). TS09's score is close to the 0.7 pass mark, so it may fail now and then on a rerun.

## RAG chatbot test: recall and faithfulness (23 cases)

[test_rag_chatbot.py](test_rag_chatbot.py) asks the RAG bot ([ragchatbot.py](../chatbot/ragchatbot.py)) all 23 cases with an `expected_output` and scores each answer with two metrics (pass mark 0.7 for both).

**Result: 12 passed, 11 failed** (10 minutes). Not every failure is a defect:

| Group | Cases | What happened |
|---|---|---|
| Real retrieval defects | TS03, TS09, TS19 | All FD questions. The FD section was never found ("FD" never matches "Fixed Deposit"), so the bot said "I don't have that information". Recall 0.0, 0.33, 0.0 |
| Real answer defect | TS30 | Retrieval was fine (the Fees section with ₹750 was found), but the bot still said "I don't have that information" instead of correcting the ₹1,000 premise. The LLM failed, not the search |
| Real behaviour defect | TS06 | For "What's the rate?" the bot listed personal loan rates instead of asking which product. The full-policy bot asks back correctly |
| Metric doesn't fit | TS04, TS14, TS20, TS26 | Correct answers, but recall 0.5: conclusions in the expected output like "so a 20-year-old is not eligible yet" are worked out, not written in the policy, so they can't be found in the retrieved text |
| Metric doesn't fit | TS10 | "Hi" needs no policy, so retrieving nothing is correct, but recall still scores 0 |
| Not a defect | TS07 | `groq.RateLimitError`: too many API calls |

### Bugs fixed before the first run

- Four wrong auto-added imports (`chatbot.ragchatbot`, `deepeval_testing.calibrate_judge`, `deepeval_testing.test_correctness_chatbot`, and `web_fileresponse` from `aiohttp`). `from ragchatbot import ask_rag_bot` has to come after `sys.path.append`, so Python knows to look in `chatbot/`
- `with open(...)` without `as file:`, the same bug as in the two earlier test files
- The venv was not active, so the system Python 3.8 ran pytest and warned "Unknown config option: asyncio_default_fixture_loop_scope"

## RAG diagnosis: recall vs faithfulness

Two metrics together should tell you where a RAG bot breaks:

| Contextual recall | Faithfulness | Diagnosis |
|---|---|---|
| High | High | Working well |
| Low | High | Retrieval problem: fix the librarian (the search) |
| High | Low | Hallucination: the AI made things up |
| Low | Low | Both broken |

- **Contextual recall** asks: does the retrieved text contain what's needed for the expected answer?
- **Faithfulness** asks: does the bot's answer stick to the retrieved text?

To check the table, [rag_diagnosis.py](rag_diagnosis.py) builds one case for each corner. The sections come from the real search (`retrieve()`). The real bot never made anything up, so the two hallucinated answers were written by hand.

| Case | Sections found | Answer | Recall | Faithfulness | Expected diagnosis | Got |
|---|---|---|---|---|---|---|
| Home loan rate | Home Loan, Personal Loan | "8.5% per year" (correct) | 1.0 | 1.0 | Working well | **Working well** ✅ |
| FD rate for a senior citizen | Personal Loan, Home Loan (wrong) | "I'm sorry, I don't have that information." | 0.0 | **0.0** | Retrieval problem | **Both broken** ❌ |
| Home loan rate | Home Loan, Personal Loan | "8.5% per year, **no processing fee**, and **a free credit card**" (made up) | 1.0 | 0.67 | Hallucination | **Hallucination** ✅ |
| Withdraw FD on the 3rd day | ATM withdrawal limit (wrong) | "Yes, **at any time with a 2% penalty**" (made up) | 0.0 | **1.0** | Both broken | **Retrieval problem** ❌ |

**2 of 4 matched the table. The 2 that didn't show how Faithfulness really works.**

### Finding 1: Faithfulness only catches claims that contradict the retrieved text

- **Hallucination case (0.67).** The judge caught "no processing fee", because the retrieved Personal Loan section says "Processing fee: 1%". It **missed** "a free credit card": no retrieved section mentions credit cards, so nothing contradicted it. The judge's reason: "the actual output incorrectly states that Sahyadri Bank's personal loan has no processing fee, directly contradicting the retrieval context". It said nothing about the credit card.
- **Both broken case (1.0).** "Withdraw at any time with a 2% penalty" is completely made up, but the only retrieved section was the ATM limit, which says nothing about FDs. With nothing to contradict it, the judge said "there are no contradictions, indicating perfect faithfulness."

So in DeepEval, **Faithfulness means "not contradicted", not "supported"**. A made-up claim on a topic the retrieved text doesn't cover gets a perfect score. That is most dangerous exactly when retrieval fails, because then the retrieved text covers nothing relevant.

### Finding 2: a refusal has no fixed faithfulness score

The same answer, "I'm sorry, I don't have that information", to the same TS03 question with the same retrieved sections:

- In the [RAG test run](test_rag_chatbot.py): Faithfulness **1.0**
- In this diagnosis run: Faithfulness **0.0**, because "the actual output incorrectly claims the information is unavailable, yet the retrieval context contains multiple specific details about personal and home loan interest rates"

A refusal makes no factual claim, so the judge has to guess how to score it, and it guessed differently each time. Faithfulness can't reliably say whether a refusal was right.

### What this means for the table

- The table works when the bot **answers** and the retrieved text **covers the topic** (cases 1 and 3).
- When retrieval fails, a low Faithfulness score is not guaranteed even for a made-up answer, so "Both broken" can look like "Retrieval problem".
- When the bot **refuses**, Faithfulness is unpredictable, so "Retrieval problem" can look like "Both broken".
- **Always look at recall first.** If recall is low, the search failed, and Faithfulness alone can't tell you whether the answer is also wrong. Check the answer against `expected_output` too (for example with GEval correctness).
- **Not every failing test is a defect.** 5 of the 11 RAG failures came from a metric that doesn't fit the case (worked-out conclusions, a greeting that needs no policy). Check whether the bot or the test is wrong before reporting a defect.
- **Faithfulness means "not contradicted", not "supported".** A made-up answer about a topic the retrieved text doesn't cover scores 1.0, so read recall first.
