from pulp_solve.q1 import CSR_required_each_day as q1
from pulp_solve.q2 import CSR_required_week as q2
from pulp_solve.q3 import CSR_fair_schedule as q3
from pulp_solve.q3_replace import CSR_fair_schedule as q3_replace
from pulp_solve.q3_group import CSR_fair_schedule as q3_group
from pulp_solve.q4 import CSR_fair_weekend_schedule as q4
from pulp_solve.q4_replace import CSR_fair_weekend_schedule as q4_replace
from pulp_solve.q4_group import CSR_fair_weekend_schedule as q4_group
from utils import *

import random
import resource
import numpy as np
import timeout_decorator
from utils import add_pad_schedule
import time
import psutil

class TimeOut(Exception):
    pass
    
def limit_memory(maxsize):
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (maxsize, hard))

def random_requires(min, max):
    return [[random.randint(min, max) for _ in range(13)] for _ in range(7)]

@timeout_decorator.timeout(200, timeout_exception=TimeOut)
def run(requires, func):
    return func(requires)
     
if __name__ == '__main__':
    list_func = [q1, q2, q3, q3_replace, q3_group, q4, q4_replace, q4_group]
    list_func_name = ['q1', 'q2', 'q3', 'q3_replace', 'q3_group', 'q4', 'q4_replace', 'q4_group']
    min_max = [
        [0, 10],
        [10, 100],
        [100, 1000],
        [1000, 5000],
        [5000, 10000],
    ]
    
    with open('result_shift1.csv', 'w') as fw:
        print('min_max_n,func,n_csr,obj,runtime', file=fw)
    for min, max in min_max:
        for i in range(1, 4):
            for func, func_name in zip(list_func, list_func_name):
                # requires = random_requires(min, max)
                # with open(f'test_case/{min}_{max}_{i}.in', 'w') as fl:
                #     fl.write('\n'.join([' '.join(map(str, day)) for day in requires]))
                requires = read_requires(f'test_case/{min}_{max}_{i}.in')
                time.sleep(1)
                try:
                    print(f"Running {min} {max} {i} {func.__name__}")
                    limit_memory(8 * (1024 ** 3))
                    output = run(requires, func)
                    
                    # Parse output Q1
                    if len(output) == 3:
                        num_csr_each_day, schedule, runtime = output
                        obj = np.sum(np.array(add_pad_schedule(schedule)) > 0)
                        print(f"{min}_{max}_{i}", func_name, '', obj, runtime, sep=',', file=open('result_shift1.csv', 'a'))
                    # Parse output Q2, Q3, Q4
                    elif len(output) == 4:
                        num_csr, num_csr_each_day, schedule, runtime = output
                        obj = np.sum(np.array(schedule) > 0)
                        print(f"{min}_{max}_{i}", func_name,num_csr, obj, runtime, sep=',', file=open('result_shift1.csv', 'a'))
                    
                    # Print result
                    with open(f'test_case/{min}_{max}_{i}_{func_name}_shift1.out', 'w') as fw:
                        for day, n_csr, day_schedule in zip(WEEK, num_csr_each_day, schedule):
                            print(f"{day} need {n_csr}, schedule: {day_schedule}", file=fw)
                except MemoryError as me:
                    print(f"{min}_{max}_{i}", func_name, '', '', 'memoryout', sep=',', file=open('result_shift1.csv', 'a'))
                except TimeOut as te:
                    print(f"{min}_{max}_{i}", func_name, '', '', 'timeout', sep=',', file=open('result_shift1.csv', 'a'))
                except Infeasible as ie:
                    print(f"{min}_{max}_{i}", func_name, '', '', 'infeasible', sep=',', file=open('result_shift1.csv', 'a'))
                except Exception as e:
                    print(f"{min}_{max}_{i}", func_name, '', '', 'error', e, sep=',', file=open('result_shift1.csv', 'a'))
                for proc in psutil.process_iter():
                    if proc.name() == "cbc":
                        proc.kill()


