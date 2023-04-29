import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from pulp import *
from typing import List, Dict, Tuple
import math
from time import time, process_time

from pulp_solve.q2 import CSR_required_week
from data import REQUIRES, WEEK, SHIFTS, MINIMUM_DAY_OFF
from utils import *

def CSR_schedule_split(num_csr: int, count_shift_each_day: List[Dict[int, int]], shifts: List[List[int]] = SHIFTS,  minimum_day_off: int = MINIMUM_DAY_OFF) -> List[List[int]]:
    # number of csr required in week
    num_workday = len(WEEK)
    num_shifts = len(shifts)

    # Create the optimization model
    model = LpProblem('CSR_Fair_Scheduling', LpMinimize)

    NM = [(i,j,k) for i in range(num_csr) for j in range(num_workday) for k in range(num_shifts)]

    x = LpVariable.dicts('x', NM, 0, 1, LpBinary)

    # Define the objective function
    model += lpSum(x[(i,j,k)] for i in range(num_csr) for j in range(num_workday) for k in range(1, num_shifts))

    # Define the constraints
    # (7)
    for i in range(num_csr):
        for j in range(num_workday):
            sum_k = lpSum(x[(i,j,k)] for k in range(num_shifts))
            model += sum_k == 1

    # (8)
    for i in range(num_csr):
        sum_ij = lpSum(x[(i,j,k)] for k in range(1, num_shifts) for j in range(num_workday))
        model += sum_ij <= num_workday - minimum_day_off
    
    # (9)
    count_shift_week = [0] * num_shifts

    for count_shift in count_shift_each_day:
        for k, count in count_shift.items():
            count_shift_week[k] += count

    for j, count_shift_day in enumerate(count_shift_each_day):
        for k, count_k in count_shift_day.items():
            sum_i = lpSum(x[(i,j,k)] for i in range(num_csr))
            model += sum_i == count_k
    
    # (10)
    for k in range(num_shifts):
        for i in range(num_csr):
            sum_j = lpSum(x[(i,j,k)] for j in range(num_workday))
            model += math.floor(count_shift_week[k] / num_csr) <= sum_j
            model += sum_j <= math.ceil(count_shift_week[k] / num_csr)
            
    # Week-end constraints
    num_work_weekend = 2 * num_csr
    for count_shift in count_shift_each_day[-2:]:
        num_work_weekend -= count_shift.get(0, 0)
    
    for i in range(num_csr):
        sum_j = lpSum(x[i,j,k] for j in [5,6] for k in range(1, num_shifts))
        model += math.floor(num_work_weekend / num_csr) <= sum_j
        model += sum_j <= math.ceil(num_work_weekend / num_csr)

    model.solve(PULP_CBC_CMD(msg=False))

    if model.status != LpStatusOptimal:
        raise Infeasible()


    week_schedule = [[0] * num_csr for _ in range(7)]
    for j in range(num_workday):
        for i in range(num_csr):
            for k in range(num_shifts):
                value = x[(i,j,k)].value()
                if value == 1:
                    week_schedule[j][i] = k

    return week_schedule

def group_CSR_schedule(csr_each_group: List[int], week_schedule: List[List[int]], week_requires: List[List[int]], shifts: List[List[int]] = SHIFTS,  minimum_day_off: int = MINIMUM_DAY_OFF) -> List[List[int]]:
    # number of csr required in week
    num_group = len(csr_each_group)
    num_csr = len(week_schedule[0])
    num_workday = len(week_requires)
    num_shifts = len(shifts)

    # Create the optimization model
    model = LpProblem('CSR_Fair_Scheduling', LpMinimize)

    NM = [(i,j,k) for i in range(num_group) for j in range(num_workday) for k in range(num_shifts)]

    x = LpVariable.dicts('x', NM, 0, max(csr_each_group), LpInteger)

    # Define the objective function
    model += lpSum(x[(i,j,k)] for i in range(num_group) for j in range(num_workday) for k in range(1, num_shifts))

    # Define the constraints
    # (7)
    for i in range(num_group):
        for j in range(num_workday):
            sum_k = lpSum(x[(i,j,k)] for k in range(num_shifts))
            model += sum_k == csr_each_group[i]

    # (8)
    for i in range(num_group):
        sum_ij = lpSum(x[(i,j,k)] for k in range(1, num_shifts) for j in range(num_workday))
        model += sum_ij <= (num_workday - minimum_day_off) * csr_each_group[i]

    # (9)
    for j in range(num_workday):
        num_time_period = len(week_requires[j])
        for t in range(num_time_period):
            sum_ik = lpSum(x[(i,j,k)] * shifts[k][t] for i in range(num_group) for k in range(num_shifts))
            model += sum_ik >= week_requires[j][t]

    # (10)
    ncks = [0] * num_shifts
    for day in week_schedule:
        for shift in day:
            ncks[shift] += 1
    
    for k in range(num_shifts):
        for i in range(num_group):
            sum_j = lpSum(x[(i,j,k)] for j in range(num_workday))
            model += math.floor(ncks[k] / num_csr) * csr_each_group[i] <= sum_j
            model += sum_j <= math.ceil(ncks[k] / num_csr) * csr_each_group[i]
    
    # Week-end constraints
    num_work_weekend = 0
    for day in week_schedule[-2:]:
        for shift in day:
            if shift != 0:
                num_work_weekend += 1

    for i in range(num_group):
        sum_j = lpSum(x[i,j,k] for j in [5,6] for k in range(1, num_shifts))
        model += math.floor(num_work_weekend / num_csr) * csr_each_group[i] <= sum_j
        model += sum_j <= math.ceil(num_work_weekend / num_csr) * csr_each_group[i]
        
    model.solve(PULP_CBC_CMD(msg=False))

    if model.status != LpStatusOptimal:
        raise Infeasible()


    group_schedule = [[dict() for _ in range(num_workday)] for _ in range(num_group)]
    
    for i in range(num_group):
        for j in range(num_workday):
            for k in range(num_shifts):
                value = x[(i,j,k)].value()
                if value > 0:
                    group_schedule[i][j][k] = int(value)

    return group_schedule

def CSR_fair_weekend_schedule(week_requires: List[List[int]], n_split: int = -1, shifts: List[List[int]] = SHIFTS,  minimum_day_off: int = MINIMUM_DAY_OFF) -> Tuple[int, List[int], List[List[int]], float]:
    # number of csr required in week
    num_csr, num_csr_each_day, week_schedule, _, _ = CSR_required_week(week_requires)
    num_workday = len(week_requires)
    
    start = time()
    start_cpu = process_time()
    if n_split == -1:
        n_split = num_csr // 1000 + 1
    
    # Split csr to group
    lb_csr = num_csr // n_split
    ub_csr = lb_csr + 1
    n_ub = num_csr - n_split * lb_csr
    n_lb = n_split - n_ub 
    csr_each_group = n_lb * [lb_csr] + n_ub * [ub_csr]
    
    # Split shift to group
    splited_schedule = group_CSR_schedule(csr_each_group, week_schedule, week_requires, shifts, minimum_day_off)
    
    # Schedule each group
    splited_schedule = [
        CSR_schedule_split(n_csr, split, shifts, minimum_day_off) 
        for n_csr, split in zip(csr_each_group, splited_schedule)
    ]
    
    # Merge solution
    week_schedule = [sum(map(lambda x: x[day], splited_schedule), []) for day in range(num_workday)]
    end_cpu = process_time()
    end = time()

    # Check constraint
    week_schedule = check_maximum_onboard_day_constraint(week_schedule)
    week_schedule = check_requires_constraint_all_day(week_schedule, week_requires, shifts)
    week_schedule = check_fair_scheduling(week_schedule, shifts)
    week_schedule = check_fair_weekend_scheduling(week_schedule)
    return num_csr, num_csr_each_day, week_schedule, round(end - start, 2), round(end_cpu - start_cpu, 2)

if __name__ == '__main__':
    num_csr, num_csr_each_day, week_schedule, _, _ = CSR_fair_weekend_schedule(REQUIRES)
    # week_schedule = add_pad_schedule(week_schedule)
    # for day, day_schedule in zip(WEEK, week_schedule):
    #     print(f"{day}, schedule: {day_schedule}")
