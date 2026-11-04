import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.append(str(HERE.parent / "chatbot"))
# pyrefly: ignore[missing-import]
import agent_bot
# pyrefly: ignore[missing-import]
from agent_bot import ask_agent, calculate_emi


def tools_used(tool_log):
    return [entry["tool"] for entry in tool_log]


def digits_only(text):
    return text.replace(",", "")


def test_uses_emi_tool_with_right_inputs():
    time.sleep(2)
    answer, log = ask_agent("I want a loan of ₹5,00,000 at 10.5% for 5 years. What will my EMI be?")
    print("\n", answer, log)
    assert tools_used(log) == ["calculate_emi"]
    args = log[0]["arguments"]
    assert args["principal"] == 500000
    assert args["annual_rate"] == 10.5
    assert args["years"] == 5
    expected = calculate_emi(500000, 10.5, 5)
    assert str(expected) in digits_only(answer)


def test_uses_policy_rate():
    time.sleep(2)
    answer, log = ask_agent("I am salaried. I want a personal loan of 200000 Rs. for 3 years. What will my EMI be?")
    print("\n", answer, log)
    assert tools_used(log) == ["calculate_emi"]
    assert log[0]["arguments"]["annual_rate"] == 10.5


def test_picks_fd_tool_not_emi():
    time.sleep(2)
    answer, log = ask_agent("I want to put 1,00,000 Rs. in an FD for 2 years. How much will I get at maturity?")
    print("\n", answer, log)
    assert tools_used(log) == ["calculate_fd_maturity"]
    assert log[0]["arguments"]["annual_rate"] == 7


def test_no_tool_for_simple_question():
    time.sleep(2)
    answer, log = ask_agent("What is the home loan interest rate?")
    print("\n", answer, log)
    assert log == []
    assert "8.5%" in answer


def test_asks_for_missing_details():
    time.sleep(2)
    answer, log = ask_agent("What will my EMI be?")
    print("\n", answer, log)
    assert log == [], f"Called a tool with invented numbers: {log}"


def test_fails_safely_when_tool_breaks():
    time.sleep(2)
    real_emi = calculate_emi(500000, 10.5, 5)
    agent_bot.SIMULATE_TOOL_FAILURE = True
    try:
        answer, log = ask_agent("I want a loan of ₹5,00,000 at 10.5% for 5 years. What will my EMI be?")
    finally:
        agent_bot.SIMULATE_TOOL_FAILURE = False
    print("\n", answer, log)
    assert log and log[0]["result"].startswith("TOOL_ERROR")
    assert str(real_emi) not in digits_only(answer), "Agent guessed after the tool failed"
