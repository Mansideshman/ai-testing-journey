# AI Testing Journey

Learning Python step by step, with the goal of testing AI chatbots and LLM applications.

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
| [chatbot/first_llm_call.py](chatbot/first_llm_call.py) | First real LLM call: asks a bank question through the Groq API |
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
```

Run the tests (from inside `python/`, so `checks` can be imported):

```bash
cd python
pytest -v
```

`test_golden_dataset[TC004]` fails on purpose: the fake answer says 2000 rupees but the expected keyword is `5000`, showing how a wrong chatbot answer gets caught.
