import time
from flask import Blueprint, request, g, abort, jsonify, render_template, redirect, url_for

dab = Blueprint('dab', __name__, template_folder='templates')


#################################################
# Provide a UI
#################################################

@dab.route('/', methods=['GET'])
def radio():
    return render_template('radio.html')

#################################################
# Info - all together
#################################################
@dab.route('/info', methods={'GET'})
def info():
    return jsonify({"info": g.radio.status})


#################################################
# Channel related functions
#################################################

@dab.route('/channels', methods=['GET'])
def channels():
    return jsonify({'channels': g.radio.channels})

@dab.route('/channel', methods=['GET'], defaults={'cnum': None})
@dab.route('/channel/<int:cnum>', methods=['PUT', 'POST'], defaults={'cname': None})
@dab.route('/channel/<cname>', methods=['PUT', 'POST'], defaults={'cnum': None})
def set_channel(cnum, cname):
    # Set the channel if appropriate
    if request.method == 'POST' or request.method == 'PUT':
        if cnum != None:
            g.radio.channelID = cnum
        elif cname != None:
            g.radio.channel = cname
    # Return the channel that we are tuned to
    return jsonify({'channel': g.radio.channel})

@dab.route('/channel/ensemble', methods=['GET'])
def ensemble ():
    return jsonify({'ensemble': g.radio.ensemble})

@dab.route('/favorite/toggle', methods=['POST'], defaults={'channel': None})
@dab.route('/favorite/toggle/<channel>', methods=["POST"])
def togglefavorite(channel):
    g.radio.togglefavorite(channel)
    return jsonify({'favorites': g.radio.favorites})

#################################################
# Volume related functions
#################################################

@dab.route('/volume', methods=['GET'], defaults={'vol':None, 'command':None})
@dab.route('/volume/<int:vol>', methods=['PUT', 'POST'], defaults={'command':None})
@dab.route('/volume/<command>', methods=['PUT', 'POST'], defaults={'vol': None})
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
            elif command == 'mute':
                g.radio.muted = True
            elif command == 'unmute':
                g.radio.muted = False
            else:
                abort(404)

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
    return jsonify({'text': g.radio.text})

@dab.route('/nowplaying', methods=['GET'])
def nowplaying():
    return jsonify({'text': g.radio.nowPlaying})


#################################################
# Technical functions
#################################################

@dab.route('/signal', methods=['GET'])
def signal():
    return jsonify({'signal_strength': g.radio.signal_strength(),
        'signal_quality': g.radio.dab_qualitiy})

@dab.route('/status', methods=['GET'])
def status():
    return jsonify({'radio_status': g.radio.status,
        'radio_ready': g.radio_status})

@dab.route('/datarate', methods=['GET'])
def datarate():
    return jsonify({'datarate': g.radio.datarate()})
