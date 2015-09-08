import time
from flask import Blueprint, request, g, abort, jsonify, render_template

dab = Blueprint('dab', __name__, template_folder='templates')

@dab.route('/channels', methods=['GET'])
def channels():
	print("Getting channels")
	channels = g.radio.programs
	names = {}
	for c in channels:
		names[c.name] = c.index
	return jsonify({'channels': names})

@dab.route('/channel', methods=['GET'], defaults={'cnum': None})
@dab.route('/channel/<int:cnum>', methods=['GET', 'POST'])
def set_channel_by_index(cnum):
	# Set the channel if appropriate
	if request.method == 'POST':
		channels = g.radio.programs
		if cnum < len(channels):
			channel = channels[cnum]
			g.radio.stereo = True
			g.radio.volume = 10
			channel.play()
	# Must check the status or the channel doesn't play!
			while g.radio.status != 0:
				time.sleep(1)

	# Return the channel that we are tuned to	
	channel = g.radio.currently_playing
	if channel != None:
		return jsonify({'channel': channel.name})
	else:
		return jsonify({'channel': 'None'})
	

@dab.route('/volume', methods=['GET'], defaults={'vol':None})
@dab.route('/volume/<int:vol>', methods=['GET', 'POST'])
def set_volume(vol):
	# Set the volume if appropriate
	if request.method == 'POST':
		if vol != None:
			if vol < 0:
				 vol = 0
			if vol > 16:
				 vol = 16
			g.radio.volume = vol

	# Return the volume setting
	return jsonify({'volume': str(g.radio.volume)})

@dab.route('/signal', methods=['GET'])
def signal():
	return jsonify({'strength': g.radio.signal_strength.strength})

@dab.route('/status', methods=['GET'])
def status():
	return jsonify({'status': g.radio.status,
			'ready': g.radio.is_system_ready()})

@dab.route('/datarate', methods=['GET'])
def data_rate():
	return jsonify({'datarate': g.radio.data_rate})

@dab.route('/channel/next', methods=['POST'])
def next_channel():
	g.radio.next_stream()
	return jsonify({'channel': g.radio.currently_playing.name})


@dab.route('/channel/prev', methods=['POST'])
def prev_channel():
	g.radio.prev_stream()
	return jsonify({'channel': g.radio.currently_playing.name})
