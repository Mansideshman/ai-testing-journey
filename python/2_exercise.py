# a fake chatbot that “answers” each question, and a loop that checks each answer and counts results.

# Using golden_dataset and fake_answers, write a loop that:
# Gets the answer for each test case using its id
# Prints TC001: PASS or TC002: FAIL
# At the end prints Passed: 2, Failed: 1
golden_dataset = [
    {"id":"TC001","question":"Personal loan rate?","expected_keyword":"10.5%"},
    {"id":"TC002","question":"FD early closure penalty?","expected_keyword":"1%"},
    {"id":"TC003","question":"Credit card annual fee?","expected_keyword":"500"},
    {"id": "TC004", "question": "Minimum balance for savings account?", "expected_keyword": "5000"} 
]

fake_answers = {
    "TC001": "The rate is 10.5% per year.",
    "TC002": "There is no penalty for early closure.",
    "TC003": "The annual fee is 500 rupees.",
     "TC004": "The minimum balance for a savings account is 5000 rupees." 
}


passed = 0
failed =0

for case in golden_dataset:
    case_id = case["id"]
    expected = case["expected_keyword"]
    answer = fake_answers[case_id]

    if expected in answer:
        print(case)


