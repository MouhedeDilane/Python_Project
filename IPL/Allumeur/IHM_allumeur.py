import sys      # Used for system manipulation ( system error,...)
from socket import *    # Has a buffer (any delay doesn't mean loss of data)
import csv      # Store data received from the arduino
import time     # Used to ensure synchronisation
import threading    # Used to get data and plot them at the same time
import numpy as np  # Used to generate data when there's no arduino

# PyQT5 library to construct the interface
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *

# MatPlotLib library for in-real-time plot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Worker(QObject):
    update_signal = pyqtSignal(list)    # Define a signal used for synchronisation

    def __init__(self):
        super().__init__()

        # Allows to run program in test mode whithout needing a connected Arduino (set to 0 to go in test mode)
        self.arduino = 1       
        # Define the frequency at which you received data
        self.freq=10

    # Collect the data sent by the arduino (or generate values)
    def write_csv_arduino(self):
        i = 0

        # Connect the program to the Arduino
        address = ('192.168.0.100', 5000)  # define server IP and port
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.sendto(b"TEST", address)  # Launch the Arduino
        
        # Collection (or generation) of data 
        while True:
            t0 = time.perf_counter()
            if self.arduino == 0:
                # Generate random values and append them to the list
                values = [0.5*i] + [round(100*np.sin(2*np.pi*0.02*i + 3*k/2),1) for k in range(16)]
                self.update_signal.emit(values)     # Send the signal to the main

                # Write the data in a csv
                with open('data.csv', 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(values)
                i += 1

            else:
                try:
                    data, addr = client_socket.recvfrom(4096)  # Read response from arduino
                    if data != b'Exit':
                        a = []
                        if len(data) == 0:
                            print("No data received")
                            self.update_signal.emit([None for _ in range(17)])
                        else:
                            # Convert the data received (byte) into digital values
                            # Time value
                            
                            # Values of the sensors (pressure, temperature, force, flowrate)
                            a1 = (int(data[2]) << 8
                                    | int(data[3]))
                            a1 = (25/(4))*(a1 * (5 / 1023)-0.5)
                            a.append(round(a1, 2))
                            self.update_signal.emit(a)
                            with open('data.csv', 'a', newline='') as file:
                                writer = csv.writer(file)
                                writer.writerow(a)

                except:
                    pass
            
            # Ensure synchronisation at the desired frequency
            t1 = time.perf_counter()
            elapsed_time = t1 - t0
            if elapsed_time < 1:
                time.sleep(1/self.freq - elapsed_time)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget =  QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.b1 =  QPushButton(self.centralwidget)
        self.b1.setGeometry( QRect(170, 70, 93, 28))
        self.b1.setObjectName("b1")
        self.b2 =  QPushButton(self.centralwidget)
        self.b2.setGeometry( QRect(170, 110, 93, 28))
        self.b2.setObjectName("b2")
        self.b3 =  QPushButton(self.centralwidget)
        self.b3.setGeometry( QRect(280, 70, 93, 28))
        self.b3.setObjectName("b3")
        self.b4 =  QPushButton(self.centralwidget)
        self.b4.setGeometry( QRect(280, 110, 93, 28))
        self.b4.setObjectName("b4")
        self.b5 =  QPushButton(self.centralwidget)
        self.b5.setGeometry( QRect(390, 70, 93, 28))
        self.b5.setObjectName("b5")
        self.b6 =  QPushButton(self.centralwidget)
        self.b6.setGeometry( QRect(390, 110, 93, 28))
        self.b6.setObjectName("b6")
        self.b7 =  QPushButton(self.centralwidget)
        self.b7.setGeometry( QRect(500, 70, 93, 28))
        self.b7.setObjectName("b7")
        self.b8 =  QPushButton(self.centralwidget)
        self.b8.setGeometry( QRect(500, 110, 93, 28))
        self.b8.setObjectName("b8")
        self.plotWidget = PlotWidget(self.centralwidget)
        self.plotWidget.setGeometry(QRect(50, 200, 700, 300))
        self.plotWidget.setObjectName("plotWidget")
        self.timer = QTimer()
        self.timer.timeout.connect(self.reset_labels)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar =  QMenuBar(MainWindow)
        self.menubar.setGeometry( QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar =  QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate =  QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.b1.setText(_translate("MainWindow", "S"))
        self.b2.setText(_translate("MainWindow", "I"))
        self.b3.setText(_translate("MainWindow", "VEO"))
        self.b4.setText(_translate("MainWindow", "VEC"))
        self.b5.setText(_translate("MainWindow", "VGO"))
        self.b6.setText(_translate("MainWindow", "VGC"))
        self.b7.setText(_translate("MainWindow", "1"))
        self.b8.setText(_translate("MainWindow", "2"))
        self.b1.clicked.connect(self.on_click1)
        self.b2.clicked.connect(self.on_click2)
        self.b3.clicked.connect(self.on_click3)
        self.b4.clicked.connect(self.on_click4)
        self.b5.clicked.connect(self.on_click5)
        self.b6.clicked.connect(self.on_click6)
        self.b7.clicked.connect(self.on_click7)
        self.b8.clicked.connect(self.on_click8)
        self.worker = Worker()
        self.worker_thread = threading.Thread(target=self.worker.write_csv_arduino)    # Put the worker in a thread
        self.worker_thread.daemon = True    
        self.worker_thread.start()

    def on_click1(self):
        try:
            address = ('192.168.0.100', 5000) #Defind who you are talking to (must match arduino IP and port)
            client_socket = socket(AF_INET, SOCK_DGRAM) #Set Up the Socket
            client_socket.settimeout(1)
            client_socket.sendto(str.encode("S"), address) #send command to arduino
            _translate =  QCoreApplication.translate
            rec_data, addr = client_socket.recvfrom(1024)
            if rec_data == f"1_ok".encode():
                self.b2.setText(_translate("MainWindow", "I"))
                self.b1.setText(_translate("MainWindow", "Started"))
        except:
            pass
    def on_click2(self):
        try:
            address = ('192.168.0.100', 5000) #Defind who you are talking to (must match arduino IP and port)
            client_socket = socket(AF_INET, SOCK_DGRAM) #Set Up the Socket
            client_socket.settimeout(1)
            client_socket.sendto(str.encode("I"), address) #send command to arduino
            _translate =  QCoreApplication.translate
            rec_data, addr = client_socket.recvfrom(1024)
            if rec_data == f"2_ok".encode():
                self.b2.setText(_translate("MainWindow", "Interrupted"))
                self.b1.setText(_translate("MainWindow", "S"))
        except:
            pass
    def on_click3(self):
        try:
            address = ('192.168.0.100', 5000) #Defind who you are talking to (must match arduino IP and port)
            client_socket = socket(AF_INET, SOCK_DGRAM) #Set Up the Socket
            client_socket.settimeout(1)
            client_socket.sendto(str.encode("VEO"), address) #send command to arduino
            _translate =  QCoreApplication.translate
            rec_data, addr = client_socket.recvfrom(1024)
            if rec_data == f"3_ok".encode():
                self.b3.setText(_translate("MainWindow", "Open"))
                self.b4.setText(_translate("MainWindow", "VEC"))
        except:
            pass     
    def on_click4(self):
        try:
            address = ('192.168.0.100', 5000) #Defind who you are talking to (must match arduino IP and port)
            client_socket = socket(AF_INET, SOCK_DGRAM) #Set Up the Socket
            client_socket.settimeout(1)
            client_socket.sendto(str.encode("VEC"), address) #send command to arduino
            _translate =  QCoreApplication.translate
            rec_data, addr = client_socket.recvfrom(1024)
            if rec_data == f"4_ok".encode():
                self.b3.setText(_translate("MainWindow", "VEO"))
                self.b4.setText(_translate("MainWindow", "Closed"))
        except:
            pass
    def on_click5(self):
        try:
            address = ('192.168.0.100', 5000) #Defind who you are talking to (must match arduino IP and port)
            client_socket = socket(AF_INET, SOCK_DGRAM) #Set Up the Socket
            client_socket.settimeout(1)
            client_socket.sendto(str.encode("VGO"), address) #send command to arduino
            _translate =  QCoreApplication.translate
            rec_data, addr = client_socket.recvfrom(1024)
            if rec_data == f"5_ok".encode():
                self.b5.setText(_translate("MainWindow", "Open"))
                self.b6.setText(_translate("MainWindow", "VGC"))
        except:
            pass
    def on_click6(self):
        try:
            address = ('192.168.0.100', 5000) #Defind who you are talking to (must match arduino IP and port)
            client_socket = socket(AF_INET, SOCK_DGRAM) #Set Up the Socket
            client_socket.settimeout(1)
            client_socket.sendto(str.encode("VGC"), address) #send command to arduino
            _translate =  QCoreApplication.translate
            rec_data, addr = client_socket.recvfrom(1024)
            if rec_data == f"6_ok".encode():
                self.b5.setText(_translate("MainWindow", "VGC"))
                self.b6.setText(_translate("MainWindow", "Closed"))
        except:
            pass
    def on_click7(self):
        try:
            address = ('192.168.0.100', 5000) #Defind who you are talking to (must match arduino IP and port)
            client_socket = socket(AF_INET, SOCK_DGRAM) #Set Up the Socket
            client_socket.settimeout(1)
            client_socket.sendto(str.encode("1"), address) #send command to arduino
            _translate =  QCoreApplication.translate
            rec_data, addr = client_socket.recvfrom(1024)
            if rec_data == f"7_ok".encode():
                self.b7.setText(_translate("MainWindow", "Launch"))
            self.timer.start(1000)
            
        except:
            pass
    def on_click8(self):
        try:
            address = ('192.168.0.100', 5000) #Defind who you are talking to (must match arduino IP and port)
            client_socket = socket(AF_INET, SOCK_DGRAM) #Set Up the Socket
            client_socket.settimeout(1)
            client_socket.sendto(str.encode("2"), address) #send command to arduino
            _translate =  QCoreApplication.translate
            rec_data, addr = client_socket.recvfrom(1024)
            if rec_data == f"8_ok".encode():
                self.b8.setText(_translate("MainWindow", "Launch"))
            self.timer.start(1000)
            
        except:
            pass
    def reset_labels(self):
        _translate =  QCoreApplication.translate
        self.b7.setText(_translate("MainWindow", "1"))
        self.b8.setText(_translate("MainWindow", "2"))
        self.timer.stop()
class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.values = []

    def update_plot(self, values):
        with open("data.csv", "r") as file:
            csv_reader = csv.reader(file)
            self.y_data = []
             
            for row in csv_reader:
                self.y_data.append(float(row[0]))

        self.ax.clear()
        self.ax.plot(self.y_data)
        self.canvas.draw()

class Ui_MainWindow(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.plotWidget = PlotWidget(self.centralwidget)
        self.plotWidget.setGeometry(QRect(50, 200, 700, 300))
        self.plotWidget.setObjectName("plotWidget")
        self.worker.update_signal.connect(self.plotWidget.update_plot)

if __name__ == "__main__":
    app =  QApplication(sys.argv)
    MainWindow =  QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())