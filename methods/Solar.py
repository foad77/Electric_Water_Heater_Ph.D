# definning the Pulp variables
prob = LpProblem('Solar Smart Water Heater', LpMinimize)

dummy_setpoint = LpVariable.dicts('Solar dummy setpoint', interval_set, t_min*temp_resolution, t_max*temp_resolution, 'Integer')
ts_setpoint = LpVariable.dicts('Solar Thermostat setpoint', interval_set, t_min, t_max, 'Continuous')
sim_tank_temp = LpVariable.dicts('Solar Simulated Tank Temp',TIMEPOINTS,t_min-65,t_max+10,'Continuous')
conservative_sim_tank_temp = LpVariable.dicts('Solar Conservative Temperature',TIMEPOINTS,-40,t_max+10,'Continuous')
temp_shortfall = LpVariable.dicts('Solar Temperature shortfall',TIMEPOINTS, 0, t_min+25, 'Continuous')

heater_at_max = LpVariable.dicts('Solar Max heater',TIMEPOINTS,0,1, cat='Binary')
heater_coasting = LpVariable.dicts('Solar Heater Coasting',TIMEPOINTS,0,1, cat='Binary')
tempBelowMin = LpVariable.dicts('Solar Under Heated Water',TIMEPOINTS,0,1, cat='Binary')

NRG_input = LpVariable.dicts('Solar Energy input', TIMEPOINTS, 0, max_energy_input_per_interval, 'Continuous')
NRG_shortfall_Solar = LpVariable.dicts('Solar Energy Shortfall',TIMEPOINTS,0,None,'Continuous')
NRG_withdrawn_Solar = LpVariable.dicts('Solar Energy Withdrawn',TIMEPOINTS,0,None,'Continuous')
NRG_total = LpVariable.dicts('Solar Energy total', TIMEPOINTS, 0, 10, 'Continuous')
NRG_solar = LpVariable.dicts('Solar Energy solar', TIMEPOINTS, 0, 10, 'Continuous')



# available_solar[current_day, t]
# defining the cost function
ThreeBinary_start_time = time.time()
total_cost_Solar = sum(
  price_of_power[current_day,b] * NRG_input[a,b] + shortfall_penalty_range[j] * NRG_shortfall_Solar[a,b]
  for (a, b) in TIMEPOINTS )/lookback_length
prob += total_cost_Solar

#constraint
for t in TIMEPOINTS:
        prob += (NRG_shortfall_Solar[t] == energy_req[t] - NRG_withdrawn_Solar[t])
        prob += (NRG_shortfall_Solar[t] == energy_req[t] * temp_shortfall[t] / (t_min_shortfall - t_in[current_day]))
        prob += (NRG_total[t] <= (1-heater_coasting[t])*(max_energy_input_per_interval+available_solar[current_day, b]),'Solar Energy input constraint 1 {}'.format(t))
        prob += (NRG_total[t] >= heater_at_max[t] * (max_energy_input_per_interval+available_solar[current_day, b]),'Solar Energy input constraint 2 {}'.format(t))
        
        if Conservative_Penalty_Status:
         prob += (temp_shortfall[t] >= t_min_shortfall - conservative_sim_tank_temp[t],'Solar Conservative Temperature shortfall constraint {}'.format(t))
         # the following four constraints prevents MILP to have high amount of temperature shorftall when penalty is low.
         prob += (temp_shortfall[t] <= (t_min_shortfall - conservative_sim_tank_temp[t]+(1-tempBelowMin[t])*big_temp),'Solar coservative Temp lower limit shortfall constraint {}'.format(t))
         prob += (temp_shortfall[t] <= tempBelowMin[t]*big_temp)
         prob += (tempBelowMin[t]*big_temp >= t_min_shortfall - conservative_sim_tank_temp[t])
         prob += ((1-tempBelowMin[t])*big_temp >=  conservative_sim_tank_temp[t] - t_min_shortfall)
        else:
         prob += (temp_shortfall[t] >= (t_min_shortfall - sim_tank_temp[t]),'Solar Temperature upper limit shortfall constraint {}'.format(t))                       
         # the following four constraints prevents MILP to have high amount of temperature shorftall when penalty is low.
         prob += (temp_shortfall[t] <= (t_min_shortfall - sim_tank_temp[t]+(1-tempBelowMin[t])*big_temp),'Solar Temperature lower limit shortfall constraint {}'.format(t))
         prob += (temp_shortfall[t] <= tempBelowMin[t]*big_temp)
         prob += (tempBelowMin[t]*big_temp >= t_min_shortfall - sim_tank_temp[t])
         prob += ((1-tempBelowMin[t])*big_temp >=  sim_tank_temp[t] - t_min_shortfall)
for (a, b) in TIMEPOINTS:
        prob += (dummy_setpoint[b] == ts_setpoint[b] * (temp_resolution))
        #prob += (dummy_NRG_input[a,b] == NRG_input[a,b] * (NRG_resolution))
        prob += (sim_tank_temp[a, b] >= ts_setpoint[b] - heater_at_max[a, b] * big_temp,'Solar Thermostat setpoint constraint {}'.format((a, b)))
        prob += (sim_tank_temp[a, b] <= ts_setpoint[b] + heater_coasting[a, b] * big_temp, 'Solar Heater coasting constraint {}'.format((a, b)))
        # these two are the new constraint regarding adding solar energy to the problem. also, the thermodynamic energy input changed
        # to total energy rather than just electrical energy
        prob += (NRG_total[a, b] == NRG_solar[a,b] + NRG_input[a, b], ' Solar energy sum constraint {}'.format((a, b)))
        prob += (NRG_solar[a, b] <=  available_solar[current_day, b], ' solar limit constraint {}'.format((a, b)))
        # this is a new constraint. based on the value of the 'Hourly_TS_setpoint_interval', the code decides to keep the
        # thermostat setpoints hourly or keep it with the lenght of intervlas
        if int((b-1)/interval_per_hour)+1 == int((b)/interval_per_hour) == int((b+1)/interval_per_hour):
            for i in range(interval_per_hour):
                ts_setpoint[b-i] = ts_setpoint[b]
        if b == 1:
            i_prev = max(interval_set)
            d_prev = a
        else:
         i_prev = b - 1
         d_prev = a
        prob += (conservative_sim_tank_temp[a,b] == sim_tank_temp[d_prev,i_prev]+(- NRG_withdrawn_Solar[a,b]) / degree_of_water_per_kwh )  

        prob += (sim_tank_temp[a,b]*degree_of_water_per_kwh == conservative_sim_tank_temp[a,b]*degree_of_water_per_kwh + (NRG_total[a,b]) 
               - heat_loss_rate *degree_of_water_per_kwh*(conservative_sim_tank_temp[a,b] - t_amb[current_day,b]))

#=================================
# solves the problem using CPLEX.
#optimization_result = prob.solve(CPLEX_CMD(
#        options=['set emphasis mip 4',
#                 'set mip tolerances mipgap {}'.format(Optimality_gap),
#                 'set workmem 20000',
#                 'set timelimit {}'.format(Run_Time), 
#                 'set mip strategy file 3', 
#                 'set workdir {}'.format(tempdir)
#                         ],msg=1
#     ))
#Solar_time=time.time() - ThreeBinary_start_time
#print(" %s Solar Model" % (time.time() - start_time))
#=================================
# these are other solves that can be used to solve the model
optimization_result = prob.solve(PULP_CBC_CMD(msg=0))
#optimization_result = prob.solve(CPLEX_PY(mip=True,msg=True))
#optimization_result = prob.solve(GUROBI_CMD(msg=0))
#       optimization_result = prob.solve(GLPK_CMD(msg=0))

#================================
# calculates the total cost for each run based on optimizaed value that are found by solving the problem
electrical_Solar = sum(price_of_power[current_day,b] * NRG_input[a,b].value()  for (a, b) in TIMEPOINTS)/lookback_length
shortfall_Solar = sum(NRG_shortfall_Solar[a,b].value() for (a, b) in TIMEPOINTS)/lookback_length
#=======================================

temp_setpoints={}
# this line generates temperature setpoints based on the price for Apt&Goh method
for b in sorted(interval_set):
  temp_setpoints[b]=ts_setpoint[b].value()

# generates actual results based on termostate setpoint and  required energy. for more information please go to "Input/import.py"
Solar_dict={}
Solar_dic=Actual_Result_Generator(temp_setpoints,sim_tank_temp[a,24*(60/min_slot)].value()) 
methods_dictionary.update(Solar_dic)
Solar_dict.update({'Exp_C_Solar':electrical_Solar,'Exp_Dis_Solar':shortfall_Solar})
methods_dictionary.update(Solar_dict)

for (a, b) in sorted(TIMEPOINTS):
        OneDayDF.loc[b,'Act_temp_Solar']= sim_tank_temp[a,b].value()
        OneDayDF.loc[b,'set_temp_Solar']= ts_setpoint[b].value()
        OneDayDF.loc[b,'NRG_in_Elec']= NRG_input[a,b].value()
        OneDayDF.loc[b,'NRG_in_Solar']=NRG_solar[a, b].value()
# decided whats MILP&Goh and Du&Lu initial temperature should be. it is explained in the 'Main.py' more.
#init_temp(Initial_Temperature_Status,current_day)






