import imports
current_day=365;lookback_length=365;
execfile('Region_generator.py')
min_slots=[1,2,3,4,5,6,10,12,15,20,30,60]
cluster_set=[2,3,4,5,6,7,8,9,10]
for min_slot in min_slots:
    for n in cluster_set:
        

