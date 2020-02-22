
import subprocess
import urllib.request, urllib.parse, urllib.error
import http.client
import minimalmodbus
import datetime
import time
import serial
import Light #don't forget to change name of other module with actual function for lights
import Water #import functions for waterprobes

start = 11
end = start +10
Connect = 0
Division = 2

#while True:

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



Water.Slave = 2
Test = [0,2]
for n in range(2):
    Water.ProbeID = Test[n]
    Measurement()
   
'''
        #rs485V10.LightOne(start,end)
        #rs485Water.Plugged()
    test = Water.Water1.write_register(1,1) #register number, number of decimals
    time.sleep(5)
    Status = Water.Water1.read_register(5,0) #register number, number of decimals 
    print(Status)

    #Status = Water1.write_register(1,1) #register number, number of decimals 
'''
