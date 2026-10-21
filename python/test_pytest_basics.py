from checks import check_answer, is_short

def test_answer_contains_keyword():
    answer = "The rate is 10.5% per year"
    assert check_answer(answer,"10.5%") == "PASS"

def test_answer_missing_keyword():
    answer = "There is no penalty for early closure"
    assert check_answer(answer, "1%") == "PASS"

def test_short_answer():
    assert is_short("The annual fee is 500 rupees") == True

def test_long_answer_is_not_short():
    long_answer =(
        "Thank you for your question.The personal loan interest rate at our bank"
        "is 10.5% per year for salaried customers, and it may vary for"
        "self-employed customers depending on their income and credit history"
    )
    assert is_short(long_answer) == False

import pytest

@pytest.mark.parametrize("answer, keyword, expected",
[
    ("The rate is 10.5% per year","10.5%","PASS"),
    ("FD early closure has a 1% penalty","1%","PASS"),
    ("The annual fee is 500 rupees.","500","PASS"),
    ("There is no penalty","1%","FAIL"),
    ("The minimum balance is 5000 rupees.","5000","PASS"),
])

def test_check_answer_many(answer, keyword, expected):
    assert check_answer(answer, keyword) == expected