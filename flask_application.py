from flask import Flask, render_template, request, redirect, url_for, flash
import subprocess
import os
import yaml
import uuid

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
            subprocess.run(["python", "Solve.py"])
            
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
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
