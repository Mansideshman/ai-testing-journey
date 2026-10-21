# AI Testing Journey

Learning Python step by step, with the goal of testing AI chatbots and LLM applications.

## Structure

| File | Topic |
|------|-------|
| [python/variables_and_print.py.py](python/variables_and_print.py.py) | Variables and `print` |
| [python/lists_dicts_loops_ifelse.py.py](python/lists_dicts_loops_ifelse.py.py) | Lists, dictionaries, and a list of dictionaries (golden dataset) |
| [python/2_exercise.py](python/2_exercise.py) | Exercise: loop over a golden dataset, check fake chatbot answers for expected keywords, count PASS/FAIL |
| [python/functions_and_json.py.py](python/functions_and_json.py.py) | Functions: checking answers and answer length |
| [python/readjson.py](python/readjson.py) | Reading and writing JSON test case files |
| [JSON/testcases.json](JSON/testcases.json) | Test case data |

## Key concepts so far

- **Variables and types:** `str`, `float`, `bool`, `type()`
- **Lists:** indexing starts at 0, `len()`, `append()`
- **Dictionaries:** key–value pairs, access with `dict["key"]`, add new keys
- **Golden dataset:** a list of test case dictionaries (`id`, `question`, `expected_keyword`) used to check chatbot answers

## Running

```bash
python3 python/2.py
```
