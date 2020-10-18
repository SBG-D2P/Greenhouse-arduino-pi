import subprocess
import time
import datetime
import serial
import pandas as pd
import numpy as np

 df3 = pd.read_csv('Data.csv',names=columns, header=None)
df4[df.probeID = 'ProbeID'] #probeID is temporary and should be replaced with the actuall column's name and variable
df5 = df4.tail(2)
df6 = df4[1] - df4[2]
df6.drop(columns=18)#columns='R' maybe?

for i in range(17,18):#loops to check temperature and humidity
 if df6[i] > 0.1:
  #email
 else:return

for j in range(0,16):#loops 
 if df6[j] > 0.1:
  #email
  break #needed to terminated loop and avoid 16 notification for a single failure
 else:return
