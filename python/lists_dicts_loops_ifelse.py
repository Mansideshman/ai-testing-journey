# question = "What is the personal loan interest rate?"
# expected_rate = 10.5
# is_in_scope = True

# print(question)
# print(expected_rate)
# print(type(expected_rate))


# questions = ["What is the personal loan interest rate?","Can I close my FD early?","What is the credit card annual fee?"]

# print(questions[0])
# print(len(questions))
# questions.append("What documents do I need for a loan?")
# print(len(questions))


#Dictionaries :Labelled boxes together

# test_case =
# {
#     "id":"TC001",
#     "question":"What is the personal loan interest rate?",
#     "expected_keyword":"10.5%",
#     "category":"loans"
# }


# test_case = {
#     "id":"TC002",
#     "question":"How much limit for credit card?",
#     "expected_keyword": "500000",
#     "category":"Credit card"
# }

# print(test_case["question"])
# print(test_case["expected_keyword"])
# test_case["priority"] = "high"
# print(test_case)


# A list of dictionaries = a golden dataset

golden_dataset = [
    {"id":"TC001","question":"Personal loan rate?","expected_keyword":"10.5%"},
    {"id":"TC002","question":"FD early closure penalty?","expected_keyword":"1%"},
    {"id":"TC003","question":"Credit card annual fee?","expected_keyword":"500"}
]

# print(golden_dataset[2]["question"])
# print(golden_dataset[2]["expected_keyword"])


# if/else :making a pass or fail decision

# bot_answer = "The personal loan interest rate is 10.5% per year"
# expected_keyword = "10.5%"

# if expected_keyword in bot_answer:
#     print("PASS")
# else:
#     print("FAIL")

# for loops:running every test case


for case in golden_dataset:
    print(case["id"],"-",case["question"])