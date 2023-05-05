# definning the Pulp variables
TIMEPOINTS = [(a, b) for a in day_set for b in interval_set];import pulp
prob = pulp.LpProblem('Smart Water Heater', LpMinimize)
# dummy_setpoint = LpVariable.dicts('dummy setpoint', interval_set, t_min*temp_resolution, t_max*temp_resolution, 'Integer')
ts_setpoint = LpVariable.dicts('Thermostat setpoint', interval_set, t_min, t_max, 'Continuous')
NRG_input = LpVariable.dicts('Energy input', TIMEPOINTS, 0, max_energy_input_per_interval, 'Continuous')
temp_shortfall = LpVariable.dicts('Temperature shortfall',TIMEPOINTS, 0, t_min+25, 'Continuous')

Spill_Control= LpVariable.dicts('Spill Energy Controller',TIMEPOINTS,0,1, cat='Binary') # only for negotiator
heater_at_max = LpVariable.dicts('Max heater',TIMEPOINTS,0,1, cat='Binary')
heater_coasting = LpVariable.dicts('Heater Coasting',TIMEPOINTS,0,1, cat='Binary')
tempBelowMin = LpVariable.dicts('Under Heated Water',TIMEPOINTS,0,1, cat='Binary')


NRG_Spillover = LpVariable.dicts('Energy Spill over',TIMEPOINTS,0,None,'Continuous')
NRG_shortfall_f = LpVariable.dicts('Energy Shortfall',TIMEPOINTS,0,None,'Continuous')
NRG_withdrawn_f = LpVariable.dicts('Energy Withdrawn',TIMEPOINTS,0,None,'Continuous')
sim_tank_temp = LpVariable.dicts('Simulated Tank Temp',TIMEPOINTS,t_min-65,t_max+10,'Continuous')
conservative_sim_tank_temp = LpVariable.dicts('Conservative Temperature',TIMEPOINTS,-40,t_max+10,'Continuous')
# defining the cost function
ThreeBinary_start_time = time.time()
#average of the total energy consumption of the day. 
#e_ave = sum(energy_req_average[i] for i in interval_set)/len(interval_set)
e_ave = 0.3
rate= 1 # multiplied by the e_ave.
total_cost_f = sum(
  price_of_power[current_day,b] * NRG_input[a,b] + NRG_Spillover[a,b] * 0.1*price_of_power[current_day,b]  +shortfall_penalty_range[j] * NRG_shortfall_f[a,b]
  for (a, b) in TIMEPOINTS )/lookback_length
prob += total_cost_f

#================ adding initial energy withdrawal to the dataframe
for b in interval_set:
  Bidding_iteration.loc[(0,b),'House_{}'.format(unit)]=energy_req[current_day,b]

#constraint
for t in TIMEPOINTS:
        prob += (NRG_shortfall_f[t] == energy_req[t] - NRG_withdrawn_f[t])
        prob += (NRG_shortfall_f[t] == energy_req[t] * temp_shortfall[t] / (t_min_shortfall - t_in[current_day]))
        prob += (NRG_input[t] <= (1-heater_coasting[t])*max_energy_input_per_interval,'Energy input constraint 1 {}'.format(t))
        prob += (NRG_input[t] >= heater_at_max[t] * max_energy_input_per_interval,'Energy input constraint 2 {}'.format(t))

        prob += (temp_shortfall[t] >= t_min_shortfall - conservative_sim_tank_temp[t],'Conservative Temperature shortfall constraint {}'.format(t))
        # the following four constraints prevents MILP to have high amount of temperature shorftall when penalty is low.
        prob += (temp_shortfall[t] <= (t_min_shortfall - conservative_sim_tank_temp[t]+(1-tempBelowMin[t])*big_temp),'coservative Temp lower limit shortfall constraint {}'.format(t))
        prob += (temp_shortfall[t] <= tempBelowMin[t]*big_temp)
        prob += (tempBelowMin[t]*big_temp >= t_min_shortfall - conservative_sim_tank_temp[t])
        prob += ((1-tempBelowMin[t])*big_temp >=  conservative_sim_tank_temp[t] - t_min_shortfall)

        # # these constraints are to damp over injection of energy in one specefic hour. it is used to stop zig zag effect
        # # specefic for Negotiator code only
        # prob += (NRG_Spillover[t] >= NRG_input[t]- rate*e_ave)
        # prob += (NRG_Spillover[t] <= NRG_input[t]- rate*e_ave + (1-Spill_Control[t])*big_temp)
        # prob += (NRG_Spillover[t] <= Spill_Control[t]*big_temp)
        # # the following two constraints are to control the Spill_control status
        # prob += (Spill_Control[t]*big_temp >= NRG_input[t]- rate*e_ave)
        # prob += ((1-Spill_Control[t])*big_temp >=  rate*e_ave - NRG_input[t])


               
for (a, b) in TIMEPOINTS:
        # prob += (dummy_setpoint[b] == ts_setpoint[b] * (temp_resolution))
        #prob += (dummy_NRG_input[a,b] == NRG_input[a,b] * (NRG_resolution))
        prob += (sim_tank_temp[a, b] >= ts_setpoint[b] - heater_at_max[a, b] * big_temp,'Thermostat setpoint constraint {}'.format((a, b)))
        prob += (sim_tank_temp[a, b] <= ts_setpoint[b] + heater_coasting[a, b] * big_temp, 'Heater coasting constraint {}'.format((a, b)))

        # this is a new constraint. based on the value of the 'Hourly_TS_setpoint_interval', the code decides to keep the
        # thermostat setpoints hourly or keep it with the lenght of intervlas
        if int((b-1)/interval_per_hour)+1 == int((b)/interval_per_hour) == int((b+1)/interval_per_hour):
            for i in range(int(interval_per_hour)):
                prob += (ts_setpoint[b-i] == ts_setpoint[b])
        if b == 1:
            i_prev = max(interval_set)
            d_prev = a
        else:
         i_prev = b - 1
         d_prev = a
        prob += (conservative_sim_tank_temp[a,b] == sim_tank_temp[d_prev,i_prev]+(- NRG_withdrawn_f[a,b]) / degree_of_water_per_kwh )
        if version ==3:
           prob += (sim_tank_temp[a,b]*degree_of_water_per_kwh == conservative_sim_tank_temp[a,b]*degree_of_water_per_kwh + (NRG_input[a,b]) 
               - heat_loss_rate *degree_of_water_per_kwh*(conservative_sim_tank_temp[a,b] - t_amb[current_day,b]))
        if version ==2:
           prob += (sim_tank_temp[a,b] == conservative_sim_tank_temp[a,b] + (NRG_input[a,b]) / degree_of_water_per_kwh
               - heat_loss_rate * (conservative_sim_tank_temp[a,b] - t_amb[current_day,b])) 
#=================================
# solves the problem using CPLEX.
# when I wasd looking into CPLEX options, i saw the crossover function which is a genetic algorithm operator. it divesifyies the samples.
# it seems that by default CPLEX do not! uses methaheuristic algorithm such as genetic algorithm.
# by adding the 'set barrier crossover 2' option, our method runs much much faster.

# optimization_result = prob.solve(CPLEX_CMD(
#         options=['set emphasis mip 4',
# #                 'set barrier crossover 2',
# #                 'mip strategy heuristicfreq 2',
# #                 'mip strategy rinsheur -1',
# #                 'mip limits submipnodelim 500',
#                   'set mip tolerances mipgap {}'.format(Optimality_gap),
#                   'set workmem 20000',
#                   'set timelimit {}'.format(Run_Time), 
#                   'set mip strategy file 3', 
#                   #'read PreSolution\average Sol',
#                   #'set threads 8',
#                   'set workdir {}'.format(tempdir)
#                           ],msg=1
#       ))
Three_Binary_Run_time=time.time() - ThreeBinary_start_time
print(" %s seconds for Three binary (original) Model" % (time.time() - ThreeBinary_start_time))
#=================================
# these are other solves that can be used to solve the model
#optimization_result = prob.solve(PULP_CBC_CMD(msg=0))
#optimization_result = prob.solve(CPLEX_PY(mip=True,msg=True))
#optimization_result = prob.solve(CPLEX_PY(msg=0))
optimization_result = prob.solve(GUROBI_CMD(msg=0))
#optimization_result = prob.solve(GLPK_CMD(msg=0))

#================================
# calculates the total cost for each run based on optimizaed value that are found by solving the problem
electrical_f = sum(price_of_power[current_day,b] * NRG_input[a,b].value()  for (a, b) in TIMEPOINTS)/lookback_length
shortfall_f = sum(NRG_shortfall_f[a,b].value() for (a, b) in TIMEPOINTS)/lookback_length
#=======================================

# if the code is in stochastic mode, it applies the thermostat setpoints that already found by the solver on tomorrow withdrawal pattern and electrical cost
#if 

E_w1=dict();E_w2=dict();E_er=dict() 
for b in sorted(interval_set):
        NRG_shortfall_our[b]=0
        if b == 1:
            i_prev = max(interval_set)
        else:
            i_prev = b - 1            
         
        t_tank_our[24*(60/min_slot)]=sim_tank_temp[a,24*(60/min_slot)].value()   
        t_tank_our[b]=ts_setpoint[b].value()
        NRG_withdrawn_our[b]=energy_req_tomorrow[b]
        t= t_tank_our[b]*(1+heat_loss_rate) - heat_loss_rate * t_amb[current_day,b] - t_tank_our[i_prev]
        k=  degree_of_water_per_kwh * (t)
        E_in_our[b]=k+NRG_withdrawn_our[b]+0.00001

        E_w1[b]=1
        E_w2[b]=0
        
        if (E_in_our[b] >= max_energy_input_per_interval):
          E_in_our[b]=max_energy_input_per_interval
          t_tank_our[b]=(1/(1+heat_loss_rate))*(((E_in_our[b]-NRG_withdrawn_our[b])/degree_of_water_per_kwh)+t_amb[current_day,b]*heat_loss_rate+t_tank_our[i_prev])
          
          while (abs(E_w1[b]-E_w2[b]) >= 0.001):      
                  
            t_shortfall_our[b] = t_min_shortfall - t_tank_our[b]+0.0000001
            if (t_shortfall_our[b] <0):
                t_shortfall_our[b] =0
            E_w1[b] = energy_req_tomorrow[b] * t_shortfall_our[b] / (t_min_shortfall - t_in[current_day])+0.0000001
#            E_w2[b] = energy_req_tomorrow[b] - NRG_shortfall_our[b]

            k=  degree_of_water_per_kwh * (t_tank_our[b]*(1+heat_loss_rate) - heat_loss_rate * t_amb[current_day,b] - t_tank_our[i_prev])+0.0000001
            E_w2[b]=k+energy_req_tomorrow[b]-max_energy_input_per_interval
#            E_in_our[b]=energy_req_tomorrow[b] - E_w1[b]+0.0000001
#            while (E_in_our[b] <= (max_energy_input_per_interval-0.2)):
#                 E_w1[b]=1
#                 E_w2[b]=0
            NRG_shortfall_our[b]=E_w1[b]
            t_tank_our[b]=t_tank_our[b]+0.001
            E_er[b]=abs(E_w1[b]-E_w2[b])

        if (E_in_our[b] <=0):

          while (abs(E_w1[b]-E_w2[b]) >= 0.001):
            
            E_w1[b]=degree_of_water_per_kwh*(t_tank_our[b]*(-1-heat_loss_rate)+ t_tank_our[i_prev] + heat_loss_rate * t_amb[current_day,b])+0.0000001        
            t_shortfall_our[b] = t_min_shortfall - t_tank_our[b]+0.0000001
            if (t_shortfall_our[b] <0):
                t_shortfall_our[b] =0
            NRG_shortfall_our[b] = energy_req_tomorrow[b] * t_shortfall_our[b] / (t_min_shortfall - t_in[current_day])
            E_w2[b] = energy_req_tomorrow[b] - NRG_shortfall_our[b]

            k=  degree_of_water_per_kwh * (t_tank_our[b]*(1+heat_loss_rate) - heat_loss_rate * t_amb[current_day,b] - t_tank_our[i_prev])
            E_in_our[b]=k+E_w1[b]+0.0000001
            if (E_in_our[b] <= -0.1):
                 E_w1[b]=1
                 E_w2[b]=0

            t_tank_our[b]=t_tank_our[b]+0.001
            E_er[b]=abs(E_w1[b]-E_w2[b])
            
        if (E_in_our[b] >=0.1) and (E_in_our[b] <=max_energy_input_per_interval-0.1) and (t_tank_our[b] <= t_min_shortfall-0.2) :
            t_shortfall_our[b] = t_min_shortfall - t_tank_our[b]+0.0000001
#            if (t_shortfall_our[b] <0):
#                t_shortfall_our[b] =0
            NRG_shortfall_our[b] = energy_req_tomorrow[b] * t_shortfall_our[b] / (t_min_shortfall - t_in[current_day])
            k=  degree_of_water_per_kwh * (t_tank_our[b]*(1+heat_loss_rate) - heat_loss_rate * t_amb[current_day,b] - t_tank_our[i_prev])+0.0000001
            E_in_our[b]=k+energy_req_tomorrow[b]-NRG_shortfall_our[b]+0.000001
        OneDayDF.loc[b,'Act_temp_Negotiator']= t_tank_our[b] 
        OneDayDF.loc[b,'set_temp_Negotiator']= ts_setpoint[b].value()
        OneDayDF.loc[b,'NRG_in_Negotiator']= E_in_our[b]
        # OneDayDF.loc[b,'NRG_Spillover_Negotiator']= NRG_Spillover[current_day,b].value()
        # OneDayDF.loc[b,'Spill_Control']= Spill_Control[current_day,b].value()
            
electrical_f_actual=sum(price_of_power[current_day,b] * E_in_our[b]  for b in interval_set)                  
shortfall_f_actual = sum(NRG_shortfall_our[b] for b in interval_set)


for b in interval_set:           
       Bidding_iteration.loc[(s,b),'House_{}'.format(unit)]=NRG_input[current_day,b].value()
E_in_our.clear()       
      
# decided whats MILP&Goh and Du&Lu initial temperature should be. it is explained in the 'Main.py' more.
init_temp(Initial_Temperature_Status,current_day)

MILP_dict={}
MILP_dict={'Exp_C_Negotiator':electrical_f,'Exp_Dis_Negotiator':shortfall_f,'LastTemp_Negotiator':t_tank_our[max(interval_set)],
                      'Act_Dis_Negotiator':shortfall_f_actual,'Act_C_Negotiator':electrical_f_actual}
methods_dictionary.update(MILP_dict)







