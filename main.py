""" 
arduino_dataaq
Python App to read temperature data from Arduino
"""
import serial
import matplotlib.pyplot as plt
from drawnow import *

#Set serial port settings here!
serialPort = '/dev/ttyUSB0'
baudRate = 115200

arduinoData = serial.Serial(serialPort, baudRate) #Initialize serialMon

while True:
    while (arduinoData.inWaiting() == 0): #Wait until there is Data available
        pass
    arduinoString = arduinoData.readline().decode('ASCII') #read and convert str to byte
    temperature = arduinoString.split(',')
    print(float(temperature[0]))
    print(float(temperature[1]))

