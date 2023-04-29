from pulp import *
from typing import List, Tuple
import math
from time import time, process_time
import numpy as np

from q2 import CSR_required_week
from data import REQUIRES, WEEK, SHIFTS, MINIMUM_DAY_OFF
from utils import *

def CSR_schedule_split(week_schedule: List[List[int]], shifts: List[List[int]] = SHIFTS,  minimum_day_off: int = MINIMUM_DAY_OFF) -> Tuple[int, List[int], List[List[int]]]:
    # number of csr required in week
    num_csr = len(week_schedule[0])
    num_workday = len(week_schedule)
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
    count_shift_each_day = [dict() for _ in range(num_workday)]
    for j, day in enumerate(week_schedule):
        for shift in day:
            count_shift_week[shift] += 1
            count_shift_each_day[j][shift] = count_shift_each_day[j].get(shift, 0) + 1

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

    model.solve(PULP_CBC_CMD(msg=False))

    if model.status == LpStatusOptimal:
        pass
    elif model.status == LpStatusInfeasible:
        raise Exception("Problem is infeasible")
    else:
        raise Exception("Problem status: ", LpStatus[model.status])

    week_schedule = [[0] * num_csr for _ in range(7)]
    for j in range(num_workday):
        for i in range(num_csr):
            for k in range(num_shifts):
                value = x[(i,j,k)].value()
                if value == 1:
                    week_schedule[j][i] = k

    return week_schedule

def split_schedule(week_schedule: List[int], n_split: int):
    week_schedule = np.array(week_schedule)
    splited_schedule = [[] for _ in range(n_split)]
    
    idx_split = 0
    for i in range(len(week_schedule[0])):
        splited_schedule[idx_split].append(week_schedule[:,i])
        idx_split = (idx_split + 1) % n_split
    splited_schedule = [np.transpose(np.stack(split)) for split in splited_schedule]
    return splited_schedule
    

def CSR_schedule(week_requires: List[List[int]], shifts: List[List[int]] = SHIFTS,  minimum_day_off: int = MINIMUM_DAY_OFF, n_split: int = 1000) -> Tuple[int, List[int], List[List[int]]]:
    # number of csr required in week
    num_csr, num_csr_each_day, week_schedule, _ = CSR_required_week(week_requires)
    num_workday = len(week_requires)

    start = time()
    start_cpu = process_time()
    splited_schedule =  split_schedule(week_schedule, n_split)
    splited_schedule = [
        CSR_schedule_split(split, shifts, minimum_day_off) 
        for split in splited_schedule
    ]
    end_cpu = process_time()
    end = time()
    
    week_schedule = [sum(map(lambda x: x[day], splited_schedule), []) for day in range(num_workday)]

    week_schedule = check_maximum_onboard_day_constraint(week_schedule)
    week_schedule = check_requires_constraint_all_day(week_schedule, week_requires, shifts)
    week_schedule = check_fair_scheduling(week_schedule, shifts)

    return num_csr, num_csr_each_day, week_schedule, round(end - start, 2), round(end_cpu - start_cpu, 2)

if __name__ == '__main__':
    num_csr, num_csr_each_day, week_schedule, _, _ = CSR_schedule(REQUIRES)
    # week_schedule = add_pad_schedule(week_schedule)
    # for day, day_schedule in zip(WEEK, week_schedule):
    #     print(f"{day}, schedule: {day_schedule}")