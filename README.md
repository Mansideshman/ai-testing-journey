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
| [chatbot/notes.md](chatbot/notes.md) | Findings: how answers change between temperature 0 and 1, why AI tests must check meaning, not exact text, multi-turn memory results, and a memory trap test where the bot used the customer's name and then claimed not to know it |
| [chatbot/read_policies.py](chatbot/read_policies.py) | Reads the bank policy files and joins them into one text (the knowledge the chatbot will answer from) |
| [chatbot/chatbot.py](chatbot/chatbot.py) | Sahyadri Bank chatbot: answers only from the policy documents, greets customers, refuses privacy requests, remembers the conversation for follow-up questions; type questions, `exit` to quit |
| [chatbot/chatbot_notes.md](chatbot/chatbot_notes.md) | Week 2 testing notes: non-determinism, first manual test session, 2 defects found and fixed, lessons learned |
| [chatbot/data/policies/](chatbot/data/policies/) | Fictional Sahyadri Bank policies: [loans](chatbot/data/policies/loans.md), [credit cards](chatbot/data/policies/credit_cards.md), [fixed deposits](chatbot/data/policies/fixed_deposits.md) |
| [chatbot_testing/test-scenarios.md](chatbot_testing/test-scenarios.md) | 30 test scenarios for the chatbot with expected behaviour, across happy path, conditions, calculations, exceptions, out of scope, unclear, spelling, multi-turn, safety, and tricky questions |
| [chatbot_testing/Data/goldentestdata.json](chatbot_testing/Data/goldentestdata.json) | Golden dataset: the 30 test scenarios as JSON, each with `id`, `category`, `question`, `expected_keywords`, `should_refuse` |
| [chatbot_testing/check_dataset.py](chatbot_testing/check_dataset.py) | Checks the golden dataset: total cases, count per category, and any missing required fields |
| [chatbot_testing/test_chatbot_golden.py](chatbot_testing/test_chatbot_golden.py) | Automated chatbot tests: asks the real bot every golden dataset question (replaying `history` for multi-turn cases), checks expected keywords or a refusal |
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
- **API keys:** kept in a `.env` file (ignored by git) and loaded with `python-dotenv`, never written in code

## Setup

[requirements.txt](requirements.txt) records which packages the project uses, so anyone (including CI later) can install them:

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

If you see `ModuleNotFoundError: No module named 'groq'`, the venv is not active: run `source .venv/bin/activate` first.

`test_golden_dataset[TC004]` fails on purpose: the fake answer says 2000 rupees but the expected keyword is `5000`, showing how a wrong chatbot answer gets caught.
