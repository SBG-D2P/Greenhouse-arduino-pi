
import subprocess
import time
import RPi.GPIO as GPIO
import urllib.request, urllib.parse, urllib.error
import http.client
import minimalmodbus
import datetime
import serial

Light1 = minimalmodbus.Instrument('/dev/ttyUSB0', 1) #port name , slave address(in decimal)
Light1.serial.baudrate                                      = 19200
Light1.serial.bytesize                                      = 8
Light1.serial.parity                                        = serial.PARITY_NONE
Light1.serial.stopbits                                      = 1
Light1.serial.timeout                                       = 1                             # secondes
Light1.mode                                                 = minimalmodbus.MODE_RTU        # rtu ou ascii // MODE_ASCII ou MODE_RTU
Light1.debug                                                = False
Light1.serial.xonxoff                                       = True
Light1.serial.rtscts                                        = False
Light1.serial.dsrdtr                                        = False
minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL        = True
    


#-----------------------------------------------------------------------------------------------------------------------------------------------#

def LightOne(start,end):
    print(start)
    
    t = datetime.datetime.now()
    Status = Light1.read_register(0,1) #register number, number of decimals 
                #print(Status)

    if t.minute >= start  and t.minute < end and Status != 1: #turns light ON if daytime
            Light1.write_register(0, 1, 0)
            #test = Light1.read_register(9,1) #register number, number of decimals
            #print(test)


    elif t.minute >= start  and t.minute < end and Status == 1: #checks if there is a issue with lights during daytime
            Relay1 = Light1.read_register(3,1) #register number, number of decimals
            Relay2 = Light1.read_register(4,1) #register number, number of decimals
            if Relay1 != 1 or Relay2 != 1:
                    print("x")
                                #email

    elif t.minute < start  or t.minute >= end:
            if Status != 2: #turns lights OFF during nighttime
                    Light1.write_register(0, 2, 0)

    elif  t.minute < start  or t.minute >= end:
            if Status ==2:  #checks if there is an issue with lights during nighttime
                    Relay1 = Light1.read_register(3,1) #register number, number of decimals
                    Relay2 = Light1.read_register(4,1) #register number, number of decimals
                    if Relay1 != 1 or Relay2 != 1:
                            print("y")
                                        #email



