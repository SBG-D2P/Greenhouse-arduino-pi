
import subprocess
import time
import RPi.GPIO as GPIO
import urllib.request, urllib.parse, urllib.error
import http.client
import minimalmodbus
import datetime
import serial
import pandas as pd
import numpy as np
import Water

#-----------------------------------------------------------------------------------------------------------------------------------------------#
columns=['A', 'B', 'C']
ProbeID = 0
#Sequence of functions to gather data from any slave/probe
def Measurement():
    Water.Probes = Water.ProbesPlugged(Water.Slave)
    time.sleep(0.1)
    Water.TemporaryData = Water.FetchData(Water.ProbeID)
    time.sleep(0.1)
    Water.DHTWrite()
    time.sleep(0.1)
    [Water.Havg, Water.Tavg] = Water.DHTRead()
    time.sleep(0.1)
    Water.DataToCSV()

def WaterOne():
    #print(start)
    
    t = datetime.datetime.now()
    df3 = pd.read_csv('CheckPoint.csv',names=columns, header=None)
    
    
    if t.minute >= 6  and t.minute < 60 and df3.at[0,'B'] == 0: #turns light ON if daytime
        Water.Slave = 2
        Water.Water1.write_register(1, 1, 0) #tells slave to plugged detection (mode 1)
        time.sleep(5)
        Probes = Water.ProbesPlugged(Water.Slave)
        print(Water.Probes)
        Test = [0,2]
        '''for n in range(0,2):
            Water.ProbeID = Test[n]
            Measurement()'''
        for n in range(0,16):
            print(n)
            print(Water.Probes[n])
            if Water.Probes[n] == 1:
                Water.ProbeID = n
                Measurement()
        df3.at[0,'B'] = 1
        df3.to_csv('CheckPoint.csv', mode='w' ,index=False, header=False)
        

    elif t.minute >= 6  and t.minute < 60 and df3.at[0,'B'] == 1: #checks if there is a issue with lights during daytime
        pass

    elif t.minute < 6  or t.minute < 60:
        df3.at[0,'B'] = 0
        df3.to_csv('CheckPoint.csv', mode='w' ,index=False, header=False)





