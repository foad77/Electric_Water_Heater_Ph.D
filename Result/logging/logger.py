# logging the result of optimization for each loook_back, minutes of interval, penalty factor and tomorrow (day):
# the result for each indivudual combination of above sets is saved seperatly. So, if we needed to rerun the code, we can skip the previously solved problem 
# to avoid confusion, data is saved seperately. the way I planned to save it is like this: first, a folder for 
# each look_back and minute_interval is created. inside this directory, various subdirectories are created. in each 
# subdirectory, a .csv file is created that saves the optimization result for each tomorrow day.
#=========================================

#===============================
# """for storing energy input to pass to the aggregator.py (for price flatening algorithm)"""
# if len(sys.argv) == 2:
#    #tempDf= pd.DataFrame()
#    for b in interval_set:     
#       tempDf.loc[b,'unit_x']= NRG_input[current_day,b].value()
#    with pd.ExcelWriter('Result/Price_negotiating_algorithm/temp/energy_input.xlsx') as writer:
#      tempDf.to_excel(writer, sheet_name='temp_energy',index=False)
   
      
#========================================      
# first we create a directory for each pair of look_back and minute_interval

if len(sys.argv) >= 3:
    # if the number of arguments are less than 3, it means that no arguments are passed from the CMD.
    # therefore, the value from penalty is taken from the inside of the code.
    # if it is bigger than 3, it means that an argument is passed to the code through the CMD
    # and it should be replaced by the value value that is defined inside of the code
   current_Ps = float(sys.argv[2])
else:
    if len(sys.argv) == 1:
      current_Ps= penalty_vector[j]
    else:
     current_Ps= penalty_vector[j-1]   

try:
# for j in range(0,resolution):
#     for current_day in range(tomorrow,tomorrow+loop):                 
 for k in names_combination:
                newdf.loc[(penalty_vector[j],current_day),k] = methods_dictionary[k]

#writer = pd.ExcelWriter(Current_File, engine='xlsxwriter') 
 dd= newdf.copy()
 dd.reset_index(inplace=True)
 if not test_mode:
    dd.to_excel(Current_File,engine='xlsxwriter',index=False)    
    writer.save()   
except: pass
if len(sys.argv) == 1:
    for (a, b) in sorted(TIMEPOINTS):
      OneDayDF.loc[b,'Price']=price_of_power[current_day,b]
      OneDayDF.loc[b,'NRG_Req']=energy_req_tomorrow[b]
      OneDayDF.loc[b,'Solar']=available_solar[current_day,b]

     