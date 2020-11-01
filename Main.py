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

#------------------------------------------------------Water hub probes----------------------------------------------------------

Probes = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] # array to check which probes are plugged

def ProbesPlugged(Slave):#ask hub to check which probes are plugged and convert 16bit number into an array

    SlaveID[Slave].write_register(1, 1, 0)#array position 1 mode "plugged"
    time.sleep(10)
    num = SlaveID[Slave].read_register(4,0) #fetch info about which probes are plugged (position 4 of array, 0 decimal)
    for n in range(1,17):
        bitpos = n
        Probes[n-1] = (num >> (bitpos-1))&1
    #print(Probes)
    return Probes
#--------------------------------------------------------------------------------------------------------------------------------------


#-------------------------------Gather soil moisture data as CSV------------------------------------------------------------------------

TemporaryData = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]#measure for level 0-15 and 16 = Temp°C, 17 = Humi%, 18 = slaveID + prodeID, 19 = Date

def FetchData(ProbeID,Slave):

    TemporaryData = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    TemporaryData[18] = str(Slave) + '-' + str(ProbeID)#identifiyer for each plant
    SlaveID[Slave].write_register(2, ProbeID, 0) #tells which probe to get data from -- array position 2 probe n
    time.sleep(.04)
    SlaveID[Slave].write_register(1, 2, 0) #tells slave to measure (mode 2) indicated probe
    time.sleep(10)
    for i in range(0,16):#loops between each level of the probe
        SlaveID[Slave].write_register(7, i, 0) #tells which level of the probe to get data from -- array position 7 probe n
        time.sleep(.1)
        SlaveID[Slave].write_register(1, 3, 0)#tells arduino to enter data transfer mode
        time.sleep(0.2)
        TemporaryData[i] = SlaveID[Slave].read_register(3, 0)#read value written by arduino for measurement
        time.sleep(0.1)
    print(TemporaryData)
    return TemporaryData

                            
#-------------------------------TEMPERATURE-AND-HUMIDITY-VIA-DHT-----------------------------------------------------------------------

Havg = 0
Tavg = 0

def GetDHT():
    Water1.write_register(1, 5, 0)#Tell arduino to enter DHT mode
    time.sleep(0.04)
    T = Water1.read_register(5, 1)
    print(T,'°C' )
    H = Water1.read_register(6, 0)
    print(H,'%')
    TemporaryData[16] = T*10 # the data fram will not take floats with other int
    TemporaryData[17] = H
    
#--------------------------------------------------------------------------------------------------------------------------------------

#-------------------------------SAVE-DATA-AS-CSV---------------------------------------------------------------------------------------

def DataToCSV():

    TemporaryData[19] = datetime.datetime.now()
    df1 = pd.DataFrame(np.array(TemporaryData))
    df1_transposed = df1.T
    time.sleep(0.04)
    df1_transposed.to_csv('Data.csv', mode='a', sep= '\t', index=False, header=False)



#--------------------------------FUNCTION-CALLED-BY-MAIN-------------------------------------------------------------------------------

def WaterMeasurement():
    
    for i in range (100):
        if CurrentDevices.at[i,'A'] == 2:# Checks if that slave is a water hub
            Probes = ProbesPlugged(i)    #checks which probes are plugged in that slave
            print(Probes)
            time.sleep(1)#0.1
            for n in range (17)
                if Probes == 1:
                    TemporaryData = FetchData(n,i)
                    time.sleep(1)#0.1
                    print(TemporaryData)
                    
            GetDHT()
            time.sleep(1)#0.1
            DataToCSV()

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
    
