import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

HERE = Path(__file__).parent
load_dotenv(HERE / ".env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"


STOP_WORDS = {"what", "is", "the", "a", "an", "for", "of", "on", "my", "i",
              "do", "can", "how", "much", "to", "in", "and", "are", "if", "does"}


def load_chunks():
    chunks = []
    policy_folder = HERE / "data" / "policies"
    for path in sorted(policy_folder.glob("*.md")):
        text = path.read_text()
        sections = text.split("\n## ")
        title = sections[0].strip().split("\n")[0]
        for section in sections[1:]:
            chunks.append(title + "\n## " + section.strip())
    return chunks


CHUNKS = load_chunks()


def get_words(text):
    cleaned = ""
    for character in text.lower():
        if character.isalnum() or character == " ":
            cleaned = cleaned + character
        else:
            cleaned = cleaned + " "
    word_set = set()
    for word in cleaned.split():
        if word not in STOP_WORDS:
            word_set.add(word)
    return word_set


def retrieve(question, top_k=2):
    question_words = get_words(question)
    scored = []
    for chunk in CHUNKS:
        overlap = len(question_words & get_words(chunk))
        scored.append((overlap, chunk))
    scored.sort(reverse=True)
    if not scored or scored[0][0] == 0:
        return []
    # Keep every section that ties with the last place, so a tie never drops the right one
    cutoff = scored[min(top_k, len(scored)) - 1][0]
    best = []
    for score, chunk in scored:
        if score >= cutoff and score > 0:
            best.append(chunk)
    return best


def ask_rag_bot(question, history):
    context_chunks = retrieve(question)
    context = "\n\n".join(context_chunks)

    system_prompt = f"""You are the customer assistant for Sahyadri Bank.

IMPORTANT PRIVACY RULE: If anyone asks for another person's or any customer's account details, balance, or personal information, reply exactly: "I'm sorry, I can't share any customer's personal or account information for privacy reasons."

If the customer greets you, greet them politely and ask how you can help.
Answer ONLY using the policy sections below.
If the answer is not in them, say: "I'm sorry, I don't have that information."
Keep answers short and clear.

POLICY SECTIONS:
{context}
"""

    history.append({"role": "user", "content": question})
    messages = [{"role": "system", "content": system_prompt}] + history
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=messages
    )
    answer = response.choices[0].message.content
    history.append({"role": "assistant", "content": answer})
    return answer, context_chunks


if __name__ == "__main__":
    print("Number of policy chunks:", len(CHUNKS))
    print("Sahyadri Bank RAG Assistant (type 'exit' to quit)")
    history = []
    while True:
        question = input("You: ")
        if question == "exit":
            break
        answer, chunks = ask_rag_bot(question, history)
        print("\n[Retrieved sections]")
        for chunk in chunks:
            print(" -", chunk.split("\n")[1])
        print("\nBot:", answer, "\n")