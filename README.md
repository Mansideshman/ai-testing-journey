# AI Testing Journey

Hands-on journey into AI testing: chatbot testing, LLM evaluation with DeepEval, RAG evaluation, safety and bias testing, and ML model validation.

It starts with Python basics, then moves on to testing a real LLM chatbot.

## Structure

| File | Topic |
|------|-------|
| [python/variables_and_print.py](python/variables_and_print.py) | Variables and `print` |
| [python/lists_dicts_loops_ifelse.py](python/lists_dicts_loops_ifelse.py) | Lists, dictionaries, and a list of dictionaries (golden dataset) |
| [python/2_exercise.py](python/2_exercise.py) | Exercise: loop over a golden dataset, check fake chatbot answers for expected keywords, count PASS/FAIL |
| [python/functions_and_json.py](python/functions_and_json.py) | Functions: checking answers and answer length |
| [python/readjson.py](python/readjson.py) | Reading and writing JSON test case files |
| [python/checks.py](python/checks.py) | Reusable check functions: `check_answer` (keyword PASS/FAIL) and `is_short` (under 20 words) |
| [python/test_pytest_basics.py](python/test_pytest_basics.py) | First pytest tests for the functions in `checks.py` |
| [python/case_runner.py](python/case_runner.py) | Test runner: loads test cases and answers from JSON, checks each one, prints a summary, saves results |
| [python/test_goldendataset.py](python/test_goldendataset.py) | Data-driven pytest: one test per golden dataset case using `@pytest.mark.parametrize` |
| [chatbot/first_llm_call.py](chatbot/first_llm_call.py) | First real LLM call: asks a bank question through the Groq API, with `temperature` to control randomness |
| [chatbot/notes.md](chatbot/notes.md) | Findings: how answers change between temperature 0 and 1, why AI tests must check meaning, not exact text, multi-turn memory results, a memory trap test where the bot used the customer's name and then claimed not to know it, testing the tests by breaking two cases on purpose, and stability results from 3 full runs of the golden suite |
| [chatbot/read_policies.py](chatbot/read_policies.py) | Reads the bank policy files and joins them into one text (the knowledge the chatbot will answer from) |
| [chatbot/chatbot.py](chatbot/chatbot.py) | Sahyadri Bank chatbot: answers only from the policy documents, greets customers, refuses privacy requests, remembers the conversation for follow-up questions; type questions, `exit` to quit |
| [chatbot/chatbot_notes.md](chatbot/chatbot_notes.md) | Week 2 testing notes: non-determinism, first manual test session, 2 defects found and fixed, lessons learned |
| [chatbot/ragchatbot.py](chatbot/ragchatbot.py) | RAG chatbot: splits the policies into 10 sections, finds the 2 sections that share the most words with the question, and answers only from those; prints which sections it retrieved |
| [chatbot/RAGBot_notes.md](chatbot/RAGBot_notes.md) | RAG retrieval investigation: 14 golden questions, 12 correct; both failures (TS03, TS19) came from the search, not the LLM ("FD" never matches "Fixed Deposit", plurals don't match, ties favour loan sections) |
| [chatbot/data/policies/](chatbot/data/policies/) | Fictional Sahyadri Bank policies: [loans](chatbot/data/policies/loans.md), [credit cards](chatbot/data/policies/credit_cards.md), [fixed deposits](chatbot/data/policies/fixed_deposits.md) |
| [chatbot_testing/test-scenarios.md](chatbot_testing/test-scenarios.md) | 30 test scenarios for the chatbot with expected behaviour, across happy path, conditions, calculations, exceptions, out of scope, unclear, spelling, multi-turn, safety, and tricky questions |
| [chatbot_testing/Data/goldentestdata.json](chatbot_testing/Data/goldentestdata.json) | Golden dataset: the 30 test scenarios as JSON, each with `id`, `category`, `question`, `expected_keywords`, `should_refuse`, and an `expected_output` for 10 cases (used by GEval) |
| [chatbot_testing/check_dataset.py](chatbot_testing/check_dataset.py) | Checks the golden dataset: total cases, count per category, and any missing required fields |
| [chatbot_testing/test_chatbot_golden.py](chatbot_testing/test_chatbot_golden.py) | Automated chatbot tests: asks the real bot every golden dataset question (replaying `history` for multi-turn cases), checks expected keywords or a refusal |
| [chatbot_testing/reports/failed_tests_demo.md](chatbot_testing/reports/failed_tests_demo.md) | Failed test record: two golden cases broken on purpose (TS01 expects a refusal, TS02 expects the wrong rate), the raw pytest output, and how to read a failure and decide whether the bot or the test data is wrong |
| [deepeval_testing/readme.md](deepeval_testing/readme.md) | DeepEval notes: how the LLM judge works, the Answer Relevancy experiment (a wrong 15% answer scored a perfect 1.00), and lessons learned |
| [deepeval_testing/groq_judge.py](deepeval_testing/groq_judge.py) | `GroqJudge`: a custom DeepEval judge model that scores answers through the Groq API |
| [deepeval_testing/test_deepeval_first.py](deepeval_testing/test_deepeval_first.py) | First DeepEval tests: `AnswerRelevancyMetric` passes a relevant answer and fails an irrelevant one |
| [deepeval_testing/test_relevancy_chatbot.py](deepeval_testing/test_relevancy_chatbot.py) | DeepEval on the real chatbot: the first 10 answerable golden dataset questions scored with `AnswerRelevancyMetric` (9/10 passed; TS03 was flaky and passed on rerun; TS06's clarifying question scored 1.00 but with an inaccurate reason) |
| [deepeval_testing/test_correctness_chatbot.py](deepeval_testing/test_correctness_chatbot.py) | GEval correctness test on the real chatbot: compares each answer with the golden dataset's `expected_output` (10/10 passed at first, but the judge was too lenient on TS09; after calibration and the policy fix, TS09 passes with the correct answer) and saves results to [correctness_results.jsonl](deepeval_testing/results/correctness_results.jsonl) |
| [deepeval_testing/calibrate_judge.py](deepeval_testing/calibrate_judge.py) | Judge calibration: compares the GEval judge's pass/fail verdicts with my own labels in [human_labels.json](deepeval_testing/human_labels.json) (90% agreement, then 100% after making TS09's expected output precise) |
| [JSON/testcases.json](JSON/testcases.json) | Golden dataset: test cases with `id`, `question`, `expected_keyword`, `category` |
| [JSON/fake_answers.json](JSON/fake_answers.json) | Fake chatbot answers, keyed by test case id |
| [JSON/results.json](JSON/results.json) | Results written by `case_runner.py` and `readjson.py` |

## Key concepts so far

- **Variables and types:** `str`, `float`, `bool`, `type()`
- **Lists:** indexing starts at 0, `len()`, `append()`
- **Dictionaries:** key–value pairs, access with `dict["key"]`, add new keys
- **Golden dataset:** a list of test case dictionaries (`id`, `question`, `expected_keyword`) used to check chatbot answers
- **Functions:** `def`, parameters, `return`, importing functions from another file
- **JSON:** `json.load` to read test cases, `json.dump` to write results to a separate file
- **pytest:** test functions must start with `test_`, `assert` checks a condition, a failed assert fails the test
- **Data-driven tests:** `@pytest.mark.parametrize` runs one test function once per test case loaded from JSON
- **LLM API calls:** a system message sets the bot's role, a user message asks the question, the reply is in `response.choices[0].message.content`
- **Temperature:** `0` gives near-identical answers each run (good for repeatable tests); `1` changes wording, order, and sometimes meaning
- **Testing AI output:** exact-match tests break on non-deterministic answers, so testers check meaning, not just keywords
- **Reading text files:** `file.read()` returns a whole file as one string; strings join with `+`
- **System prompt grounding:** putting the policy text in the system prompt and telling the bot to answer ONLY from it, and to refuse when the answer isn't there
- **Chatbot defect testing:** a safety rule can break normal behaviour (greetings); rule order in the prompt matters; re-test after every fix and re-run old tests (regression)
- **Conversation memory:** the model remembers nothing between calls, so every user and assistant message is kept in a `history` list and resent with each call; roles are `system` (rules), `user` (customer), `assistant` (bot replies)
- **Conflicting rules:** prompt rules can override each other ("answer only from policies" beat conversation memory), causing inconsistent behaviour; some fixes need a product decision, not just a prompt change
- **Test scenario design:** cover more than happy paths: conditions, calculations, exceptions, out-of-scope, unclear and misspelt questions, multi-turn, safety (prompt injection), and false premises the bot must correct
- **Test data quality:** check the dataset itself before using it: every case has all required fields, and category counts show whether coverage is balanced (counting with a dict as a tally sheet)
- **Automated LLM tests:** one pytest case per golden dataset entry; refusal cases look for refusal phrases, others look for expected keywords
- **Flaky text matching:** LLMs may write `1 %` or use unusual spaces (`\u202f`), so answers are normalized before comparing keywords
- **Rate limits:** many API calls in a row can hit the provider's limit; a short pause between tests avoids it
- **False premises:** tests caught the bot refusing questions with wrong facts ("since the penalty is 5%..."); a prompt rule to correct wrong information fixed it
- **Reading test failures:** a pytest failure shows the test data, the failed `assert` line, the custom error message (expected vs actual), and the printed bot answer; then decide if the bot (defect) or the test data is wrong
- **Testing the tests:** break a case on purpose to prove the suite can catch a wrong answer
- **Stability runs:** an LLM is non-deterministic, so run the suite several times; "all passed" can still hide defects when a case has weak checks (no keywords), so eye-check those answers
- **LLM as a judge:** DeepEval asks a second LLM to score answers by meaning; a custom judge subclasses `DeepEvalBaseLLM`
- **Relevancy is not correctness:** `AnswerRelevancyMetric` gave a wrong answer (15% instead of 8.5%) a perfect score and punished a correct answer full of small talk; checking facts needs a metric with the truth, like `FaithfulnessMetric`
- **Flaky LLM judges:** the judge's score for the same answer can change between runs (TS03: 0.67, then 1.00); `--reruns 1` from `pytest-rerunfailures` retries a failed case once
- **Judging the judge:** a correct score can come with a wrong reason, so read the judge's reasons, and save the bot's answer in failure messages so every judgement can be checked
- **GEval correctness:** write the grading rules in plain English and compare each answer with an `expected_output`; the wrong 15% answer that Answer Relevancy scored 1.00 got 0.0 from GEval; a score is only as strict as the criteria (TS09 passed with "1% of the interest earned" when the policy says "1% on the interest rate")
- **Judge calibration:** label answers yourself without looking at the judge's scores, then measure agreement; a precise `expected_output` fixed a disagreement that a stricter rubric could not
- **Fix defects at the source:** the misleading FD penalty answer came from ambiguous policy wording; after fixing the policy, the keyword, expected output, GEval criteria and human label all had to be updated to match the corrected answer
- **RAG (Retrieval-Augmented Generation):** search the documents first and send only the matching parts to the LLM; a wrong answer can come from the search, so always log what was retrieved
- **API keys:** kept in a `.env` file (ignored by git) and loaded with `python-dotenv`, never written in code

## Setup

[requirements.txt](requirements.txt) records which packages the project uses, so anyone (including CI later) can install them:

Use Python 3.9 or newer (DeepEval needs it; this project uses 3.11, the same as CI). On Ubuntu 20.04, which only has 3.8, install 3.11 with [uv](https://docs.astral.sh/uv/) and create the venv with `uv venv --python 3.11 .venv`.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For the chatbot, create `chatbot/.env` with your [Groq API key](https://console.groq.com/keys):

```
GROQ_API_KEY=your_key_here
```

After installing a new package, update the file from inside the venv with `pip freeze > requirements.txt`.

## Running

```bash
python3 python/2_exercise.py
python3 python/case_runner.py
cd chatbot && python3 first_llm_call.py
python3 chatbot/read_policies.py
python3 chatbot_testing/check_dataset.py
cd chatbot && python3 chatbot.py   # interactive, type 'exit' to quit
cd chatbot && python3 ragchatbot.py   # RAG version, shows the retrieved sections
```

Run the tests (from inside `python/`, so `checks` can be imported):

```bash
cd python
pytest -v
```

Run the automated chatbot tests (from the repo root, with the venv active; needs the Groq API key and takes about 1.5 minutes):

```bash
pytest chatbot_testing/test_chatbot_golden.py -v
```

Useful options: `-k TS09` runs one case, `--lf` reruns only the last failed tests, `-rf` lists failures in the summary, `-s` shows each bot answer. See [failed_tests_demo.md](chatbot_testing/reports/failed_tests_demo.md) for what a failed run looks like.

Run the DeepEval tests (needs the Groq API key):

```bash
cd deepeval_testing
pytest test_deepeval_first.py -v -s
pytest test_relevancy_chatbot.py -v -s --reruns 1   # real chatbot, about 1.5 minutes
pytest test_correctness_chatbot.py -v -s             # GEval facts check, about 1 minute
python calibrate_judge.py                            # compare the judge with human labels
```

If you see `ModuleNotFoundError: No module named 'groq'`, the venv is not active: run `source .venv/bin/activate` first.

`test_golden_dataset[TC004]` fails on purpose: the fake answer says 2000 rupees but the expected keyword is `5000`, showing how a wrong chatbot answer gets caught.
