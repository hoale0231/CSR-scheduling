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

def CSR_fair_weekend_schedule(week_requires: List[List[int]], shifts: List[List[int]] = SHIFTS,  minimum_day_off: int = MINIMUM_DAY_OFF) -> Tuple[int, List[int], List[List[int]]]:
    # number of csr required in week
    num_csr, num_csr_each_day, week_schedule, _ = CSR_required_week(week_requires)
    start = time()
    
    num_workday = len(week_requires)
    num_shifts = len(SHIFTS)

    # Create the optimization model
    model = LpProblem('CSR_Fair_weekend_Scheduling', LpMinimize)

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

    # (9):  thay ràng buộc CSR phải đáp ứng đủ số lượng yêu cầu tại mỗi khung thời gian trong một ngày
    #       bằng ràng buộc các shift trong 1 ngày phải trùng với Q1 
    #       (vì Q1 đã thỏa điều kiện đủ KPI nên Q3 chỉ cần sắp xếp lại lịch cho thỏa các ràng buộc khác là được)
    count_shift_each_day = [dict() for _ in range(num_workday)]
    num_csr_each_shift = [0] * num_shifts
    for j, day in enumerate(week_schedule):
        for shift in day:
            num_csr_each_shift[shift] += 1
            count_shift_each_day[j][shift] = count_shift_each_day[j].get(shift, 0) + 1
    
    for j, count_shift_day in enumerate(count_shift_each_day):
        for k, count_k in count_shift_day.items():
            sum_i = lpSum(x[(i,j,k)] for i in range(num_csr))
            model += sum_i == count_k

    # (10)
    for k in range(num_shifts):
        for i in range(num_csr):
            sum_j = lpSum(x[(i,j,k)] for j in range(num_workday))
            model += math.floor(num_csr_each_shift[k] / num_csr) <= sum_j
            model += sum_j <= math.ceil(num_csr_each_shift[k] / num_csr)

    # Week-end constraints
    num_work_weekend = 0
    for day in week_schedule[-2:]:
        for shift in day:
            if shift != 0:
                num_work_weekend += 1
    
    for i in range(num_csr):
        sum_j = lpSum(x[i,j,k] for j in [5,6] for k in range(1, num_shifts))
        model += math.floor(num_work_weekend / num_csr) <= sum_j
        model += sum_j <= math.ceil(num_work_weekend / num_csr)

    model.solve(PULP_CBC_CMD(msg=False))
    end = time()

    if model.status != LpStatusOptimal:
        raise Infeasible()

    week_schedule = [[0] * num_csr for i in range(7)]
    for j in range(num_workday):
        for i in range(num_csr):
            for k in range(num_shifts):
                value = x[(i,j,k)].value()
                if value == 1:
                    week_schedule[j][i] = k
    week_schedule = check_maximum_onboard_day_constraint(week_schedule)
    week_schedule = check_requires_constraint_all_day(week_schedule, week_requires, shifts)
    week_schedule = check_fair_scheduling(week_schedule, shifts)
    week_schedule = check_fair_weekend_scheduling(week_schedule)
    return num_csr, num_csr_each_day, week_schedule, round(end - start, 2)

if __name__ == '__main__':
    num_csr, num_csr_each_day, week_schedule, _, _ = CSR_fair_weekend_schedule(REQUIRES)
    week_schedule = add_pad_schedule(week_schedule)
    for day, day_schedule in zip(WEEK, week_schedule):
        print(f"{day}, schedule: {day_schedule}")