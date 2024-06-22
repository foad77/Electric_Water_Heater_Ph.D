from flask import Flask, render_template, request, redirect, url_for, session
import subprocess , os, json

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Store the "tomorrow" value and "method" in session
        session['tomorrow'] = request.form['tomorrow']
        session['method'] = request.form.getlist('method')

        # Debugging: Print session values
        print("Tomorrow:", session['tomorrow'])
        print("Method:", session['method'])
        
        # Set environment variables for the subprocess
        os.environ['TOMORROW'] = session['tomorrow']
        os.environ['METHOD'] = json.dumps(session['method'])


        # Debugging: Print environment variables
        print("Environment TOMORROW:", os.environ['TOMORROW'])
        print("Environment METHOD:", os.environ['METHOD'])
        
        # Run solve.py with the "tomorrow" value and "method" as environment variables
        subprocess.run(["python", "solve.py"])
        
        return redirect(url_for('results'))
    return render_template('form.html')

@app.route('/results')
def results():
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
