########################################
average_Electrical_Expected_our=dict();average_Discomfort_Expected_our=dict();average_Electrical_Actual_our=dict();average_Discomfort_Actual_our=dict()
average_Electrical_Expected_Du=dict();average_Discomfort_Expected_Du=dict();average_Electrical_Actual_Du=dict();average_Discomfort_Actual_Du=dict()
average_Electrical_Actual_Apt=dict();average_Discomfort_Actual_Apt=dict()
#########################################
for i in range(0, len(penalty_vector)):
     if os.path.exists('Result/logging/{}d_lookBack & {}m_Intrv/{} penalty'.format(lookback_length,min_slot,penalty_vector[i]))==True: 
       DIR = 'Result/logging/{}d_lookBack & {}m_Intrv/{} penalty'.format(lookback_length,min_slot,penalty_vector[i])
       tomorrow_days_number = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
       ##############################################
       Sum_Electrical_Expected_our=0;Sum_Discomfort_Expected_our=0;Sum_Electrical_Actual_our=0;Sum_Discomfort_Actual_our=0
       Sum_Electrical_Expected_Du=0;Sum_Discomfort_Expected_Du=0;Sum_Electrical_Actual_Du=0;Sum_Discomfort_Actual_Du=0
       Sum_Electrical_Actual_Apt=0;Sum_Discomfort_Actual_Apt=0
       ##############################################
       for j in range(1,364):
          current_file='Result/logging/{}d_lookBack & {}m_Intrv/{} penalty/{} tomorrow.csv'.format(lookback_length,min_slot,penalty_vector[i],j)
          if os.path.isfile(current_file)==True: 
              df = pd.read_csv(current_file)
              df.head()
              # the data for our method
              Electrical_Expected_our=float((df['Expected_Cost_our'][0]))
              Sum_Electrical_Expected_our=Sum_Electrical_Expected_our+Electrical_Expected_our              
              Discomfort_Expected_our=float((df['Expected_Discomfort_our'][0]))
              Sum_Discomfort_Expected_our=Sum_Discomfort_Expected_our+Discomfort_Expected_our             
              Electrical_Actual_our=float((df['Expected_Cost_our'][2]))
              Sum_Electrical_Actual_our=Sum_Electrical_Actual_our+Electrical_Actual_our              
              Discomfort_Actual_our=float((df['Expected_Discomfort_our'][2]))
              Sum_Discomfort_Actual_our=Sum_Discomfort_Actual_our+Discomfort_Actual_our
              # the data for Du&Lu method
              Electrical_Expected_Du=float((df['Expected_Cost_our'][4]))
              Sum_Electrical_Expected_Du=Sum_Electrical_Expected_Du+Electrical_Expected_Du
              Discomfort_Expected_Du=float((df['Expected_Discomfort_our'][4]))     
              Sum_Discomfort_Expected_Du=Sum_Discomfort_Expected_Du+Discomfort_Expected_Du
              Electrical_Actual_Du=float((df['Expected_Cost_our'][6]))
              Sum_Electrical_Actual_Du=Sum_Electrical_Actual_Du+Electrical_Actual_Du
              Discomfort_Actual_Du=float((df['Expected_Discomfort_our'][6]))
              Sum_Discomfort_Actual_Du=Sum_Discomfort_Actual_Du+Discomfort_Actual_Du
              # the data for Apt&Goh method
              Electrical_Actual_Apt=float((df['Expected_Cost_our'][8]))
              Sum_Electrical_Actual_Apt=Sum_Electrical_Actual_Apt+Electrical_Actual_Apt
              Discomfort_Actual_Apt=float((df['Expected_Discomfort_our'][8]))
              Sum_Discomfort_Actual_Apt=Sum_Discomfort_Actual_Apt+Discomfort_Actual_Apt
       #averaging the summed values
       average_Electrical_Expected_our[i]=Sum_Electrical_Expected_our/tomorrow_days_number
       average_Discomfort_Expected_our[i]=Sum_Discomfort_Expected_our/tomorrow_days_number
       average_Electrical_Actual_our[i]=Sum_Electrical_Actual_our/tomorrow_days_number
       average_Discomfort_Actual_our[i]=Sum_Discomfort_Actual_our/tomorrow_days_number
       # averaging on Du&Lu
       average_Electrical_Expected_Du[i]=Sum_Electrical_Expected_Du/tomorrow_days_number
       average_Discomfort_Expected_Du[i]=Sum_Discomfort_Expected_Du/tomorrow_days_number
       average_Electrical_Actual_Du[i]=Sum_Electrical_Actual_Du/tomorrow_days_number
       average_Discomfort_Actual_Du[i]=Sum_Discomfort_Actual_Du/tomorrow_days_number
       # averaging on Apt&Goh
       average_Electrical_Actual_Apt[i]=Sum_Electrical_Actual_Apt/tomorrow_days_number
       average_Discomfort_Actual_Apt[i]=Sum_Discomfort_Actual_Apt/tomorrow_days_number
       
#               url_csv = 'https://vincentarelbundock.github.io/Rdatasets/csv/boot/amis.csv'
#               df = pd.read_csv(url_csv)
plt.scatter(average_Electrical_Expected_our.values(), average_Discomfort_Expected_our.values(),label='Ours', color='green',hold=True)
plt.scatter(average_Electrical_Expected_Du.values(), average_Discomfort_Expected_Du.values(),label='D&L',color='red',hold=True)
plt.scatter(average_Electrical_Actual_Apt.values(), average_Discomfort_Actual_Apt.values(),label='A&G',color='blue')
plt.xlabel('Electric Cost($)')
plt.ylabel('Under Heated(energy)')
plt.grid(True)
plt.legend()
plt.savefig('cost_Vs_Discomfort.pdf')
plt.show() 

           

