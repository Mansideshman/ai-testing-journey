import json
from pathlib import Path

HERE = Path(__file__).parent
RESULTS_FILE = HERE / "results" / "correctness_results.jsonl"
LABELS_FILE = HERE / "human_labels.json"
PASS_MARK = 0.7

latest_results = {}
with open(RESULTS_FILE) as file:
    for line in file:
        record = json.loads(line)
        latest_results[record["id"]] = record

with open(LABELS_FILE) as file:
    human_labels = json.load(file)

agree = 0
disagreements = []

for test_id, human_verdict in human_labels.items():
    if test_id not in latest_results:
        print("No judge result for", test_id)
        continue

    record = latest_results[test_id]
    if record["score"] >= PASS_MARK:
        judge_verdict = "pass"
    else:
        judge_verdict = "fail"
    
    if judge_verdict ==  human_verdict:
        agree = agree + 1
    else:
        disagreements.append((test_id, human_verdict, judge_verdict, record["score"], record["reason"]))

total = agree + len(disagreements)
print("Agreement:", agree, "out of", total)
print("Agreement rate:", round(agree / total * 100), "%")

print("\nDisagreements:")

for test_id, human, judge, score, reason in disagreements:
    print("-",test_id,"| You:", human, "| Judge:", judge, "| Score:", score)
    print(" Judge's reason:", reason)
