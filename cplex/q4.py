from docplex.mp.model import Model
from typing import List, Tuple
import math

from q2 import CSR_required_week
from data import REQUIRES, WEEK, SHIFTS
from utils import check_requires_constraint_all_day, check_maximum_onboard_day_constraint, add_pad_schedule

def CSR_schedule(week_requires: List[List[int]]) -> Tuple[int, List[int], List[List[int]]]:
    # number of csr required in week
    num_csr, _, week_schedule = CSR_required_week(week_requires)
    
    # number of work day in week
    num_workday = len(week_requires)
    num_shifts = len(SHIFTS)

    # Create the optimization model
    model = Model(name='CSR Fair Scheduling')

    NM = [(i,j,k) for i in range(num_csr) for j in range(num_workday) for k in range(num_shifts)]

    x = {}
    for i,j,k in NM:
        x[i,j,k] = model.binary_var(name=('x_' + str(i) + '_' + str(j)+ '_' + str(k)))

    # Define the objective function
    model.minimize(model.sum(x[i,j,k] for i in range(num_csr) for j in range(num_workday) for k in range(num_shifts)))

    # Define the constraints
    # (7)
    for i in range(num_csr):
        for j in range(num_workday):
            sum_k = model.sum(x[i,j,k] for k in range(num_shifts))
            model.add_constraint(sum_k <= 1)
    
    # (8)
    for i in range(num_csr):
        sum_ij = model.sum(x[i,j,k] for k in range(num_shifts) for j in range(num_workday))
        model.add_constraint(sum_ij <= num_workday-1)
    
    # (9)
    for j in range(num_workday):
        num_time_period = len(REQUIRES[j])
        for t in range(num_time_period):
            sum_ik = model.sum(x[i,j,k] * SHIFTS[k][t] for i in range(num_csr) for k in range(num_shifts))
            model.add_constraint(sum_ik >= REQUIRES[j][t])
    
    # (10)
    ncks = [0] * num_shifts
    for day in week_schedule:
        for shift in day:
            ncks[shift] += 1

    for k in range(num_shifts):
        if k == 0:
            continue
        for i in range(num_csr):
            sum_j = model.sum(x[i,j,k] for j in range(num_workday))
            model.add_constraint(math.floor(ncks[k] / num_csr) <= sum_j)
            model.add_constraint(sum_j <= math.ceil(ncks[k] / num_csr))
            
    # Week-end constraints
    num_work_weekend = 0
    for day in week_schedule[-2:]:
        for shift in day:
            if shift != 0:
                num_work_weekend += 1
    
    for i in range(num_csr):
        sum_j = model.sum(x[i,j,k] for j in [5,6] for k in range(num_shifts))
        # print(i, math.floor(num_work_weekend / num_csr), math.ceil(num_work_weekend / num_csr), sum_j)
        model.add_constraint(math.floor(num_work_weekend / num_csr) <= sum_j)
        model.add_constraint(sum_j <= math.ceil(num_work_weekend / num_csr))

    model.solve()
    
    schedule = [[0] * num_csr for i in range(7)]
    for j in range(num_workday):
        for i in range(num_csr):
            for k in range(num_shifts):
                value = model.solution.get_value(x[i,j,k])
                if value == 1:
                    schedule[j][i] = k
    schedule = check_maximum_onboard_day_constraint(schedule)
    schedule = check_requires_constraint_all_day(schedule, week_requires)
    return schedule

if __name__ == '__main__':
    week_schedule = CSR_schedule(REQUIRES)
    week_schedule = add_pad_schedule(week_schedule)
    for day, day_schedule in zip(WEEK, week_schedule):
        print(f"{day}, schedule: {day_schedule}")