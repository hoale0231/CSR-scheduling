REQUIRES = [
    [ 6, 9,  9, 8, 3, 3, 7, 8, 8, 5, 3, 3, 2], # Monday
    [ 6, 10, 7, 7, 3, 4, 7, 5, 9, 5, 3, 4, 3], # Tuesday
    [ 7, 9,  9, 6, 3, 4, 6, 8, 7, 4, 3, 3, 3], # Wednesday
    [ 6, 9,  8, 6, 4, 4, 5, 8, 7, 5, 4, 3, 4], # Thursday
    [ 6, 7,  8, 7, 3, 5, 6, 7, 6, 5, 3, 3, 3], # Friday
    [ 6, 9,  9, 4, 3, 3, 4, 5, 5, 5, 3, 3, 2], # Saturday
    [ 5, 7,  6, 5, 4, 3, 4, 5, 6, 5, 3, 3, 3]  # Sunday
] 
SHIFTS = [
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Off day
    [ 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0],  # C1
    [ 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0],  # C2
    [ 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0],  # C3
    [ 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0],  # C4
    [ 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1],  # C5
    [ 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1]   # C6
] 

WEEK = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
