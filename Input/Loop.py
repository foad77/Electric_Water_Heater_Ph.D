# this file consist of the main loop. when every thing is loaded into memory, the loop starts
# it also defines whether the value for 'current_day' and 'penalty_factor' should be taken from command
# or from inside of the file. if no argument is passed in command line, the code takes these values from inside of the code,
# other wise, it will take the values from the command line arguments. 
# so, the code works in both methods, with or without arguments.
import pandas as pd
methods_series=pd.Series(methods).astype(str)
#===========================================================
if len(sys.argv) == 1:
# it loops through different values of penalty factor. it runs the code for each value of penalty factor
# the 'frange' fuction creates a fractual range between 'k_min' and 'k_man' with 'step' steps
  if test_mode:
      loop=1
  else:
       loop=1   
  for current_day in range(tomorrow,tomorrow+loop):
      if methods_series[0]=="Negotiator":
       #current_day=unit
           pass  
      #print (current_day)
      #import sys; sys.exit()
       
 
      # it loops through tomorrow days. e.g., if tomorrow days are 5(loop=5), it loops though the methods (out method, Apt&Goh and Du&Lu) for
      # 5 days and reports the average of these 5 days as cost of specefic value for a singular penalty facotor.          
      for j in range(0,size(penalty_vector)):
          exec(compile(open('Input/Region_generator.py', "rb").read(), 'Input/Region_generator.py', 'exec'))

          #execute_file('Input/Region_generator.py')
          print (current_day,j)
          for m in methods_series.keys():
            if (newdf.loc[(penalty_vector[j],current_day),'Act_C_{}'.format(methods_series[m])] != check_if_runned) and not test_mode:                 
                 print ('{} penalty and {} tomorrow was runned for {}'.format(penalty_vector[j],current_day,methods_series[m]))            
            else:                
                #try:
                    exec(compile(open('methods/{}.py'.format(methods_series[m]), "rb").read(), 'methods/{}.py'.format(methods_series[m]), 'exec'))
             
                #except:execute_file('methods/MILP.py');execute_file('methods/{}.py'.format(methods_series[m]))
          
          execute_file('Result/logging/logger.py')  


if len(sys.argv) == 2:
    current_day = int(sys.argv[1])
    j=1 
    exec(compile(open('Input/Region_generator.py', "rb").read(), 'Input/Region_generator.py', 'exec'))
    exec(compile(open('methods/Negotiator.py', "rb").read(), 'methods/Negotiator.py.py', 'exec'))
    exec(compile(open('Result/logging/logger.py', "rb").read(), 'Result/logging/logger.py', 'exec'))
    exit()

if len(sys.argv) == 3:
     current_day = int(sys.argv[1])
     shortfall_penalty_range.clear()
     t_min_range.clear()
     j=1 
     execute_file('Input/Region_generator.py')       
     shortfall_penalty_range[1]=float(sys.argv[2])
     t_min_range[1]=t_min
     for m in methods:
            if newdf.loc[(penalty_vector[j-1],current_day),'Act_C_{}'.format(m)] != check_if_runned:                 
                 print ('{} penalty and {} tomorrow was runned'.format(penalty_vector[j-1],current_day))
                 sys.exit()
            else:
                execute_file('methods/{}.py'.format(m))
     execute_file('Result/logging/logger.py')
     sys.exit()
     
if len(sys.argv) == 4:
     shortfall_penalty_range.clear()
     t_min_range.clear()
     j=1
     current_day = int(sys.argv[1])
     lookback_length = int(sys.argv[3])    
     execute_file('Input/Region_generator.py')
     shortfall_penalty_range[1]=float(sys.argv[2])
     t_min_range[1]=t_min
     for m in methods:
            if newdf.loc[(penalty_vector[j],current_day),'Act_C_{}'.format(m)] != check_if_runned:                 
                 print ('{} penalty and {} tomorrow was runned'.format(penalty_vector[j],current_day)) 
                 sys.exit()
            else:
                execute_file('methods/{}.py'.format(m))
     execute_file('Result/logging/logger.py') 
     sys.exit()