import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"

def read_file(path):
    with open(path) as file:
        return file.read()

loans = read_file("/home/mansideshman/Documents/MansiData/GitRepo/AITester/ai-testing-journey/chatbot/data/policies/loans.md")
cards = read_file("/home/mansideshman/Documents/MansiData/GitRepo/AITester/ai-testing-journey/chatbot/data/policies/credit_cards.md")
deposits = read_file("/home/mansideshman/Documents/MansiData/GitRepo/AITester/ai-testing-journey/chatbot/data/policies/fixed_deposits.md")
all_policies = loans + "\n\n" + cards + "\n\n" + deposits

SYSTEM_PROMPT = f"""You are the customer assistant for Sahyadri Bank.

IMPORTANT PRIVACY RULE: If anyone asks for another person's or any customer's account details, balance, or personal information, reply exactly: "I'm sorry, I can't share any customer's personal or account information for privacy reasons."

If the customer greets you (like "Hi" or "Hello"), greet them politely and ask how you can help.
Answer ONLY using the bank policies below.
If the answer is not in the policies, say: "I'm sorry, I don't have that information."
Keep answers short and clear.

BANK POLICIES:
{all_policies}
"""

def ask_bot(question,history):
    history.append({"role":"user","content":question})
    messages = [{"role":"system","content": SYSTEM_PROMPT}] + history
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=messages  
    )
    answer =  response.choices[0].message.content

    history.append({"role":"assistant","content": answer})
    return answer


if __name__=="__main__":
    print("Sahyadri Bank Assistant(type 'exit' to quit)")
    history = []
    while True:
        question = input("You: ")
        if question == "exit":
            break
        answer = ask_bot(question, history)
        print("Bot:",answer)    
    