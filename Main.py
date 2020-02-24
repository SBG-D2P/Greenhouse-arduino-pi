
import subprocess
import urllib.request, urllib.parse, urllib.error
import http.client
import minimalmodbus
import datetime
import time
import serial
import Light #don't forget to change name of other module with actual function for lights
import Water #import functions for waterprobes
import WaterSequence #Sequence of functions and checkpoints to do water measurements

start = 11
end = start +10
Connect = 0
Division = 2




while True:
    
    if Connect == 5:
        print ("Device X not connected")
    try:
        WaterSequence.WaterOne()
        
    except ValueError as error:
        Connect = Connect + 1
        print("not connected")
    
    time.sleep(1)

   
#rs485V10.LightOne(start,end) #Function to control lights
