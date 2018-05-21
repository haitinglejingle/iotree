import json
import socket
import datetime
import paho.mqtt.client  as mqtt_client
from time import sleep


# udp ports
S_UDP_PORT = 4444
R_UDP_PORT = 4445
# setting prefixes
SENSE_FREQ = "sense_freq="
REP        = "rep="
AUTO       = "auto="
AUDIO_UP   = "audio_upload="

MQTT_PORT = 1883
# mqtt receiving
ctrl_topic  = "elec3542/iotree/ctrl-dat"

class IOTr_Ctrl:

    def __init__(self):
        # ports
        self.S_UDP_PORT = 4444
        self.R_UDP_PORT = 4445
        self.raw_data = [];
        self.data_keys = [];

    def setupSockets(send_addr):
        ssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        rsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # bind the receiving socket to the port
        rec_addr  = (send_addr, R_UDP_PORT)
        rsock.bind(rec_addr)

        return (ssock, rsock)

    # send message
    def sendSetting(setting, sense_addr, srsockpair):
        srsockpair[0].sendto(setting.encode("utf-8"), (sense_addr, S_UDP_PORT))
        msg, rec_addr = srsockpair[1].recvfrom(R_UDP_PORT)
        return msg.decode("utf-8")

    def changeSetting(setting, sense_addr):
        srpair = IOTr_Ctrl.setupSockets(sense_addr)
        response = IOTr_Ctrl.sendSetting(setting, sense_addr, srpair)
        srpair[0].close()
        srpair[1].close()
        return response

    # change settings
    def changeSenseFreq(sense_addr, new_freq):
        sense_freq = SENSE_FREQ + str(new_freq)
        return IOTr_Ctrl.changeSetting(sense_freq, sense_addr)

    def changeRep(sense_addr, is_rep):
        rep = REP + str(is_rep)
        return IOTr_Ctrl.changeSetting(rep, sense_addr)

    def startInterface(self):
        print("Controls Interface is up and running!")
        while True:
            com = input().split()
            try:
                if len(com) == 0:
                    pass
                elif com[0] == '-s':    
                    sense_addr = com[1] 
                    sense_freq = com[2]
                    print(IOTr_Ctrl.changeSenseFreq(sense_addr, sense_freq))
                elif com[0] == '-r':
                    sense_addr = com[1] 
                    is_rep     = com[2]
                    print(IOTr_Ctrl.changeRep(sense_addr, is_rep))
                elif com[0] == '-a':
                    print('not implemented yet')
                else:
                    print("Unkown input")
            except IndexError: 
                    print("Unkown input")
### INIT ###
# auto       = AUTO       + "True"
# audio_up   = AUDIO_UP   + "./testfile.mp3"

    def decodeData(self, s_id="", temp="", hum="", ts=""):
        # get data here
        pass

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to IoTree Network!")
            # Subscribe to topics
            client.subscribe(ctrl_topic)

    def on_message(self, client, userdata, message):
        self.raw_data = json.loads(message.payload.decode("utf-8"))
        for i in range(0, len(self.raw_data)):
            dat = json.loads(self.raw_data[i])
#            self.decodeData(dat)
            self.data_keys.append(dat)
        print("Data received on: " + str(datetime.datetime.now()))


    def printDataCollection(self):
        print(self.data_keys)

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Manager disconnected unexpectedly from sensor network")

    def startSensorConnect(self):
        client = mqtt_client.Client()
        client.on_connect    = self.on_connect
        client.on_message    = self.on_message
        client.on_disconnect = self.on_disconnect

        sense_freq = 50
        keepalive = 50 * sense_freq  # keep network up
        client.connect("iot.eclipse.org", MQTT_PORT, keepalive)
        # Network loop runs in the background to listen to the events
        client.loop_start()
