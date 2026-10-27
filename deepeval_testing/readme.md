# DeepEval Testing

First steps with [DeepEval](https://deepeval.com): using an LLM as a judge to score chatbot answers by meaning, not by exact keywords.

## Files

| File | What it does |
|------|--------------|
| [groq_judge.py](groq_judge.py) | `GroqJudge`: a custom DeepEval judge model that sends DeepEval's scoring prompts to Groq (`openai/gpt-oss-120b`, `temperature=0`). Loads the API key from `chatbot/.env` |
| [test_deepeval_first.py](test_deepeval_first.py) | Two `AnswerRelevancyMetric` tests: a relevant answer must score at least 0.7, and an irrelevant answer must score below 0.7 |

## How to run

DeepEval needs Python 3.9 or newer (this project uses 3.11). From inside this folder, with the venv active:

```bash
cd deepeval_testing
pytest test_deepeval_first.py -v -s
```

`-s` prints the judge's score and reason.

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

## What I learned

- **Relevancy is not correctness.** Answer Relevancy only checks whether the answer stays on topic. A wrong answer (15% instead of 8.5%) got a perfect 1.00. For a bank chatbot, that is a dangerous gap.
- **Extra chatter is punished.** The metric splits the answer into statements and counts how many address the question. A correct answer buried in small talk scored only 0.17.
- **One metric is not enough.** To catch wrong facts, use a metric that knows the truth: `FaithfulnessMetric` (checks the answer against the policy text given as `retrieval_context`) or `GEval` with an `expected_output`.
- **Every test needs an assert.** A test that only prints a score can never fail.
- **Small typos break LLM tests.** A leading space in the model name (`" openai/gpt-oss-120b"`) gave a 404 error, and `threashold` instead of `threshold` gave a `TypeError`.
