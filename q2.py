from typing import List, Tuple

from q1 import CSR_required_each_day
from data import REQUIRES, WEEK
from utils import check_requires_constraint_all_day, check_maximum_onboard_day_constraint, add_pad_schedule

def CSR_required_week(week_requires: List[List[int]]) -> Tuple[int, List[int], List[List[int]]]:
    """
    Find minimum CSR in a week and corresponding schedule
    Input:
        requires: REQUIRES in data.py
    Output:
        minimum_csr: int
        num_csr_each_day: [int] * 7
        week_schedule: list of day_schedule
    """
    num_csr_each_day, week_schedule = CSR_required_each_day(week_requires)
    num_csr = max([len(day) for day in week_schedule]) # max(nc_j)
    num_empty_slot = len(week_schedule) * num_csr - sum(num_csr_each_day) # nd * max(nc_j) - sum(nc_j)
    
    while num_empty_slot < num_csr:
        num_csr += 1
        num_empty_slot += 7
    
    idx_csr = 0
    for day, day_schedule in enumerate(week_schedule):
        n_empty_slot_day = num_csr - num_csr_each_day[day]
        week_schedule[day] = day_schedule[:idx_csr] + [0] * n_empty_slot_day + day_schedule[idx_csr:]
        idx_csr += n_empty_slot_day
    
    week_schedule = check_maximum_onboard_day_constraint(week_schedule)
    week_schedule = check_requires_constraint_all_day(week_schedule, week_requires)
    return num_csr, num_csr_each_day, week_schedule

if __name__ == '__main__':
    minimum_csr, num_csr_each_day, week_schedule = CSR_required_week(REQUIRES)
    week_schedule = add_pad_schedule(week_schedule)
    
    print("Minimum CSR in a week:", minimum_csr)
    for day, n_csr, day_schedule in zip(WEEK, num_csr_each_day, week_schedule):
        print(f"{day} need {n_csr}, schedule: {day_schedule}")