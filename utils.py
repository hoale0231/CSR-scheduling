from typing import List
from data import SHIFTS, WEEK, MINIMUM_DAY_OFF

def add_pad_schedule(schedule: List[List[int]]) -> List[List[int]]:
    num_csr = max([len(day) for day in schedule])
    return [
        day + [0] * (num_csr - len(day))
        for day in schedule
    ]
    
def check_requires_constraint_one_day(day_schedule: List[int], day_requires: List[int]) -> List[List[int]]:
    """
    Check requires constraint one day
    Intput:
        day_schedule: list of shift index
        requires: a row in REQUIRES in data.py
    """
    for k in day_schedule:
        for t, s_kt in enumerate(SHIFTS[k]):
            if s_kt == 1:
                day_requires[t] -= 1
                
    for t, requires in enumerate(day_requires):
        if requires > 0:
            raise Exception(f"time periods {t} need more {requires} CSRs")

def check_requires_constraint_all_day(week_schedule: List[List[int]], week_requires: List[List[int]]) -> bool:
    """
    Check requires constraint each day
    Intput:
        week_schedule: list of day_schedule
        requires: REQUIRES in data.py
    Output:
        Return week_schedule if it satisfy constraint, otherwise raise error
    """
    for idx, (day_result, day_requires) in enumerate(zip(week_schedule, week_requires)):
        try:
            check_requires_constraint_one_day(day_result, day_requires)
        except Exception as e:
            str_week_schedule = ""
            for day, day_schedule in zip(WEEK, week_schedule):
                str_week_schedule += f"{day}: {day_schedule}\n"
            raise Exception(f"{WEEK[idx]} is not satisfy constraint, {str(e)}\nSchedule:\n{str_week_schedule}FAIL!!")
    return week_schedule

def check_maximum_onboard_day_constraint(week_schedule: List[List[int]]):
    num_csr = max([len(day) for day in week_schedule])
    day_work_of_csr = [0] * num_csr
    for day_schedule in week_schedule:
        for csr, shift in enumerate(day_schedule):
            if shift != 0:
                day_work_of_csr[csr] += 1
    if any([day_work > (len(WEEK) - MINIMUM_DAY_OFF) for day_work in day_work_of_csr]):
        str_week_schedule = ""
        for day, day_schedule in zip(WEEK, week_schedule):
           str_week_schedule += f"{day}: {day_schedule}\n"
        raise Exception(f"Have a CSR work more than {len(WEEK) - MINIMUM_DAY_OFF} days: {day_work_of_csr}\nSchedule:\n{str_week_schedule}FAIL!!")
    return week_schedule
