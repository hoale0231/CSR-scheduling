from pulp_solve.q1 import CSR_required_each_day as q1
from pulp_solve.q2 import CSR_required_week as q2
from pulp_solve.q3 import CSR_fair_schedule as q3
from pulp_solve.q4 import CSR_fair_weekend_schedule as q4
from pulp_solve.q3_group import CSR_fair_schedule as q3_group
from pulp_solve.q4_group import CSR_fair_weekend_schedule as q4_group
from utils import Infeasible

import random
import signal
import resource

def time_exceeded(signo, frame):
    raise SystemExit(1)
  
def set_max_runtime(seconds):
    soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
    resource.setrlimit(resource.RLIMIT_CPU, (seconds, hard))
    signal.signal(signal.SIGXCPU, time_exceeded)
    
def limit_memory(maxsize):
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (maxsize, hard))

def random_input(min, max):
    return [[random.randint(min, max) for _ in range(13)] for _ in range(7)]
     
if __name__ == '__main__':
    list_func = [q1, q2, q3, q3_group, q4, q4_group]
    list_func_name = ['q1', 'q2', 'q3', 'q3_group', 'q4', 'q4_group']
    min_max = [
        [0, 10],
        [10, 100],
        [100, 1000],
        [1000, 10000],
        [10000, 100000],
    ]
    with open('result.csv', 'w') as fw:
        print('min,max,n,n_csr,time,runtime', file=fw)

    for min, max in min_max:
        for i in range(5):
            requires = random_input(min, max)
            with open(f'log/{min}_{max}_{i}.log', 'w') as fl:
                fl.write('\n'.join([' '.join(map(str, day)) for day in requires]))
            for func, func_name in zip(list_func, list_func_name):
                try:
                    print(f"Running {min} {max} {i} {func.__name__}")
                    set_max_runtime(1)
                    limit_memory(8 * (1024 ** 3))
                    output = func(requires)
                    if len(output) == 4:
                        _, _, time, cputime = output
                        print(min, max, i, func_name,'', time, cputime, sep=',', file=open('result.csv', 'a'))
                    elif len(output) == 5:
                        num_csr, _, _, time, cputime = output
                        print(min, max, i, func_name,num_csr, time, cputime, sep=',', file=open('result.csv', 'a'))
                except MemoryError as me:
                    print(min, max, i, func_name,'', 'memory out', 'memory out', sep=',', file=open('result.csv', 'a'))
                except SystemExit as se:
                    print(min, max, i, func_name,'', 'time out', 'time out', sep=',', file=open('result.csv', 'a'))
                except Infeasible as ie:
                    print(min, max, i, func_name,'', 'infeasible', 'infeasible', sep=',', file=open('result.csv', 'a'))
                except Exception as e:
                    print(min, max, i, func_name,'', 'error', e, sep=',', file=open('result.csv', 'a'))

