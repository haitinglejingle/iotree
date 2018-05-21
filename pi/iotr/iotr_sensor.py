#!/usr/bin/python3

# from sense_hat import SenseHat
#sense = SenseHat()

import random
from time import sleep
import datetime
import socket
import sys
import re
import json

import paho.mqtt.publish as publish
import paho.mqtt.client  as mqtt_client

HUM_THRESHOLD_L  = 33 # rH
HUM_THRESHOLD_H  = 66 # rH
TEMP_THRESHOLD_H = 50 # c

NUM_PIS = 3

class IOTr_Sensor:

    def __init__(self, addr, ctrl_addr, 
            r_udp_port=4444, s_udp_port=4445, mqtt_port=1883, 
            sense_freq=1.0, is_rep=False,
            hostname="iot.eclipse.org", 
            sense_topic="elec3542/iotree/sense-dat", 
            ctrl_topic="elec3542/iotree/ctrl-dat"):
        # init settings
        self.sense_freq  = sense_freq # in seconds
        self.is_rep      = is_rep     # the representative
        self.auto        = False      # automatic setting adjustments
        self.min_reports = NUM_PIS

        # vars
        self.fire       = False
        self.data       = {}
        self.repdata    = []

        # settings + ctrl (udp)
        self.addr       = addr
        self.ctrl_addr  = ctrl_addr
        self.R_UDP_PORT = r_udp_port
        self.S_UDP_PORT = s_udp_port

        # data (mqtt)
        self.client = mqtt_client.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.sub_hostname = hostname
        self.pub_hostname = hostname
        self.sense_topic  = sense_topic
        self.ctrl_topic   = ctrl_topic
        self.MQTT_PORT    = mqtt_port 

        if self.is_rep:
            self.subscribeToSensors()
        # future work: multiple rep 

  #####
# UDP #
#####
    def connectToControl(self):
        # Create a TCP/IP socket each for send/receive
        rsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        # Bind the receiving socket to the port
        self.rec_addrp  = (self.ctrl_addr, self.R_UDP_PORT)
        self.send_addrp = (self.ctrl_addr, self.S_UDP_PORT)
        rsock.bind(self.rec_addrp)
        while True:
            settings, rec_addr = rsock.recvfrom(self.R_UDP_PORT)
            if settings:
                settings = settings.decode("utf-8")
                send_msg = self.decodeCommand(settings)
                # Report msg received
                sent = ssock.sendto((send_msg).encode("utf-8"), self.send_addrp)

    # takes raw_settings as string
    def decodeCommand(self, settings):
        m = re.search("=", settings)
        if m != None:
            i = re.search("=", settings).start() + 1
            val = settings[i:]
        else:
            return "Error: illegal format"

        if re.match("sense_freq", settings):
            try:
                self.sense_freq = float(val)
                return "Sensor frequency set"
            except ValueError:
                return "Error: non-numeric sensor frequency"
        elif re.match("rep", settings):
            if val == "False":
                if self.is_rep:
                    self.is_rep = False
                    self.client.loop_stop()
                return "Rep at " + self.addr + " unselected"
            elif val == "True":
                if not self.is_rep:
                    self.is_rep = True
                    self.subscribeToSensors()
                return "Rep at " + self.addr + " selected"
            else:
                return "Error: non-boolean rep setting"
        elif re.match("auto", settings):
            if val == "False":
                self.auto = False
                return "Auto off"
            elif val == "True":
                self.auto = True
                return "Auto on"
            else:
                return "Error: non-boolean auto setting"
        else:
            return "Error: unknown input"

  ######
# MQTT #
#######

### Setup ###
         
    def setupMQTT(self, hostname, sense_topic, ctrl_topic):
        self.pub_hostname = hostname # iot.eclipse.org
        self.sub_hostname = hostname # iot.eclipse.org
        self.sense_topic = sense_topic
        self.ctrl_topic = ctrl_topic

    def setMQTTPublishHost(self, hostname):
        self.pub_hostname = hostname # iot.eclipse.org

    def setMQTTPublishCtrlTopic(self, topic):
        self.ctrl_topic = topic

    def setMQTTPublishSenseTopic(self, topic):
        self.sense_topic = topic

    def setMQTTSubscribeHost(self, hostname):
        self.sub_hostname = hostname
        
    def setMQTTSubscribeTopic(self, topic):
        self.sensor_topic = topic

### Publish ###

    def publishData(self):
        if self.is_rep:
            self.publishDataToCtrl()
        else:
#            print('send to other sensors')
            self.publishDataToSensors()
            
    def publishDataToSensors(self):
        data = json.dumps(self.data)
        publish.single(self.sense_topic, payload=data, 
                qos=0,
                hostname=self.pub_hostname,
                port=self.MQTT_PORT)

    def publishDataToCtrl(self):
        if len(self.repdata) >= self.min_reports:
            repdata = json.dumps(self.repdata)
            publish.single(self.ctrl_topic, payload=repdata, 
                    qos=2,
                    hostname=self.pub_hostname,
                    port=self.MQTT_PORT)
            self.repdata = []

### Subscribe ### (to other sensors)
    def on_connect(self, client, userdata, flags, rc):
        # Successful connection is '0'
#       print("Connection result: " + str(rc))
        if rc == 0:
                # Subscribe to topics
                self.client.subscribe(self.sense_topic)


    def on_message(self, client, userdata, message):
        self.repdata.append(message.payload.decode("utf-8"))
        print("Data received: " + message.payload.decode("utf-8"))
        # print("Received message on %s: %s (QoS = %s)" % 
        #         (message.topic, message.payload.decode("utf-8"), str(message.qos)))

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Sensor " + str(self.addr) + " disconnected unexpectedly")

    def subscribeToSensors(self):
        # Connect to the specified broker
        keepalive = self.sense_freq * 5 # allow for 5x sense freq
        self.client.connect(self.sub_hostname, self.MQTT_PORT, keepalive)
        # Network loop runs in the background to listen to the events
        self.client.loop_start()

  ###########
# Detection #
###########

    def measureData(self):
    ##||## 
        #    temperature = sense.get_temperature()
        #    humidity    = sense.get_humidity()
    ##||## 
    ##--##
        temp = random.random()
        hum  = random.random()
        ts   = str(datetime.datetime.now())
        self.data = {"id": self.addr, "temp": temp, "hum": hum, "ts": ts}
        return temp, hum
    ##--##

    def checkFire(self, temp, hum):
        if (hum < HUM_THRESHOLD_L):
            self.risk = "low"
        elif (HUM_THRESHOLD_L < hum and hum < HUM_THRESHOLD_H):
            self.risk = "med"
        elif (hum > HUM_THRESHOLD_H):
            self.risk = "hi"
        if (temp > TEMP_THRESHOLD_H):
            self.fire = True
        else:
            self.fire = False

        def localResponse(self):
            if (self.fire):
                print("fire detected")
                # audio                
                # TODO: uncomment this below for rpi
#                sense.show_message("Fire detected!", text_colour=[255, 0, 0])

    def beginIOTr(self):
        while True:
            temp, hum = IOTr_Sensor.measureData(self)
#            print("rep sensor: " + str(self.is_rep))
            if (self.is_rep):
                print("Rep has " + str(len(self.repdata)) + " data in queue to be sent")
            self.publishData()
            self.checkFire(temp, hum)

            sleep(self.sense_freq)

