""" 
arduino_dataaq
Python App to read temperature data from Arduino
To run, you need the following libraries:
    matplotlib, pyserial and wxPython

Developped by: Luiz Guilherme Marin
This is part of my Master Thesis Project
Masters in Mechanical Engineering at Universidade Federal do Paraná
"""
import wx
import matplotlib
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
import serial
import time
import csv
import sys

#Create the top panel
class TopPanel(wx.Panel): 
    def __init__(self, parent):
        wx.Panel.__init__(self, parent = parent)
        
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)               #define the box sizer 
        self.sizer.Add(self.canvas, 1, wx.EXPAND)           #Add sizer to the canvas
        self.SetSizer(self.sizer)                           #same
        #self.axes.set_ylabel("Temperature °C")

    def draw(self, x, sensor1, sensor2, sensor3, sensor4, sensor5):
        self.axes.clear()
        self.axes.plot(x,sensor1, 'ro-', label="Sensor 1")
        self.axes.plot(x,sensor2, 'go-', label="Sensor 2")
        self.axes.plot(x,sensor3, 'bo-', label="Sensor 3")
        self.axes.plot(x,sensor4, 'co-', label="Sensor 4")
        self.axes.plot(x,sensor5, 'ko-', label="Sensor 5")
        self.axes.legend()
        #self.axes.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
        #self.axes.subplots_adjust(right=0.76)
        self.canvas.draw()

    def changeAxis(self, min, max):
        self.axes.set_ylim(float(min), float(max))
        self.canvas.draw()

#create bottom panel
class BottomPanel(wx.Panel):
    def __init__(self, parent, top):
        wx.Panel.__init__(self, parent = parent)

        self.graph = top

        #Check for system OS to show correct port address
        if sys.platform == 'win32':
            com_ports = ["COM3", "COM5"]
        else:
            com_ports = ["/dev/ttyUSB0", "/dev/COM3"]

        baud_rates = ["115200"]

        #Create TButton and create the toggle event (id = -1 - auto set)
        labelConnection = wx.StaticText(self, -1, label="Conexão com Arduino", pos=(10,10))
        self.comboPorts = wx.ComboBox(self, -1, "/dev/ttyUSB0", choices=com_ports, pos=(10,30), size=(140,-1))
        self.comboBaud = wx.ComboBox(self, -1, "115200", choices=baud_rates, pos=(10,62), size=(140,-1))
        self.togglebuttonStart = wx.ToggleButton(self, id=-1, label="Conectar", pos=(10,95), size=(140,-1))
        self.togglebuttonStart.Bind(wx.EVT_TOGGLEBUTTON, self.OnStartClick)

        labelSaveCSV = wx.StaticText(self, -1, label="Gravar dados para CSV", pos=(200,10))
        labelFileName = wx.StaticText(self, -1, label="Arquivo:", pos=(200,40))
        self.tbFileName = wx.TextCtrl(self, -1, "dados", pos = (260,30), size=(130,-1))
        self.tbSaveCSV = wx.ToggleButton(self, id=-1, label="&Iniciar Gravação", pos=(200,95), size=(190,-1))
        self.tbSaveCSV.Disable()
        self.tbSaveCSV.Bind(wx.EVT_TOGGLEBUTTON, self.OnRecordClick)

        labelGraphConfig = wx.StaticText(self, -1, label="Configurar Eixos", pos=(450,10))
        labelMinY = wx.StaticText(self, -1, label="Min Y:", pos=(450,38))
        self.textboxMinY = wx.TextCtrl(self, -1, "25", pos = (500,30), size=(60,-1))
        labelMaxY = wx.StaticText(self, -1, label="Max Y:", pos=(450,68))
        self.textboxMaxY = wx.TextCtrl(self, -1, "150", pos = (500,60), size=(60,-1))
        self.buttonRange = wx.Button(self, id=-1, label="Setar Eixos", pos=(450,95), size=(120,-1))
        self.buttonRange.Bind(wx.EVT_BUTTON, self.SetButtonRange)

        labelAbout = wx.StaticText(self, -1, label="LABATS", pos=(650,10))
        labelAbout1 = wx.StaticText(self, -1, label="Laboratório de Aspersão Térmica e Soldagens Especiais", pos=(650,30))
        labelAbout2 = wx.StaticText(self, -1, label="Universidade Federal do Paraná", pos=(650,45))
        labelAbout3 = wx.StaticText(self, -1, label="Desenvolvido por: Luiz Guilherme Marin", pos=(650,70))
        labelAbout4 = wx.StaticText(self, -1, label="Orientador: Dr. Ramón Cortés Paredes", pos=(650,90))
        labelAbout5 = wx.StaticText(self, -1, label="Co-Orientador: Dr. Christian Scapulatempo Strobel", pos=(650,105))

        #Create Timer to manage the threads
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.TimeInterval, self.timer)

        self.serial_connection = False

        #create empty array
        self.x_counter = 0
        self.x = []
        self.sensor1 = []
        self.sensor2 = []
        self.sensor3 = []
        self.sensor4 = []
        self.sensor5 = []

        self.recording = False

    def ShowError(self, message):
        wx.MessageBox(message, 'Error', wx.OK | wx.ICON_ERROR)

    def SetButtonRange(self, event):
        min = self.textboxMinY.GetValue()
        max = self.textboxMaxY.GetValue()
        self.graph.changeAxis(min, max)

    def OnRecordClick(self, event):
        val = self.tbSaveCSV.GetValue()
        if (val == True):
            print("Recording to: "+self.tbFileName.GetValue()+".csv")
            self.tbFileName.Disable()
            self.recording = True
            self.dataFile = open(self.tbFileName.GetValue()+'.csv', 'w')
            self.tbSaveCSV.SetLabel("Parar Gravação")
        else:
            print("Recording Stopped")
            self.tbFileName.Enable()
            self.recording = False
            self.dataFile.close()
            self.tbSaveCSV.SetLabel("Iniciar Gravação")
            wx.MessageBox('Data saved to '+self.tbFileName.GetValue()+".csv", 'Info', wx.OK | wx.ICON_INFORMATION)

    def OnStartClick(self, event):
        val = self.togglebuttonStart.GetValue()
        if (val == True):
            self.togglebuttonStart.SetLabel("Desconectar")
            self.comboBaud.Disable()
            self.comboPorts.Disable()
            self.tbSaveCSV.Enable()
            self.ArduinoConnect(self.comboPorts.GetValue(),self.comboBaud.GetValue())
            #self.timer.Start(250)
        else:
            self.togglebuttonStart.SetLabel("Conectar")
            self.timer.Stop()
            self.comboBaud.Enable()
            self.comboPorts.Enable()
            self.tbSaveCSV.Disable()
            print("Disconnected")

    def TimeInterval(self, event):
        tmp = self.serial_arduino.readline().decode()
        #remove trailing char (/n) and separate
        data = tmp.rstrip().split(',')
        self.sensor1.append(float(data[0]))
        self.sensor2.append(float(data[1]))
        self.sensor3.append(float(data[2]))
        self.sensor4.append(float(data[3]))
        self.sensor5.append(float(data[4]))
        self.x.append(self.x_counter)
        self.x_counter += 1

        self.graph.draw(self.x,self.sensor1,self.sensor2,self.sensor3,self.sensor4,self.sensor5)

        if (self.recording == True):
            dataWrite = csv.writer(self.dataFile)
            dataWrite.writerow(data)

        if (self.x_counter > 50):
            self.sensor1.pop(0)
            self.sensor2.pop(0)
            self.sensor3.pop(0)
            self.sensor4.pop(0)
            self.sensor5.pop(0)
            self.x.pop(0)

    def ArduinoConnect(self, port, brate):
        if (self.serial_connection == False):
            print('Trying to connect to: ' + str(port) + ' at ' + str(brate))
            try:
                self.serial_arduino = serial.Serial(str(port), int(brate), timeout = 2)
                time.sleep(2)
                self.serial_arduino.flushInput() #Clean data queue
                self.timer.Start(250)
                print('Connected to: ' + str(port) + ' at ' + str(brate))
            except:
                print('Failed to connect to: ' + str(port) + ' at ' + str(brate))
                self.togglebuttonStart.SetValue(False)
                self.togglebuttonStart.SetLabel("Connect")
                self.comboBaud.Enable()
                self.comboPorts.Enable()
                self.tbSaveCSV.Disable()
                self.ShowError('Failed to connect to: ' + str(port) + ' at ' + str(brate))
        
class Main(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent = None, title = "LABATS - Aquisição de Dados", size = (1000,800), style=wx.SYSTEM_MENU | wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX)
        splitter = wx.SplitterWindow(self)
        top = TopPanel(splitter)
        bottom = BottomPanel(splitter, top) #pass a reference to top pannel ,top
        splitter.SplitHorizontally(top, bottom)
        splitter.SetMinimumPaneSize(620)

        top.draw(0,0,0,0,0,0)

if __name__ == "__main__":
    app = wx.App()
    frame = Main()
    frame.Show()
    app.MainLoop()