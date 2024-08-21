from flask import Flask, render_template, request, redirect, url_for, flash
import subprocess , os , yaml , uuid , pandas as pd, sys

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        try:
            # Collect form data
            form_data = {
                'tomorrow': int(request.form['tomorrow']),
                't_max': int(request.form['t_max']),
                't_min': int(request.form['t_min']),
                't_min_shortfall': int(request.form['t_min_shortfall']),
                'max_energy_input_per_hour': float(request.form['max_energy_input_per_hour']),
                'v': float(request.form['v']),
                'method': request.form.getlist('method')  # Get list of selected methods
            }
            
            # Debugging: Print form data
            print("Form Data:", form_data)
            
            # Create a unique filename using a UUID
            unique_id = uuid.uuid4()
            temp_config_filename = f'temp_config_{unique_id}.yaml'
            temp_config_path = os.path.join('/tmp', temp_config_filename)
            
            # Write form data to the temporary YAML file
            with open(temp_config_path, 'w') as temp_config_file:
                yaml.dump(form_data, temp_config_file)
            
            # Set an environment variable with the path of the temporary YAML file
            os.environ['TEMP_CONFIG_PATH'] = temp_config_path
            
            # Run Solve.py
            subprocess.run([sys.executable, "Solve.py"])
            
            # Cleanup temporary file
            if os.path.exists(temp_config_path):
                os.remove(temp_config_path)
            
            return redirect(url_for('results'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
            return redirect(url_for('form'))
    return render_template('form.html')

@app.route('/results')
def results():
    csv_file_path = 'OneDayDF.csv'  # Ensure this path is correct

    # Check if file exists before proceeding
    if not os.path.exists(csv_file_path):
        return "CSV file not found", 404

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Log the columns present in the DataFrame
    app.logger.debug(f"CSV Columns: {df.columns.tolist()}")

    # Get selected methods from form submission (assuming it's stored in session or passed here)
    selected_methods = ['MILP', 'Du', 'Apt', 'Fixed', 'Solar']  # Replace with the actual methods from the form

    # Initialize total_cost, savings, discomfort_cost, and discomfort_savings dictionaries
    total_cost = {}
    savings = {}
    discomfort_cost = {}
    discomfort_savings = {}

    # Mapping columns to methods
    cost_mapping = {
        'MILP': 'Act_C_MILP',
        'Du': 'Act_C_Du',
        'Apt': 'Act_C_Apt',
        'Fixed': 'Act_C_Fixed',
        'Solar': 'Act_C_Solar'
    }
    
    discomfort_mapping = {
        'MILP': 'Act_Dis_MILP',
        'Du': 'Act_Dis_Du',
        'Apt': 'Act_Dis_Apt',
        'Fixed': 'Act_Dis_Fixed',
        'Solar': 'Act_Dis_Solar'
    }

    fixed_setpoint_cost = 0
    fixed_setpoint_discomfort = 0

    for method in selected_methods:
        cost_column = cost_mapping.get(method)
        discomfort_column = discomfort_mapping.get(method)

        if cost_column in df.columns:
            total_value = df[cost_column].sum()
            total_cost[method] = round(total_value, 2)
            if method == 'Fixed':
                fixed_setpoint_cost = total_value

        if discomfort_column in df.columns:
            discomfort_value = df[discomfort_column].sum()
            discomfort_cost[method] = round(discomfort_value, 2)
            if method == 'Fixed':
                fixed_setpoint_discomfort = discomfort_value

    # Calculate savings compared to Fixed setpoint
    for method in total_cost:
        if method != 'Fixed' and fixed_setpoint_cost > 0:
            savings[method] = round((fixed_setpoint_cost - total_cost[method]) / fixed_setpoint_cost * 100, 2)
        else:
            savings[method] = 0  # No savings calculation for Fixed method itself

    # Calculate discomfort savings compared to Fixed setpoint
    for method in discomfort_cost:
        if method != 'Fixed' and fixed_setpoint_discomfort > 0:
            discomfort_savings[method] = round((fixed_setpoint_discomfort - discomfort_cost[method]) / fixed_setpoint_discomfort * 100, 2)
        else:
            discomfort_savings[method] = 0  # No discomfort savings calculation for Fixed method itself

    # Render the results page with the calculated totals, savings, and discomfort
    return render_template('results.html', total_cost=total_cost, savings=savings, discomfort_cost=discomfort_cost, discomfort_savings=discomfort_savings)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
