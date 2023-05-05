# definning the Pulp variables
prob = LpProblem('Smart Water Heater', LpMinimize)
dummy_setpoint = LpVariable.dicts('dummy setpoint', interval_set, t_min*temp_resolution, t_max*temp_resolution, 'Integer')
ts_setpoint = LpVariable.dicts('Thermostat setpoint', interval_set, t_min, t_max, 'Continuous')
NRG_input = LpVariable.dicts('Energy input', TIMEPOINTS, 0, max_energy_input_per_interval, 'Continuous')
temp_shortfall = LpVariable.dicts('Temperature shortfall',TIMEPOINTS, 0, t_min+5, 'Continuous')
heater_at_max = LpVariable.dicts('Max heater',TIMEPOINTS,0,1, cat='Binary')
NRG_shortfall_f = LpVariable.dicts('Energy Shortfall',TIMEPOINTS,0,None,'Continuous')
NRG_withdrawn_f = LpVariable.dicts('Energy Withdrawn',TIMEPOINTS,0,None,'Continuous')
sim_tank_temp = LpVariable.dicts('Simulated Tank Temp',TIMEPOINTS,t_min-20,t_max,'Continuous')

OneBinary_start_time = time.time()
# defining the cost function
total_cost_f = sum(
        price_of_power[current_day,b] * NRG_input[a,b] + shortfall_penalty_range[j] * NRG_shortfall_f[a,b]
        for (a, b) in TIMEPOINTS )
prob += total_cost_f

#constraint
for t in TIMEPOINTS:

        prob += (NRG_shortfall_f[t] == energy_req[t] - NRG_withdrawn_f[t])
        prob += (NRG_input[t] == heater_at_max[t] * max_energy_input_per_interval)
        prob += (temp_shortfall[t] >= t_min_range[j] - sim_tank_temp[t],'Temperature shortfall constraint {}'.format(t))
        prob += (NRG_shortfall_f[t] == energy_req[t] * temp_shortfall[t] / (t_min_range[j] - t_in[current_day]))
for (a, b) in TIMEPOINTS:

        # this is a new constraint. based on the value of the 'Hourly_TS_setpoint_interval', the code decides to keep the
        # thermostat setpoints hourly or keep it with the lenght of intervals
        if int((b-1)/interval_per_hour)+1 == int((b)/interval_per_hour) == int((b+1)/interval_per_hour):
            for i in range(interval_per_hour):
                ts_setpoint[b-i]=ts_setpoint[b]
        if b == 1:
            i_prev = max(interval_set)
            d_prev = a
        else:
         i_prev = b - 1
         
        prob += (
            sim_tank_temp[a,b]
            ==
            sim_tank_temp[a,i_prev]
            + (NRG_input[a,b] - NRG_withdrawn_f[a,b]) / degree_of_water_per_kwh
            - heat_loss_rate * (sim_tank_temp[a,b] - t_amb[current_day,b])
        )
#        prob += (dummy_setpoint[b] == ts_setpoint[b] * (temp_resolution))
        prob += (sim_tank_temp[a,b] >= ts_setpoint[b] - heater_at_max[a, b] * big_temp)
        prob += (sim_tank_temp[a,b] <= ts_setpoint[b] + (1-heater_at_max[a, b]) * big_temp)

#=================================
optimization_result = prob.solve(CPLEX_CMD(
        msg=1,
        options=['set emphasis mip 4',
                 'set workdir {}'.format(tempdir)]
     ))
# these are other solves that can be used to solve the model
#optimization_result = prob.solve(PULP_CBC_CMD(msg=0))
#optimization_result = prob.solve(CPLEX_PY(mip=True,msg=True))
#optimization_result = prob.solve(GUROBI_CMD(msg=0))
#       optimization_result = prob.solve(GLPK_CMD(msg=0))


print(" %s seconds for One binary Model" % (time.time() - OneBinary_start_time))

for (a, b) in sorted(TIMEPOINTS):
    ts_setpoint_normal[b]=ts_setpoint[b].value()
    sim_tank_temp_normal[a,b]=sim_tank_temp[a,b].value()
    NRG_input_normal[a,b]=NRG_input[a,b].value()
    NRG_Req_normal[a,b]=energy_req[a,b]
    at_max[a, b]=heater_at_max[a, b].value()
