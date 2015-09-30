import sys
import logging
from flask import Flask, g, request, redirect, url_for

#from reverseproxy import ReverseProxied
from bp.dab import dab
from lib.dabRadio import DABRadio as DABRadio

# Settings
RADIO_DEVICE = '/dev/ttyACM0'

# Get a logger
logger = logging.getLogger(__name__)

# Global variable to hold the Radio object
radio = None

# Setup the application
app = Flask(__name__)
app.config.from_object(__name__)
#app.wsgi_app = ReverseProxied(app.wsgi_app)
app.register_blueprint(dab)

# Function to return the radio object
def get_radio():
	global radio
	if radio is None:
		logger.debug("Trying to open radio on " + app.config['RADIO_DEVICE'])
		try:
			radio = DABRadio(app.config['RADIO_DEVICE'])
		except:
			print ("Error opening Radio")
			sys.exit(-1)
	else:
		logger.debug("Using existing radio")
	return radio

# Pre-request setup
@app.before_request
def before_request():
	g.radio = get_radio()

@app.after_request
def after_request(response):
	return response


if __name__ == '__main__':
#	app.run(host='0.0.0.0')
	app.run(host='0.0.0.0', debug=True)
