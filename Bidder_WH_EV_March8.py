from __future__ import division;import platform
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# eliminate rounding
round = lambda x, *args: x
# if platform.system() == 'Linux':
#   !clear
"""
Created on Sat May 23 11:18:49 2020

@author: foad
"""

'''
this set is going to be the units. for example, [2,3,88,150] means a network with 4 units 
while 2 referes to the consumption pattern of first units in the excel file. 150 means the
consumption pattern of forth unit which i 150th day from excel file.
'''
user_pattern=[99,100,105];
    # adjust the next line to change the number of vehicles bidding
    # (len(user_pattern) assigns 1 vehicle per user)
#ev_count = len(user_pattern)
"""
the difference between S_best and S_known. if the "gap"  is smaller than this value, loop will stop.
"""
iteration=15
optimality_gap=-50
   
#===========================================
## some model paramters.
min_slot=60;interval_per_hour=60/min_slot; specific_heat = 0.001148;t_min = 25;t_in=13.88;t_out=54.4
penalty_shortfall=2;
US_average_price=0.2 
#=============================================
'''
next, we read the corresponding days from the excel file.
'''
from openpyxl import load_workbook;import subprocess,os,sys;import pandas as  pd;import numpy as np;import time; import pulp
from pyomo.environ import *;import pyomo.environ as pyo;from pyomo.opt import SolverFactory; import xlsxwriter
import matplotlib.pyplot as plt
# this package is used to creat animation
from celluloid import Camera # getting the camera
sys.path.insert(0, './methods') # this line tells python where to look for "ev_bids.py"
from ev_bids import get_ev_bid

sys.path.insert(0, './methods') # this line is to tell python where to look for the "ev_bids.py"
wb = load_workbook('Input/withdrawal/usage.xlsx', read_only = True, data_only=True)  
sheet = wb['{}min_usage'.format(min_slot)]   

#=========================================================================
# loading consumption pattern of each unit from the excel file
interval=set();unit_withdrawn_pattern=dict();price=dict()
for unit in user_pattern:
    lookback_start_row_tomorrow = 24*(60/min_slot)*(unit-1)+2
    lookback_end_row_tomorrow  = 24*(60/min_slot)*(unit)+1
    region_label_tomorrow = 'A{}:N{}'.format(int(lookback_start_row_tomorrow), int(lookback_end_row_tomorrow))
    region_tomorrow = sheet[region_label_tomorrow]
    for r in region_tomorrow:
        z = int(r[0].value)
        t = int(r[1].value)
        interval.add(t)
        unit_withdrawn_pattern[unit, t] = float(r[2].value)*(max(t_out,t_min)-t_in) * specific_heat
#========================================================================
'''
creating p^{0}. the initial price vector based on averaging policy which will be broadcasted to the units the solve the optimization problem 
based on this initial price and their own comsumption pattern.
'''
# i had a short look into data. it seems the price range is between 0-1 dollar and the withdrawal was about 0-20 liter most of the time
# so for them to be in the same scare, i selected convesion rate of 1/20 just forthe sake of experiment. furthure analysis and
# investigation could be made on price policy in the furture.s
conversion_rate=1
for hour in interval:
    price[0,hour]=(1/len(user_pattern))*(1/conversion_rate)*(sum([unit_withdrawn_pattern[unit, hour] for unit in user_pattern]))
max_price=max(price.values())   
for hour in interval:
    price[0,hour]=price[0,hour]/max_price+0.02
#add price to Df
#========================================================================
"""creating a data frame to save the price and energy inputs"""  
#===========
#creating index. we have two: iteration and intervals
iteration_set=[]
for i in range(0,iteration+1):
        iteration_set.append(i)
interval_set=[]
for i in range(1,24*int(interval_per_hour)+1):
        interval_set.append(i)
iterables = [iteration_set, interval_set]
indexing=pd.MultiIndex.from_product(iterables, names=['iteration', 'interval'])

user_list_names=['price','gap','S_best','S_known','STD_price','PAR_price','STD_demand','PAR_demand','user_payment','generation_cost_1','generation_cost_2','generation_cost_total','benefit_total','demand_total']  
#user_list_names.append('price')
house_list=[]
for  hours in user_pattern:
    srts='House_{}'.format(hours)
    house_list.append(srts)
    user_list_names.append(srts)
Bidding_iteration= pd.DataFrame(index=indexing,columns=user_list_names)
Bidding_iteration.fillna(0,inplace=True)
Bidding_iteration.head()
#========================================================================
#adding P_0 to the data frame
for b in interval_set:
    #for unit in user_pattern:
       #Bidding_iteration.loc[(0,b),'House_{}'.format(unit)]=round(unit_withdrawn_pattern[unit, b],2)
       #Bidding_iteration.loc[(0,b),'demand_total']=round(sum([Bidding_iteration.loc[(0,b),unit] for unit in house_list]),2)
    Bidding_iteration.loc[(1,b),'price']=round(price[0,b],2)
Bidding_iteration.loc[(0,1),'benefit_total']=penalty_shortfall*round(Bidding_iteration.groupby('iteration').demand_total.sum()[0],2) 
#=============================================================
"""this is temporary dataframe that is used in the logger.py file to store energy input for the aggregator
model. note: if data frame creation is moved to the logger file, it won't save the output for some reason. this could also
be moved to the aggregator.py too """
tempDf= pd.DataFrame()
#==============================================================
# #the main loop
iteration_set.remove(0)
for s in iteration_set:
    for unit in user_pattern:
        exec(compile(open('Solve.py', "rb").read(), 'Solve', 'exec'))     
    ########
    for b in interval_set:
        Bidding_iteration.loc[(s,b),'demand_total']=round(sum([Bidding_iteration.loc[(s,b),unit] for unit in house_list]),2)
        #Bidding_iteration.loc[(s,b),'generation_cost_1']=US_average_price*(sum(pyo.value(model.weight_vector[i])*Bidding_iteration.loc[(i,b),'demand_total'] for i in weight_set))**2
        Bidding_iteration.loc[(s,b),'generation_cost_2']=US_average_price*Bidding_iteration.loc[(s,b),'demand_total']*Bidding_iteration.loc[(s,b),'demand_total']

        
    Bidding_iteration.loc[(s,1),'STD_price']= round(Bidding_iteration.groupby('iteration').price.std()[s],3)
    Bidding_iteration.loc[(s,1),'PAR_price']= round(Bidding_iteration.groupby('iteration').price.max()[s]/Bidding_iteration.groupby('iteration').price.mean()[s],3)
    
    Bidding_iteration.loc[(s,1),'STD_demand']= round(Bidding_iteration.groupby('iteration').demand_total.std()[s],3)
    Bidding_iteration.loc[(s,1),'PAR_demand']= round(Bidding_iteration.groupby('iteration').demand_total.max()[s]/Bidding_iteration.groupby('iteration').demand_total.mean()[s],3)
    Bidding_iteration.loc[(s,1),'benefit_total']=penalty_shortfall*round(Bidding_iteration.groupby('iteration').demand_total.sum()[s],2)
    Bidding_iteration.loc[(s,1),'generation_cost_total']=Bidding_iteration.groupby('iteration').generation_cost_2.sum()[s]
    Bidding_iteration.loc[(s,1),'user_payment']=sum(Bidding_iteration.loc[(s-1,b),'demand_total']*Bidding_iteration.loc[(s,b),'price'] for b in interval_set)
    
    # #############
    # # get EV bids for this iteration    
    # # adjust the next line to avoid charging above a certain price
    # ev_max_price = 10  # $/kWh

    # ev_prices = Bidding_iteration.loc[s, 'price'].reset_index()
    # ev_prices['hour'] = ev_prices['interval'] - 1

    # # get bid
    # ev_bids, ev_windows = get_ev_bid(ev_prices, ev_count, ev_max_price)
    
    # # set ev_bids indexing to match Bidding_iteration
    # # (needs both index columns or else df.loc[first_index, col] = series 
    # # will assign NaN; see https://stackoverflow.com/q/68986766/)
    # ev_bids['iteration'] = s
    # ev_bids['interval'] = ev_bids['hour'] + 1
    # ev_bids = ev_bids.drop('hour', axis=1).set_index(['iteration', 'interval'])

    # # add ev bids to the bidding data frame (adding columns if needed)
    # Bidding_iteration.loc[ev_bids.index, ev_bids.columns] = ev_bids
    # Bidding_iteration.loc[s, 'demand_total'] = Bidding_iteration.loc[s, 'demand_total'] + ev_bids.sum(axis=1)
    # Bidding_iteration.loc[(s,1), 'benefit_total'] += ev_max_price * ev_bids.sum().sum()

    # # add ev_windows to the dataframe too
    # ev_windows['iteration'] = s
    # ev_windows['interval'] = ev_windows['hour'] + 1
    # ev_windows = ev_windows.drop('hour', axis=1).set_index(['iteration', 'interval'])
    # Bidding_iteration.loc[ev_windows.index, ev_windows.columns] = ev_windows

    # end EV bids
    #########

    weight_set=set()
    weight_set.clear()
    for i in range(1,s+1):
        weight_set.add(i)
    model = ConcreteModel(name="(Appliance bidding)")
    #Variables
    #=====================================================
    model.weight_vector = Var(weight_set,  bounds=(0,1), within=NonNegativeReals)
    #========================================
    #Constraints definition
    
    def Const_1(model,a):
          return  1 == sum(model.weight_vector[i] for i in weight_set)
    model.Const_1_ = Constraint(weight_set, rule=Const_1)

    #========================================
    #objective function

    def benefit_rule(model):
        global marginal_cost
        benefit = sum(model.weight_vector[i]*Bidding_iteration.loc[(i,1),'benefit_total']  for i in weight_set)
        inner_sigma=dict()
        inner_sigma.clear()
        for h in interval_set:
            inner_sigma[h]=0
            for i in weight_set:
                inner_sigma[h]=++ US_average_price*(model.weight_vector[i]*Bidding_iteration.loc[(i,h),'demand_total'])*(model.weight_vector[i]*Bidding_iteration.loc[(i,h),'demand_total'])
        #marginal_cost=sum(inner_sigma[h] for h in interval_set)
                
        marginal_cost=sum(US_average_price*(sum(model.weight_vector[i]*Bidding_iteration.loc[(i,h),'demand_total'] for i in weight_set))**2 for h in interval_set)

        return benefit - marginal_cost
    model.cost = Objective(rule=benefit_rule,sense=maximize)
    #========================================
    #solving the model
    solver = SolverFactory('cplex')
    solver.options['workdir']='{}'.format(tempdir)
    solver.options['emphasis mip 4']
    solver.options['write avvvvvvv sol all']
    Results=solver.solve(model)
    
    for b in interval_set:
        Bidding_iteration.loc[(s+1,b),'price']=US_average_price*sum(pyo.value(model.weight_vector[i])*Bidding_iteration.loc[(i,b),'demand_total'] for i in weight_set)
        #Bidding_iteration.loc[(s,b),'generation_cost_1']=US_average_price*(sum(pyo.value(model.weight_vector[i])*Bidding_iteration.loc[(i,b),'demand_total'] for i in weight_set))**2

    Bidding_iteration.loc[(s,1),'S_best']=round(Bidding_iteration.loc[(s,1),'benefit_total'] - sum(Bidding_iteration.loc[(s,i),'demand_total']*Bidding_iteration.loc[(s,i),'price']   for i in interval_set),2)   
    Bidding_iteration.loc[(s,1),'S_known']=round(sum(pyo.value(model.weight_vector[i])*Bidding_iteration.loc[(i,1),'benefit_total'] for i in weight_set)-sum(Bidding_iteration.loc[(s,b),'price']*sum(pyo.value(model.weight_vector[i])*Bidding_iteration.loc[(i,b),'demand_total']for i in weight_set)for b in interval_set),2) 
    Bidding_iteration.loc[(s,1),'gap']=Bidding_iteration.loc[(s,1),'S_best'] - Bidding_iteration.loc[(s,1),'S_known']
    if Bidding_iteration.loc[(s,1),'gap'] <= optimality_gap and not s==1:
        break
for b in interval_set:
   Bidding_iteration.loc[(0,b),'demand_total']=round(sum([Bidding_iteration.loc[(0,b),unit] for unit in house_list]),2)
   
for b in interval_set:  # this is the second way of calculating the total cost. both approches have the same results!
    for s in iteration_set:
       Bidding_iteration.loc[(s,b),'generation_cost_2']=US_average_price*Bidding_iteration.loc[(s,b),'demand_total']*Bidding_iteration.loc[(s,b),'demand_total']

Bidding_iteration.loc[(0,1),'generation_cost_total']=Bidding_iteration.groupby('iteration').generation_cost_2.sum()[0]

    
writer = pd.ExcelWriter('Bidding_iteration.xlsx', engine='xlsxwriter')
Bidding_iteration.to_excel(writer,sheet_name='iter_1ter',index=True)
workbook=writer.book
worksheet = writer.sheets['iter_1ter']

##### formating the excel file with some details
worksheet.freeze_panes(1, 1)  # it freezes the frist column and row ( usefull when dataframe became large)
worksheet.write_comment('A2', 'The Iteration 0 only contains the intial energy withdrawals (sent from each household individually to the aggregator)')
worksheet.write_comment('A26', 'The initial price bid (P_1) is created proportional to  "demand_total" at the step 0')
worksheet.write_comment('D26', 'The loop wont break at this step since the S_best & S_know \n will be equal in this step.since only one sample exists.')
worksheet.write_comment('D{}'.format(s*24+2), 'The loop break at this point since the "gap" is \n below the "optimality_gap" or it reached the maximum iteration')
worksheet.write_comment('C1', 'P_{i}')
worksheet.write_comment('D1', '=S_best - S_known')
worksheet.write_comment('E1', '=b_{i}-P_{i}*d_{i}')
worksheet.write_comment('F1', '=sum(w_{i}*b_{i})-P_{i}*sum(w_{i}*d_{i})\n \n the w_{i} comes from the result of optimization')
worksheet.write_comment('G1', 'The standard diviation of Price')
worksheet.write_comment('H1', 'The standard diviation of d_{i}')
worksheet.write_comment('I1', 'The overal cost paid by the end-users P_{i}*d_{i}')
worksheet.write_comment('J1', 'b_{i}= P_s*Sum(d_{i}{h} for h in intervals) \n \n the benefit for each step. the scalar value equal to the penalty_factor*sum of d_{i} on all intervals')
worksheet.write_comment('K1', 'd_{i}=sum(household_{x} for x in houselist) \n \n the summation of demand of all  household_x for each interval')
#worksheet.conditional_format('B2:B8', {'type': '3_color_scale'})
bold = workbook.add_format({'bold': True,'fg_color': '#D7E4BC'})
cell_format = workbook.add_format()
cell_format.set_bold()
cell_format.set_font_color('blue')

for s in weight_set:
    worksheet.write('D{}'.format(s*24+2), Bidding_iteration.loc[(s,1),'gap'], cell_format)
worksheet.conditional_format('D2:D10', {'type': 'Red','fg_color': 'green'})
#worksheet.conditional_format('D2:D10', bold)
writer.save()



from celluloid import Camera # getting the camera
import math
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import HTML # to show the animation in Jupyter
 # creating my fig
fig, axes = plt.subplots(ncols=2,nrows=2, figsize=(15, 12), gridspec_kw={'width_ratios': [5, 5]})
camera = Camera(fig)# the camera gets the fig we'll plot
for i in range(iteration):
    axes[0, 0].step(list(interval_set),Bidding_iteration['price'][i], c='orange') 
    axes[0, 0].set_title('Price')
    axes[0, 0].set_xlabel('Intervals (Hour)')
    axes[0, 0].set_ylabel('$/kWh')
    #axes[0, 0].set_ylim([0,1])
    
##############################################    
    if i == 1:
     for j in house_list:       
       if j ==house_list[1]: 
         axes[0, 1].step(list(interval_set),Bidding_iteration['demand_total'][i],label="aggregate demand" ,c='black') # 5 element array from 0 to 9
         axes[0, 1].step(list(interval_set),Bidding_iteration[j][i], c='gray',label="individual demand",linestyle='dashed')
         axes[0, 1].legend()         
       axes[0, 1].step(list(interval_set),Bidding_iteration[j][i], c='gray',linestyle='dashed')  
       axes[0, 1].set_xlabel('Intervals (Hour)')
       axes[0, 1].set_title('Demand')          
       axes[0, 1].legend()
    for j in house_list:  
       axes[0, 1].step(list(interval_set),Bidding_iteration['demand_total'][i], c='black')
       axes[0, 1].step(list(interval_set),Bidding_iteration[j][i], c='gray',linestyle='dashed')
    axes[0, 1].set_xlabel('Intervals (Hour)')
    axes[0, 1].set_title('Demand')
    
    
##################################################    
    if i == 1:
      axes[1, 0].plot(range(1,i,1),Bidding_iteration.gap.loc[2:i,1], c='blue',label="gap")
      axes[1, 0].plot(range(1,i,1),Bidding_iteration.generation_cost_total.loc[2:i,1], c='black',label="generation cost")
      axes[1, 0].plot(range(1,i,1),Bidding_iteration.user_payment.loc[2:i,1], c='red',label="user payment")
      axes[1, 0].set_title('gap')    
      axes[1, 0].legend()
      axes[1, 0].set_xlabel('Iteration')
    #if i == 4:  
    axes[1, 0].plot(range(1,i,1),Bidding_iteration.gap.loc[2:i,1], c='blue')
    axes[1, 0].plot(range(1,i,1),Bidding_iteration.generation_cost_total.loc[2:i,1], c='black')
    axes[1, 0].plot(range(1,i,1),Bidding_iteration.user_payment.loc[2:i,1], c='red')
    axes[1, 0].set_title('gap')    
    axes[1, 0].set_xlabel('Iteration')
#####################################################  
    
    axes[1, 1].plot(range(1,i,1),Bidding_iteration.STD_demand.loc[2:i,1], c='green')
    axes[1, 1].plot(range(1,i,1),Bidding_iteration.STD_price.loc[2:i,1], c='orange')
    axes[1, 1].plot(range(1,i,1),Bidding_iteration.PAR_demand.loc[2:i,1], c='green',linestyle='dashed')
    axes[1, 1].plot(range(1,i,1),Bidding_iteration.PAR_price.loc[2:i,1], c='orange',linestyle='dashed')
    axes[1, 1].set_title('STD_demand')
    axes[1, 1].set_xlabel('Iteration')
    
    
    fig.suptitle('Progress through iterations', fontsize=16)
    camera.snap() # the camera takes a snapshot of the plot

animation = camera.animate() # animation ready
animation.save("Bidding_Animation.gif", writer='imagemagick')



##### Plotting section  ##########


fig2, ax = plt.subplots(ncols=1,nrows=2, figsize=(12, 9))
ax[0].bar(list(interval_set),Bidding_iteration['price'][2], color='blue') 
ax[0].set_title('Price')
ax[0].set_xlabel('Intervals (Hour)')
ax[0].set_ylabel('$/kWh')

ax[1].step(list(interval_set),Bidding_iteration['demand_total'][2], c='black')
ax[1].set_title('Demand')
ax[1].set_xlabel('Intervals (Hour)')
ax[1].set_ylabel('kWh')
fig2.savefig('demand&price_initial.svg')


fig3, ax3 = plt.subplots(ncols=1,nrows=2, figsize=(12, 9))
ax3[0].bar(list(interval_set),Bidding_iteration['price'][iteration], color='blue') 
ax3[0].set_title('Price')
ax3[0].set_xlabel('Intervals (Hour)')
ax3[0].set_ylabel('$/kWh')

ax3[1].step(list(interval_set),Bidding_iteration['demand_total'][iteration], c='black')
ax3[1].set_title('Demand')
ax3[1].set_xlabel('Intervals (Hour)')
ax3[1].set_ylabel('kWh')
fig3.savefig('demand&price_last.svg')



fig4, ax4 = plt.subplots(ncols=1,nrows=1, figsize=(12, 9))
ax4.plot(range(1,iteration,1),Bidding_iteration.gap.loc[2:iteration,1], c='black',linestyle='-.')
ax4.set_title('gap')
ax4.set_xlabel('Iteration')
fig4.savefig('Gap.svg')























    