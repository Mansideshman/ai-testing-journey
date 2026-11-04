import os
import json
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

HERE = Path(__file__).parent
load_dotenv(HERE / ".env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"), max_retries=6)  # wait and retry when the per-minute token limit is hit
MODEL = "openai/gpt-oss-120b"

SIMULATE_TOOL_FAILURE = False


def read_policies():
    texts = []
    for path in sorted((HERE / "data" / "policies").glob("*.md")):
        texts.append(path.read_text())
    return "\n\n".join(texts)


def calculate_emi(principal, annual_rate, years):
    if SIMULATE_TOOL_FAILURE:
        raise ConnectionError("Calculator service is down")
    monthly_rate = annual_rate / 12 / 100
    months = years * 12
    growth = (1 + monthly_rate) ** months
    emi = principal * monthly_rate * growth / (growth - 1)
    return round(emi)


def calculate_fd_maturity(amount, annual_rate, years):
    if SIMULATE_TOOL_FAILURE:
        raise ConnectionError("Calculator service is down")
    maturity = amount * (1 + annual_rate / 100) ** years
    return round(maturity)


TOOL_FUNCTIONS = {
    "calculate_emi": calculate_emi,
    "calculate_fd_maturity": calculate_fd_maturity,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_emi",
            "description": "Calculate the monthly EMI for a loan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "principal": {"type": "number", "description": "Loan amount in rupees"},
                    "annual_rate": {"type": "number", "description": "Yearly interest rate in percent, for example 10.5"},
                    "years": {"type": "number", "description": "Loan tenure in years"}
                },
                "required": ["principal", "annual_rate", "years"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_fd_maturity",
            "description": "Calculate the maturity amount of a fixed deposit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Deposit amount in rupees"},
                    "annual_rate": {"type": "number", "description": "Yearly FD interest rate in percent, for example 7"},
                    "years": {"type": "number", "description": "Deposit period in years"}
                },
                "required": ["amount", "annual_rate", "years"]
            }
        }
    }
]

SYSTEM_PROMPT = f"""You are the customer assistant for Sahyadri Bank.
Use the bank policies below for all rates and rules.
For any EMI or FD maturity calculation, always use the calculator tools. Never calculate it yourself.
If the customer has not given the amount or the period, ask for it. Never invent numbers.
If a tool result starts with TOOL_ERROR, apologise and say the calculator is not available right now. Do not guess a number.
Keep answers short and clear.

BANK POLICIES:
{read_policies()}
"""


def run_tool(name, arguments):
    try:
        result = TOOL_FUNCTIONS[name](**arguments)
        return str(result)
    except Exception as error:
        return f"TOOL_ERROR: {error}"


def ask_agent(question):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    tool_log = []

    response = client.chat.completions.create(
        model=MODEL, temperature=0, messages=messages,
        tools=TOOLS, tool_choice="auto"
    )
    message = response.choices[0].message

    if not message.tool_calls:
        return message.content, tool_log

    messages.append({
        "role": "assistant",
        "content": message.content or "",
        "tool_calls": [
            {"id": call.id, "type": "function",
             "function": {"name": call.function.name, "arguments": call.function.arguments}}
            for call in message.tool_calls
        ]
    })

    for call in message.tool_calls:
        arguments = json.loads(call.function.arguments)
        result = run_tool(call.function.name, arguments)
        tool_log.append({"tool": call.function.name, "arguments": arguments, "result": result})
        messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    final = client.chat.completions.create(
        model=MODEL, temperature=0, messages=messages, tools=TOOLS
    )
    return final.choices[0].message.content, tool_log


if __name__ == "__main__":
    print("Sahyadri Bank Agent (type 'exit' to quit)")
    while True:
        question = input("You: ")
        if question == "exit":
            break
        answer, log = ask_agent(question)
        for entry in log:
            print("[TOOL]", entry["tool"], entry["arguments"], "→", entry["result"])
        print("Bot:", answer, "\n")