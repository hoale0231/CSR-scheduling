import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from pulp import *
from typing import List, Tuple
from time import time

from utils import *
from data import *

def schedule_one_day(requires_day: List[int], shifts: List[List[int]]) -> List[int]:
    """
    Schedule one day with a minimum number CSRs
    Input:
        requires: a row in REQUIRES in data.py
    Output:
        day_schedule: list of shift index
    """
    num_time_period = len(requires_day)
    num_shifts = len(shifts)

    # Create the optimization model
    model = LpProblem(name='CSR_Scheduling', sense=LpMinimize)

    # Define the decision variables
    x = LpVariable.dicts('x', [k for k in range(num_shifts)], 0, max(requires_day), LpInteger)

    # Define the objective function
    model += lpSum(x[k] for k in range(num_shifts))

    # Define the constraints
    for t in range(num_time_period):
        model += lpSum(x[k] * shifts[k][t] for k in range(num_shifts)) >= requires_day[t]

    # Solve the model
    model.solve(PULP_CBC_CMD(msg=False))

    day_schedule = []
    for k in range(num_shifts):
        n_csr = int(x[k].value())
        if n_csr > 0:
            day_schedule += [k] * n_csr

    return day_schedule

def CSR_required_each_day(week_requires: List[List[int]], shifts: List[List[int]] = SHIFTS) -> Tuple[List[int], List[List[int]]]:
    """
    How many CSRs are required each day? and corresponding schedule
    Input:
        requires: REQUIRES in data.py
    Output:
        num_csr_each_day: [int] * 7
        week_schedule: list of day_schedule
    """
    # cplex solution
    start = time()
    week_schedule = [
        schedule_one_day(requires, shifts) for requires in week_requires
    ]
    end = time()

    num_csr_each_day = [len(day_schedule) for day_schedule in week_schedule]
    week_schedule = check_requires_constraint_all_day(week_schedule, week_requires, shifts)
    return num_csr_each_day, week_schedule, round(end - start, 2)

if __name__ == '__main__':
    num_csr_each_day, week_schedule, runtime = CSR_required_each_day(REQUIRES)
    week_schedule = add_pad_schedule(week_schedule)
    for day, n_csr, day_schedule in zip(WEEK, num_csr_each_day, week_schedule):
        print(f"{day} need {n_csr}, schedule: {day_schedule}")

