from __future__ import division
from pyomo.environ import *

from pyomo.environ import*
from pyomo.opt import SolverFactory




Pyomo_start_time = time.time()

model = ConcreteModel(name="(WH)")
#Variables
#=====================================================
model.dummy_setpoint  = Var(interval_set,          bounds=(t_min*temp_resolution, t_max*temp_resolution),   within=NonNegativeIntegers)
model.ts_setpoint     = Var(interval_set,          bounds=(t_min,t_max),                                    within=NonNegativeReals)
model.sim_tank_temp   = Var(day_set,interval_set,  bounds=(t_min-20,t_max),                                 within=NonNegativeReals)
model.NRG_input       = Var(day_set,interval_set,  bounds=(0,max_energy_input_per_interval),                within=NonNegativeReals)
model.temp_shortfall  = Var(day_set,interval_set,  bounds=(0, t_min+5),                                     within=NonNegativeReals)
model.NRG_shortfall_f = Var(day_set,interval_set,  bounds=(0, None),                                        within=NonNegativeReals)
model.NRG_withdrawn_f = Var(day_set,interval_set,  bounds=(0, None),                                        within=NonNegativeReals)
model.conservative_temp=Var(day_set,interval_set,  bounds=(t_min-20,t_max),                                 within=NonNegativeReals)
model.heater_at_max   = Var(day_set,interval_set,                                                           within=Binary)
model.heater_coasting = Var(day_set,interval_set,                                                           within=Binary)

#========================================
#Constraints definition

def Const_1(model,a , b):
    return  energy_req[a, b] - model.NRG_withdrawn_f[a, b] == model.NRG_shortfall_f[a, b]
model.Const_1_ = Constraint(day_set,interval_set, rule=Const_1)

def Const_2(model,a , b):
    return (1-model.heater_coasting[a, b])*max_energy_input_per_interval >= model.NRG_input[a, b]
model.Const_2_ = Constraint(day_set,interval_set, rule=Const_2)

def Const_3(model,a , b):
    return model.heater_at_max[a, b] * max_energy_input_per_interval <= model.NRG_input[a, b]
model.Const_3_ = Constraint(day_set,interval_set, rule=Const_3)

def Const_4(model,a , b):
    return t_min_range[j] - model.sim_tank_temp[a, b] <= model.temp_shortfall[a, b]
model.Const_4_ = Constraint(day_set,interval_set, rule=Const_4)

def Const_5(model,a , b):
    return energy_req[a, b] * model.temp_shortfall[a, b] / (t_min_range[j] - t_in[current_day]) == model.NRG_shortfall_f[a, b]
model.Const_5_ = Constraint(day_set,interval_set, rule=Const_5)

def Const_6(model,a , b):
    return model.ts_setpoint[b] - model.heater_at_max[a, b] * big_temp <= model.sim_tank_temp[a, b]
model.Const_6_ = Constraint(day_set,interval_set, rule=Const_6)

def Const_7(model,a , b):
    return model.ts_setpoint[b] + model.heater_coasting[a, b] * big_temp >= model.sim_tank_temp[a, b]
model.Const_7_ = Constraint(day_set,interval_set, rule=Const_7)

def Const_8(model,a , b):
    return  model.conservative_temp[a,b] + (model.NRG_input[a,b]) / degree_of_water_per_kwh - heat_loss_rate * (model.sim_tank_temp[a,b] - t_amb[current_day,b] ) == model.sim_tank_temp[a,b]                
model.Const_8_ = Constraint(day_set,interval_set, rule=Const_8)

def Const_9(model,a , b):
    global d_prev
    if b == 1:
       i_prev = max(interval_set)
       d_prev = a
    else:
       i_prev = b - 1
       d_prev = a
    return model.sim_tank_temp[d_prev,i_prev]+ (- model.NRG_withdrawn_f[a,b]) / degree_of_water_per_kwh == model.conservative_temp[a,b]
model.Const_9_ = Constraint(day_set,interval_set, rule=Const_9)



def Const_10(model,b):
    return  model.dummy_setpoint[b] /(temp_resolution) == model.ts_setpoint[b]  
model.Const_10_ = Constraint(interval_set, rule=Const_10)
#========================================
#objective function

def cost_rule(model):
    return sum(price_of_power[current_day,b] * model.NRG_input[a,b] + shortfall_penalty_range[j] * model.NRG_shortfall_f[a,b] 
               for a  in day_set for b in interval_set )
model.cost = Objective(rule=cost_rule)

#model.cost = Objective(expr=sum(price_of_power[current_day,b] * model.NRG_input[a,b] + shortfall_penalty_range[j] * model.NRG_shortfall_f[a,b] 
#               for a  in day_set for b in interval_set ) )



#========================================
#solving the model

#SolverFactory('glpk').solve(model)
#SolverFactory('cplex').solve(model)
solver = SolverFactory('cplex')
solver.options['workdir']='{}'.format(tempdir)
solver.options['timelimit']=3600
#solver.options['threads']=10
solver.options['emphasis mip 4']
solver.options['write avvvvvvv sol all']
Results=solver.solve(model)
#SolverFactory('gurobi').solve(model)

model.ts_setpoint.pprint()
#model.heater_coasting.pprint()
#model.display()
#model.pprint()
print(" %s seconds for Pyomo Model" % (time.time() - Pyomo_start_time))