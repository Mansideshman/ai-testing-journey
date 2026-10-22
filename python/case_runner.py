import json
from checks import check_answer


def load_json(path):
    with open(path) as file:
        return json.load(file)


def run_tests(test_cases, answers):
    results = []
    for case in test_cases:
        answer = answers[case["id"]]                          # blank 1
        result = check_answer(answer, case["expected_keyword"])   # blank 2
        results.append({
            "id": case["id"],
            "category": case["category"],
            "result": result                                  # blank 3
        })
    return results


def print_summary(results):
    passed = 0
    failed = 0
    for r in results:
        if r["result"] == "PASS":
            passed = passed + 1
        else:
            failed = failed + 1
            print("FAILED:", r["id"], "(" + r["category"] + ")")
    print("Total:", len(results), "| Passed:", passed, "| Failed:", failed)


test_cases = load_json("/home/mansideshman/Documents/MansiData/GitRepo/AITester/ai-testing-journey/JSON/testcases.json")
answers = load_json("/home/mansideshman/Documents/MansiData/GitRepo/AITester/ai-testing-journey/JSON/fake_answers.json")                 # blank 4
results = run_tests(test_cases, answers)
print_summary(results)

with open("/home/mansideshman/Documents/MansiData/GitRepo/AITester/ai-testing-journey/JSON/results.json", "w") as file:
    json.dump(results, file, indent=4)




