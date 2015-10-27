import threading
import datetime as dt
import json
import logging
import os.path
import time
import re

from keystone.radio import Radio as Radio

###########################################################
# Default variables and Global Variables
###########################################################

DEFAULT_RADIO_CONFIG = {"radioDevice": "/dev/ttyACM0", "volume": 9, "stereo": True, "station": 26, "npRegex": "Now Playing: (.*)", "favorites":[]}

exitFlag = 0

###########################################################
# TxtThread Class provides a background thread to
# continuously query the radio for txt info
###########################################################

class TxtThread (threading.Thread):
    def __init__(self, parent, threadName, seconds=1):
        self.logger = logging.getLogger(threadName)
        self.logger.info("Starting radio txt thread")
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.parent = parent
        self.seconds = seconds

    def run(self):
        global exitFlag
        txt = None
        while exitFlag == 0:
            self.logger.debug("Looking for radio txt")
            # Start threadsafe access to the radio
            self.parent.radioLock.acquire()
            if self.parent.radio.currently_playing != None:
                txt = self.parent.radio.currently_playing.text
            self.parent.radioLock.release()
            # End of threadsafe access to the radio
            if txt != None and txt != "":
                self.parent.add_txt(unicode(txt))
            time.sleep(self.seconds)
        self.logger.info("Radio txt thread stopping")
        return True


###########################################################
# RadioText class manages and deduplicates DAB Text
###########################################################

class RadioText(object):
    def __init__(self, npRegex=None, ageout=300, maxNp=30):
        self.logger = logging.getLogger(__name__)
        if npRegex != None:
            self.npRegex = re.compile(npRegex)
        else:
            self.npRegex = None
        self.ageout = ageout
        self.maxNp = maxNp
        self._lck = threading.Lock()
        self.reset()

    def add(self, text):
        self._lck.acquire()
        if text != None:
            self.logger.debug("Adding: " + text)
            matched = False
            if self.npRegex != None:
                self.logger.debug("Checking for Now Playing match")
                track = self.npRegex.match(text)
                if track:
                    self.logger.debug("Matched the Now Playing regex")
                    matched = True
                    nowPlaying = track.group(1)
                    if len(self.np) == 0 or nowPlaying != self.np[0]:
                        self.logger.info("Adding new Now Playing Track: " + nowPlaying)
                        self.np = [nowPlaying] + self.np
                    else:
                        self.logger.debug("Already notified of this track: " + nowPlaying)
            if not matched:
                self.logger.debug("Adding to the messages")
                if text in self.txt:
                    self.logger.debug("Seen this message before, pushing to the top")
                    # we have seen this message before
                    self.txt_list.remove(text)
                else:
                    self.logger.info("New message: " + text)
                self.txt[text] = dt.datetime.utcnow()
                self.txt_list = [text] + self.txt_list

        # Expire old messages
        t = dt.datetime.utcnow()
        self.logger.debug("Expiring messages older than %d seconds" % self.ageout)
        for msg in self.txt_list:
            if (t - self.txt[msg]).seconds > self.ageout:
                self.logger.debug("Expiring: " + msg)
                self.txt_list.remove(msg)
                del self.txt[msg]
        # remove old Now Playing entries
        if len(self.np) > self.maxNp:
            self.logger.debug("Trimming Now Playing list")
            self.np = self.np[:self.maxNp]
        self._lck.release()

    def text(self, max=None):
        txt = None
        self._lck.acquire()
        if max == None or max > len(self.txt_list):
            txt = self.txt_list
        else:
            txt = self.txt_list[:max]
        self._lck.release()
        return txt

    def nowPlaying(self, max=None):
        np = None
        self._lck.acquire()
        if max == None or max > len(self.np):
            np = self.np
        else:
            np = self.np[:max]
        self._lck.release()
        return np

    def reset(self):
        self._lck.acquire()
        self.txt = {}
        self.txt_list = []
        self.np = []
        self._lck.release()


###########################################################
# DABException Class gives an identifiable error
###########################################################

class DABException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


###########################################################
# DABRadio class encapsulates communication with the radio
###########################################################

class DABRadio(object):

###########################################################
# Basic class functions
###########################################################

    def __init__(self, radioDevice=None, npRegex = None, configFile="dab.json"):
        # Start logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("Started logging...")

        # Create a Lock to control access to the radio
        self.radioLock = threading.Lock()

        #Save the config file location
        self.configFile = configFile

        # Load the config file if it exists
        try:
            self.logger.info("Attempting to load radio state from " + configFile)
            # Check to see that the file exists
            if os.path.isfile(configFile):
                # Load the data
                with open(configFile) as datafile:
                    self.config = json.load(datafile)
                    self.logger.info("Successfully loaded radio state")
            else:
                self.logger.warning("Radio state file does not exist, starting radio with default options")
                self.config = DEFAULT_RADIO_CONFIG
        except:
            self.logger("Error reading radio state from " + configFile)
            self.config = DEFAULT_RADIO_CONFIG

        # If a radioDevice was provided then use that instead of the one in the config
        if radioDevice != None:
            self.logger.info("Using radio device: " + radioDevice)
            self.config["radioDevice"] = radioDevice

        # Open the radio device
        self.logger.info("Trying to open radio on " + self.config["radioDevice"])
        try:
            self.radio = Radio(self.config["radioDevice"])
            self.radio.open()
            self.logger.info("Successfully opened the radio on " + self.config["radioDevice"])
        except:
            self.logger.critical("Error opening Radio on " + self.config["radioDevice"])
            raise DABException("Unable to open radio on " + self.config["radioDevice"])

        # Kick off the radio text thread
        if npRegex != None:
            self.config["npRegex"] = npRegex
        self.rt = RadioText(npRegex = self.config["npRegex"])
        self.logger.debug("Starting the radio txt thread")
        self.txtThread = TxtThread(self, "TxtThread", 1)
        self.txtThread.start()

        # Set up the radio
        self._channels = self.channels
        self.volume = self.config["volume"]
        self.stereo = self.config["stereo"]
        self.channelID = self.config["station"]

        # Set up Mute variables
        self._muted = False
        self.unmute_volume = self.config["volume"]


        # Write out the config to disk
        self.updateStatus()


    def __str__(self):
        return repr(self.config["radioDevice"])

###########################################################
# Current Radio Status in one call
###########################################################
    @property
    def status(self):
        status = {}
        status['radio_status'] = self.radio_status
        status['radio_ready'] = self.radio_ready
        status['signal_strength'] = self.signal_strength
        status['dab_quality'] = self.dab_quality
        status['datarate'] = self.datarate
        status['volume'] = self.volume
        status['channel'] = self.channel
        status['channel_id'] = self.channelID
        status['favorites'] = self.config["favorites"]
        status['ensemble'] = self.ensemble
        status['stereo'] = self.stereo
        status['text'] = self.text
        status['now_playing'] = self.nowPlaying
        return status

###########################################################
# Text related functions
###########################################################

    def add_txt(self, txt):
        self.rt.add(txt)

    @property
    def text(self, max=None):
        return self.rt.text(max=max)

    @property
    def nowPlaying(self, max=None):
        return self.rt.nowPlaying(max=max)


###########################################################
# Channel related functions
###########################################################

    @property
    def channels(self):
        self.radioLock.acquire()
        channels = self.radio.programs
        self.radioLock.release()
        self._channels = {}
        for c in channels:
            if c.application_type == 255:
                self._channels[c.name] = c.index

        return self._channels

    @property
    def channel(self):
        self.logger.debug("Reading current Channel from radio")
        self.radioLock.acquire()
        c = self.radio.currently_playing.name
        self.radioLock.release()
        return c

    @channel.setter
    def channel(self, channel_name):
        channels = self.channels
        if channel_name in channels:
            self.channelID = channels[channel_name]


    @property
    def channelID(self):
        self.logger.debug("Reading current Channel ID from radio")
        self.radioLock.acquire()
        c = self.radio.currently_playing.index
        self.radioLock.release()
        return c

    @channelID.setter
    def channelID(self, channelID):
        self.logger.info("Changing channel to ChannelID: " + str(channelID))
        self.radioLock.acquire()
        channels = self.radio.programs
        self.radioLock.release()
        if channelID < len(channels):
            channel = channels[channelID]
            self.radioLock.acquire()
            channel.play()
            self.radioLock.release()
            self.rt.reset()
            # Must check the status or the channel doesn't play...
            self.radio_status_check()
            self.logger.info("Channel changed to: " + str(channelID))
            self.updateStatus()
        else:
            self.logger.error("Attempt to change to channel outside the maximum number of channels.  Requested channel ID %d, maximum ID %d" % channelID, len(channels))
        return self

    @property
    def favorites(self):
        return self.config["favorites"]

    @favorites.setter
    def favorites(self, fav_list):
        if type(fav_list) == type([]):
            self.logger.info("Setting favorites to: " + str(fav_list))
            self.config["favorites"] = fav_list
        else:
            self.logger.error("Attempt to set favorites with something that is not a list")
        self.updateStatus()
        return self

    def favorite(self, channel_name=None):
        if channel_name == None:
            channel_name = self.channel
        if not channel_name in self.config["favorites"]:
            self.config["favorites"].append(channel_name)
        self.updateStatus()

    def unfavorite(self, channel_name=None):
        if channel_name == None:
            channel_name = self.channel
        if channel_name in self.config["favorites"]:
            self.config["favorites"].remove(channel_name)
        self.updateStatus()

    def togglefavorite(self, channel_name=None):
        if channel_name == None:
            channel_name = self.channel
        if channel_name in self.config["favorites"]:
            self.unfavorite(channel_name)
        else:
            self.favorite(channel_name)
        self.updateStatus()


    @property
    def ensemble(self):
        self.radioLock.acquire()
        e = self.radio.ensemble_name(self.radio.currently_playing.index, 'DAB')
        self.radioLock.release()
        return e

###########################################################
# Audio related functions
###########################################################

    @property
    def volume(self):
        self.logger.debug("Reading current Volume from radio")
        self.radioLock.acquire()
        v = self.radio.volume
        self.radioLock.release()
        return v

    @volume.setter
    def volume(self, vol):
        self.logger.debug("Setting Volume to " + str(vol))
        if vol >= 0 and vol <= 16:
            self.radioLock.acquire()
            self.radio.volume = vol
            self.radioLock.release()
            self.logger.info("Set Volume to " + str(vol))
            self.config["volume"] = vol
            self.updateStatus()
        else:
            self.logger.warning("Attempt to set volume outside valid range, ignored...")

    @property
    def muted(self):
        return self._muted

    @muted.setter
    def muted(self, value):
        if value == True and self.muted == False:
            self._muted = True
            self.unmute_volume = self.volume
            self.radioLock.acquire()
            self.radio.mute()
            self.radioLock.release()
        elif value == False and self._muted == True:
            self._muted = False
            self.radioLock.acquire()
            self.radio.volume = self.unmute_volume
            self.radioLock.release()
        self.radio_status_check()

    @property
    def stereo(self):
        self.radioLock.acquire()
        s = self.radio.stereo
        self.radioLock.release()
        return s

    @stereo.setter
    def stereo(self, mode=stereo):
        if mode == 'stereo':
            mode = True
        elif mode == 'mono':
            mode = False
        self.radioLock.acquire()
        self.radio.stereo = mode
        self.radioLock.release()
        self.config["stereo"] = mode
        self.updateStatus()


###########################################################
# Signal related functions
###########################################################

    @property
    def signal_strength(self):
        self.radioLock.acquire()
        s = self.radio.signal_strength.strength
        self.radioLock.release()
        return s

    @property
    def dab_quality(self):
        self.radioLock.acquire()
        d = self.radio.dab_signal_quality
        self.radioLock.release()
        return d

    @property
    def radio_status(self):
        self.radioLock.acquire()
        s = self.radio.status
        self.radioLock.release()
        return s

    @property
    def radio_ready(self):
        self.radioLock.acquire()
        r = self.radio.is_system_ready()
        self.radioLock.release()
        return r

    @property
    def datarate(self):
        self.radioLock.acquire()
        d = self.radio.data_rate
        self.radioLock.release()
        return d

###########################################################
# Helper functions
###########################################################

    def updateStatus(self):
        self.logger.debug("Updating status")
        self.radioLock.acquire()
        cp = self.radio.currently_playing
        self.radioLock.release()
        if cp != None:
            self.radioLock.acquire()
            self.config["volume"] = self.radio.volume
            self.config["stereo"] = self.radio.stereo
            self.radioLock.release()
            self.config["station"] = cp.index
            self.logger.debug("Attempting to write radio status to " + self.configFile)
            try:
                with open(self.configFile, "w+") as datafile:
                    json.dump(self.config, datafile)
            except:
                self.logger.error("Problem writing radio status to: " + self.configFile)
        else:
            self.logger.warning("Attempted to update the status, but the radio is not playing...")

    def radio_status_check(self, timeout = 5):
        i = 0
        success = None
        while success == None:
            self.radioLock.acquire()
            status = self.radio.status
            self.radioLock.release()
            if status != 0:
                time.sleep(1)
                i += 1
            else:
                success = True
            if i > timeout:
                success= False
                break
        return success

    def exit(self):
        # Don't use the volume setter as it keeps state so will come on at zero volume next time...
        self.radioLock.acquire()
        self.radio.volume = 0
        self.radioLock.release()
        # Signal the txt thread to exit
        exitFlag = 1
import os
import json
import logging.config

def setup_logging(
        default_path='logging.json',
        default_level=logging.INFO,
        env_key='LOG_CFG'
        ):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

if __name__ == "__main__":
    import select # for detecting user input with timeout
    import sys

    # Start Logging
    setup_logging()

    # Create a radio instance with the standard BBC Now Playing marker
    d = DABRadio(npRegex="Now Playing: (.*)")
    print("This program will play the radio until you type something and hit return...")
    i = False
    while not i:
        i, o, e = select.select( [sys.stdin], [], [], 15 )
        print()
        print(dt.datetime.now().isoformat(' '))
        print(d.text)
        print(d.nowPlaying)
    d.exit()
