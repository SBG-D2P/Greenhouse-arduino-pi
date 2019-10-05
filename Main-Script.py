
import subprocess
import time
import RPi.GPIO as GPIO
import urllib.request, urllib.parse, urllib.error
import http.client
import minimalmodbus
import datetime
import serial
import rs485V10 # don't forget to change name of other module with actual function for lights

start = 56
end = start +1
Connect = 0
Division = 2

while True:
    
    if Connect == 5:
        print ("Device X not connected")
    try:
        rs485V10.LightOne(start,end)
    except ValueError as error:
        Connect = Connect + 1
        print("not connected")
    
    time.sleep(1)

'''
Test code to measure and gather data from probe
#while True:

for n in range(0,16):  
    Water.Water1.write_register(2, n, 0) #write probe number n no deciaml - register number, number of decimals
    time.sleep(0.04)
    Status = Water.Water1.read_register(2,0) #register number, number of decimals 
    print(Status)
    Water.Water1.write_register(1, 2, 0) #register number, number of decimals
    time.sleep(5)
    #Status = Water.Water1.read_register(1,0) #register number, number of decimals 
    #print(Status)
    Water.FetchData(n)        
   
'''
