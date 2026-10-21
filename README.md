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
| [JSON/testcases.json](JSON/testcases.json) | Test case data |
| [JSON/results.json](JSON/results.json) | Results written by `readjson.py` |

## Key concepts so far

- **Variables and types:** `str`, `float`, `bool`, `type()`
- **Lists:** indexing starts at 0, `len()`, `append()`
- **Dictionaries:** key–value pairs, access with `dict["key"]`, add new keys
- **Golden dataset:** a list of test case dictionaries (`id`, `question`, `expected_keyword`) used to check chatbot answers
- **Functions:** `def`, parameters, `return`, importing functions from another file
- **JSON:** `json.load` to read test cases, `json.dump` to write results to a separate file
- **pytest:** test functions must start with `test_`, `assert` checks a condition, a failed assert fails the test

## Setup

[requirements.txt](requirements.txt) records which packages the project uses, so anyone (including CI later) can install them:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

After installing a new package, update the file from inside the venv with `pip freeze > requirements.txt`.

## Running

```bash
python3 python/2_exercise.py
```

Run the tests (from inside `python/`, so `checks` can be imported):

```bash
cd python
pytest -v
```
