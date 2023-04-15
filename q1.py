from docplex.mp.model import Model
from typing import List

from utils import add_pad_schedule, check_requires_constraint_all_day
from data import REQUIRES, SHIFTS, WEEK

def CSR_required_one_day(requires_day: List[int]) -> List[int]:
    """
    How many CSR is required in a day?
    Input:
        requires: a row in REQUIRES in data.py
    Output:
        day_result: list of shift index
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
    
    result = []
    for k in range(num_shifts):
        n_csr = int(model.solution.get_value(x[k]))
        if n_csr > 0: 
            result += [k] * n_csr
            
    return result

def CSR_required_each_day(week_requires: List[List[int]]) -> List[List[int]]:
    """
    How many CSR is required in each day?
    Input:
        requires: REQUIRES in data.py
    Output:
        result: list of day_result
    """
    # cplex solution
    week_result = add_pad_schedule([
        CSR_required_one_day(requires) for requires in week_requires
    ])

    # Sample solution
    # week_result = add_pad_schedule([
    #     [1, 1, 1, 2, 2, 2, 3, 3, 3, 6, 6, 6],
    #     [1, 1, 1, 2, 2, 2, 3, 3, 3, 6, 6, 6, 6],
    #     [1, 1, 1, 1, 2, 2, 3, 5, 5, 6, 6, 6],
    #     [1, 1, 1, 1, 2, 2, 2, 3, 3, 5, 5, 6, 6],
    #     [1, 1, 1, 2, 3, 3, 4, 6, 6, 6],
    #     [1, 1, 1, 2, 2, 2, 3, 5, 5, 6, 6, 6],
    #     [1, 1, 2, 2, 3, 3, 5, 5, 6, 6, 6]
    # ])
    
    return check_requires_constraint_all_day(week_result, week_requires)

if __name__ == '__main__':
    week_result = CSR_required_each_day(REQUIRES)
    for day, day_result in zip(WEEK, week_result):
        print(f"{day} need {sum(map(lambda x: x != 0, day_result))}, schedule: {day_result}")

