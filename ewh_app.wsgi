#!/usr/bin/python3
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/home/Web/EWH_WEB_APP/")

from flask_application import app as application  # Update this line to point to 'flask_application.py'
