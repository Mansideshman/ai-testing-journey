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
| [JSON/testcases.json](JSON/testcases.json) | Test case data |

## Key concepts so far

- **Variables and types:** `str`, `float`, `bool`, `type()`
- **Lists:** indexing starts at 0, `len()`, `append()`
- **Dictionaries:** key–value pairs, access with `dict["key"]`, add new keys
- **Golden dataset:** a list of test case dictionaries (`id`, `question`, `expected_keyword`) used to check chatbot answers

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
