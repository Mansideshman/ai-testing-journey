# with open("/home/mansideshman/Documents/MansiData/GitRepo/AITester/ai-testing-journey/chatbot/data/policies/loans.md") as file:
#     loan_policy = file.read()

# print(loan_policy)


def read_file(path):
    with open(path) as file:
        return file.read()

loans = read_file("/home/mansideshman/Documents/MansiData/GitRepo/AITester/ai-testing-journey/chatbot/data/policies/loans.md")
cards = read_file("/home/mansideshman/Documents/MansiData/GitRepo/AITester/ai-testing-journey/chatbot/data/policies/credit_cards.md")
deposits = read_file("/home/mansideshman/Documents/MansiData/GitRepo/AITester/ai-testing-journey/chatbot/data/policies/fixed_deposits.md")

all_policies = loans + "\n\n" + cards + "\n\n" + deposits

print(all_policies)
print("Total characters:",len(all_policies))
