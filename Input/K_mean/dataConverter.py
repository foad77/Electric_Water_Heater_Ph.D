# the original data in {}min_usage.xlsx files are added horizontaly. However, usually
#the machine learning algorithm thart work with panda, usually import each vector of
# data vertically.
#so, this file convert withdrawal from vertical position into horizontal.
# this file is needed to be run only once. when the vertical .csv files are generated
# this file is not needed to be runned again! 


from openpyxl import load_workbook;#from csv import*
from numpy import*;#import numpy as np;
day_set=set();interval_set=set();historical_volume_withdrawn=dict()
#minutes_intervals=[1,2,3,4,5,6,10,12,15,20,30,60]
# i got an error for 1 and 2 minutes interval. other intervals were fine!
minutes_intervals=[1]
for min_slot in minutes_intervals:
## importing from 'hourly hot water' excel file
   wb = load_workbook('{}min_usage.xlsx'.format(min_slot), read_only = True, data_only=True)
   sheet = wb['{}min_usage'.format(min_slot)]
   start_row = 2
   end_row = 24*(60/min_slot)*(365)+1
   region_label = 'A{}:J{}'.format(start_row, end_row)
   region = sheet[region_label]    
#===========================
   for r in region:
        # each row contains date, interval, water temperature, withdrawal
        d = int(r[0].value)
        i = int(r[1].value)
        day_set.add(d)
        interval_set.add(i)
        historical_volume_withdrawn[d, i] = float(r[2].value) # also convert to liters!
   # exporting Data
   with open("ConvertedDataKmean/{}min_withdrawal.csv".format(min_slot), "w") as f:
        for b in sorted(interval_set):
          f.write(str(b)+',')
        f.write('\n')
        for d in sorted(day_set):
          for b in sorted(interval_set):
            f.write( str(historical_volume_withdrawn[d, b]) +',')
          f.write('\n')