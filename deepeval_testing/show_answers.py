import json
from pathlib import Path

HERE = Path(__file__).parent
RESULTS_FILE = HERE / "results" / "correctness_results.jsonl"
LABELS_FILE = HERE / "human_labels.json"

latest_results = {}
with open(RESULTS_FILE) as file:
    for line in file:
        record = json.loads(line)
        latest_results[record["id"]] = record

with open(LABELS_FILE) as file:
    human_labels = json.load(file)

# Show only the answers that still need a human label, without the judge's score or reason
for test_id, record in latest_results.items():
    if test_id in human_labels:
        continue
    print("=" * 60)
    print(test_id)
    print("Question:", record["question"])
    print("Expected:", record["expected"])
    print("Answer:  ", record["answer"])
