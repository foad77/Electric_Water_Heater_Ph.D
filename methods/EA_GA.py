#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#!clear
"""
Created on Fri Dec 25 09:21:29 2020

@author: foad
here i develop an evolutionary algorithm to solve the EWH problem.
here is the approach:
    basically, there are different approaches to solve a constraint problem. i used one of the methods in:
        http://www.academia.edu/download/3960584/10.1.1.92.6108.pdf
        it is a well-known paper regarding solving constraint problem using EA algorithms.
        there are four main approach to deal with the constraints.
        i use the mathod based on "penalty function" (section 3.2). it basically turns the constrained probelem to a
        non-constraint problem by moving the contraint to the cost function but with a penalty factor for
        each violated constaint.
        I specifically try to solve it with "annealing penalty" in section 3.2.3.
software:
    there a couple of liberaries to model a EA algorithm. I use "DEAP" which is flexible platform for formulating
    and solving EA algorithm. it's document says it supports parallel computation.
    I specifically followed this example (knapsack problem) which is a simple constrainted integer problem.
    https://github.com/DEAP/deap/blob/master/examples/ga/knapsack.py
    
installing DEAP for conda:
    https://anaconda.org/conda-forge/deap
    i used the second command, spyder IDE for some reason didn't recognized the installation path of the first command.
    
"""

import random
import numpy as np
from deap import algorithms, base, creator, tools


creator.create("Fitness", base.Fitness, weights=(-1,))
creator.create("Individual", np.ndarray, fitness=creator.Fitness)

toolbox = base.Toolbox() 

temperature_setpoints={}
for b in sorted(interval_set):
          temperature_setpoints[b]=t_max-(price_of_power[current_day,b]-p_min)/(p_max-p_min)*(t_max-t_min_range[j])
# Attribute generator
def ind_init(icls):
      # integer
    global temperature_setpoints
    ts_setpoint = np.random.randint(t_min*temp_resolution, t_max*temp_resolution, len(interval_set))/temp_resolution   

    ind = ts_setpoint
    return icls(ind)


toolbox.register("individual", ind_init, creator.Individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


    

resolution= 0
temp_0 = 40     
def object_function(individual):
  global temp_0, resolution,E_Input,t_Actual,t_setpoint
  total=dict();total.clear()
  step=0.005
  for day in day_set:  

      Ew1=dict();Ew2=dict();E_error=dict();NRG_short=dict();t_Actual=dict();E_Input=dict();t_setpoint=dict()
      dictionaries= [Ew1,Ew2,E_error,NRG_short,t_Actual,NRG_withdrawn,E_Input,t_shortfall];
      for d in dictionaries:
          d.clear()
      for b in sorted(interval_set):
        NRG_short[b]=0
        if b == 1:
            i_prev = max(interval_set)
        else:
            i_prev = b - 1
        
        try: t_Actual[24*(60/min_slot)]=t_tank_our[24*(60/min_slot)]    
        except:t_Actual[24*(60/min_slot)]=temp_0
        
        try: t_setpoint[b]=float(individual[b])         
        except:t_setpoint[b]=individual[list(interval_set).index(b)]  
        
        try: del t_setpoint[b][0]
        except: pass
    
        try:t_Actual[b]=t_setpoint[b][0]
        except: t_Actual[b]=t_setpoint[b]
        
        NRG_withdrawn[b]=energy_req[day,b]
        E_Input[b]=degree_of_water_per_kwh * (t_Actual[b]*(1+heat_loss_rate) - heat_loss_rate * t_amb[current_day,b] - t_Actual[i_prev])+NRG_withdrawn[b]+resolution

        Ew1[b]=1; Ew2[b]=0
        
        if (E_Input[b] >= max_energy_input_per_interval):
          E_Input[b]=max_energy_input_per_interval
          t_Actual[b]=(1/(1+heat_loss_rate))*(((E_Input[b]-NRG_withdrawn[b])/degree_of_water_per_kwh)+t_amb[current_day,b]*heat_loss_rate+t_Actual[i_prev])    
          
          while (abs(Ew1[b]-Ew2[b]) >= 0.1):                        
            t_shortfall[b] = t_min_shortfall - t_Actual[b]+resolution
            if (t_shortfall[b] <0):
                t_shortfall[b] =0
            Ew1[b] = energy_req[day,b] * t_shortfall[b] / (t_min_shortfall - t_in[current_day])+resolution
            k=  degree_of_water_per_kwh * (t_Actual[b]*(1+heat_loss_rate) - heat_loss_rate * t_amb[current_day,b] - t_Actual[i_prev])+resolution
            Ew2[b]=k+energy_req[day,b]-max_energy_input_per_interval
            NRG_short[b]=Ew1[b]
            t_Actual[b]=t_Actual[b]+step
            E_error[b]=abs(Ew1[b]-Ew2[b])
            
        if (E_Input[b] <=0):
            
          E_Input[b]=0
          t_Actual[b]=(1/(1+heat_loss_rate))*(((E_Input[b]-NRG_withdrawn[b])/degree_of_water_per_kwh)+t_amb[current_day,b]*heat_loss_rate+t_Actual[i_prev])     
          
          while (abs(Ew1[b]-Ew2[b]) >= 0.001):                             
            t_shortfall[b] = t_min_shortfall - t_Actual[b]+resolution
            if (t_shortfall[b] <0):
                t_shortfall[b] =0
            Ew1[b]=degree_of_water_per_kwh*(t_Actual[b]*(-1-heat_loss_rate)+ t_Actual[i_prev] + heat_loss_rate * t_amb[current_day,b])+resolution 
            NRG_short[b] = energy_req[day,b] * t_shortfall[b] / (t_min_shortfall - t_in[current_day])
            Ew2[b] = energy_req[day,b] - NRG_short[b]
            k=  degree_of_water_per_kwh * (t_Actual[b]*(1+heat_loss_rate) - heat_loss_rate * t_amb[current_day,b] - t_Actual[i_prev])
            E_Input[b]=k+Ew1[b]+resolution
            if (E_Input[b] <= -0.1):
                  Ew1[b]=1
                  Ew2[b]=0            
            t_Actual[b]=t_Actual[b] +step
            E_error[b]=abs(Ew1[b]-Ew2[b]) 
        if (E_Input[b] >=0.1) and (E_Input[b] <=max_energy_input_per_interval-0.1) and (t_Actual[b] <= t_min_shortfall-0.2) :
            
            t_shortfall[b] = t_min_shortfall - t_Actual[b]+resolution
            NRG_short[b] = energy_req[day,b] * t_shortfall[b] / (t_min_shortfall - t_in[current_day])
            k=  degree_of_water_per_kwh * (t_Actual[b]*(1+heat_loss_rate) - heat_loss_rate * t_amb[current_day,b] - t_Actual[i_prev])+resolution
            E_Input[b]=k+energy_req_tomorrow[b]-NRG_short[b]+resolution     
      electrical_cost=sum(price_of_power[current_day,b] * E_Input[b]  for b in interval_set)                  
      shortfall_cost = sum(NRG_short[b] for b in interval_set)
      total[day]=  electrical_cost +  shortfall_cost   
          
  objective=sum(total[day] for day in day_set)/lookback_length
  return objective,



# # Operator registering
toolbox.register("evaluate", object_function)
#toolbox.decorate("evaluate", tools.DeltaPenalty(feasible, 0,distance))
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.1)
toolbox.register("select", tools.selNSGA2)

print( "--------------------------------------------------------------------------------")
print( "the  Genetic Algorithm (GA) optimization starts ...." ) 
def main():
    random.seed(170)
    NGEN = 80
    MU = 100
    LAMBDA = 40
    CXPB = 0.5
    MUTPB = 0.5
    
    pop = toolbox.population(n=MU)
    hof = tools.HallOfFame(1, similar=np.array_equal)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean, axis=0)
    stats.register("std", np.std, axis=0)
    stats.register("min", np.min, axis=0)
    stats.register("max", np.max, axis=0)
    
    algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats,
                              halloffame=hof)

    
    return pop, stats, hof
                 
if __name__ == "__main__":
    main()  
 
for b in sorted(interval_set):
  energy_req[current_day,b]=energy_req_tomorrow[b] 
dict_t_setpoint=list()
for key, value in t_setpoint.items():
   # temp = [key,value]
    temp = value
    dict_t_setpoint.append(temp)  
object_function(dict_t_setpoint)

   
for b in sorted(interval_set):
    
        OneDayDF.loc[b,'Act_temp_EA_GA']= t_Actual[b] 
        OneDayDF.loc[b,'set_temp_EA_GA']= t_setpoint[b]
        OneDayDF.loc[b,'NRG_in_EA_GA']= E_Input[b]
try:
    print( "--------------------------------------------------------------------------------")
    print( "--- $%s is the Total MILP COST of Stochastic Optimization (past days)" % (total_cost_f.value()))
    print( "--- $%s when decision valiable is applied on tomorrow withdrawal (tomorrow)" % (electrical_f_actual+shortfall_f_actual))
    print( "--------------------------------------------------------------------------------")  
    
except: pass      
        
        
        