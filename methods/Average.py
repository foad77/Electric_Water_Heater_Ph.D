# definning the Pulp variables
prob = LpProblem('Smart Water Heater', LpMinimize)
dummy_setpoint = LpVariable.dicts('dummy setpoint', interval_set, t_min*temp_resolution, t_max*temp_resolution, 'Integer')
ts_setpoint = LpVariable.dicts('Thermostat setpoint', interval_set, t_min, t_max, 'Continuous')
NRG_input_average = LpVariable.dicts('Energy input average', interval_set, 0, max_energy_input_per_interval, 'Continuous')
temp_shortfall_average = LpVariable.dicts('Temperature shortfall',interval_set, 0, t_min+5, 'Continuous')
heater_at_maxl_average = LpVariable.dicts('Max heater',interval_set,0,1, cat='Binary')
heater_coastingl_average = LpVariable.dicts('Heater Coasting',interval_set,0,1, cat='Binary')
tempBelowMin = LpVariable.dicts('Under Heated Water',interval_set,0,1, cat='Binary')
NRG_shortfall_average = LpVariable.dicts('Energy Shortfall',interval_set,0,None,'Continuous')
NRG_withdrawn_average = LpVariable.dicts('Energy Withdrawn',interval_set,0,None,'Continuous')
sim_tank_temp_average = LpVariable.dicts('Simulated Tank Temp_average',interval_set,t_min-35,t_max+5,'Continuous')
conservative_sim_tank_temp = LpVariable.dicts('Conservative Temperature',interval_set,-10,t_max+5,'Continuous')
# defining the cost function
WH_MILP_start_time = time.time()
total_cost_f = sum(
  price_of_power[current_day,t] * NRG_input_average[t] + shortfall_penalty_range[j] * NRG_shortfall_average[t]
  for (t) in interval_set )
prob += total_cost_f
#constraint
for t in interval_set:
        prob += (NRG_shortfall_average[t] == energy_req_average[t] - NRG_withdrawn_average[t])
        prob += (NRG_shortfall_average[t] == energy_req_average[t] * temp_shortfall_average[t] / (t_min_shortfall - t_in[current_day]))
        prob += (NRG_input_average[t] <= (1-heater_coastingl_average[t])*max_energy_input_per_interval,'Energy input constraint 1 {}'.format(t))
        prob += (NRG_input_average[t] >= heater_at_maxl_average[t] * max_energy_input_per_interval,'Energy input constraint 2 {}'.format(t))        
        if Conservative_Penalty_Status:
         prob += (temp_shortfall_average[t] >= t_min_shortfall - conservative_sim_tank_temp[t],'Conservative Temperature shortfall constraint {}'.format(t))
         # the following four constraints prevents MILP to have high amount of temperature shorftall when penalty is low.
         prob += (temp_shortfall_average[t] <= (t_min_shortfall - conservative_sim_tank_temp[t]+(1-tempBelowMin[t])*big_temp),'coservative Temp lower limit shortfall constraint {}'.format(t))
         prob += (temp_shortfall_average[t] <= tempBelowMin[t]*big_temp)
         prob += (tempBelowMin[t]*big_temp >= t_min_shortfall - conservative_sim_tank_temp[t])
         prob += ((1-tempBelowMin[t])*big_temp >=  conservative_sim_tank_temp[t] - t_min_shortfall)
        else:
         prob += (temp_shortfall_average[t] >= (t_min_shortfall - sim_tank_temp_average[t]),'Temperature upper limit shortfall constraint {}'.format(t))                       
         # the following four constraints prevents MILP to have high amount of temperature shorftall when penalty is low.
         prob += (temp_shortfall_average[t] <= (t_min_shortfall - sim_tank_temp_average[t]+(1-tempBelowMin[t])*big_temp),'Temperature lower limit shortfall constraint {}'.format(t))
         prob += (temp_shortfall_average[t] <= tempBelowMin[t]*big_temp)
         prob += (tempBelowMin[t]*big_temp >= t_min_shortfall - sim_tank_temp_average[t])
         prob += ((1-tempBelowMin[t])*big_temp >=  sim_tank_temp_average[t] - t_min_shortfall)
        prob += (dummy_setpoint[t] == ts_setpoint[t] * (temp_resolution))
        prob += (sim_tank_temp_average[t] >= ts_setpoint[t] - heater_at_maxl_average[t] * big_temp,'Thermostat setpoint constraint {}'.format((t)))
        prob += (sim_tank_temp_average[t] <= ts_setpoint[t] + heater_coastingl_average[t] * big_temp, 'Heater coasting constraint {}'.format((t)))

        # this is a new constraint. based on the value of the 'Hourly_TS_setpoint_interval', the code decides to keep the
        # thermostat setpoints hourly or keep it with the lenght of intervlas
        if int((t-1)/interval_per_hour)+1 == int((t)/interval_per_hour) == int((t+1)/interval_per_hour):
            for i in range(interval_per_hour):
                ts_setpoint[t-i] = ts_setpoint[t]
        if t == 1:
            i_prev = max(interval_set)
        else:
         i_prev = t - 1
        prob += (conservative_sim_tank_temp[t] == sim_tank_temp_average[i_prev]+(- NRG_withdrawn_average[t]) / degree_of_water_per_kwh )  
        if version ==3:
           prob += (sim_tank_temp[a,b]*degree_of_water_per_kwh == conservative_sim_tank_temp[a,b]*degree_of_water_per_kwh + (NRG_input[a,b]) 
               - heat_loss_rate *degree_of_water_per_kwh*(conservative_sim_tank_temp[a,b] - t_amb[current_day,b]))
        if version ==2:
           prob += (sim_tank_temp[a,b] == conservative_sim_tank_temp[a,b] + (NRG_input[a,b]) / degree_of_water_per_kwh
               - heat_loss_rate * (conservative_sim_tank_temp[a,b] - t_amb[current_day,b]))
#=================================

optimization_result = prob.solve(CPLEX_CMD(
        options=['set emphasis mip 4',

                 'set mip tolerances mipgap {}'.format(Optimality_gap),
                 'set workmem 20000',
                 'set timelimit {}'.format(Run_Time), 
                 'set mip strategy file 3', 
                 'set workdir {}'.format(tempdir)
                         ],msg=1
     ))
Three_Binary_Run_time=time.time() - ThreeBinary_start_time
print(" %s seconds for WH_MILP_Average" % (time.time() - WH_MILP_start_time))
#=================================
# these are other solves that can be used to solve the model
#optimization_result = prob.solve(PULP_CBC_CMD(msg=0))
#optimization_result = prob.solve(CPLEX_PY(mip=True,msg=True))
#optimization_result = prob.solve(GUROBI_CMD(msg=0))
#       optimization_result = prob.solve(GLPK_CMD(msg=0))
#================================
# calculates the total cost for each run based on optimizaed value that are found by solving the problem
electrical_f_average = sum(price_of_power[current_day,t] * NRG_input_average[t].value()  for (t) in interval_set)
shortfall_f_average = sum(NRG_shortfall_average[t].value() for (t) in interval_set)
#=======================================

# if the code is in stochastic mode, it applies the thermostat setpoints that already found by the solver on tomorrow withdrawal pattern and electrical cost
#if 
dictionaries=[E_w1,E_w2,E_er,NRG_shortfall_WH_MILP_average,t_tank_WH_MILP_average,NRG_withdrawn_WH_MILP_average,E_in_WH_MILP_average,t_shortfall_WH_MILP_average]
for g in dictionaries:
    g.clear()
E_w1=dict();E_w2=dict();E_er=dict() 
for b in sorted(interval_set):
        NRG_shortfall_WH_MILP_average[b]=0
        if b == 1:
            i_prev = max(interval_set)
        else:
            i_prev = b - 1                     
        t_tank_WH_MILP_average[24*(60/min_slot)]=sim_tank_temp_average[24*(60/min_slot)].value()   
        t_tank_WH_MILP_average[b]=ts_setpoint[b].value()
        NRG_withdrawn_WH_MILP_average[b]=energy_req_tomorrow[b]
        t= t_tank_WH_MILP_average[b]*(1+heat_loss_rate) - heat_loss_rate * t_amb[current_day,b] - t_tank_WH_MILP_average[i_prev]
        k=  degree_of_water_per_kwh * (t)
        E_in_WH_MILP_average[b]=k+NRG_withdrawn_WH_MILP_average[b]+0.00001

        E_w1[b]=1
        E_w2[b]=0
        
        if (E_in_WH_MILP_average[b] >= max_energy_input_per_interval):
          E_in_WH_MILP_average[b]=max_energy_input_per_interval
          t_tank_WH_MILP_average[b]=(1/(1+heat_loss_rate))*(((E_in_WH_MILP_average[b]-NRG_withdrawn_WH_MILP_average[b])/degree_of_water_per_kwh)+t_amb[current_day,b]*heat_loss_rate+t_tank_WH_MILP_average[i_prev])
          
          while (abs(E_w1[b]-E_w2[b]) >= 0.001):      
                  
            t_shortfall_WH_MILP_average[b] = t_min_shortfall - t_tank_WH_MILP_average[b]+0.0000001
            if (t_shortfall_WH_MILP_average[b] <0):
                t_shortfall_WH_MILP_average[b] =0
            E_w1[b] = energy_req_tomorrow[b] * t_shortfall_WH_MILP_average[b] / (t_min_shortfall - t_in[current_day])+0.0000001

            k=  degree_of_water_per_kwh * (t_tank_WH_MILP_average[b]*(1+heat_loss_rate) - heat_loss_rate * t_amb[current_day,b] - t_tank_WH_MILP_average[i_prev])+0.0000001
            E_w2[b]=k+energy_req_tomorrow[b]-max_energy_input_per_interval

            NRG_shortfall_WH_MILP_average[b]=E_w1[b]
            t_tank_WH_MILP_average[b]=t_tank_WH_MILP_average[b]+0.001
            E_er[b]=abs(E_w1[b]-E_w2[b])

        if (E_in_WH_MILP_average[b] <=0):

          while (abs(E_w1[b]-E_w2[b]) >= 0.001):
            
            E_w1[b]=degree_of_water_per_kwh*(t_tank_WH_MILP_average[b]*(-1-heat_loss_rate)+ t_tank_WH_MILP_average[i_prev] + heat_loss_rate * t_amb[current_day,b])+0.0000001        
            t_shortfall_WH_MILP_average[b] = t_min_shortfall - t_tank_WH_MILP_average[b]+0.0000001
            if (t_shortfall_WH_MILP_average[b] <0):
                t_shortfall_WH_MILP_average[b] =0
            NRG_shortfall_WH_MILP_average[b] = energy_req_tomorrow[b] * t_shortfall_WH_MILP_average[b] / (t_min_shortfall - t_in[current_day])
            E_w2[b] = energy_req_tomorrow[b] - NRG_shortfall_WH_MILP_average[b]

            k=  degree_of_water_per_kwh * (t_tank_WH_MILP_average[b]*(1+heat_loss_rate) - heat_loss_rate * t_amb[current_day,b] - t_tank_WH_MILP_average[i_prev])
            E_in_WH_MILP_average[b]=k+E_w1[b]+0.0000001
            if (E_in_WH_MILP_average[b] <= -0.1):
                 E_w1[b]=1
                 E_w2[b]=0

            t_tank_WH_MILP_average[b]=t_tank_WH_MILP_average[b]+0.001
            E_er[b]=abs(E_w1[b]-E_w2[b])
            
        if (E_in_WH_MILP_average[b] >=0.1) and (E_in_WH_MILP_average[b] <=max_energy_input_per_interval-0.1) and (t_tank_WH_MILP_average[b] <= t_min_shortfall-0.2) :
            t_shortfall_WH_MILP_average[b] = t_min_shortfall - t_tank_WH_MILP_average[b]+0.0000001
            NRG_shortfall_WH_MILP_average[b] = energy_req_tomorrow[b] * t_shortfall_WH_MILP_average[b] / (t_min_shortfall - t_in[current_day])
            k=  degree_of_water_per_kwh * (t_tank_WH_MILP_average[b]*(1+heat_loss_rate) - heat_loss_rate * t_amb[current_day,b] - t_tank_WH_MILP_average[i_prev])+0.0000001
            E_in_WH_MILP_average[b]=k+energy_req_tomorrow[b]-NRG_shortfall_WH_MILP_average[b]+0.000001

            
electrical_f_actual_average=sum(price_of_power[current_day,b] * E_in_WH_MILP_average[b]  for b in interval_set)                  
shortfall_f_actual_average = sum(NRG_shortfall_WH_MILP_average[b] for b in interval_set)


#average_path='Result/logging/stochastic/average/{} lookback/{} penalty'.format(lookback_length,current_Ps)
#if os.path.exists(average_path)==True:
#    pass
#else:
#   os.makedirs(average_path)
#
#with open('Result/logging/stochastic/average/{} lookback/{} penalty/{} tomorrow.csv'.format(lookback_length,current_Ps,current_day), "w") as f: 
#          f.write(str('Expected_Cost_WH_MILP_average')+ ',' + str('Expected_Discomfort_WH_MILP_average') +','+'\n')
#          f.write(str(electrical_f_average)+ ',' + str(shortfall_f_average) +','+'\n') 
#          f.write(str('Actual_Cost_WH_MILP_average')+ ',' + str('Actual_Discomfort_WH_MILP_average') +','+'\n')
#          f.write(str(electrical_f_actual_average)+ ',' + str(shortfall_f_actual_average) +','+'\n')


Average_dict={}
Average_dict={'Exp_C_Average':electrical_f_average, 'Exp_Dis_Average':shortfall_f_average,'Act_C_Average':electrical_f_actual_average,
    'Act_Dis_Average':shortfall_f_actual_average,'LastTemp_Average':t_tank_WH_MILP_average[max(interval_set)] }
methods_dictionary.update(Average_dict)


