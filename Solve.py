import os, yaml, uuid, json
# Get the "tomorrow" value from environment variables
tomorrow = os.getenv('TOMORROW')
method = json.loads(os.getenv('METHOD'))  # Convert JSON string back to list

# Create a unique filename using the process ID and a UUID
pid = os.getpid()
unique_id = uuid.uuid4()
temp_config_filename = f'temp_config_{pid}_{unique_id}.yaml'
temp_config_path = os.path.join('/tmp', temp_config_filename)  # Using /tmp for temporary files


# Write the "tomorrow" value to the temporary YAML file
with open(temp_config_path, 'w') as temp_config_file:
    yaml.dump({'tomorrow': tomorrow, 'method': method}, temp_config_file)
# Set an environment variable with the path of the temporary YAML file
os.environ['TEMP_CONFIG_PATH'] = temp_config_path

exec(compile(open('Input/imports.py', "rb").read(), 'Input/imports.py', 'exec'))

# Cleanup temporary file
os.remove(temp_config_path)

exec(compile(open('Input/Loop.py', "rb").read(), 'Input/Loop.py', 'exec'))


#=========================================
# exporting the result and plotting the outputs
#if len(sys.argv) == 1 and loop == 1:
#      exec(compile(open('Result/C_Vs_Dis.py', "rb").read(), 'Result/C_Vs_Dis.py', 'exec'))


# it saves all the variables into two seperate .csv files in the 'Results' folder
# also it plots the second graph for the last value of  penatly factor and 'loop' value.
#if len(sys.argv) == 1 and loop == 1:
#   exec(compile(open('Result/OneDay.py', "rb").read(), 'Result/OneDay.py', 'exec'))

#exec(compile(open('Result/temPy/testQuadProb.py', "rb").read(), 'Result/testQuadProb.py', 'exec'))
#     if version ==3: exec(compile(open('Result/C_Vs_Dis.py', "rb").read()5
# , 'Result/C_Vs_Dis.py', 'exec'))
#     if version ==2: execfile('Result/C_Vs_Dis.py')

# it saves all the variables into two seperate .csv files in the 'Results' folder
# also it plots the second graph for the last value of  penatly factor and 'loop' value.
if len(sys.argv) == 1 and loop == 1:
    exec(compile(open('Result/OneDay.py', "rb").read(), 'Result/OneDay.py', 'exec'))
