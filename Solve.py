import time , yaml
from Input.imports import *

#==========================================
#this is the main loop of  the code
exec(compile(open('Input/imports.py', "rb").read(), 'Input/imports.py', 'exec'))
exec(compile(open('Input/Loop.py', "rb").read(), 'Input/Loop.py', 'exec'))


#=========================================
# exporting the result and plotting the outputs
#if len(sys.argv) == 1 and loop == 1:
#      exec(compile(open('Result/C_Vs_Dis.py', "rb").read(), 'Result/C_Vs_Dis.py', 'exec'))


# it saves all the variables into two seperate .csv files in the 'Results' folder
# also it plots the second graph for the last value of  penatly factor and 'loop' value.
if len(sys.argv) == 1 and loop == 1:
   exec(compile(open('Result/OneDay.py', "rb").read(), 'Result/OneDay.py', 'exec'))

#exec(compile(open('Result/temPy/testQuadProb.py', "rb").read(), 'Result/testQuadProb.py', 'exec'))
#     if version ==3: exec(compile(open('Result/C_Vs_Dis.py', "rb").read()5
# , 'Result/C_Vs_Dis.py', 'exec'))
#     if version ==2: execfile('Result/C_Vs_Dis.py')

# it saves all the variables into two seperate .csv files in the 'Results' folder
# also it plots the second graph for the last value of  penatly factor and 'loop' value.
# if len(sys.argv) == 1 and loop == 1:
#   if version ==3: exec(compile(open('Result/OneDay.py', "rb").read(), 'Result/OneDay.py', 'exec'))
#   if version ==2: execfile('Result/OneDay.py')
#exec(compile(open('Result/temPy/testQuadProb.py', "rb").read(), 'Result/testQuadProb.py', 'exec'))
