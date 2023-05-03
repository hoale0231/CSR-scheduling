import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from pulp import *
from typing import List, Tuple
import math
from time import time

from pulp_solve.q2 import CSR_required_week
from data import *
from utils import *

def CSR_fair_schedule(week_requires: List[List[int]], shifts: List[List[int]] = SHIFTS,  minimum_day_off: int = MINIMUM_DAY_OFF) -> Tuple[int, List[int], List[List[int]]]:
    # number of csr required in week
    num_csr, num_csr_each_day, week_schedule, _ = CSR_required_week(week_requires)
    start = time()
    num_workday = len(week_requires)
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
            model += sum_k == 1 # == due to we have shifts 0 is off day

    # (8)
    for i in range(num_csr):
        sum_ij = lpSum(x[(i,j,k)] for k in range(1, num_shifts) for j in range(num_workday))
        model += sum_ij <= num_workday - minimum_day_off

    # (9)
    for j in range(num_workday):
        num_time_period = len(week_requires[j])
        for t in range(num_time_period):
            sum_ik = lpSum(x[(i,j,k)] * shifts[k][t] for i in range(num_csr) for k in range(num_shifts))
            model += sum_ik >= week_requires[j][t]

    # (10)
    num_csr_each_shift = [0] * num_shifts
    for day in week_schedule:
        for shift in day:
            num_csr_each_shift[shift] += 1

    for k in range(num_shifts):
        for i in range(num_csr):
            sum_j = lpSum(x[(i,j,k)] for j in range(num_workday))
            model += math.floor(num_csr_each_shift[k] / num_csr) <= sum_j
            model += sum_j <= math.ceil(num_csr_each_shift[k] / num_csr)

    model.solve(PULP_CBC_CMD(msg=False))
    end = time()

    if model.status != LpStatusOptimal:
        raise Infeasible()


    week_schedule = [[0] * num_csr for _ in range(7)]
    for j in range(num_workday):
        for i in range(num_csr):
            for k in range(num_shifts):
                value = x[(i,j,k)].value()
                if value == 1:
                    week_schedule[j][i] = k
    week_schedule = check_maximum_onboard_day_constraint(week_schedule)
    week_schedule = check_requires_constraint_all_day(week_schedule, week_requires, shifts)
    week_schedule = check_fair_scheduling(week_schedule, shifts)

    return num_csr, num_csr_each_day, week_schedule, round(end - start, 2)

if __name__ == '__main__':
    num_csr, num_csr_each_day, week_schedule, _ = CSR_fair_schedule(REQUIRES)
    week_schedule = add_pad_schedule(week_schedule)
    for day, day_schedule in zip(WEEK, week_schedule):
        print(f"{day}, schedule: {day_schedule}")