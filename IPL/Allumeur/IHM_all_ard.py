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
    button_signal = pyqtSignal(str)     # Define a signal to change button color
    command_signal = pyqtSignal(str)    # Define a signal to send command to worker

    def __init__(self):
        super().__init__()

        # Allows to run program in test mode without needing a connected Arduino (set to True to go in test mode)
        self.simulation_mode = True
        
        # Define the frequency at which you received data
        self.freq = 1

    # Collect the data sent by the arduino (or generate values)
    def write_csv_arduino(self):
        i = 0

        # Collection (or generation) of data 
        while True:
            t0 = time.perf_counter()
            if self.simulation_mode:
                # Generate random values and append them to the list
                values = [0.5*i] + [round(100*np.sin(2*np.pi*0.02*i + 3*k/2), 1) for k in range(16)]
                self.update_signal.emit(values)     # Send the signal to the main

                # Write the data in a csv
                with open('data.csv', 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(values)
                i += 1

            else:
                try:
                    # Simulating data received from the Arduino
                    values = [0.5*i] + [round(100*np.sin(2*np.pi*0.02*i + 3*k/2), 1) for k in range(16)]
                    self.update_signal.emit(values)     # Send the signal to the main

                    # Write the data in a csv
                    with open('data.csv', 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(values)
                    i += 1

                except:
                    pass
            
            # Ensure synchronisation at the desired frequency
            t1 = time.perf_counter()
            elapsed_time = t1 - t0
            if elapsed_time < 1:
                time.sleep(1/self.freq - elapsed_time)
        
    def receive_command(self, command):
        # Handle received command
        print("Data received")
        self.Ui_MainWindow.receive_command(command)
        
        # Do whatever you need to do with the command

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.b1 = QPushButton(self.centralwidget)
        self.b1.setGeometry(QRect(170, 70, 93, 28))
        self.b1.setObjectName("b1")
        self.b2 = QPushButton(self.centralwidget)
        self.b2.setGeometry(QRect(170, 110, 93, 28))
        self.b2.setObjectName("b2")
        self.b3 = QPushButton(self.centralwidget)
        self.b3.setGeometry(QRect(280, 70, 93, 28))
        self.b3.setObjectName("b3")
        self.b4 = QPushButton(self.centralwidget)
        self.b4.setGeometry(QRect(280, 110, 93, 28))
        self.b4.setObjectName("b4")
        self.b5 = QPushButton(self.centralwidget)
        self.b5.setGeometry(QRect(390, 70, 93, 28))
        self.b5.setObjectName("b5")
        self.b6 = QPushButton(self.centralwidget)
        self.b6.setGeometry(QRect(390, 110, 93, 28))
        self.b6.setObjectName("b6")
        self.b7 = QPushButton(self.centralwidget)
        self.b7.setGeometry(QRect(500, 70, 93, 28))
        self.b7.setObjectName("b7")
        self.b8 = QPushButton(self.centralwidget)
        self.b8.setGeometry(QRect(500, 110, 93, 28))
        self.b8.setObjectName("b8")
        self.plotWidget = PlotWidget(self.centralwidget)
        self.plotWidget.setGeometry(QRect(50, 200, 700, 300))
        self.plotWidget.setObjectName("plotWidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.b1.setText(_translate("MainWindow", "S"))
        self.b2.setText(_translate("MainWindow", "I"))
        self.b3.setText(_translate("MainWindow", "VEO"))
        self.b4.setText(_translate("MainWindow", "VEC"))
        self.b5.setText(_translate("MainWindow", "VGO"))
        self.b6.setText(_translate("MainWindow", "VGC"))
        self.b7.setText(_translate("MainWindow", "1"))
        self.b8.setText(_translate("MainWindow", "2"))
        self.b1.clicked.connect(lambda: self.send_command("S"))
        self.b2.clicked.connect(lambda: self.send_command("I"))
        self.b3.clicked.connect(lambda: self.send_command("VEO"))
        self.b4.clicked.connect(lambda: self.send_command("VEC"))
        self.b5.clicked.connect(lambda: self.send_command("VGO"))
        self.b6.clicked.connect(lambda: self.send_command("VGC"))
        self.b7.clicked.connect(lambda: self.send_command("1"))
        self.b8.clicked.connect(lambda: self.send_command("2"))

        self.worker = Worker()
        self.worker_thread = threading.Thread(target=self.worker.write_csv_arduino)    # Put the worker in a thread
        self.worker_thread.daemon = True
        self.worker_thread.start()
        self.worker.command_signal.connect(self.receive_command)

    def send_command(self, command):
        self.worker.command_signal.emit(command)
        print("Command sent:", command)

    def receive_command(self, command):
        print("Command received:", command)
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
        if len(values) > 1:
            self.values.append(values[1])
            if len(self.values) > 100:  # Limiting the plot to show last 100 data points
                self.values.pop(0)
            self.ax.clear()
            self.ax.plot(range(len(self.values)), self.values)
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