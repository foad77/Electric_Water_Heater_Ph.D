temperature_setpoints={}
# this line generates temperature setpoints based on the price for Apt&Goh method
for b in sorted(interval_set):
  temperature_setpoints[b]=t_max-(price_of_power[current_day,b]-p_min)/(p_max-p_min)*(t_max-t_min_range[j]) 

# generates actual results based on termostate setpoint and  required energy. for more information please go to "Input/import.py"
cost_dic=Actual_Result_Generator(temperature_setpoints,temp_0_Apt) 
cost_dic.update({'Exp_C_Apt':None})
cost_dic.update({'Exp_Dis_Apt':None})
methods_dictionary.update(cost_dic)

#Apt_dict={}
#Apt_dict={'Exp_C_Apt':electrical_7,'Exp_Dis_Apt':shortfall_7,'Act_Dis_Apt':shortfall_7,'LastTemp_Apt':t_tank_7[max(interval_set)],'Act_C_Apt':electrical_7}
#methods_dictionary.update(Apt_dict)

resolution= 0.001
temp_0 = 40
def object_function(individual):
    
  global temp_0, resolution
  
  total=dict();total.clear()
  for day in day_set:  

      Ew1=dict();Ew2=dict();t_tank_conservative=dict();E_error=dict();NRG_short=dict();t_Actual=dict();E_Input=dict();t_setpoint=dict()
      dictionaries= [Ew1,Ew2,E_error,NRG_short,t_Actual,NRG_withdrawn,E_Input,t_shortfall];
      for d in dictionaries:
         d.clear()
      for b in sorted(interval_set):
        NRG_short[b]=0
        if b == 1:
            i_prev = max(interval_set)
        else:
            i_prev = b - 1            
        t_Actual[24*(60/min_slot)]=temp_0
        t_setpoint[b]=individual[b]
        t_Actual[b]=t_setpoint[b]
        NRG_withdrawn[b]=energy_req[day,b]
        E_Input[b]=degree_of_water_per_kwh * (t_Actual[b]*(1+heat_loss_rate) - heat_loss_rate * t_amb[current_day,b] - t_Actual[i_prev])+NRG_withdrawn[b]+resolution

        Ew1[b]=1; Ew2[b]=0
        
        if (E_Input[b] >= max_energy_input_per_interval):
          E_Input[b]=max_energy_input_per_interval
          t_Actual[b]=(1/(1+heat_loss_rate))*(((E_Input[b]-NRG_withdrawn[b])/degree_of_water_per_kwh)+t_amb[current_day,b]*heat_loss_rate+t_Actual[i_prev])
          
          while (abs(Ew1[b]-Ew2[b]) >= 0.001):      
                  
            t_shortfall[b] = t_min_shortfall - t_Actual[b]+resolution
            if (t_shortfall[b] <0):
                t_shortfall[b] =0
            Ew1[b] = energy_req[day,b] * t_shortfall[b] / (t_min_shortfall - t_in[current_day])+resolution
            k=  degree_of_water_per_kwh * (t_Actual[b]*(1+heat_loss_rate) - heat_loss_rate * t_amb[current_day,b] - t_Actual[i_prev])+resolution
            Ew2[b]=k+energy_req[day,b]-max_energy_input_per_interval

            NRG_short[b]=Ew1[b]
            t_Actual[b]=t_Actual[b]+0.001
            E_error[b]=abs(Ew1[b]-Ew2[b])

        if (E_Input[b] <=0):

          while (abs(Ew1[b]-Ew2[b]) >= 0.001):
            
            Ew1[b]=degree_of_water_per_kwh*(t_Actual[b]*(-1-heat_loss_rate)+ t_Actual[i_prev] + heat_loss_rate * t_amb[current_day,b])+resolution        
            t_shortfall[b] = t_min_shortfall - t_Actual[b]+resolution
            if (t_shortfall[b] <0):
                t_shortfall[b] =0
            NRG_short[b] = energy_req[day,b] * t_shortfall[b] / (t_min_shortfall - t_in[current_day])
            Ew2[b] = energy_req[day,b] - NRG_short[b]

            k=  degree_of_water_per_kwh * (t_Actual[b]*(1+heat_loss_rate) - heat_loss_rate * t_amb[current_day,b] - t_Actual[i_prev])
            E_Input[b]=k+Ew1[b]+resolution
            if (E_Input[b] <= -0.1):
                 Ew1[b]=1
                 Ew2[b]=0
    
            t_Actual[b]=t_Actual[b] +0.001
            E_error[b]=abs(Ew1[b]-Ew2[b])
            
        if (E_Input[b] >=0.1) and (E_Input[b] <=max_energy_input_per_interval-0.1) and (t_Actual[b] <= t_min_shortfall-0.2) :
            t_shortfall[b] = t_min_shortfall - t_Actual[b]+resolution
            NRG_short[b] = energy_req[day,b] * t_shortfall[b] / (t_min_shortfall - t_in[current_day])
            k=  degree_of_water_per_kwh * (t_Actual[b]*(1+heat_loss_rate) - heat_loss_rate * t_amb[current_day,b] - t_Actual[i_prev])+resolution
            E_Input[b]=k+energy_req_tomorrow[b]-NRG_short[b]+resolution 
           
      electrical_cost=sum(price_of_power[current_day,b] * E_Input[b]  for b in interval_set)                  
      shortfall_cost = sum(NRG_short[b] for b in interval_set)
      total[day]=  electrical_cost +  shortfall_cost 
  objective=sum(total[day] for day in day_set)
  return objective,



cost2=object_function(temperature_setpoints)