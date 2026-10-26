import json

with open("/home/mansideshman/Documents/MansiData/GitRepo/AITester/ai-testing-journey/chatbot-testing/Data/goldentestdata.json") as file:
    dataset = json.load(file)
    
print("Total test cases:",len(dataset))

category_counts = {}
for case in dataset:
    category = case["category"]
    if category in category_counts:
        category_counts[category] = category_counts[category] + 1
    else:
        category_counts[category] = 1

print("\n Test cases per category:")
for category, count in category_counts.items():
    print(category,":",count)


required_fields = ["id","category","question","expected_keywords", "should_refuse"]
for case in dataset:
    for field in required_fields:
        if field not in case:
            print("MISSING FIELD:",field,"in", case.get("id","unknown"))



