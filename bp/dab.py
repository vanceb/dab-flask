import time
from flask import Blueprint, request, g, abort, jsonify, render_template

dab = Blueprint('dab', __name__, template_folder='templates')

#################################################
# Info - all together
#################################################
@dab.route('/info', methods={'GET'})
def info():
	info = {}
	info['radio_status'] = g.radio.status
	info['radio_ready'] = g.radio.is_system_ready()
	if g.radio.currently_playing != None:
		# Signal Info
		info['signal_strength'] = g.radio.signal_strength.strength
		info['data_rate'] = g.radio.data_rate
		info['signal_quality'] = g.radio.dab_signal_quality
		# Channel Info
		info['channel'] = g.radio.currently_playing.name
		info['ensemble'] = g.radio.ensemble_name(g.radio.currently_playing.index, 'DAB')
		# Volume
		info['volume'] = g.radio.volume
		info['stereo'] = g.radio.stereo
	return jsonify(info)


#################################################
# Channel related functions
#################################################

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
			status_check()

	# Return the channel that we are tuned to	
	channel = g.radio.currently_playing
	if channel != None:
		return jsonify({'channel': channel.name})
	else:
		return jsonify({'channel': 'None'})
	
@dab.route('/channel/next', methods=['POST'])
def next_channel():
	g.radio.next_stream()
	return jsonify({'channel': g.radio.currently_playing.name})


@dab.route('/channel/prev', methods=['POST'])
def prev_channel():
	g.radio.prev_stream()
	return jsonify({'channel': g.radio.currently_playing.name})


@dab.route('/channel/ensemble', methods=['GET'])
def ensemble ():
	return jsonify({'ensemble': g.radio.ensemble_name(g.radio.currently_playing.index, 'DAB')})

#################################################
# Volume related functions
#################################################

@dab.route('/volume', methods=['GET'], defaults={'vol':None, 'command':None})
@dab.route('/volume/<int:vol>', methods=['GET', 'POST'], defaults={'command':None})
@dab.route('/volume/<command>', methods=['POST'], defaults={'vol': None})
def set_volume(vol, command):
	# Get the current volume
	current_volume = g.radio.volume
	# Set the volume if appropriate
	if request.method == 'POST':
		if vol != None:
			if vol < 0:
				 vol = 0
			if vol > 16:
				 vol = 16
			g.radio.volume = vol
		elif command != None:
			if command == 'up' and current_volume < 16:
				g.radio.volume = current_volume + 1
			elif command == 'down' and current_volume > 0:
				g.radio.volume = current_volume - 1
			elif command == 'mute' and g.muted == False:
				g.muted = True
				g.premute_volume = current_volume
				g.radio.mute()
			elif command == 'unmute' and g.muted == True:
				g.muted = False
				g.radio.volume = g.premute_volume
			else:
				abort(404)
			# Coming out of mute needs this check!
			status_check()

	# Return the volume setting
	return jsonify({'volume': g.radio.volume})

@dab.route('/stereo', methods=['GET'], defaults={'mode':None})
@dab.route('/stereo/<mode>', methods=['POST'])
def stereo(mode):
	if request.method == 'POST':
		if mode == 'stereo' or mode == 'true':
			g.radio.stereo = True
		elif mode == 'mono' or mode == 'false':
			g.radio.stereo = False
		else:
			abort(404)

	return jsonify({'stereo': g.radio.stereo})

#################################################
# Text related functions
#################################################

@dab.route('/text', methods=['GET'])
def text():
	text = []
	t = g.radio.currently_playing.text
	while t != None:
		text.append(t)
		t = g.radio.currently_playing.text
	return jsonify({'text': text})

#################################################
# Technical functions
#################################################

@dab.route('/signal', methods=['GET'])
def signal():
	return jsonify({'signal_strength': g.radio.signal_strength.strength,
			'signal_quality': g.radio.dab_signal_quality})

@dab.route('/status', methods=['GET'])
def status():
	return jsonify({'radio_status': g.radio.status,
			'radio_ready': g.radio.is_system_ready()})

@dab.route('/datarate', methods=['GET'])
def data_rate():
	return jsonify({'data_rate': g.radio.data_rate})

#################################################
# Helper functions
#################################################

# Create a function that checks the status of the radio
# Required to get some changes to be reflected in the readio
def status_check(timeout=5):
	i = 0
	success = True
	while g.radio.status != 0:
		time.sleep(1)	
		i += 1
		if i > timeout:
			success = Fail
			break
	return success
