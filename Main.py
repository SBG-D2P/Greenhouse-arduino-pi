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
Columns = ['A','B','C'] #A is type of device; for A = 1, B is start time, C is stop time; for A = 2, ???
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
    OldDevices = pd.read_csv('Devices.csv', names = Columns)
    print(OldDevices)
    print(CurrentDevices)
    #print(CurrentDevices['A'] < OldDevices['A'])
    
    for k in range (100):
        if CurrentDevices.at[k,'A'] == 0 and OldDevices.at[k,'A'] != 0:
            print('Device' + str(k) + 'is disconected')
            #add script for emails
        elif CurrentDevices.at[k,'A'] > 0 and OldDevices.at[k,'A'] == 0:
            print('Device' + str(k) + 'is now conected')
            if CurrentDevices.at[k,'A'] == 1:# if Light Controller is connected turn ONOFF are set to default
                CurrentDevices.at[k,'B'] = 8
                CurrentDevices.at[k,'C'] = 20
            #CurrentDevices.at[k,'B'] =
        elif CurrentDevices.at[k,'A'] > 0 and OldDevices.at[k,'A'] > 0 and CurrentDevices.at[k,'A'] != OldDevices.at[k,'A']:
            print('Did you change the device?')
        else:
            print('else')
    
    CurrentDevices.to_csv('Devices.csv', mode='w' ,index=False, header=False)
    time.sleep(10)
#---------------------------------------------------------------------------------------------------------------

#--------------------------------------Light Controller---------------------------------------------------------

def Light():
    for l in range(100):
        if CurrentDevices.at[l,'A'] == 1:
                start = CurrentDevices.at[l,'B']#loading start and stop time set for specific controllers
                end = CurrentDevices.at[l,'C']
    
                t = datetime.datetime.now()
                Status = SlaveID[l].read_register(0,1) #register number, number of decimals 
                #print(Status)

                if t.hour >= start  and t.hour < end and Status != 1: #turns light ON if daytime
                        SlaveID[l].write_register(0, 1, 0)


                elif t.hour >= start  and t.hour < end and Status == 1: #checks if there is a issue with lights during daytime
                        Relay1 = SlaveID[l].read_register(3,1) #register number, number of decimals
                        Relay2 = SlaveID[l].read_register(4,1) #register number, number of decimals
                        if Relay1 != 1 or Relay2 != 1:
                                print("One relay has failed")
                                #email

                elif t.hour < start  or t.hour >= end:
                        if Status != 2: #turns lights OFF during nighttime
                                SlaveID[l].write_register(0, 2, 0)

                elif  t.hour < start  or t.hour >= end:
                        if Status ==2:  #checks if there is an issue with lights during nighttime
                                Relay1 = SlaveID[l].read_register(3,1) #register number, number of decimals
                                Relay2 = SlaveID[l].read_register(4,1) #register number, number of decimals
                                if Relay1 != 1 or Relay2 != 1:
                                    print("y")
                                    #email

#----------------------------------------------------------------------------------------------------------

while True: #-----------------------MAIN LOOP-----------------------------------------------------
    
    Poll()
    Devices()
    Light()
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
