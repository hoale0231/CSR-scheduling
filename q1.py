from data import REQUIRES, SHIFTS, WEEK
from typing import List

def CSR_required_a_day(requires_day: List[int]) -> List[int]:
    """
    How many CSR is required in a day?
    Input:
        requires: a row in REQUIRES in data.py
        shifts: SHIFTS ind data.py
    Output:
        day_result: list of shift index
    """
    pass


def CSR_required_all_day(week_requires: List[List[int]]) -> List[List[int]]:
    """
    How many CSR is required in each day?
    Input:
        requires: REQUIRES in data.py
        shifts: SHIFTS ind data.py
    Output:
        result: list of day_result
    """
    return [
        [1, 1, 1, 2, 2, 2, 3, 3, 3, 6, 6, 6],
        [1, 1, 1, 2, 2, 2, 3, 3, 3, 6, 6, 6, 6],
        [1, 1, 1, 1, 2, 2, 3, 5, 5, 6, 6, 6],
        [1, 1, 1, 1, 2, 2, 2, 3, 3, 5, 5, 6, 6],
        [1, 1, 1, 2, 3, 3, 4, 6, 6, 6],
        [1, 1, 1, 2, 2, 2, 3, 5, 5, 6, 6, 6],
        [1, 1, 2, 2, 3, 3, 5, 5, 6, 6, 6]
    ]
    
    return [
        CSR_required_a_day(requires) for requires in week_requires
    ]

def check_constraint_a_day(day_result: List[int], day_requires: List[int]) -> bool:
    """
    Intput:
        result: list of shift index
        requires: a row in REQUIRES in data.py
        shifts: SHIFTS ind data.py
    Output:
        True if constraint satisfy, otherwise False
    """
    for k in day_result:
        for t, s_kt in enumerate(SHIFTS[k]):
            if s_kt == 1:
                day_requires[t] -= 1
                
    for t, requires in enumerate(day_requires):
        if requires > 0:
            print(f"Time periods {t} need more {requires} CSRs")
            return False
    return True

def check_constraint_all_day(weak_result, week_requires: List[List[int]]) -> bool:
    for idx, (day_result, day_requires) in enumerate(zip(weak_result, week_requires)):
        if not check_constraint_a_day(day_result, day_requires):
            print(WEEK[idx], "is not satisfy constraint")
            return False
    return True

if __name__ == '__main__':
    
    week_result = CSR_required_all_day(REQUIRES)
    print("Result:")
    for day, day_result in zip(WEEK, week_result):
        print(f"{day} need {sum(map(lambda x: x != 0, day_result))}, schedule: {day_result}")
    if check_constraint_all_day(week_result, REQUIRES):
        print("All OK")
