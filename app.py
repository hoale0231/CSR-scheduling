import tkinter as tk
from tkinter import *
import tkinter.scrolledtext as tkscrolled
from utils import add_pad_schedule
import random
from pulp_solve.q1 import CSR_required_each_day as q1
from pulp_solve.q2 import CSR_required_week as q2
from pulp_solve.q3 import CSR_fair_schedule as q3
from pulp_solve.q4 import CSR_fair_weekend_schedule as q4

ws = tk.Tk()
ws.title("CSR Scheduler")

title1 = tk.Label(ws, text="Requires", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan= 3)

input_text1 = tk.Text(ws, width=75, height=10)
input_text1.grid(row=1, column=0, padx=5, pady=5, columnspan=3)

title2 = tk.Label(ws, text="Shifts", font=('Helvetica', 12, 'bold')).grid(row=0, column=3, columnspan= 2)

input_text2 = tk.Text(ws, width=50, height=10)
input_text2.grid(row=1, column=3, padx=5, pady=5, columnspan=2)

# title3 = tk.Label(ws, text="Week", font=('Helvetica', 12, 'bold')).grid(row=2, column=0)
# listbox3 = tk.Listbox(ws, width=10, height=7, exportselection=0, selectmode="multiple")
# listbox3.insert(1, "Monday")
# listbox3.insert(2, "Tuesday")
# listbox3.insert(3, "Wednesday")
# listbox3.insert(4, "Thursday")
# listbox3.insert(5, "Friday")
# listbox3.insert(6, "Saturday")
# listbox3.insert(7, "Sunday")
# listbox3.select_set(0, 6)
# listbox3.grid(row=3, column=0, padx=5, pady=5)


listbox = tk.Listbox(ws, width=20, height=4, exportselection=0)
listbox.insert(1, "Question 1")
listbox.insert(2, "Question 2")
listbox.insert(3, "Question 3")
listbox.insert(4, "Question 4")
listbox.select_set(0)


title5 = tk.Label(ws, text="Question", font=('Helvetica', 12, 'bold')).grid(row=2, column=2)
title6 = tk.Label(ws, text="Solver", font=('Helvetica', 12, 'bold')).grid(row=2, column=3)

title7 = tk.Label(ws, text="Minimum gap", font=('Helvetica', 12, 'bold')).grid(row=2, column=1)
input_text3 = tk.Entry(ws, width=10, justify="center")
input_text3.grid(row=3, column=1, padx=5, pady=5)
input_text3.insert(0, "1")

listbox2 = tk.Listbox(ws, width=20, height=1, exportselection=0)
listbox2.insert(1, "PulP")
listbox2.select_set(0)

listbox.grid(row=3, column=2, padx=5, pady=5, rowspan=2)
listbox2.grid(row=3, column=3, padx=5, pady=5)


title4 = tk.Label(ws, text=" - "*16+" OUTPUT "+" - "*16, font=('Helvetica', 12, 'bold')).grid(row=7, column=0, columnspan=5)
# output_text = tkscrolled.ScrolledText(ws, width=50, height=10, wrap = 'word')
# # tkscrolled.ScrolledText(10, width=width, height=height, wrap='word')
# output_text.grid(row=9, column=0, padx=5, pady=5, columnspan=4)
# output_text.config(state="disabled")
canvas = tk.Canvas(ws, borderwidth=0, background="#ffffff", width=75, height=10)
canvas.grid(row=9, column=2, padx=5, pady=5, columnspan=4)

xscrollbar = tk.Scrollbar(canvas, orient="horizontal", jump=1)
xscrollbar.grid(row=1, column=0, sticky=N+S+E+W)

yscrollbar = tk.Scrollbar(canvas, jump=1)
yscrollbar.grid(row=0, column=1, sticky=N+S+E+W)

output_text = tk.Text(canvas, wrap=NONE, width=75, height=7, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
output_text.grid(row=0, column=0, padx=5, pady=5)

xscrollbar.config(command=output_text.xview)
yscrollbar.config(command=output_text.yview)

title5 = tk.Label(ws, text="Time execute", font=('Helvetica', 10)).grid(row=8, column=0)
output_text1 = tk.Entry(ws, width=20)
output_text1.grid(row=8, column=1, padx=5, pady=5)

title6 = tk.Label(ws, text="Mon\nTue\nWed\nThu\nFri\nSat\nSun", font=('Helvetica', 10), wraplength=200).grid(row=9, column=0)
output_text2 = tk.Text(ws, height=7, width=15)
output_text2.grid(row=9, column=1, padx=5, pady=5)

title8 = tk.Label(ws, text="Minimum number of crs", font=('Helvetica', 10)).grid(row=8, column=2)
output_text3 = tk.Entry(ws, width=20)
output_text3.grid(row=8, column=3, padx=5, pady=5)


def solve():
    output_text.config(state="normal")
    output_text.delete('1.0', tk.END)
    output_text1.delete(0, tk.END)
    output_text2.delete('1.0', tk.END)
    output_text3.delete(0, tk.END)
    # for i in listbox.curselection():
    #     print(listbox.get(i))
    # for i in listbox2.curselection():
    #     print(listbox2.get(i))

    input1 = input_text1.get("1.0", "end-1c")
    input2 = input_text2.get("1.0", "end-1c")
    minimum_gap = int(input_text3.get())
    requires = process_input(input1)
    shifts = process_input(input2)
    if listbox2.get(listbox2.curselection()) == "PulP":
        if listbox.get(listbox.curselection()) == "Question 1":
            num_csr_each_day, week_schedule, time_executed, cpu_time = q1(requires, shifts)
            minimum_csr = max(num_csr_each_day)
            week_schedule = add_pad_schedule(week_schedule)
            return_num_csr_each_day = '\n'.join(map(str, num_csr_each_day))
            return_day_schedule = process_output(week_schedule)
            output_text.insert(tk.END, return_day_schedule)
            output_text2.insert(tk.END, return_num_csr_each_day)
            output_text3.insert(0, minimum_csr)
            output_text1.insert(0, time_executed)

        if listbox.get(listbox.curselection()) == "Question 2":
            minimum_csr, num_csr_each_day, week_schedule, time_executed, cpu_time = q2(requires, shifts, minimum_gap)
            week_schedule = add_pad_schedule(week_schedule)
            return_num_csr_each_day = '\n'.join(map(str, num_csr_each_day))
            return_day_schedule = process_output(week_schedule)
            output_text.insert(tk.END, return_day_schedule)
            output_text2.insert(tk.END, return_num_csr_each_day)
            output_text3.insert(0, minimum_csr)
            output_text1.insert(0, time_executed)

        if listbox.get(listbox.curselection()) == "Question 3":
            minimum_csr, num_csr_each_day, week_schedule, time_executed, cpu_time = q3(requires, shifts, minimum_gap)
            week_schedule = add_pad_schedule(week_schedule)
            return_num_csr_each_day = '\n'.join(map(str, num_csr_each_day))
            return_day_schedule = process_output(week_schedule)
            output_text.insert(tk.END, return_day_schedule)
            output_text2.insert(tk.END, return_num_csr_each_day)
            output_text3.insert(0, minimum_csr)
            output_text1.insert(0, time_executed)

        if listbox.get(listbox.curselection()) == "Question 4":
            minimum_csr, num_csr_each_day, week_schedule, time_executed, cpu_time = q4(requires, shifts, minimum_gap)
            week_schedule = add_pad_schedule(week_schedule)
            return_num_csr_each_day = '\n'.join(map(str, num_csr_each_day))
            return_day_schedule = process_output(week_schedule)
            output_text.insert(tk.END, return_day_schedule)
            output_text2.insert(tk.END, return_num_csr_each_day)
            output_text3.insert(0, minimum_csr)
            output_text1.insert(0, time_executed)

    output_text.config(state="disabled")


title_min_random_input = tk.Label(ws, text="Min requires", font=('Helvetica', 10))
title_min_random_input.grid(row=3, column=0)
min_random_input = tk.Entry(ws, width=10, justify="center")
min_random_input.grid(row=4, column=0)
min_random_input.insert(0, "5")
title_max_random_input = tk.Label(ws, text="Max requires", font=('Helvetica', 10))
title_max_random_input.grid(row=5, column=0)
max_random_input = tk.Entry(ws, width=10, justify="center")
max_random_input.grid(row=6, column=0)
max_random_input.insert(0, "10")

def random_input():
    random_requires = [[str(random.randint(int(min_random_input.get()), int(max_random_input.get()))) for _ in range(13)] for _ in range(7)]
    random_requires = '\n'.join([' '.join(row) for row in random_requires])
    input_text1.delete('1.0', tk.END)
    input_text1.insert(tk.END, random_requires)

def process_input(input):
    lines = input.split("\n")
    res = []
    for line in lines:
        nums = list(map(lambda x: int(x), line.split()))
        res.append(nums)
    return res


def process_output(output):
    res = []
    for line in output:
        res += [" ".join(str(v) for v in line)]
    res = '\n'.join(res)
    return res

btn = tk.Button(ws, text='Solve', command=solve)
btn.grid(row=3, column=4, padx=5, pady=5)

random_btn = tk.Button(ws, text='Random', command=random_input)
random_btn.grid(row=2, column=0, padx=5, pady=5)


ws.mainloop()
