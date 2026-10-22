def check_answer(answer, expected_keyword):
    if expected_keyword in answer:
        return "PASS"
    else:
        return "FAIL"


def is_short(answer):
    return len(answer.split()) < 20
