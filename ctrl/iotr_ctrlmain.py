from threading import Thread
from iotr.iotr_ctrl import IOTr_Ctrl

# sense_addr = "localhost"

ctrl = IOTr_Ctrl();
ctrl.startSensorConnect()
ctrl.startInterface()

#
#print("prepping data for sophisticated sensor fusion...") 
