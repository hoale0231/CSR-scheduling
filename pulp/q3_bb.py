from typing import List, Tuple, Dict
import math
from time import time
from copy import deepcopy

from q2 import CSR_required_week
from data import REQUIRES, WEEK, SHIFTS, MINIMUM_DAY_OFF
from utils import *

class Success(Exception):
    def __init__(self, week_schedule: List[List[int]]):
        super().__init__()
        self.week_schedule = week_schedule

class Failed(Exception):
    pass

iter = 0

def brand_and_bound(week_schedule: List[List[int]], days_count_shift: List[Dict[int, int]], lb_shift: List[int], ub_shift: List[int], i = 0, j = 0):
    global iter
    
    shift_count = [0] * len(SHIFTS)
    for i_ in range(i+1):
        shift_count[week_schedule[i_][j]] += 1
    
    for k in range(len(SHIFTS)):
        if shift_count[k] > ub_shift[k]:
            # iter += 1
            # if iter % 100_000 == 0:
            #     print('='* 20)
            #     print(i, j, k)
            #     for day, day_schedule in zip(WEEK, week_schedule):
            #         print(f"{day}, schedule: {day_schedule}")
            raise Failed()
        
    if i == len(week_schedule) - 1:
        for k in range(len(SHIFTS)):
            if shift_count[k] < lb_shift[k]:
                raise Failed()
    
    
    i += 1
    if i == len(week_schedule):
        i = 1
    if i == 1:
        j += 1
    if j == len(week_schedule[0]):
        raise Success(week_schedule)
        
    # j = (j + 1) % len(week_schedule[0])
    # i = (i + 1) if j == 0 else i
    # if i == len(week_schedule):
    #     raise Success(week_schedule)

    for k, v in days_count_shift[i].items():
        if v == 0:
            continue
        
        days_count_shift[i][k] -= 1
        week_schedule[i][j] = k
        
        try:
            brand_and_bound(week_schedule, days_count_shift, lb_shift, ub_shift, i, j)
        except Failed:
            days_count_shift[i][k] += 1
            week_schedule[i][j] = -1
            
            continue
        
    raise Failed()
    

def CSR_schedule(week_requires: List[List[int]]) -> Tuple[int, List[int], List[List[int]]]:
    # number of csr required in week
    num_csr, _, week_schedule = CSR_required_week(week_requires)
    num_workday = len(week_requires)
    num_shifts = len(SHIFTS)

    days_count_shift = []
    total_csr_in_shifts = [0] * num_shifts
    
    for day_schedule in week_schedule:
        day_count_shift = dict()
        for shift in day_schedule:
            total_csr_in_shifts[shift] += 1  
            day_count_shift[shift] = day_count_shift.get(shift, 0) + 1
        days_count_shift.append(day_count_shift)
    
    lb_shift = [math.floor(n / num_csr) for n in total_csr_in_shifts]
    ub_shift = [math.ceil(n / num_csr) for n in total_csr_in_shifts]
    
    new_week_schedule = [[-1] * num_csr for _ in week_requires]
    new_week_schedule[0] = week_schedule[0]
    print(days_count_shift)
    print(lb_shift)
    print(ub_shift)
    start = time()
    try:
        brand_and_bound(deepcopy(new_week_schedule), days_count_shift, lb_shift, ub_shift, 0, -1)
    except Success as e:
        # print(e.week_schedule)
        fair_schedule = e.week_schedule
    # except Exception as e:
    #     print(e)
    #     exit()
    end = time()
    print(f"Solve time q3 {round(end-start,2)}s")
    
    fair_schedule = check_maximum_onboard_day_constraint(fair_schedule)
    fair_schedule = check_requires_constraint_all_day(fair_schedule, week_requires)
    fair_schedule = check_fair_scheduling(fair_schedule)
    return fair_schedule


if __name__ == '__main__':
    week_schedule = CSR_schedule(REQUIRES)
    week_schedule = add_pad_schedule(week_schedule)
    for day, day_schedule in zip(WEEK, week_schedule):
        print(f"{day}, schedule: {day_schedule}")