
import subprocess
import time
import RPi.GPIO as GPIO
import urllib.request, urllib.parse, urllib.error
import http.client
import minimalmodbus
import datetime
import serial

Water1 = minimalmodbus.Instrument('/dev/ttyUSB0', 2) #port name , slave address(in decimal)
Water1.serial.baudrate                                      = 19200
Water1.serial.bytesize                                      = 8
Water1.serial.parity                                        = serial.PARITY_NONE
Water1.serial.stopbits                                      = 1
Water1.serial.timeout                                       = 1                             # secondes
Water1.mode                                                 = minimalmodbus.MODE_RTU        # rtu ou ascii // MODE_ASCII ou MODE_RTU
Water1.debug                                                = False
Water1.serial.xonxoff                                       = True
Water1.serial.rtscts                                        = False
Water1.serial.dsrdtr                                        = False
minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL        = True
    


#-----------------------------------------------------------------------------------------------------------------------------------------------#

def WaterOne(start,end, Division):
    #print(start)
    60 / Division = TimePoints #calculates at which interval to measure according to Main code
    
    t = datetime.datetime.now()# look current time
    CheckPoint = Light1.read_register(0,1) #look on arduino at which checkpoint it currently is; register number, number of decimals 
                #print(Status)
    
    for x in range(Division)#checks every time point where measurment is expected
    
        if t.minute >= (TimePoints * x) and CheckPoint <= x: # change to hours
            
            
            #do measurment sequence
            Water1.write_register(0, x, 0)
        
        elif t.minute >= 0 and CheckPoint >= Divison:
            Water1.write_register(0, 0, 0)
