from pulp import *
from typing import List, Tuple
import math
from time import time

from q2 import CSR_required_week
from data import REQUIRES, WEEK, SHIFTS, MINIMUM_DAY_OFF
from utils import *

def CSR_schedule(week_requires: List[List[int]]) -> Tuple[int, List[int], List[List[int]]]:
    # number of csr required in week
    num_csr, _, week_schedule = CSR_required_week(week_requires)
    num_workday = len(week_requires)
    num_shifts = len(SHIFTS)

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
        model += sum_ij <= num_workday - MINIMUM_DAY_OFF

    # (9)
    for j in range(num_workday):
        num_time_period = len(REQUIRES[j])
        for t in range(num_time_period):
            sum_ik = lpSum(x[(i,j,k)] * SHIFTS[k][t] for i in range(num_csr) for k in range(num_shifts))
            model += sum_ik >= REQUIRES[j][t]

    # (10)
    ncks = [0] * num_shifts
    for day in week_schedule:
        for shift in day:
            ncks[shift] += 1            

    for k in range(num_shifts):
        for i in range(num_csr):
            sum_j = lpSum(x[(i,j,k)] for j in range(num_workday))
            model += math.floor(ncks[k] / num_csr) <= sum_j
            model += sum_j <= math.ceil(ncks[k] / num_csr)

    start = time()
    model.solve(PULP_CBC_CMD(msg=False))
    end = time()
    
    if model.status == LpStatusOptimal:
        print(f"Optimal solution found in {round(end - start, 2)} s")
    elif model.status == LpStatusInfeasible:
        raise Exception("Problem is infeasible")
    else:
        raise Exception("Problem status: ", LpStatus[model.status])
        
    schedule = [[0] * num_csr for _ in range(7)]
    for j in range(num_workday):
        for i in range(num_csr):
            for k in range(num_shifts):
                value = x[(i,j,k)].value()
                if value == 1:
                    schedule[j][i] = k
    schedule = check_maximum_onboard_day_constraint(schedule)
    schedule = check_requires_constraint_all_day(schedule, week_requires)
    schedule = check_fair_scheduling(schedule)
    return schedule

if __name__ == '__main__':
    week_schedule = CSR_schedule(REQUIRES)
    week_schedule = add_pad_schedule(week_schedule)
    for day, day_schedule in zip(WEEK, week_schedule):
        print(f"{day}, schedule: {day_schedule}")