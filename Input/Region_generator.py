### this code is runned once for each penalty factor value and tomorrow day. based on these values, it loads different part of
# excel file as an input file.
#=============================
# reseting all input values
Group=[t_in,t_amb,price_of_power,tomorrow_volume_withdrawn,tomorrow_t_out,t_out,historical_volume_withdrawn,day_set,available_solar]
for g in Group:
    g.clear()
#=========================================================================
### Region for tomorrow
## the code is now updated and historical days are before tomorrow.
lookback_start_row_tomorrow = 24*(60/min_slot)*(current_day-1)+2
lookback_end_row_tomorrow  = 24*(60/min_slot)*(current_day)+1
region_label_tomorrow = 'A{}:N{}'.format(int(lookback_start_row_tomorrow), int(lookback_end_row_tomorrow))
#print('{}').format(region_label_tomorrow)
region_tomorrow = sheet[region_label_tomorrow]
for r in region_tomorrow:
        z = int(r[0].value)
        t = int(r[1].value)
        interval.add(t)
        t_in[z] = (float(r[6].value)-32)/1.3
        t_amb[current_day, t] = float(r[4].value)
        price_of_power[current_day, t]= float(r[5].value)
        tomorrow_volume_withdrawn[current_day, t] = float(r[2].value) 
        tomorrow_t_out[current_day, t]=r[3].value
        available_solar[current_day, t]=r[7].value
#========================================================================
### Region for Historical Days
#print('{}'.format(current_day))
if current_day>=(lookback_length+1):
   lookback_end_row = 24*(60/min_slot)*(current_day-1)+1
   lookback_start_row = lookback_end_row - 24*(60/min_slot)*(lookback_length)+1
   region_label = 'A{}:J{}'.format(int(lookback_start_row), int(lookback_end_row))
   region = sheet[region_label]
   region2=region
   
if current_day==(lookback_length):
   end_row2 = 24*(60/min_slot)*(365)+1
   start_row2 = end_row2 - 24*(60/min_slot)*((lookback_length-current_day)+1)+1
   region_label2 = 'A{}:J{}'.format(int(start_row2), int(end_row2))
   region2 = sheet[region_label2] 
   region=region2
     
if current_day<=(lookback_length-1):   
   start_row1 = 2
   end_row1 = 24*(60/min_slot)*(current_day-1)+1
   region_label1 = 'A{}:J{}'.format(int(start_row1), int(end_row1))
   region = sheet[region_label1]

   end_row2 = 24*(60/min_slot)*(365)+1
   start_row2 = end_row2 - 24*(60/min_slot)*((lookback_length-current_day)+1)+1
   region_label2 = 'A{}:J{}'.format(int(start_row2), int(end_row2))
   region2 = sheet[region_label2] 
    
#===========================
for r in region:
        # each row contains date, interval, water temperature, withdrawal
        d = int(r[0].value)
        i = int(r[1].value)
        day_set.add(d)
        interval_set.add(i)
        t_out[d, i] = r[3].value
        historical_volume_withdrawn[d, i] = float(r[2].value) # also convert to liters!
for r in region2:
        # each row contains date, interval, water temperature, withdrawal
        c = int(r[0].value)
        k = int(r[1].value)
        day_set.add(c)
        interval_set.add(k)
        t_out[c, k] = r[3].value
        historical_volume_withdrawn[c, k] = float(r[2].value) # also convert to liters!        
#===========================
# loading the price for price negotiating algorithm  
# interval_agg=set()
# if len(sys.argv) == 2:
#     ww = load_workbook('Result/Price_negotiating_algorithm/temp/price.xlsx', read_only = True, data_only=True)
#     region_tomorrow=ww['temp_price']['A2:B25'];price_of_power.clear()    
#     for k in region_tomorrow:
#          q = int(k[0].value);interval_agg.add(q);price_of_power[current_day, q]= float(k[1].value)
#if methods_series[0]=="Negotiator":
# for b in interval_set:
#    price_of_power[current_day, b]=Bidding_iteration  .loc[(s,b),'price']

      
        
#===================================        
### these four value are used for visualization and finding the per unit value.
p_min=min(price_of_power.values())
p_max=max(price_of_power.values())
# p_ave=mean(price_of_power.values());p_dev=std(price_of_power.values())

#==============================
# the 'status' function defines whether the code should be runned in stochastic or perfect forecast mode
# based on the value of 'stochastic_status'. if it is 'True' it loads the past days withdrawals and uses their average for prediction of tomorrow 
# tomorrow for du&Lu and Apt&Goh. also, out method is runned through all the past days.
# if it is "False'. it means perfect forecast situation. it loads tomorrow withdrawal as the prediction of tomorrow withdrawal.
# then, the code is runned only for tomorrow and 'lookback_lenght' is disabled (for all methods)
status(stochastic_status,day_set,historical_volume_withdrawn,tomorrow_volume_withdrawn,tomorrow_t_out,t_out)

#=========================================
#generates requied energy based on tomorrow water inlet temperature and historical withdrawal data.
# it is used when the code runs in perferct forecast mode.then, this value is used as the prediction for the methods.
TIMEPOINTS = [(a, b) for a in day_set for b in interval_set]
for b in interval_set:
    energy_req_tomorrow[b] = tomorrow_volume_withdrawn[current_day,b]  * (max(tomorrow_t_out[current_day,b],t_min)-t_in[current_day]) * specific_heat
#=========================================
### calculating requiered energy for the past days based on historical data
for (a, b) in TIMEPOINTS:
    energy_req[a,b] = historical_volume_withdrawn[a,b] * (max(t_out[a,b],t_min)-t_in[current_day]) * specific_heat
#=========================================
### it find the average of  requiered energy for the past days.
### it is used as prediction for the Du&Lu and Apt&goh.
if len(sys.argv) == 1:
  for i in interval_set:
    energy_req_average[i]= np.sum(energy_req[a,i] for a in day_set)/lookback_length
#=====================================================================
# since Du&Lu and Apt&Goh produce POINTS ob cost_Vs_Doscomfort, this can be used to creat a CURVE on the graph by changing the minimum 
# temperature. the option that whether we want to have a fixed minimum temperature or ranged minimum temperature is made by
# the 'penalty' function
step=(t_min_shortfall-t_min+0.0001)/(len(penalty_vector))
t_min_range[j]=j*step + t_min
#=================================
# created a range for penalty factor. the main loop of the code is based on this variable
#shortfall_penalty_range[j]=((shortfall_penalty_max-shortfall_penalty_min)/(k_max-k_min))*(j-k_min)+shortfall_penalty_min
if len(sys.argv) == 1:
  shortfall_penalty_range.clear()
  shortfall_penalty_range[j]=penalty_vector[j]
if len(sys.argv) == 2:
    shortfall_penalty_range[j]=2
#=================================
# decides wether should we run the code on a ranged minimum temperature of fixed one. the value of the function is loaded from 
# the 'Import.py' file
penalty(Ranged_Temperature_penalty_status,t_min_range,t_min)
#===================================
# decides whether thermostat setpoints should be shorter or it should be kept hourly.
#the value of the function is loaded from  the 'Import.py' file.
short_TS_Interval(Hourly_TS_setpoint_interval)
#======================================
formulator(problem_formulator_status)
#=============================================
#==========================================================
# this is an empty dictionary to bridge old names into new names for new saving method'
methods_dictionary.clear()
 
# decided whats MILP&Goh and Du&Lu initial temperature should be. it is explained in the 'Main.py' more.
init_temp(Initial_Temperature_Status,current_day)

