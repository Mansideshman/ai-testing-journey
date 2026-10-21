# AI Testing Journey

Learning Python step by step, with the goal of testing AI chatbots and LLM applications.

## Structure

| File | Topic |
|------|-------|
| [python/1.py](python/1.py) | Variables and `print` |
| [python/2.py](python/2.py) | Lists, dictionaries, and a list of dictionaries (golden dataset) |
| [python/2_exercise.py](python/2_exercise.py) | Exercise: loop over a golden dataset, check fake chatbot answers for expected keywords, count PASS/FAIL |

## Key concepts so far

- **Variables and types:** `str`, `float`, `bool`, `type()`
- **Lists:** indexing starts at 0, `len()`, `append()`
- **Dictionaries:** key–value pairs, access with `dict["key"]`, add new keys
- **Golden dataset:** a list of test case dictionaries (`id`, `question`, `expected_keyword`) used to check chatbot answers

## Running

```bash
python3 python/2.py
```
