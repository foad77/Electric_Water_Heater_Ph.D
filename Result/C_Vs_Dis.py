import pandas as pd; import os;import matplotlib.pyplot as plt;import subprocess
#########################################
Sum_run_times=0;stochastic_status=True
########################################
methods=["Du",'MILP','Apt','Fixed'] 
# os.path.exists(DIR)==True: 
# os.path.isfile(os.path.join(DIR, name))])
# os.path.isfile(current_file)==True: 
method_color_dic={};method_marker_dic={};plot_style_dic={};name_label_dic={};fill_holow_dic={};df=pd.DataFrame();df_perfect=pd.DataFrame();df_stochas=pd.DataFrame()

#df = pd.read_excel(Current_File)
df1 = pd.read_excel('MILP81-25.xlsx')
df2 = pd.read_excel('file_old.xlsx')
df3 = pd.read_excel('stochastic.xlsx')
df4 = pd.read_excel('Du&Lu_updated_init_cicle.xlsx')
# [['Exp_C_MILP','Exp_Dis_MILP']],df2[['Act_C_Du','Act_Dis_Du','Act_C_Apt','Act_Dis_Apt','Act_C_Fixed','Act_Dis_Fixed']]
# 1, 2 for perfect forecast graph
df_perfect=pd.concat([df1,df2[['Act_C_Du','Act_Dis_Du','Act_C_Apt','Act_Dis_Apt','Act_C_Fixed','Act_Dis_Fixed']]],axis=1)


# 3  ,2   ,4   for actual result graph
df2.drop(['Act_C_Du', 'Act_Dis_Du','Exp_C_Du', 'Exp_Dis_Du'], axis=1,inplace=True)
df_stochas=pd.concat([df2,df3[['Act_C_MILP_60','Act_Dis_MILP_60']],df4[['Act_C_Du','Act_Dis_Du']]],axis=1)

df=df_stochas

#df=pd.concat([df,df4[['Act_C_MILP','Act_Dis_MILP']]],axis=1)
#remove_list=['Exp_C_MILP','Exp_C_Fixed','Exp_C_Du','Exp_C_Apt','Act_C_Solar']
remove_list=['Exp_C_MILP','Exp_C_Fixed','Exp_C_Apt','Act_C_Solar','Exp_C_Du','Act_C_MILP']
#===================================================================
method_color_dic={'MILP':'Green','Du':'red','Apt':'blue','Average':'gray','Fixed':'Black','Solar':'Yellow'}
method_marker_dic={'MILP':'D','Du':'P','Apt':'C','Average':'M','Fixed':'K','Solar':'D'}
name_label_dic={'MILP':'WH-MILP','Du':'Du&Lu','Apt':'Apt&Goh','Average':'average','Fixed':'Fixed_Setpoint','Solar':'Solar-MILP'}
Exp_Act=['Act','Exp'];plot_style_dic={'Act':'solid','Exp':'dashed'};fill_holow_dic={}
def Scatter_plot (m,b):  
   global method_color_dic, method_marker_dic,average_vector
   average_vector=df.groupby('penalty').mean()
   # to get a holow graph, use ,facecolor='none'
   plt.scatter(average_vector['{}_C_{}'.format(b,m)],average_vector['{}_Dis_{}'.format(b,m)],label=None,color=method_color_dic[m],marker="D")
   plt.plot(average_vector['{}_C_{}'.format(b,m)],average_vector['{}_Dis_{}'.format(b,m)],label='{}'.format(name_label_dic[m],b),color=method_color_dic[m],linestyle=plot_style_dic[b])     
#===================================================================
for m in methods:
         for b in Exp_Act:
             if ('{}_C_{}'.format(b,m)) in remove_list:
                 pass
             else:
                 Scatter_plot(m,b)
m='MILP';b='Act'
plt.scatter(average_vector['Act_C_MILP_60'],average_vector['Act_Dis_MILP_60'],label=None,color=method_color_dic[m],marker="D")
plt.plot(average_vector['Act_C_MILP_60'],average_vector['Act_Dis_MILP_60'],label='MILP(Act_60)',color=method_color_dic[m],linestyle=plot_style_dic[b]) 


df33=pd.read_excel('file_old.xlsx')
average_du=df33.groupby('penalty').mean()
plt.scatter(average_du['Act_C_Du'],average_du['Act_Dis_Du'],label=None,color='red',marker="D", facecolors='none')
plt.plot(average_du['Act_C_Du'],average_du['Act_Dis_Du'],label='Du&Lu(perfect)',color='red',linestyle='dashed')


new_ave=df1.groupby('penalty').mean()
plt.scatter(new_ave['Act_C_MILP'],new_ave['Act_Dis_MILP'],label=None,color=method_color_dic[m],marker="D", facecolors='none')
plt.plot(new_ave['Act_C_MILP'],new_ave['Act_Dis_MILP'],label='MILP(perfect)',color=method_color_dic[m],linestyle='dashed') 

#ax = average_vector.plot(kind='scatter', x='Act_C_Fixed', y='Act_Dis_Fixed')    
#=========================================
## the report file! shows onder what setting the results are obtained!
#if stochastic_status:
#   status = 'stochastic'
#else:
#   status = 'perfect_forecast'
#
#with open('Result/logging/{}/{}d_lookBack & {}m_Intrv/settings&statistics.csv'.format(status,lookback_length,min_slot), "w") as f:
#       f.write(str('average Run Time')+ ',' + str(average_run_times) +','+'\n')
#       f.write(str('look back days')+ ',' + str(lookback_length) +','+'\n')
#       f.write(str('temperature resolution')+ ',' + str(temp_resolution) +','+'\n')
#       f.write(str('Initial_Temperature_Status')+ ',' + str(Initial_Temperature_Status) +','+'\n')
#       f.write(str('t_max')+ ',' + str(t_max) +','+'\n')
#       f.write(str('t_min')+ ',' + str(t_min) +','+'\n')
#       f.write(str('t_min_shortfall')+ ',' + str(t_min_shortfall) +','+'\n')
#
#       
#       
#       
#===================================================================       
if stochastic_status:
      name = '(stochastic)'
else:
      name = '(perfect_forecast)'
plt.xlabel('Electric Cost($/day)')
plt.ylabel('Underheated Water(kWh/day)')
plt.grid(True)
plt.legend(loc='upper right')
plt.savefig('Graphs/cost_Vs_Discomfort{}.svg'.format(name))
plt.show() 
#===============================
#this will remove the log files that are generated by CPLEX
#for windows
# cmd_1 = ["del", "clo*"]
# subprocess.call(cmd_1,shell=True) 
# #for linux 
# bash = ["rm", "clo*"]
# subprocess.call(bash,shell=True)

           

