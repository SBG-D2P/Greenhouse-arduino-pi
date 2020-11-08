import subprocess
import time
import datetime
import serial
import pandas as pd
import numpy as np

#Indexes = range(100)
Columns = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S']#might need to remove extra letters (only ABC)
CurrentDevices = pd.read_csv('Devices.csv', names = Columns)
df3 = pd.read_csv('Data.csv',names = Columns, header=None, sep= '\t')


for i in range (100):#checks each devices if water hub
    if CurrentDevices.at[i,'A'] == 2:
        
        CurrentProbes = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] # array to check which probes are plugged
        num = int(CurrentDevices.at[i,'C'])
        for n in range(1,17):#convert number to plugged probes
            bitpos = n
            CurrentProbes[n-1] = (num >> (bitpos-1))&1
        
        for m in range(1,16):# verify each probes of each devices
            if CurrentProbes[m] == 1:
                Tnum = (str(i) + '-' + str(m))
                #print(df3)
                df4 = df3[df3['R'] == Tnum]#creates new datafram with only data from single probe
                #print(df4)
                df5 = df4.tail(2)
                df5.reset_index(inplace=True)
                df5 = df5.drop(columns=['R','S'])#columns='R' maybe?
                #print(df5)
                df5 = df5.astype(int)
                df6 = df5.loc[0] - df5.loc[1]
                print(df6)


                for p in range(17,18):#loops to check temperature and humidity
                    if df6[p] > 0.1:
                        print('test')
                        #email

                for q in range(0,16):#loops 
                    if df6[q] > 0.1:
                        print('test2')
                        #email
                        break #needed to terminated loop and avoid 16 notification for a single failure

