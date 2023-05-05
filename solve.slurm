#!/bin/bash

#SBATCH --job-name=WaterHeater
#SBATCH --partition=kill.q
#SBATCH --time=0-01:30:00 ## time format is DD-HH:MM:SS
## task-per-node x cpus-per-task should not typically exceed core count on an individual node
#SBATCH --nodes=5
#SBATCH --tasks-per-node=20
#SBATCH --cpus-per-task=1
#SBATCH --array=1-1000   # if the number of penalties are 10 and want to run it for 25 days of tomorrows, the
## value should be 25*10=250
## maximum number of allowed 'array' is 1000
#SBATCH --mem=6400 ## max amount of memory per node you require
#SBATCH --error=Result/Error_Out/WaterHeater-%A.err ## %A - filled with jobid
#SBATCH --output=Result/Error_Out/WaterHeater-%A.out ## %A - filled with jobid
#SBATCH --mail-type=BEGIN,END,FAIL,REQUEUE,TIME_LIMIT_80
#SBATCH --mail-user=fnajafi@hawaii.edu

## All options and environment variables found on schedMD site: http://slurm.schedmd.com/sbatch.html

####module load lang/Python/2.7.10/python
module load lang/Python/2.7.15-intel-2018.5.274
python launch_job.py