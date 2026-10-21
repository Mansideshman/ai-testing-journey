import json

with open("/home/mansideshman/Documents/MansiData/GitRepo/AITester/ai-testing-journey/JSON/testcases.json") as file:
    golden_dataset = json.load(file)

print(len(golden_dataset),"test cases loaded")
print(golden_dataset[0]["question"])

results = [{"id":"TC001", "result": "PASS"}]
with open("/home/mansideshman/Documents/MansiData/GitRepo/AITester/ai-testing-journey/JSON/results.json","w")as file:
    json.dump(results, file, indent=4)


