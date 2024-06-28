import os, yaml, uuid, json, sys , logging

# Set up logging
logging.basicConfig(filename='/tmp/solve.log', level=logging.DEBUG)
logging.debug("Solve.py started")

try:
    # Change working directory to the script location
    script_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)

    exec(compile(open('Input/imports.py', "rb").read(), 'Input/imports.py', 'exec'))
    logging.debug("Imports.py executed")

    exec(compile(open('Input/Loop.py', "rb").read(), 'Input/Loop.py', 'exec'))
    logging.debug("Loop.py executed")

    
    exec(compile(open('Result/OneDay.py', "rb").read(), 'Result/OneDay.py', 'exec'))
    logging.debug("OneDay.py executed")

    logging.debug("Solve.py completed successfully")
except Exception as e:
    logging.error(f"An error occurred in Solve.py: {e}")

