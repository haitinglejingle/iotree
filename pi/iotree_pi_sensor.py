from threading import Thread
from iotr.iotr_sensor import IOTr_Sensor

########
# Main #
########

# udp 
sense_addr = "localhost"
ctrl_addr  = "localhost"
r_udp_port = 4444
s_udp_port = 4445

# mqtt
mqtt_port   = 1883 
hostname    = "iot.eclipse.org"
sense_topic = "elec3542/iotree/sense-dat"
ctrl_topic  = "elec3542/iotree/ctrl-dat"

sense_freq = 1
is_rep1    = True
is_rep2    = False

s1 = IOTr_Sensor(sense_addr, ctrl_addr, 
        r_udp_port, s_udp_port, mqtt_port, 
        sense_freq, is_rep1,
        hostname, sense_topic, ctrl_topic)

Thread(target=s1.connectToControl).start()
s1.beginIOTr()
