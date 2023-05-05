#===================================
#methods=["MILP", "Du","Apt","Pyomo","Fixed","Average","Solar","Negotiator","Negotiator_Linear","EA_GA"]         
methods=["Negotiator"]
import time; start_time = time.time()
#=================================
# defines the length of tomorrow days. e.g., if 'loop' is '4' and 'tomorrow' is 300, it runs the code for days 300, 301, 302 and 303
# then the average of these 4 days is reported as the expected cost. this value is different from 'lookback_length' which loops through
# past days for each tomorrow day.
#===================================
# if true, it won't log anything. used for when not wanting anything to be saved. since it won't run again and the log file must
# be delected eveytime
test_mode=True
#====================================
# if 'True':
#for out method: it will solve the problem for the lengh of 'lookback_length' and applies the optained termostat setpoint
# to tomorrow withdrawal pattern and price. for Du&u and Apt&Goh: find the average of withdrawal pattern for the 'lookback_length'
# and applies it to tomorrow withdrawal pattern.

# if 'False': assimilate the pefect forecast situtation. i.e,. we know exactly what tomorrow price and withdrawal pattern would be
# useful to benchmark our methord against other method when all method have access to exactly the same information.
#so, it solves the problem only for tomorrow. for our method and other methods.
stochastic_status=False
#=======================
# defines the length of previous days to solve the problem. the average of these days is used as the input (prediction) of withdrawal
# pattern for the Du&Lu and Apt&Goh. if the 'lookback' is bigger than 'tomorrow', it will add days from end of the year. e.g., tomorrow=2 and lookback_lengh=4
# then the lookback days set is {1,363,364,365} 
lookback_length =8
#====================================
# defines tomorrow
# example: if 'tomorrow' is 200 and 'loop' is 10. the code loops through 10 days starting from 200
tomorrow =176
#====================================
# the resolution of intervals. it  can be: 1, 2, 3, 4, 5, 6, 10, 12, 15, 30, 60 minutes.
min_slot=60
#====================================
# the resolution for thermostat setpoint.e.g., if the resolution is '2', thermostat setpoint can only values like: 28, 28.5, 29, 29.5. or if it is
# '4', thermostat can have values like 28.25, 28.5, 28.75, 29,...   quantizing thermostat setpoint make the code much faster
temp_resolution=10
#====================================
# CPLEX options 
# Run Time. the maximum time we allow the simulation to run.in seconds
Run_Time=500
# optimality gap
Optimality_gap= 0.0
#=================================

# it defines how many points we want on the "cost_Vs_discomfort" plot based on 'penalty_vector'.
resolution=1
#use a pre defiend vecotr of penalties
#penalty_vector= [0.9,0.1,0.105, 0.12, 0.14, 0.18, 0.2, 0.5, 0.7,2.0]
penalty_vector= [16]
#the temperature for "Fixed" method
Flate_rate_vector= [60,42, 43,45, 47,50,57,60,62,65]
#=======================================================    
# initialize termostate setpoint for Du&Lu and apt&Goh method: 
# 1: t_min_range[j]         they will use a range based on value of each 'j'.
# 2: ts_setpoint[1].value() they will start from the initial value that is defined by our method
# 3: t_min_shortfall        they will use this fixed value 
# 4: sim_tank_temp[a,24*(60/min_slot)].value()     the actual temperature of the start of the period from our method
# 5: rolling based                it will refer to the last actual temperature of the previous day
Initial_Temperature_Status=3
#============================================

#===========================================
#maximum and minimum allowed temperature
t_max=83;t_min = 25
#==========================================
# underheated hot water is calculatd based on this value
t_min_shortfall=40   
#=================================
# physical parameters
max_energy_input_per_hour = 4.5; specific_heat = 0.001148; v = 160; heat_loss_rate = 0.04
degree_of_water_per_kwh = v*specific_heat;
#==========================================
# 1= PuLP
# 2= Pyomo
problem_formulator_status=1
#===================================
# If 'True', algorithm suppose that all the hot water consumption happens at the start of each interval while no energy is added yet
# which in return causes lower temperature at each interval.
# if 'False' calculate penalty shortfall based on the end temperature of each interval. therefore, the
# temperature would be higher when the status is 'True'
Conservative_Penalty_Status=False
#==================================
# if 'True', it uses a range for minimum temperature for Du&Lu and Apt&goh to generate
# a CURVE on 'Cost VS Discomfort plot'. if the value is 'False' it uses
# a fixed miminum temperature (t_min_shortfall to calculate discomfort which
# will result a POINT on the 'Cost VS Discomfort plot'.
Ranged_Temperature_penalty_status=False
#========================================
# if equals to 'True', it will keep the termostat setpoint equal to one hour. if 'False', the termostate setpoint duration
# is qual to the length of each interval in the hour
Hourly_TS_setpoint_interval=True
#=======================================================
#this code is in charge of generating inpt data for the code. based on 'min_slot', it data for 1,2,...,60 minutes. I already
#generated **min_usage.xlsx data files which are in the main dircetory of 'Input' folder. Therefore, it is not necessary to run
#this file unless we want to change input values.

#execfile('Input/Data_generator/Interval_Generator.py')     

#=====================================================
# this file imports modules, data files and functions
import sys; version = sys.version_info[0]
if version ==3: exec(compile(open('Input/imports.py', "rb").read(), 'Input/imports.py', 'exec'))
if version ==2: execfile('Input/imports.py')
#==========================================
#==========================================
#==========================================
#this is the main loop of  the code
if version ==3: exec(compile(open('Input/Loop.py', "rb").read(), 'Input/Loop.py', 'exec'))
if version ==2: execfile('Input/Loop.py')
#=========================================
# exporting the result and plotting the outputs
#if len(sys.argv) == 1 and loop == 1:
#     if version ==3: exec(compile(open('Result/C_Vs_Dis.py', "rb").read(), 'Result/C_Vs_Dis.py', 'exec'))
#     if version ==2: execfile('Result/C_Vs_Dis.py')

# it saves all the variables into two seperate .csv files in the 'Results' folder
# also it plots the second graph for the last value of  penatly factor and 'loop' value.
# if len(sys.argv) == 1 and loop == 1:
#   if version ==3: exec(compile(open('Result/OneDay.py', "rb").read(), 'Result/OneDay.py', 'exec'))
#   if version ==2: execfile('Result/OneDay.py')
#exec(compile(open('Result/temPy/testQuadProb.py', "rb").read(), 'Result/testQuadProb.py', 'exec'))
