# def check_answer(answer, expected_keyword):
#     if expected_keyword in answer:
#         return "PASS"
#     else:
#         return "FAIL"

# print(check_answer("The rate is 10.5% per year","10.5%"))
# print(check_answer("There is no penalty","1%"))
# Exercise: write a function is_short(answer) that returns True if the answer has fewer than 20 words.

def is_short(answer):
    word_count = len(answer.split())
    if word_count < 20:
        return True
    else:
        return False
print(is_short("The rate is 10.5% per year."))

long_answer = "Thank you for your question.The personal load interest rate at our bank is 10.5% per year for salaried customer, and it may vary for slef -employed customers"

print(is_short(long_answer))



