from docplex.mp.model import Model
from typing import List, Tuple

from utils import add_pad_schedule, check_requires_constraint_all_day
from data import REQUIRES, SHIFTS, WEEK

def schedule_one_day(requires_day: List[int]) -> List[int]:
    """
    Schedule one day with a minimum number CSRs
    Input:
        requires: a row in REQUIRES in data.py
    Output:
        day_schedule: list of shift index
    """
    num_time_period = len(requires_day)
    num_shifts = len(SHIFTS)

    # Create the optimization model
    model = Model(name='CSR Scheduling')

    # Define the decision variables
    x = {
        k: model.integer_var(lb=0, ub=max(requires_day), name=f"x_{k}")
        for k in range(num_shifts)
    }

    # Define the objective function
    model.minimize(model.sum(x[k] for k in range(num_shifts)))

    # Define the constraints
    for t in range(num_time_period):
        model.add_constraint(model.sum(x[k] * SHIFTS[k][t] for k in range(num_shifts)) >= requires_day[t])
        
    # Solve the model
    model.solve()
    
    day_schedule = []
    for k in range(num_shifts):
        n_csr = int(model.solution.get_value(x[k]))
        if n_csr > 0: 
            day_schedule += [k] * n_csr
            
    return day_schedule

def CSR_required_each_day(week_requires: List[List[int]]) -> Tuple[List[int], List[List[int]]]:
    """
    How many CSRs are required each day? and corresponding schedule
    Input:
        requires: REQUIRES in data.py
    Output:
        num_csr_each_day: [int] * 7
        week_schedule: list of day_schedule
    """
    # cplex solution
    week_schedule = [
        schedule_one_day(requires) for requires in week_requires
    ]
    
    # Sample solution
    # week_schedule = [
    #     [1, 1, 1, 2, 2, 2, 3, 3, 3, 6, 6, 6],
    #     [1, 1, 1, 2, 2, 2, 3, 3, 3, 6, 6, 6, 6],
    #     [1, 1, 1, 1, 2, 2, 3, 5, 5, 6, 6, 6],
    #     [1, 1, 1, 1, 2, 2, 2, 3, 3, 5, 5, 6, 6],
    #     [1, 1, 1, 2, 3, 3, 4, 6, 6, 6],
    #     [1, 1, 1, 2, 2, 2, 3, 5, 5, 6, 6, 6],
    #     [1, 1, 2, 2, 3, 3, 5, 5, 6, 6, 6]
    # ]
    
    num_csr_each_day = [len(day_schedule) for day_schedule in week_schedule]
    week_schedule = check_requires_constraint_all_day(week_schedule, week_requires)
    return num_csr_each_day, week_schedule

if __name__ == '__main__':
    num_csr_each_day, week_schedule = CSR_required_each_day(REQUIRES)
    week_schedule = add_pad_schedule(week_schedule)
    for day, n_csr, day_schedule in zip(WEEK, num_csr_each_day, week_schedule):
        print(f"{day} need {n_csr}, schedule: {day_schedule}")

