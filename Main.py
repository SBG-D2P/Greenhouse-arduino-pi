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
    
    for k in range (100):
        if CurrentDevices.at[k,'A'] == 0 and OldDevices.at[k,'A'] != 0:
            print('Device ' + str(k) + ' is disconected')
            #add script for emails
        elif CurrentDevices.at[k,'A'] > 0 and OldDevices.at[k,'A'] == 0:
            print('Device ' + str(k) + ' is now conected')
            if CurrentDevices.at[k,'A'] == 1:# if Light Controller is connected turn ONOFF are set to default
                CurrentDevices.at[k,'B'] = 8
                CurrentDevices.at[k,'C'] = 20
            #CurrentDevices.at[k,'B'] =
        elif CurrentDevices.at[k,'A'] > 0 and OldDevices.at[k,'A'] > 0 and CurrentDevices.at[k,'A'] != OldDevices.at[k,'A']:
            print('Did you change the device?')
        
        elif CurrentDevices.at[k,'A'] > 0 and OldDevices.at[k,'A'] > 0 and CurrentDevices.at[k,'A'] == OldDevices.at[k,'A']:
            CurrentDevices.at[k,'B'] = OldDevices.at[k,'B']
            CurrentDevices.at[k,'C'] = OldDevices.at[k,'C']
        
        else:
            #print('else')
            pass
            
    CurrentDevices.to_csv('Devices.csv', mode='w' ,index=False, header=False)
    return CurrentDevices
    #time.sleep(10)
#---------------------------------------------------------------------------------------------------------------

#--------------------------------------Light Controller---------------------------------------------------------

def Light():
    for l in range(100):
        if CurrentDevices.at[l,'A'] == 1:
            start = CurrentDevices.at[l,'B']#loading start and stop time set for specific controllers
            end = CurrentDevices.at[l,'C']
    
            t = datetime.datetime.now()
            Relay1 = SlaveID[l].read_register(3,0) #register number, number of decimals
            Relay2 = SlaveID[l].read_register(4,0) #register number, number of decimals
############################################### DAY TIME ####################################################                
            if t.hour >= start  and t.hour < end and Relay1 < 2 and Relay2 == 0: #turns light ON if daytime if relays are OK
                    SlaveID[l].write_register(0, 1, 0)
                    time.sleep(1)#wait for relay to turn ON and then check status
                    Relay1 = SlaveID[l].read_register(3,0) #register number, number of decimals
                    Relay2 = SlaveID[l].read_register(4,0) #register number, number of decimals
                    
                    if Relay1 == 1 and Relay2 == 0:
                        pass
                    elif Relay1 == 3 and Relay2 == 1:
                        print('Coil of Relay 1 in light controller ' + str(l) + ' is broken')
                        print('Backup relay is ON')
                    elif Relay1 == 3 and Relay2 != 1:
                        print('Coil of Relay 1 in light controller ' + str(l) + ' is broken')
                        print('Backup relay has not turned ON')
                    
                    else:
                        print(Relay1, Relay2)
                        print('Unknown error1')
                
            elif t.hour >= start  and t.hour < end and Relay1 == 3 and Relay2 < 2 : #turns light ON if daytime  if 1st relay has failed
                    SlaveID[l].write_register(0, 1, 0)
                    time.sleep(1)#wait for relay to turn ON and then check status
                    Relay2 = SlaveID[l].read_register(4,0) #register number, number of decimals
                       
                    if Relay2 == 1:
                        pass
                    elif Relay2 == 3:
                        print('Coil of backup relay in light controller ' + str(l) + ' is broken')
                    else:
                        print(Relay1, Relay2)
                        print('Unknown error2')
                           
            elif t.hour >= start  and t.hour < end and Relay1 == 2 and Relay2 != 0 : #turns light ON if daytime if 1st relays has fused contacts
                    SlaveID[l].write_register(0, 1, 0)  
                    time.sleep(1)#wait for relay to turn ON and then check status
                    Relay2 = SlaveID[l].read_register(4,0) #register number, number of decimals 
                    if Relay2 == 0:
                        pass
                    elif Relay2 == 2:
                        print('Contacts of backup relay in light controller ' + str(l) + ' have fused')
                    else:
                        print(Relay1, Relay2)
                        print('Unknown error3')    
                   
############################################### NIGHT TIME ####################################################                
            elif t.hour >= start  and t.hour >= end and Relay1 < 3 and Relay2 == 0: #turns light OFF if nightime if
                    SlaveID[l].write_register(0, 2, 0)
                    time.sleep(1)#wait for relay to turn ON and then check status
                    Relay1 = SlaveID[l].read_register(3,0) #register number, number of decimals
                    Relay2 = SlaveID[l].read_register(4,0) #register number, number of decimals
                      
                    if Relay1 == 0 and Relay2 == 0:
                        pass
                    elif Relay1 == 2 and Relay2 == 1:
                        print('Contacts of main relay in light controller ' + str(l) + ' have fused')
                        print('Back up relay is turned ON')
                    elif Relay1 ==2 and RElay2 != 1:
                        print('Contacts of main relay in light controller ' + str(l) + ' have fused')
                        print('Back up relay has not turned ON')
                    else:
                        print(Relay1, Relay2)
                        print('Unknown error5')
                
            elif t.hour >= start  and t.hour >= end and Relay1 == 3: #turns light OFF if nightime if main relay has broken coil broken
                    SlaveID[l].write_register(0, 2, 0)
                    time.sleep(1)#wait for relay to turn ON and then check status
                    Relay1 = SlaveID[l].read_register(3,0) #register number, number of decimals
                    Relay2 = SlaveID[l].read_register(4,0) #register number, number of decimals
                    
                    if Relay1 == 3 and Relay2 == 0:
                        pass
                    if Relay1 == 3 and Relay2 == 2:
                        print('Contacts of backup relay in light controller ' + str(l) + ' have fused')
                        print('Double failure of relays, attention required now, lights are still ON')
                    else:
                        print(Relay1, Relay2)
                        print('Unknown error6')
            elif Relay1 == 3 and Relay2 == 3:
                    print('Double failure of relays coil, attention required now, lights are OFF')
            else:
                    print(Relay1, Relay2)
                    print('Unknown error4')
                
#----------------------------------------------------------------------------------------------------------

while True: #-----------------------MAIN LOOP-----------------------------------------------------
    
    first_time = datetime.datetime.now()
    Poll()
    Devices()
    Light()
    time.sleep(0.1)
    print('loopey loop')
  
    second_time = datetime.datetime.now()
    difference = second_time - first_time
    print('refresh time is ' + str(difference) + ' h:mm:ss')
    
