""" 
arduino_dataaq
Python App to read temperature data from Arduino
"""
import serial
import matplotlib.pyplot as plt
from drawnow import *

# #List serial ports available
# serial_ports = [
#     ports.device
#     #ports.description #get ports description
#     for ports in serial.tools.list_ports.comports()
# ]

#Set serial port settings here!
serialPort = '/dev/ttyUSB0'
baudRate = 115200

arduinoData = serial.Serial(serialPort, baudRate) #Initialize serialMon
arduinoData.flushInput() #Clean data queue

plt.ion() #interactive mode

sensor0 = []
sensor1 = []
counter = 0

def makePlot():
    plt.ylim(25,35)
    plt.title("Leitura Sensores")
    plt.ylabel("Temperatura °C")
    plt.plot(sensor0, 'ro-', label="Sensor 1")
    plt.plot(sensor1, 'go-', label="Sensor 2")
    #plt.legend(loc="upper left")
    plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
    plt.subplots_adjust(right=0.76)


while True:
    while (arduinoData.inWaiting() == 0): #Wait until there is Data available
        pass
    arduinoString = arduinoData.readline().decode('ASCII') #read and convert str to byte
    temperature = arduinoString.split(',')
    
    sensor0.append(float(temperature[0]))
    sensor1.append(float(temperature[1]))
    
    # print(float(temperature[0]))
    # print(float(temperature[1]))

    drawnow(makePlot)
    plt.pause(.000001)

    counter += 1 #clean data points for better visualization
    if (counter > 50):
        sensor0.pop(0)
        sensor1.pop(1)