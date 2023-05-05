import os, subprocess
array_id = int(os.environ['SLURM_ARRAY_TASK_ID'])
start_day = 61 # first day of the year to evaluate
penalty_factors = [0.09,0.1,0.105, 0.12, 0.14, 0.18, 0.2, 0.5, 0.7,2]

# get day and penalty ids
# array_id 1 gives the first day (0), first penalty factor
# array_id 2 gives the first day (0), second penalty factor
# then eventually it rotates through different days
day, pen = divmod(array_id - 1, len(penalty_factors))

day_of_year = start_day + day
penalty_factor = penalty_factors[pen]

# call the solve script
cmd = ["python", "Solve.py", str(day_of_year), str(penalty_factor)]
exit(subprocess.call(cmd))
