import sys
from flask import Flask, g, request

#from reverseproxy import ReverseProxied
from bp.dab import dab

# This needs both a shared library from Monkeyboard
# and a python wrapper to this library
# https://github.com/madpilot/keystonepy
# https://www.monkeyboard.org/tutorials/78-interfacing/87-raspberry-pi-linux-dab-fm-digital-radio
from keystone.radio import Radio as Radio

# Settings
RADIO_DEVICE = '/dev/ttyACM0'

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
		print("Trying to open radio on " + app.config['RADIO_DEVICE'])
		try:
			radio = Radio(app.config['RADIO_DEVICE'])
			radio.open()
		except:
			print ("Error opening Radio")
			sys.exit(-1)
	else:
		print("Using existing radio")
	return radio

# Pre-request setup
@app.before_request
def before_request():
	g.radio = get_radio()
		

if __name__ == '__main__':
	app.run(host='0.0.0.0')
