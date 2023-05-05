#=============================
# calcuated the tottal energy needed for study day (study day could be tomorrow if code is in perfect forecast mode or it can be the
# the average of all past days in stochastic mode)
# Du&Lu method fisrt calculates the total needed energy of that day based on perfect forecast.
# when it knows how much energy is neede for that day, uses the cheapest hour of that day to provide the required energy considering
# the fact that temperature can not go above or below meinimum.
# each time the temperature constraint is violated, it reschedule the energy alocation plan to temperature within the limmits.
q_total=0
q_total = sum(energy_req_average[i] for i in interval_set)
#=====================================
#reseting the variable values to zero
electrical_du=0;shortfall_du=0;shortfall_du_actual=0
#===========
# it is set to zero at the start of each loop
q_supplied=0
#================
# main loop
for b in interval_set:
        i_prev = b - 1
        t_tank[0]=temp_0_Du
        q_required=abs(q_total - q_supplied)
        UC[b]=U_c(q_required,b)
        q_sup[b]=UC[b]*max_energy_input_per_interval
        
        t_tank[b]=(((q_sup[b]-energy_req_average[b])/degree_of_water_per_kwh)+t_tank[i_prev])
        if (t_tank[b] >t_max):
                t_tank[b] =t_max
                q_sup[b]=energy_req_average[b]+ degree_of_water_per_kwh * (t_tank[b]*(1) - t_tank[i_prev])
        if (t_tank[b] <t_min_range[j]) and (q_sup[b] <max_energy_input_per_interval):
            while  (q_sup[b] < max_energy_input_per_interval):
                if (t_tank[b] >= t_min_range[j]) :
                    break
                q_sup[b]=q_sup[b]+0.01
                t_tank[b]=(((q_sup[b]-energy_req_average[b])/degree_of_water_per_kwh)+t_tank[i_prev])

        
        UC[b]=q_sup[b]/max_energy_input_per_interval
        t_shortfall[b] = t_min_range[j] - t_tank[b]
        if (t_shortfall[b] <0):
                t_shortfall[b] =0
        NRG_shortfall[b] = energy_req_average[b] * t_shortfall[b] / (t_min_range[j] - t_in[current_day])
        NRG_withdrawn[b] =  energy_req_average[b] - NRG_shortfall[b]
               
        q_supplied=q_supplied+q_sup[b]
#=============================
#calculating costs
electrical_du= sum(price_of_power[current_day,b] * q_sup[b] for b in interval_set)
shortfall_du = sum(NRG_shortfall[b] for b in interval_set)
print ("")
#===========================


t_tank_actual_conservative=dict()
for b in interval_set:
    
        i_prev = b - 1
        t_tank_actual[0]=temp_0_Du       
        t_tank_actual[b]=(((q_sup[b]-energy_req_tomorrow[b])/degree_of_water_per_kwh)+t_tank_actual[i_prev])
        t_shortfall_actual[b] = t_min_range[j] - t_tank_actual[b]
        if (t_shortfall_actual[b] <=0):
                t_shortfall_actual[b] =0
        # conservative temperature
        t_tank_actual_conservative[b]=(((-energy_req_tomorrow[b])/degree_of_water_per_kwh)+t_tank_actual[i_prev])    
        # if 'True' it replace actual temperature with conservative one to calculate shortfall
        if Conservative_Penalty_Status:
         t_shortfall_actual[b] = t_min_range[j] - t_tank_actual_conservative[b]
         if (t_shortfall_actual[b] <=0):
                t_shortfall_actual[b] =0
         # these lines added to compensate when energy temperature falls below a threshhold       
        while (t_shortfall_actual[b] >0):           
            q_sup[b]=q_sup[b]+0.001
            t_tank_actual[b]=(((q_sup[b]-energy_req_tomorrow[b])/degree_of_water_per_kwh)+t_tank_actual[i_prev])
            t_shortfall_actual[b] = t_min_range[j] - t_tank_actual[b]
            if q_sup[b] >= max_energy_input_per_interval:
                break  
        while (t_tank_actual[b] >t_max):           
            q_sup[b]=q_sup[b]-0.001
            t_tank_actual[b]=(((q_sup[b]-energy_req_tomorrow[b])/degree_of_water_per_kwh)+t_tank_actual[i_prev])
            if q_sup[b] <= 0:
                break 
            
        NRG_shortfall_actual[b] = energy_req_tomorrow[b] * t_shortfall_actual[b] / (t_min_range[j] - t_in[current_day])
        #NRG_withdrawn_actual[b] =  energy_req_tomorrow[b] - NRG_shortfall_actual[b]

        OneDayDF.loc[b,'Act_temp_Du']= t_tank_actual[b]
        OneDayDF.loc[b,'NRG_in_Du']= q_sup[b]
shortfall_du_actual = sum(NRG_shortfall_actual[b] for b in interval_set)
if shortfall_du_actual <0:
    shortfall_du_actual=0
cost_du_actual = sum(q_sup[b]*price_of_power[(int(current_day),b)] for b in interval_set)
Du_dict={}
Du_dict={ 'Exp_C_Du':electrical_du,'Exp_Dis_Du':shortfall_du,'Act_Dis_Du':shortfall_du_actual,
 'LastTemp_Du':t_tank_actual[max(interval_set)],'Act_C_Du':cost_du_actual,
                                                                          }
methods_dictionary.update(Du_dict)
