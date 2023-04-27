from typing import List, Tuple

from q1 import CSR_required_each_day
from data import REQUIRES, WEEK, MINIMUM_DAY_OFF
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
    num_csr_each_day, week_schedule = CSR_required_each_day(week_requires) # nc, week_schedule = [nc_1, nc_2, ..., nc_J], week_schedule
    num_csr = max([len(day) for day in week_schedule]) # I = max(nc_j)
    num_empty_slot = len(week_schedule) * num_csr - sum(num_csr_each_day) # ne = nd * max(nc_j) - sum(nc_j)

    # While we increase num_csr by 1, ne increse 7 => we just increase until ne > num_scr
    while num_empty_slot < num_csr * MINIMUM_DAY_OFF:
        num_csr += 1
        num_empty_slot += len(WEEK)

    # Greedy Scheduling: we allocate days off to CSR sequentially
    """
    Example: If we have 5 CSR and
            - mon have 3 empty slot
            - tue have 1 empty slot
            - wed have 2 empty slot
    Greedy algorithms example:
        idx_shift = 0

        Iter 1:
        Mon: [1,2]     add 3 empty slot -> [0,0,0,1,2] shift right 0 -> [0,0,0,1,2] --- idx_shift = (idx_shift + 3) % num_csr = 3

        Iter 2:
        Tue: [1,2,3,4] add 1 empty slot -> [0,1,2,3,4] shift right 3 -> [2,3,4,0,1] --- idx_shift = (idx_shift + 1) % num_csr = 4

        Iter 3:
        Wed: [1,2,3]   add 2 empty slot -> [0,0,1,2,3] shift right 4 -> [0,1,2,3,0] --- idx_shift = (idx_shift + 2) % num_csr = 1
        ...
    """
    idx_csr = 0
    for day, day_schedule in enumerate(week_schedule):
        n_empty_slot_day = num_csr - num_csr_each_day[day]
        day_schedule = [0] * n_empty_slot_day + day_schedule
        week_schedule[day] = day_schedule[-idx_csr:] + day_schedule[:-idx_csr]
        idx_csr = (idx_csr + n_empty_slot_day) % num_csr

    week_schedule = check_maximum_onboard_day_constraint(week_schedule)
    week_schedule = check_requires_constraint_all_day(week_schedule, week_requires)
    return num_csr, num_csr_each_day, week_schedule

if __name__ == '__main__':
    minimum_csr, num_csr_each_day, week_schedule = CSR_required_week(REQUIRES)
    week_schedule = add_pad_schedule(week_schedule)

    print("Minimum CSR in a week:", minimum_csr)
    for day, n_csr, day_schedule in zip(WEEK, num_csr_each_day, week_schedule):
        print(f"{day} need {n_csr}, schedule: {day_schedule}")