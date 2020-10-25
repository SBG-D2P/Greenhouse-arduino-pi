import RPi.GPIO as GPIO
import subprocess
import urllib.request, urllib.parse, urllib.error
import http.client
import minimalmodbus
import datetime
import time
import serial
#import Light #don't forget to change name of other module with actual function for lights
#import Water #import functions for waterprobes
#import WaterSequence #Sequence of functions and checkpoints to do water measurements
import pandas as pd
import numpy as np


#--------------------------------------Creates all slaves - TIME 10 miliseconds for 100 -------------------------
#first_time = datetime.datetime.now()
IDList=[[] for j in range(100)] # creates list with j items to store the slaves' names

for i in range (100):
    IDList[i] = minimalmodbus.Instrument('/dev/ttyUSB0', i)# creates the slaves and store their names

SlaveID = [] # List to store the slaves (as objects)
for i in range (100):
    SlaveID.append(minimalmodbus.Instrument('/dev/ttyUSB0', i)) #stores the slaves (objects) in the SlaveID list to be called in the code

#second_time = datetime.datetime.now()
#difference = second_time - first_time
#print(difference)
#--------------------------------------------------------------------------------------------------------------

#----------------------------------------Polls All Slaves to Get Info------------------------------------------  
Indexes = range(100)
Columns = ['A']
CurrentDevices = pd.DataFrame(index=Indexes, columns=Columns)

def Poll():

    for i in range (100):
        try:
            num = SlaveID[i].read_register(13,0)
            CurrentDevices.at[i,'A'] = num
            time.sleep(0.25)
        
        except IOError as error:
            CurrentDevices.at[i,'A'] = 0
    #CurrentDevices.to_csv('Devices.csv', mode='w' ,index=False, header=False)
    return CurrentDevices
    
#---------------------------------------------------------------------------------------------------------------

#----------------------------------------Pandas Compare Gathered Data------------------------------------------
def Devices():
    OldDevices = pd.read_csv('Devices.csv', names = 'A')
    print(OldDevices)
    print(CurrentDevices)
    #print(CurrentDevices['A'] < OldDevices['A'])
    
    for k in range (100):
        if CurrentDevices.at[k,'A'] == 0 and OldDevices.at[k,'A'] != 0:
            print('Device' + str(k) + 'is disconected')
            #add script for emails
        elif CurrentDevices.at[k,'A'] > 0 and OldDevices.at[k,'A'] == 0:
            print('Device' + str(k) + 'is now conected')
            #CurrentDevices.at[k,'B'] =
        elif CurrentDevices.at[k,'A'] > 0 and OldDevices.at[k,'A'] > 0 and CurrentDevices.at[k,'A'] != OldDevices.at[k,'A']:
            print('Did you change the device?')
        else:
            print('else')
    
    CurrentDevices.to_csv('Devices.csv', mode='w' ,index=False, header=False)
    time.sleep(10)
#---------------------------------------------------------------------------------------------------------------

while True: #-----------------------MAIN LOOP-----------------------------------------------------
    
    Poll()
    Devices()
    time.sleep(60)
    
    
    
    #num2 = SlaveID[2].read_register(4,0) #fetch info about which probes are plugged (position 4 of array, 0 decimal)

'''
    start = 11
    end = start +10
    Connect = 0
    Division = 2





    
    if Connect == 5:
        print ("Device X not connected")
    try:
        WaterSequence.WaterOne()
        
    except ValueError as error:
        Connect = Connect + 1
        print("not connected")
    
    time.sleep(1)
    '''
   
#rs485V10.LightOne(start,end) #Function to control lights
