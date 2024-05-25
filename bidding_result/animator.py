import sys; sys.path.append('C:\\Users\\foadn\\AppData\\Local\\Packages\\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\\LocalCache\\local-packages\\Python310\\site-packages')
import matplotlib.pyplot as plt
from celluloid import Camera # getting the camera
import pandas as pd

Bidding_iteration = pd.read_excel('Bidding_iteration.xlsx')
# Create a sample multi-index DataFrame
outer_index = range(0,102)
inner_index = range(1,25)

# Create the multi-index
index = pd.MultiIndex.from_product([outer_index, inner_index], names=['Iteration', 'interval'])

Bidding_iteration.set_index(index, inplace=True)
# print(Bidding_iteration.columns)
# import sys; sys.exit(0)
user_pattern= range(50,250)
iteration=70
## some model paramters.
min_slot=60;interval_per_hour=60/min_slot; specific_heat = 0.001148;t_min = 25;t_in=13.88;t_out=54.4
penalty_shortfall=2;
US_average_price=0.2
#creating index. we have two: iteration and intervals
iteration_set=[]
for i in range(0,iteration+1):
        iteration_set.append(i)
interval_set=[]
for i in range(1,24*int(interval_per_hour)+1):
        interval_set.append(i)
user_list_names=['price','gap','S_best','S_known','STD_price','PAR_price','STD_demand','PAR_demand','user_payment','generation_cost_1','generation_cost_2','generation_cost_total','benefit_total','demand_total']    
        
house_list=[]
for  hours in user_pattern:
    srts='House_{}'.format(hours)
    house_list.append(srts)
    user_list_names.append(srts)       
        
       
############## Animation Section
fontsize=25
linewidth = 4
fig, axes = plt.subplots(ncols=2,nrows=2, figsize=(15, 12), gridspec_kw={'width_ratios': [5, 5]})
camera = Camera(fig)# the camera gets the fig we'll plot
for i in range(iteration):
    axes[0, 0].step(list(interval_set),Bidding_iteration['price'][i]/25, c='orange') 
    axes[0, 0].set_title('Price')
    axes[0, 0].set_xlabel('Intervals (Hour)')
    axes[0, 0].set_ylabel('$/kWh')
    #axes[0, 0].set_ylim([0,1])
    
##############################################
    axes[0, 1].step(list(interval_set),Bidding_iteration['demand_total'][i], c='black')   
    #axes[0, 1].step(list(interval_set),Bidding_iteration['demand_total'][i],label="aggregate demand" ,c='black') # 5 element array from 0 to 9 
    axes[0, 1].set_xlabel('Intervals (Hour)')
    axes[0, 1].set_title('Demand')          
    axes[0, 1].legend()
    #for j in house_list:  
    axes[0, 1].set_xlabel('Intervals (Hour)')
    axes[0, 1].set_title('Aggregate Demand')
    
    
##################################################    
    if i == 2:
      axes[1, 0].plot(range(1,i,1),Bidding_iteration.gap.loc[2:i,1]/25, c='blue',label="gap")
      axes[1, 0].plot(range(1,i,1),Bidding_iteration.generation_cost_total.loc[2:i,1]/25, c='black',label="generation cost")
      axes[1, 0].plot(range(1,i,1),Bidding_iteration.user_payment.loc[2:i,1]/25, c='red',label="user payment")
      axes[1, 0].set_title('gap')    
      axes[1, 0].legend()
      axes[1, 0].set_xlabel('Iteration')
    if i >= 3:  
       axes[1, 0].plot(range(1,i,1),Bidding_iteration.gap.loc[2:i,1]/25, c='blue')
       axes[1, 0].plot(range(1,i,1),Bidding_iteration.generation_cost_total.loc[2:i,1]/25, c='black')
       axes[1, 0].plot(range(1,i,1),Bidding_iteration.user_payment.loc[2:i,1]/25, c='red')
       axes[1, 0].set_title('gap & generation cost & user payment')    
       axes[1, 0].set_xlabel('Iteration')
#####################################################  
    # PAR and STD
    if i == 2:
      axes[1, 1].plot(range(1,i,1),Bidding_iteration.STD_demand.loc[2:i,1], c='green',label="STD(demand)")
      axes[1, 1].plot(range(1,i,1),Bidding_iteration.STD_price.loc[2:i,1], c='green',linestyle='-.',label="STD(price)")
      ax7 = axes[1, 1].twinx()
      ax7.plot(range(1,i,1),Bidding_iteration.PAR_demand.loc[2:i,1], c='orange',label="PAR(demand)")
      ax7.plot(range(1,i,1),Bidding_iteration.PAR_price.loc[2:i,1], c='orange',linestyle='-.',label="PAR(price)")

      axes[1, 1].set_ylabel('STD', color='green')
      axes[1, 1].legend(loc=2, prop={'size': 10})
      ax7.set_ylabel('PAR' , color='orange')
      ax7.legend(loc=1, prop={'size': 10})

      axes[1, 1].set_title('PAR & STD for Price and Demand')
      axes[1, 1].set_xlabel('Iteration')
    if i >= 3:  
      axes[1, 1].plot(range(1,i,1),Bidding_iteration.STD_demand.loc[2:i,1], c='green')
      axes[1, 1].plot(range(1,i,1),Bidding_iteration.STD_price.loc[2:i,1], c='green',linestyle='-.')
      #ax7 = axes[1, 1].twinx()
      ax7.plot(range(1,i,1),Bidding_iteration.PAR_demand.loc[2:i,1], c='orange',label="PAR(demand)")
      ax7.plot(range(1,i,1),Bidding_iteration.PAR_price.loc[2:i,1], c='orange',linestyle='-.',label="PAR(price)")
 
    fig.suptitle('Progress through iterations', fontsize=16)
    camera.snap() # the camera takes a snapshot of the plot

animation = camera.animate() # animation ready
animation.save("bidding_result/Bidding_Animation.gif", writer='imagemagick')



########################### Plotting section  ##########
plt.rcParams["font.family"] = "times new roman"
#  initial price & demand 
fig2, ax = plt.subplots(ncols=1,nrows=2, figsize=(12, 9))
ax[0].step(list(interval_set),Bidding_iteration['price'][2]/25, c='orange',linewidth=linewidth) 
ax[0].set_title('Price',fontdict={'fontsize': fontsize})
#ax[0].set_xlabel('Intervals (Hour)',fontsize=fontsize)
ax[0].set_ylabel('$/kWh',fontsize=fontsize)

ax[1].bar(list(interval_set),Bidding_iteration['demand_total'][2], color='black')
ax[1].set_title('Demand',fontdict={'fontsize': fontsize})
ax[1].set_xlabel('Intervals (Hour)',fontsize=fontsize)
ax[1].set_ylabel('kWh',fontsize=fontsize)
fig2.savefig('bidding_result/demand&price_initial.svg',bbox_inches='tight')

#  End price & demand 
fig3, ax3 = plt.subplots(ncols=1,nrows=2, figsize=(12, 9))
ax3[0].step(list(interval_set),Bidding_iteration['price'][iteration]/25, c='orange',linewidth=linewidth) 
ax3[0].set_title('Price',fontdict={'fontsize': fontsize})
#ax3[0].set_xlabel('Intervals (Hour)',fontsize=fontsize)
ax3[0].set_ylabel('$/kWh',fontsize=fontsize) 

ax3[1].bar(list(interval_set),Bidding_iteration['demand_total'][iteration], color='black')
ax3[1].set_title('Demand',fontdict={'fontsize': fontsize})
ax3[1].set_xlabel('Intervals (Hour)',fontsize=fontsize)
ax3[1].set_ylabel('kWh',fontsize=fontsize)
fig3.savefig('bidding_result/demand&price_last.svg',bbox_inches='tight')


# Gap &  Generation_cost & user_payment
fig4, ax4 = plt.subplots(ncols=1,nrows=1, figsize=(12, 9))
ax4.plot(range(1,iteration,1),Bidding_iteration.gap.loc[2:iteration,1]/25, c='blue',label="gap",linewidth=linewidth)
ax4.plot(range(1,iteration,1),Bidding_iteration.user_payment.loc[2:iteration,1]/25, c='red',label="user payment",linewidth=linewidth)
ax4.plot(range(1,iteration,1),Bidding_iteration.generation_cost_total.loc[2:iteration,1]/25, c='black',label="generation cost",linewidth=linewidth)
ax4.set_title('gap & generation cost & user payment',fontdict={'fontsize': fontsize})
ax4.set_xlabel('Iteration',fontsize=fontsize)
ax4.set_ylabel('Value',fontsize=fontsize)
ax4.legend(loc=1, prop={'size': 18})
fig4.savefig('bidding_result/Gap&generation&user_cost.svg',bbox_inches='tight')


#### electric vehicle
fig5, ax5 = plt.subplots(ncols=1,nrows=1, figsize=(12, 9))
ax5.bar(list(interval_set),Bidding_iteration['EV_115_max'][iteration], color='gray')
ax5.bar(list(interval_set),Bidding_iteration['EV_115'][iteration], color='blue',alpha=0.5)
ax5.set_title('EV Schedule',fontdict={'fontsize': fontsize})
ax5.set_xlabel('Intervals (Hour)',fontsize=fontsize)
fig5.savefig('bidding_result/EV_oneDay.svg',bbox_inches='tight')

#### PAR & STD for Price and Demand

fig6, ax6 = plt.subplots(ncols=1,nrows=1, figsize=(12, 9))
ax6.plot(range(1,iteration,1),Bidding_iteration.STD_demand.loc[2:iteration,1], c='green',label="STD(demand)",linewidth=linewidth)
ax6.plot(range(1,iteration,1),Bidding_iteration.STD_price.loc[2:iteration,1], c='green',linestyle='-.',label="STD(price)",linewidth=linewidth)
ax6.set_title('PAR & STD for Price and Demand',fontdict={'fontsize': fontsize})
ax6.set_xlabel('Iteration',fontsize=fontsize)
ax6.set_ylabel('STD',fontsize=fontsize, color='green')
ax6.legend(loc=2, prop={'size': 18})
ax7 = ax6.twinx()

ax7.plot(range(1,iteration,1),Bidding_iteration.PAR_demand.loc[2:iteration,1], c='orange',label="PAR(demand)",linewidth=linewidth)
ax7.plot(range(1,iteration,1),Bidding_iteration.PAR_price.loc[2:iteration,1], c='orange',linestyle='-.',label="PAR(price)",linewidth=linewidth)
ax7.set_ylabel('PAR',fontsize=fontsize , color='orange')
ax7.legend(loc=1, prop={'size': 18})
fig6.savefig('bidding_result/PAR&STD.svg',bbox_inches='tight')

