from typing import List
from data import SHIFTS, WEEK

def add_pad_schedule(schedule: List[List[int]]) -> List[List[int]]:
    num_csr = max([len(day) for day in schedule])
    return [
        day + [0] * (num_csr - len(day))
        for day in schedule
    ]
    
def check_requires_constraint_one_day(day_result: List[int], day_requires: List[int]) -> bool:
    """
    Intput:
        result: list of shift index
        requires: a row in REQUIRES in data.py
    Output:
        True if constraint satisfy, otherwise False
    """
    for k in day_result:
        for t, s_kt in enumerate(SHIFTS[k]):
            if s_kt == 1:
                day_requires[t] -= 1
                
    for t, requires in enumerate(day_requires):
        if requires > 0:
            raise Exception(f"Time periods {t} need more {requires} CSRs")

def check_requires_constraint_all_day(weak_result, week_requires: List[List[int]]) -> bool:
    for idx, (day_result, day_requires) in enumerate(zip(weak_result, week_requires)):
        try:
            check_requires_constraint_one_day(day_result, day_requires)
        except Exception as e:
            raise Exception(f"{WEEK[idx]} is not satisfy constraint, " + str(e))
    return weak_result