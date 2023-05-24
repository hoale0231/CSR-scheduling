# CSR Scheduling

## Install
```
pip install -r requirements.txt
```

## Demo

### Run demo app:
```
python app.py
```

### Sample data:
```
# Sample required
6 9  9 8 3 3 7 8 8 5 3 3 20
6 10 7 7 3 4 7 5 9 5 3 4 3
7 9  9 6 3 4 6 8 7 4 3 3 3
6 9  8 6 4 4 5 8 7 5 4 3 4
6 7  8 7 3 5 6 7 6 5 3 3 3
6 9  9 4 3 3 4 5 5 5 3 3 2
5 7  6 5 4 3 4 5 6 5 3 3 3
----------------------------
# Shifts 1
0 0 0 0 0 0 0 0 0 0 0 0 0
1 1 1 1 0 1 1 1 1 0 0 0 0
0 1 1 1 0 1 1 1 1 1 0 0 0
0 0 1 1 1 0 1 1 1 1 1 0 0
0 0 0 1 1 1 1 1 0 1 1 1 0
0 0 0 0 1 1 1 1 1 0 1 1 1
1 1 1 1 0 0 0 0 0 1 1 1 1
```

## Run single question
```
python pulp_solve/{q1,q2,q3,q3_replace,q3_group,q4,q4_replace,q4_group}.py
```

## Run all question with all test case
```
python run.py
```
**We put inputs/outputs of all testcase in the folder test_case excluding the timeout sample**