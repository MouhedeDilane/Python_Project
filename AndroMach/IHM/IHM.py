"""
Human-Machine Interface for AndroMach's ignitor

Creator : Mehdi Delouane

"""
import sys      # Used for system manipulation ( system error,...)
import os
from socket import *    # Communication between devices  N.B. Has a buffer (any delay doesn't mean loss of data)
import csv      # Store data received from the board
import threading    # Used to get data (Worker) and perform other actions (Main) at the same time
import functools    # Link functions to button
import numpy as np  # Used to generate data when there's no board connected
from datetime import datetime   # Used to create unique csv for each run
from threading import Event

# PyQT5 library to construct the interface
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *

# MatPlotLib library for in-real-time plot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import time 

global MC_board # Variable used to test the program without board
global update_frequency # Frequency used to update the displayed values for the IRT plots
global receiving_address    # Ethernet IP address and port of the computer
global sending_address  # IP address and port of the board
global init_valve_status    # Initialise the status of the valves
global data_csv # Name of the csv 
global multi_csv    # Variable used to run the program on a default csv 
global countdown_time

MC_board=0  # 1-->board connected / 0-->no board connected
multi_csv=0 # 1-->unique csv / 0-->default csv
update_frequency=1000  # Frequency (in Hz)
receiving_address=('192.168.100.138', 9090)
sending_address=('192.168.100.211', 8080)
init_valve_status="1000000"
countdown_time=(2,0)    # Décompte (s,ms)

# Define the name of the csv (unique or default)
if multi_csv==1:
    timestamp = datetime.now().strftime("%H%M%S")
    data_csv = f"data_{timestamp}.csv"
else:
    data_csv='data.csv'

# This class collects data sent by the board / Acts also as a rising edge for the value display on the main window
class Worker(QObject):
    update_signal = pyqtSignal(list)    # Signal to send data from a sub class to another class

    def __init__(self):
        super().__init__()
        self.event1 = Event()

    def write_csv_MC_board(self):
        i = 0
        if MC_board!=0:
            client_socket = socket(AF_INET, SOCK_DGRAM)
            client_socket.bind(receiving_address)

        while True:

            # Generate data to simulate a real run
            if MC_board == 0:
                print("done")
                values = [0.5*i] + [round(100*np.sin(2*np.pi*0.02*i + 3*k/2),1) for k in range(7)]
                self.update_signal.emit(values)
                with open(data_csv, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(values)
                i += 1
                time.sleep(1)
            else:
                try:
                    data, addr = client_socket.recvfrom(256)
                    # Detect a acknowledgement message and "stop" the worker to send it to the main (using event)
                    if len(data)<=5:
                        self.data_received = data
                        self.event1.set()
                        
                    if len(data)>5:
                        decoded_data = data.decode('utf-8').strip()

                        # Parse the received data string
                        values = []
                        parts = decoded_data.split(',')
                        for part in parts:
                            values.append(float(part))
                        print(part)
                        # Send data for main window display
                        self.update_signal.emit(values)

                        # Write in csv
                        with open(data_csv, 'a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow(values)

                except Exception as e:
                    print(f"Error: {e}")
                    pass

# Main class of the program
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        # Initialise the valves
        if MC_board!=0:
            self.bits=init_valve_status
            self.client_socket = socket(AF_INET, SOCK_DGRAM)
            self.client_socket.settimeout(1)
            self.client_socket.sendto(bytes(self.bits, 'utf-8'), sending_address)

        # Create the MainWindow object and set its size
        MainWindow.resize(1922, 1237)
        self.centralwidget = QWidget(MainWindow)

        # Create the background of the main window with the P&ID and a grey background
        self.background = QLabel(self.centralwidget)
        self.background.setGeometry(QRect(30, -40, 2000, 1080))
        self.background.setPixmap(QPixmap("Synoptique_Allumeur.png"))
        self.frame1 = QFrame(self.centralwidget)
        self.frame1.setGeometry(QRect(-31, -91, 1891, 1231))
        self.frame1.setAutoFillBackground(True)
        self.frame1.setFrameShape(QFrame.StyledPanel)
        self.frame1.setFrameShadow(QFrame.Raised)
        self.frame1.raise_()
        self.background.raise_()

        # Insert the AndroMach logo
        self.logo = QLabel(self.centralwidget)
        self.logo.setGeometry(QRect(1500, 30, 500, 130))
        pixmap = QPixmap("Logo_AndroMach.png")
        scaled_pixmap = pixmap.scaled(self.logo.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo.setPixmap(scaled_pixmap)
        self.logo.setAlignment(Qt.AlignCenter)

        # Insert a table (used to sum up the valve status)
        self.table = QLabel(self.centralwidget)
        self.table.setGeometry(QRect(1250, 660, 161, 169))
        self.table.setPixmap(QPixmap("Tableau.png"))
        self.table.raise_()

        # The status display is a square (frame) with two buttons and two labels that indicates to the user the status of the valve (open/close)
        # Create all the frames for the status valves display
        self.frames = [QFrame(self.centralwidget) for _ in range(7)]
        self.dims_frame=[(654, 627, 120, 91),(981, 390, 120, 91),(981, 197, 120, 91),
              (236, 235, 120, 91),(236, 555, 120, 91),(496, 250, 120, 91),(591, 745, 120, 91)]
        
        # CSS code to change the color, border, ...
        for frame,dim in zip(self.frames,self.dims_frame):
            frame.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    background-color: rgb(230, 230, 230);\n"
        "    border: 3px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")  
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setFrameShadow(QFrame.Raised)
            x,y,h,w=dim
            frame.setGeometry(QRect(x,y,h,w))
            frame.raise_()

        # Create all the labels and buttons for the status displays
        self.status=[QLabel(self.centralwidget) for _ in range(7)]     # Indicates the status of the valve
        self.labels=[QLabel(self.centralwidget) for _ in range(7)]     # Indicates the name of the valve
        self.ouverts=[QPushButton(self.centralwidget) for _ in range(7)]   # Button to open valve
        self.fermes=[QPushButton(self.centralwidget) for _ in range(7)]    # Button to close valve
        self.ids=[QLabel(self.centralwidget) for _ in range(7)]    # Label placed in the sum up table 
        
        # Define the name and number of the valve
        self.names=['IP_SV001','IP_SV101','IO_SV001',
               'N_SV031','N_SV131','N_SV151',
               'NP_SV031']
        self.nums=[1,2,3,4,5,6,7]
        
        # Dimension and localisation of the status display objects
        self.dims_status=[(662, 637, 111, 16),(989, 400, 111, 16),(989, 207, 111, 16),
                          (246, 245, 111, 16),(246, 565, 111, 16),(601, 755, 111, 16),
                          (503, 260, 111, 16)]
        self.dims_label=[(696, 657, 55, 16),(1023, 420, 55, 16),(1023, 227, 55, 16),
                         (278, 265, 55, 16),(278, 585, 55, 16),(538, 280, 55, 16),(633, 775, 55, 16)
                         ]    
        self.dims_ouvert=[(667, 677, 41, 28),(994, 440, 41, 28),(994, 247, 41, 28),
                         (249, 285, 41, 28),(249, 605, 41, 28),(509, 300, 41, 28),(604, 795, 41, 28)
                         ]       
        self.dims_ferme=[(713, 677, 48, 28),(1040, 440, 48, 28),(1040, 247, 48, 28),
                         (295, 285, 48, 28),(295, 605, 48, 28),(555, 300, 48, 28),(650, 795, 48, 28)
                         ]  
        self.dims_idd=[(1349, 664, 55, 16),(1349, 688, 55, 16),(1349, 712, 55, 16),
                        (1349, 736, 55, 16),(1349, 760, 55, 16),(1349, 809, 55, 16),(1349, 784, 55, 16)
                        ]
        
        # Loop to place each status display
        for widget,label,ouvert,ferme,idd,dim_status,dim_label,dim_ouvert,dim_ferme,dim_idd in zip(self.status,self.labels,self.ouverts,self.fermes,self.ids,self.dims_status,self.dims_label,self.dims_ouvert,self.dims_ferme,self.dims_idd):
            # Set dimensions of each object
            x,y,h,w=dim_status
            widget.setGeometry(QRect(x,y,h,w))
            x,y,h,w=dim_label
            label.setGeometry(QRect(x,y,h,w))
            x,y,h,w=dim_ouvert
            ouvert.setGeometry(QRect(x,y,h,w))
            x,y,h,w=dim_ferme
            ferme.setGeometry(QRect(x,y,h,w))
            x,y,h,w=dim_idd
            idd.setGeometry(QRect(x,y,h,w))

            # Define writing parameters (fontsize, font,...)
            font = QFont("Arial", 8, QFont.Bold)
            widget.setFont(font)
            label.setFont(font)
            font = QFont("Arial", 7, QFont.Bold)
            ouvert.setFont(font)
            ferme.setFont(font)

            # Display the objects
            widget.raise_()
            label.raise_()
            ouvert.raise_()
            ferme.raise_()      
            idd.raise_()  

        # Frame to delimit different section on the right part of the screen 
        self.frames2 = [QFrame(self.centralwidget) for _ in range(4)]   # Define the frames
        self.dims_frame2=[(1620, 270, 336, 320),(1620, 270, 336, 200), (1620, 880, 336, 200),(1620, 270, 336, 1000)]     # Define the dimensions and localisation of the frame

        # Loop to place each frame
        for frame,dim in zip(self.frames2,self.dims_frame2):
            frame.setStyleSheet("QFrame, QLabel, QToolTip {\n"
            "    background-color: rgba(0, 0, 0, 0);\n"
            "    border: 3px solid grey;\n"
            "    border-radius: 1px;\n"
            "    padding: 2px;\n"
            "}")  
            x,y,h,w=dim
            frame.setGeometry(QRect(x,y,h,w))
            frame.raise_()
   
        # Define a button to finish the entire program (to avoid closing windows unintentionally, the close button hint is disabled)
        self.close_all = QPushButton(self.centralwidget)
        self.close_all.setGeometry(QRect(1730, 915, 120, 40))
        self.close_all.setStyleSheet("""
        QPushButton {
            border: 2px solid rgb(255,100,100);
            background-color: rgb(255,200,200);
            border-radius: 3px;
            height: 30px;
        }
        QPushButton:hover {
            background-color: rgb(255,100,100);
            border: 2px rgb(255,200,200);
        }
    """)

        # Define the launch plot button (to open a second window with IRT plots)
        self.lplot = QPushButton(self.centralwidget)
        self.lplot.setGeometry(QRect(1720,500, 100, 50))
        self.lplot.setStyleSheet("""
        QPushButton {
            border: 2px solid black;
            background-color: rgb(255,255,255);
            border-radius: 3px;
            height: 30px;
        }
        QPushButton:hover {
            background-color: lightgrey;
            border-color: lightgrey;
            border: 2px solid black;
        }
    """)

        # Define label that display in-real-time the received data of certain sensors
        self.sensors = [QLabel(self.centralwidget) for _ in range(7)]
        self.dims_sensor=[(1292, 450, 80, 21),(1292, 227, 80, 21),(821, 355, 80, 21),
                          (1262, 505, 80, 21),(1262, 145, 80, 21),(1165, 534, 80, 21),          
                          (1165, 120, 80, 21)]
        for sensor,dim in zip(self.sensors,self.dims_sensor):
            x,y,h,w=dim
            sensor.setGeometry(QRect(x,y,h,w))
            sensor.raise_()
        
        # The raise method is used to define the view localisation (foreground, background,...). 
        # These objects are updated here to make sure they are usable
        self.lplot.raise_()
        self.close_all.raise_()

        # Define a combobox to choose the test profile
        self.comboBox = QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QRect(1635,285,150,25))
        self.update_combobox()
        self.comboBox.raise_()

        # Define a button to view the test profile selected
        self.viewButton = QPushButton("View selection",self.centralwidget)
        self.viewButton.setGeometry(QRect(1800,283,100,30))
        self.viewButton.adjustSize()
        self.viewButton.clicked.connect(self.view_sequence)
        self.viewButton.raise_()

        # Labels used to display the test profile parameters
        self.title=QLabel(self.centralwidget)
        self.title.setGeometry(QRect(1655, 325, 70, 40))
        font = QFont("Arial", 10, QFont.Bold)
        self.title.setFont(font)

        self.label_preselect=[QLabel(self.centralwidget) for _ in range(15)]
        self.dim_preselect=[(1655,366,10,10),(1655,398,10,10),(1655,430,10,10),
             (1655,462,10,10),(1655,494,10,10),(1655,526,10,10),
             (1655,558,10,10)]
        
        # Define a button to start a coutdown and start the engine
        self.launch= QPushButton("START",self.centralwidget)
        self.launch.setGeometry(QRect(1720,320,100,30))
        font = QFont("Arial", 12, QFont.Bold)
        self.launch.setFont(font)
        self.launch.adjustSize()
        self.launch.setStyleSheet("""
        QPushButton {
            border: 1px solid rgb(100,100,100);
            background-color: rgb(225,225,225);
            border-radius: 1px;
            height: 30px;
        }
        QPushButton:hover {
            background-color: lightgrey;
            border-color: lightgrey;
            border: 2px solid black;
        }
    """)
        self.launch.clicked.connect(self.launch_engine)
        self.launch.raise_()

        # Button to test the sparking
        self.sparking= QPushButton("SPARK",self.centralwidget)
        self.sparking.setGeometry(QRect(1478,260,100,30))
        font = QFont("Arial", 12, QFont.Bold)
        self.sparking.setFont(font)
        self.sparking.adjustSize()
        self.sparking.setStyleSheet("""
                    QPushButton {
                        border: 1px solid rgb(255,0,0);
                        background-color: rgb(225,100,100);
                        border-radius: 1px;
                        height: 30px;
                    }
                    QPushButton:hover {
                        background-color: lightgrey;
                        border-color: lightgrey;
                        border: 2px solid black;
                    }
                """)
        self.sparking.clicked.connect(self.send_spark)
        self.sparking.raise_()
        self.spark_status=0

        # Define a chronometer since the begining of a test and a frame to deactivate valve buttons
        self.label_count = QLabel(self.centralwidget)
        self.frame_count = QFrame(self.centralwidget)
        self.frame_count.setGeometry(0, 0, 1900, 850)
        self.label_count.setGeometry(1690, 380, 160, 50)
        self.frame_count.setStyleSheet("""
                    QFrame {
                        background-color: transparent;
                    }
                """) 
        self.label_count.setStyleSheet("""
            QLabel {
                color: black; /* Text color set to black */
                font-size: 30px; /* Increased font size */
                border: 2px solid black; /* Black border with 2px width */
                padding: 5px; /* Optional: Adds some space between text and border */
            }
        """)
        self.label_count.hide()
        self.frame_count.hide()
        self.elapsed_time = 0  # Time in ms for chrono
        
        # Emergency button
        self.emergency_button= QPushButton("EMERGENCY",self.centralwidget)
        self.emergency_button.setGeometry(QRect(1700,700,100,30))
        font = QFont("Arial", 12, QFont.Bold)
        self.emergency_button.setFont(font)
        self.emergency_button.adjustSize()
        self.emergency_button.setStyleSheet("""
                    QPushButton {
                        border: 1px solid rgb(255,0,0);
                        background-color: rgb(225,100,100);
                        border-radius: 1px;
                        height: 30px;
                    }
                    QPushButton:hover {
                        background-color: lightgrey;
                        border-color: lightgrey;
                        border: 2px solid black;
                    }
                """)
        self.emergency_button.clicked.connect(self.emergency_stop)
        self.emergency_button.raise_()
        self.spark_status=0
        # Last objects of the MainWindow
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setWindowFlags(MainWindow.windowFlags() & ~Qt.WindowCloseButtonHint)     # Disable the close button hint
        MainWindow.setStyleSheet("background-color: rgb(236,236,236)")

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate

        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

        # Loop for responsivity purpose and set the default status of the valve
        for widget,label,name,ouvert,ferme,idd,num in zip(self.status,self.labels,self.names,self.ouverts,self.fermes,self.ids,self.nums):
            # Set valve to open mode and define the design of each other object
            if widget==self.status[-1]:
                widget.setText(_translate("MainWindow", "<u>"+name+" status:</u>"))
                widget.setStyleSheet("QFrame, QLabel, QToolTip {\n"
                "    background-color: rgb(230, 230, 230);\n"
                "}")
                color_effect = QGraphicsColorizeEffect()
                color_effect.setColor(Qt.darkGreen)
                label.setText(_translate("MainWindow", "Open"))
                label.setStyleSheet("QFrame, QLabel, QToolTip {\n"
                "    background-color: rgb(230, 230, 230);\n"
                "}")
                label.setGraphicsEffect(color_effect)
                widget.adjustSize() 
                label.adjustSize()
                color_effect = QGraphicsColorizeEffect()
                color_effect.setColor(Qt.darkGreen)
                idd.setText(_translate("MainWindow", "Open"))
                font = QFont("Arial", 8, QFont.Bold)
                idd.setFont(font)
                idd.setGraphicsEffect(color_effect)
                idd.adjustSize()
            # Set valve to closed mode and define the design of each other object
            else:
                widget.setText(_translate("MainWindow", "<u>"+name+" status:</u>"))
                widget.setStyleSheet("QFrame, QLabel, QToolTip {\n"
                "    background-color: rgb(230, 230, 230);\n"
                "}")
                            
                color_effect = QGraphicsColorizeEffect()
                color_effect.setColor(Qt.red)
                label.setText(_translate("MainWindow", "Closed"))
                label.setStyleSheet("QFrame, QLabel, QToolTip {\n"
                "    background-color: rgb(230, 230, 230);\n"
                "}")
                label.setGraphicsEffect(color_effect)
                widget.adjustSize() 
                label.adjustSize()
                color_effect = QGraphicsColorizeEffect()
                color_effect.setColor(Qt.red)
                idd.setText(_translate("MainWindow", "Closed"))
                idd.setGraphicsEffect(color_effect)
                font = QFont("Arial", 8, QFont.Bold)
                idd.setFont(font)
                idd.adjustSize()

            # Define the design of the button    
            ouvert.setText(_translate("MainWindow", "Open"))
            ouvert.setStyleSheet("""
            QPushButton {
                border: 1px solid black;
                background-color: white;
                border-radius: 3px;
                height: 30px;
            }
            QPushButton:hover {
                background-color: lightblue;
                border-color: lightblue;
            }
            """)
            ferme.setText(_translate("MainWindow", "Closed"))
            ferme.setStyleSheet("""
            QPushButton {
                border: 1px solid black;
                background-color: white;
                border-radius: 3px;
                height: 30px;
            }
            QPushButton:hover {
                background-color: lightblue;
                border-color: lightblue;
            }
            """)
            
            # Connect the button to a function
            ouvert.clicked.connect(functools.partial(self.open_valve, num, label, idd))
            ferme.clicked.connect(functools.partial(self.close_valve, num, label, idd))

        # Set the font,fontsize etc of some objects
        self.lplot.setText(_translate("MainWindow", "Launch Plot"))
        font = QFont("Arial", 9, QFont.Bold)
        self.lplot.setFont(font)


        self.close_all.setText(_translate("MainWindow", "End program"))
        
        font = QFont("Arial", 9, QFont.Bold)
        self.close_all.setFont(font)

        # Connect button to function
        self.lplot.clicked.connect(self.launch_plot)
        self.close_all.clicked.connect(self.close_all_program)

        # Linked the worker to the main class and launch it in a thread
        self.worker = Worker()
        self.worker_thread = threading.Thread(target=self.worker.write_csv_MC_board)    # Put the worker in a thread
        # Separate the worker from the main (if main crashes but not the program, the worker still collects data)
        self.worker_thread.daemon = True    
        self.worker_thread.start()
        self.worker.update_signal.connect(self.update_str)  # Only link between main and worker
        self.fourth_window = CountdownWidget()
        self.fourth_window.signal_activate.connect(self.activate)
        self.time_points=0
        self.ref_time=0
    
########################################################################
#   Sending related functions
########################################################################
    # Send a data to the MC_board (called by many function)
    def send_command(self,command):
        self.client_socket.sendto(bytes(command, 'utf-8'), sending_address)
        event_is_set  = self.worker.event1.wait(1)
        if event_is_set:
            data = self.worker.data_received
            self.worker.event1.clear()  # Reset the event
            return data

    # Change the status of the valve if a button is clicked
    def update_valve_status(self,valve_label, status_text, color):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        valve_label.setText(_translate("MainWindow", status_text))
        color_effect = QGraphicsColorizeEffect()
        color_effect.setColor(color)
        valve_label.setGraphicsEffect(color_effect)
        valve_label.adjustSize()

    # Change the label if it receives a signal from the MC_board
    def open_valve(self,valve_number, valve_label,valve_status):
        binary_list = list(self.bits)
        index = 7-valve_number
        binary_list[index] = str(1)
        modified_binary = ''.join(binary_list)
        if MC_board==0:
            self.update_valve_status(valve_label, "Open", Qt.darkGreen)
            self.update_valve_status(valve_status, "Open", Qt.darkGreen)
            self.bits=modified_binary
        else:
            try:
                rec_data = self.send_command(modified_binary)
                if rec_data == b"OK":
                    self.update_valve_status(valve_label, "Open", Qt.darkGreen)
                    self.update_valve_status(valve_status, "Open", Qt.darkGreen)
                    self.bits=modified_binary
            except:
                pass

    # Change the label if it receives a signal from the MC_board
    def close_valve(self,valve_number, valve_label,valve_status):
        binary_list = list(self.bits)
        index = 7-valve_number
        binary_list[index] = str(0)
        modified_binary = ''.join(binary_list)
        if MC_board==0:
            self.update_valve_status(valve_label, "Closed", Qt.red)
            self.update_valve_status(valve_status, "Closed", Qt.red)
            self.bits=modified_binary
        else:
            try:
                rec_data = self.send_command(modified_binary)
                if rec_data == b"OK":
                    self.update_valve_status(valve_label, "Closed", Qt.red)
                    self.update_valve_status(valve_status, "Closed", Qt.red)
                    self.bits=modified_binary
            except:
                pass

    # Send a spark message to test it
    def send_spark(self):
        if self.spark_status==0:
            spark="SP"
            resp=self.send_command(spark)
            self.spark_status=1

            # Update the design of the spark button to inform user
            if resp:
                self.sparking.setStyleSheet("""
                    QPushButton {
                        border: 1px solid rgb(0,255,0);
                        background-color: rgb(100,225,100);
                        border-radius: 1px;
                        height: 30px;
                    }
                    QPushButton:hover {
                        background-color: lightgrey;
                        border-color: lightgrey;
                        border: 2px solid black;
                    }
                """)
        else:
            spark="UNSP"
            resp=self.send_command(spark)
            self.spark_status=0
            if resp:
                self.sparking.setStyleSheet("""
                    QPushButton {
                        border: 1px solid rgb(255,0,0);
                        background-color: rgb(225,100,100);
                        border-radius: 1px;
                        height: 30px;
                    }
                    QPushButton:hover {
                        background-color: lightgrey;
                        border-color: lightgrey;
                        border: 2px solid black;
                    }
                """)
    
    # Stop the ongoing action
    def emergency_stop(self):
        emergency="STOP"
        resp=self.send_command(emergency)
        if resp:
            self.timer.stop()
            for k in range(len(self.labels)):
                self.update_valve_status(self.labels[6-k], "Closed", QColor(Qt.red))
                self.update_valve_status(self.ids[6-k], "Closed", QColor(Qt.red))
            self.bits="0010000"

    # Update the label sensor value to see them IRT
    def update_str(self,values):
        _translate = QCoreApplication.translate
        
        # Store the wanted value
        val = [values[1],values[2],values[3],
                   values[4],values[5],values[6],
                   values[7]]
        for i in range(0,7):
            if i==0 or i==1 or i==2:
                self.sensors[i].setText(_translate("MainWindow", str(val[i])+"bar"))
            elif i==3 or i==4:
                self.sensors[i].setText(_translate("MainWindow", str(val[i])+"K"))
            elif i==5 or i==6:
                self.sensors[i].setText(_translate("MainWindow", str(val[i])+"kg/s"))
        # Loop to print the value
        for widget in self.sensors:            
                font = QFont("Arial", 10, QFont.Bold)
                widget.setFont(font)
                widget.setStyleSheet("background-color: #dcdcdc")
                widget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)


########################################################################
#   Sequence related functions
########################################################################
    # Display the available sequence files
    def update_combobox(self):
        txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]
        self.comboBox.clear()
        self.comboBox.addItems(txt_files)
        if not txt_files:
            self.combobox.addItem('No .txt files found')

    # Display the selected test profil
    def view_sequence(self): 
        filename=self.comboBox.currentText()
        with open(filename, 'r') as file:
            lines = file.readlines()
            
            init_state_graph = lines[0].strip()
            events = {}
            
            for line in lines[1:]:
                parts = line.strip().split(',')
                valve_name = parts[0]
                times = list(map(int, parts[1:]))
                events[valve_name] = [time / 1000 for time in times]  # Convert times to seconds

        # Create the window
        self.fifth_window = QWidget()
        self.fifth_window.setWindowTitle("Valve State Graphs")
        
        # Create the layout and the figure
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        figure, axes = plt.subplots(7, 1, figsize=(15, 7), sharex=True)
        
        for i in range(7):
            valve_name = f'EV{i}'
            self.plot_valve_state(axes[i], valve_name, init_state_graph[i], events.get(valve_name, []))

        figure.subplots_adjust(hspace=0)  # Adjust hspace as needed for better spacing
        for ax in axes:
            ax.spines['bottom'].set_linestyle('--')  # Dotted line
            ax.spines['bottom'].set_linewidth(0.5)     # Adjust line width as needed
            ax.spines['bottom'].set_color('black')   # Adjust color as needed
            ax.spines['top'].set_linestyle('--')  # Dotted line
            ax.spines['top'].set_linewidth(0.5)     # Adjust line width as needed
            ax.spines['top'].set_color('black')   # Adjust color as needed
            ax.axvline(x=self.time_points-0.95, color='r', linestyle='--', label='Vertical Line')
        axes[-1].spines['bottom'].set_linestyle('-')  # Dotted line
        axes[0].spines['top'].set_linestyle('-')  # Dotted line
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)
        
        self.fifth_window.setLayout(layout)

        # Resize window
        self.fifth_window.resize(1200, 600)  # Adjust size as needed

        self.fifth_window.show()

    # Sub function of view_sequence that plot the sequence of a valve
    def plot_valve_state(self, ax, valve_name, init_state, times):
        time_points = [0] + times
        states = [int(init_state)]
        
        current_state = int(init_state)
        for _ in times:
            current_state = 1 - current_state
            states.append(current_state)
        
        time_points.append(time_points[-1] + 1)  # Extend the last time point to show the last state
        if max(time_points)>self.time_points:
            self.time_points=max(time_points)
        states.append(states[-1])
        time_points.append(time_points[-1] + 1000)
        ax.step(time_points, states + [states[-1]], where='post')
        ax.set_ylabel(f'{valve_name}')
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}'))
        ax.set_ylim(-0.25, 1.25)
        ax.set_xlim(0, self.time_points)
        
########################################################################
#   Test related functions
########################################################################
    # Launch the countdown window (in CountdownWidget class)  
    def launch_engine(self):
        filename=self.comboBox.currentText()
        with open(filename, 'r') as file:
            binary_number = file.readline().strip()
        self.client_socket.sendto(bytes(binary_number, 'utf-8'), sending_address)
        event_is_set  = self.worker.event1.wait(1)
        if event_is_set:
            rec_data = self.worker.data_received
            self.worker.event1.clear()  # Reset the event
        try:
            if rec_data == f"OK".encode():
                k=0
                for i in binary_number:
                    if i=='0':
                        self.update_valve_status(self.labels[k], "Closed", Qt.red)
                        self.update_valve_status(self.ids[k], "Closed", Qt.red)
                    elif i=='1':
                        self.update_valve_status(self.labels[k], "Open", Qt.darkGreen)
                        self.update_valve_status(self.ids[k], "Open", Qt.darkGreen)
                    k+=1

                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Warning)     # Create a warning box to make sur the closing is wanted
                reply = msgBox.warning(MainWindow, "Initialisation complete", 
                    "Initialisation completed. Do you want to proceed?", QMessageBox.Yes | 
                    QMessageBox.No, QMessageBox.No)

                # Terminate the program if Yes is selected
                if reply == QMessageBox.Yes:
                    self.fourth_window.show()
                    
        except:
            pass

    # Launch the chrono and send the sequence to the MC board
    def activate(self):
        self.fourth_window.lower()
        filename=self.comboBox.currentText()
        with open(filename, 'r') as file:
            sequences = [list(map(int, line.strip().split(',')[1:])) for line in file.readlines()]
        sequences.pop(0)
        formatted_sequences = ','.join([f"E,{','.join(map(str, seq))}" for seq in sequences])

        formatted_sequences = formatted_sequences.encode('utf-8')
        self.client_socket.sendto(formatted_sequences, sending_address)

        with open(data_csv, 'r') as file:
            reader = csv.reader(file)
            all_rows = list(reader)

        if all_rows:
            last_row = all_rows[-1]
            self.ref_time = int(float(last_row[0]))
                
        self.label_count.show()
        self.frame_count.show()
        self.timer = QTimer()
        self.running_time=max([max(val) for val in sequences])
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1)  # Update timer every second (100 ms)
    
    # Chrono since launch of the test
    def update_timer(self):
        try:
            with open(data_csv, 'r') as file:
                    reader = csv.reader(file)
                    all_rows = list(reader)
        except Exception as e:
                print(f"Error reading CSV file: {e}")
                return

        # Update valve state using csv
        if all_rows:
                last_row = all_rows[-1]
                last_7_columns = last_row[-7:]
                self.elapsed_time = int(float(last_row[0]))-int(float(self.ref_time))
                for k, value in enumerate(last_7_columns):
                    if k >= len(self.labels):
                        break
                    if value == '0.0':
                        self.update_valve_status(self.labels[6-k], "Closed", QColor(Qt.red))
                        self.update_valve_status(self.ids[6-k], "Closed", QColor(Qt.red))
                    elif value == '1.0':
                        self.update_valve_status(self.labels[6-k], "Open", QColor(Qt.darkGreen))
                        self.update_valve_status(self.ids[6-k], "Open", QColor(Qt.darkGreen))
        
        # Display the timer
        current_time = QTime(0, 0).addMSecs(self.elapsed_time)
        text = current_time.toString("mm:ss.zzz")
        self.label_count.setText(text)

        # Stop timer if it reaches the end of the test
        if self.elapsed_time-1 >= self.running_time:
            self.frame_count.hide()
            self.label_count.hide()
            self.bits=''.join(['1' if float_str == '1.0' else '0' for float_str in last_7_columns])
            self.timer.stop()

########################################################################
#   External options (plot and close program)
########################################################################
    def launch_plot(self):
        self.second_window = MultiRealTimePlot()
        self.second_window.show()

    # Function to avoid unwanted closing window due to misclicking
    def close_all_program(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)     # Create a warning box to make sur the closing is wanted
        reply = msgBox.warning(MainWindow, "Warning", 
            "Are you sure to quit?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)

        # Terminate the program if Yes is selected
        if reply == QMessageBox.Yes:
            print("\n\n\nYou closed the program.\nDid it work bitch (ง'-̀'́)ง  Ϟ  ฝ('-'ฝ)\n\n\n")
            QCoreApplication.quit()

# This class plots multiple curves in real time
class MultiRealTimePlot(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window parameters
        self.setWindowTitle("Multi Real-Time Plot")
        self.setFixedSize(1910, 990)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.real_time_plots = [self.RTP1(), self.RTP2(), self.RTP3()]
        self.x_data = []
        self.y_data = []
        self.x_axis_interval1 = 10  # Default x-axis interval plot1
        self.x_axis_interval2 = 10  # Default x-axis interval plot2
        self.x_axis_interval3 = 10  # Default x-axis interval plot3
        for plot in self.real_time_plots:
            layout.addWidget(plot)
        # Start the timer to update the plots (for synchronisation)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(int(1000/update_frequency)) 

    # Pressure plot
    def RTP1(self):
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)

        self.fig1 = Figure(figsize=(18, 6))
        self.ax1 = self.fig1.add_subplot(111)
        self.canvas1 = FigureCanvas(self.fig1)
        layout.addWidget(self.canvas1)
        self.ax1.xaxis.tick_bottom()
        self.ax1.spines['bottom'].set_position(('outward', 0))
        # Create a frame for x-axis interval and curves controls
        controls_frame = QFrame(self)
        controls_frame.setFrameShape(QFrame.StyledPanel)
        layout.addWidget(controls_frame)
        controls_frame.setFixedWidth(200)
        controls_layout = QGridLayout(controls_frame)

        x_length_label = QLabel("Time Interval:", self)
        controls_layout.addWidget(x_length_label)

        # Define multiple buttons to change the scale of the x-axis         IMPROVMENT: put everything in a loop
        # Last minute data
        self.button_1m_1 = QPushButton("10s", self)
        self.button_1m_1.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: white;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
            background-color: lightgrey;
            border-color: black;
            border: 3px solid black;
        }
""")
        self.button_1m_1.clicked.connect(lambda: self.set_x_interval1(10,1))
        controls_layout.addWidget(self.button_1m_1)

        # Last 10 min data
        self.button_10m_1 = QPushButton("30s", self)
        self.button_10m_1.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: white;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
            background-color: lightgrey;
            border-color: black;
            border: 3px solid black;
        }
""")
        self.button_10m_1.clicked.connect(lambda: self.set_x_interval1(30,2))
        controls_layout.addWidget(self.button_10m_1)

        # Last 30 min data     
        self.button_30m_1 = QPushButton("1m", self)
        self.button_30m_1.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: white;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
            background-color: lightgrey;
            border-color: black;
            border: 3px solid black;
        }
""")
        self.button_30m_1.clicked.connect(lambda: self.set_x_interval1(60,3))
        controls_layout.addWidget(self.button_30m_1)

        # All the registered data
        self.button_All_1 = QPushButton("All", self)
        self.button_All_1.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: white;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
            background-color: lightgrey;
            border-color: black;
            border: 3px solid black;
        }
""")
        self.button_All_1.clicked.connect(lambda: self.set_x_interval1(-1,4))
        controls_layout.addWidget(self.button_All_1)

        curve_label = QLabel("Sensors:", self)
        controls_layout.addWidget(curve_label)
        curve_label1 = QLabel(" ", self)
        controls_layout.addWidget(curve_label1)
        curve_label2 = QLabel(" ", self)
        controls_layout.addWidget(curve_label2)
        curve_label3 = QLabel(" ", self)
        controls_layout.addWidget(curve_label3)
        curve_label4 = QLabel(" ", self)
        controls_layout.addWidget(curve_label4)
        curve_label5 = QLabel(" ", self)
        controls_layout.addWidget(curve_label5)
        # Define checkboxes to show specific curves                     IMPROVMENT: loop
        self.checkbox_1 = QCheckBox("PS1", self)
        self.checkbox_1.setChecked(True)  # Default to show the first curve
        controls_layout.addWidget(self.checkbox_1)

        self.checkbox_2 = QCheckBox("PS2", self)
        controls_layout.addWidget(self.checkbox_2)

        self.checkbox_3 = QCheckBox("PS3", self)
        controls_layout.addWidget(self.checkbox_3)

        
        checked_boxes = [self.checkbox_1, self.checkbox_2, self.checkbox_3]

        # Responsivity (put the checbox in columns)
        rows = 4
        cols = 1
        for i, checkbox in enumerate(checked_boxes):
            row = rows + i % 5
            col = cols * (i // 5)
            controls_layout.addWidget(checkbox, row, col)

        controls_layout.addWidget(x_length_label, 0, 0)
        controls_layout.addWidget(curve_label, 3, 0)
        controls_layout.addWidget(curve_label3, 7, 0)
        controls_layout.addWidget(curve_label4, 8, 0)
        controls_layout.addWidget(curve_label5, 9, 0)
        controls_layout.addWidget(self.checkbox_1, 4, 0)
        controls_layout.addWidget(self.checkbox_2, 5, 0)
        controls_layout.addWidget(self.checkbox_3, 6, 0)
        controls_layout.addWidget(self.button_1m_1, 1, 0)
        controls_layout.addWidget(self.button_10m_1, 1, 1)
        controls_layout.addWidget(self.button_30m_1, 2, 0)
        controls_layout.addWidget(self.button_All_1, 2, 1)

        return central_widget

    # Temperature plot (same principle as RTP1)
    def RTP2(self):
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)

        self.fig2 = Figure(figsize=(18, 6))
        self.ax2 = self.fig2.add_subplot(111)
        self.canvas2 = FigureCanvas(self.fig2)
        layout.addWidget(self.canvas2)

        controls_frame = QFrame(self)
        controls_frame.setFrameShape(QFrame.StyledPanel)
        layout.addWidget(controls_frame)
        controls_frame.setFixedWidth(200)

        controls_layout = QGridLayout(controls_frame)

        x_length_label = QLabel("Time Interval:", self)
        controls_layout.addWidget(x_length_label)

        self.button_1m_2 = QPushButton("10s", self)
        self.button_1m_2.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: white;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
            background-color: lightgrey;
            border-color: black;
            border: 3px solid black;
        }
""")
        self.button_1m_2.clicked.connect(lambda: self.set_x_interval2(10,1))
        controls_layout.addWidget(self.button_1m_2)
        
        self.button_10m_2 = QPushButton("30s", self)
        self.button_10m_2.clicked.connect(lambda: self.set_x_interval2(30,2))
        self.button_10m_2.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: white;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
            background-color: lightgrey;
            border-color: black;
            border: 3px solid black;
        }
""")
        controls_layout.addWidget(self.button_10m_2)

        self.button_30m_2 = QPushButton("1m", self)
        self.button_30m_2.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: white;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
            background-color: lightgrey;
            border-color: black;
            border: 3px solid black;
        }
""")
        self.button_30m_2.clicked.connect(lambda: self.set_x_interval2(60,3))
        controls_layout.addWidget(self.button_30m_2)

        self.button_All_2 = QPushButton("All", self)
        self.button_All_2.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: white;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
            background-color: lightgrey;
            border-color: black;
            border: 3px solid black;
        }
""")
        self.button_All_2.clicked.connect(lambda: self.set_x_interval2(-1,4))
        controls_layout.addWidget(self.button_All_2)

        curve_label = QLabel("Sensors:", self)
        controls_layout.addWidget(curve_label)
        curve_label1 = QLabel(" ", self)
        controls_layout.addWidget(curve_label1)
        curve_label2 = QLabel(" ", self)
        controls_layout.addWidget(curve_label2)
        curve_label3 = QLabel(" ", self)
        controls_layout.addWidget(curve_label3)
        curve_label4 = QLabel(" ", self)
        controls_layout.addWidget(curve_label4)
        curve_label5 = QLabel(" ", self)
        controls_layout.addWidget(curve_label5)

        self.checkbox_4 = QCheckBox("TS1", self)
        self.checkbox_4.setChecked(True)
        controls_layout.addWidget(self.checkbox_4)

        self.checkbox_5 = QCheckBox("TS2", self)
        controls_layout.addWidget(self.checkbox_5)

        controls_layout.addWidget(x_length_label, 0, 0)
        controls_layout.addWidget(curve_label, 3, 0)  
        controls_layout.addWidget(curve_label2, 6, 0)
        controls_layout.addWidget(curve_label3, 7, 0)
        controls_layout.addWidget(curve_label4, 8, 0)
        controls_layout.addWidget(curve_label5, 9, 0)
        controls_layout.addWidget(self.checkbox_4, 4, 0)
        controls_layout.addWidget(self.checkbox_5, 5, 0)

        controls_layout.addWidget(self.button_1m_2, 1, 0)
        controls_layout.addWidget(self.button_10m_2, 1, 1)
        controls_layout.addWidget(self.button_30m_2, 2, 0)
        controls_layout.addWidget(self.button_All_2, 2, 1)
        return central_widget

    # Force plot (same principle as RTP1)
    def RTP3(self):
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)

        self.fig3 = Figure(figsize=(18, 6))
        self.ax3 = self.fig3.add_subplot(111)
        self.canvas3 = FigureCanvas(self.fig3)
        layout.addWidget(self.canvas3)

        controls_frame = QFrame(self)
        controls_frame.setFrameShape(QFrame.StyledPanel)
        layout.addWidget(controls_frame)
        controls_frame.setFixedWidth(200)

        controls_layout = QGridLayout(controls_frame)

        x_length_label = QLabel("Time Interval:", self)
        controls_layout.addWidget(x_length_label)

        self.button_1m_3 = QPushButton("10s", self)
        self.button_1m_3.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: white;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
            background-color: lightgrey;
            border-color: black;
            border: 3px solid black;
        }
""")
        self.button_1m_3.clicked.connect(lambda: self.set_x_interval3(10,1))
        controls_layout.addWidget(self.button_1m_3)

        self.button_10m_3 = QPushButton("30s", self)
        self.button_10m_3.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: white;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
            background-color: lightgrey;
            border-color: black;
            border: 3px solid black;
        }
""")
        self.button_10m_3.clicked.connect(lambda: self.set_x_interval3(30,2))
        controls_layout.addWidget(self.button_10m_3)

        self.button_30m_3 = QPushButton("1m", self)
        self.button_30m_3.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: white;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
            background-color: lightgrey;
            border-color: black;
            border: 3px solid black;
        }
""")
        self.button_30m_3.clicked.connect(lambda: self.set_x_interval3(60,3))
        controls_layout.addWidget(self.button_30m_3)

        self.button_All_3 = QPushButton("All", self)
        self.button_All_3.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: white;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
            background-color: lightgrey;
            border-color: black;
            border: 3px solid black;
        }
""")
        self.button_All_3.clicked.connect(lambda: self.set_x_interval3(-1,4))
        controls_layout.addWidget(self.button_All_3)

        curve_label = QLabel("Sensors:", self)
        controls_layout.addWidget(curve_label)

        curve_label1 = QLabel(" ", self)
        controls_layout.addWidget(curve_label1)
        curve_label2 = QLabel(" ", self)
        controls_layout.addWidget(curve_label2)
        curve_label3 = QLabel(" ", self)
        controls_layout.addWidget(curve_label3)
        curve_label4 = QLabel(" ", self)
        controls_layout.addWidget(curve_label4)
        curve_label5 = QLabel(" ", self)
        controls_layout.addWidget(curve_label5)

        self.checkbox_6 = QCheckBox("FS1", self)
        self.checkbox_6.setChecked(True)
        controls_layout.addWidget(self.checkbox_6)
        self.checkbox_7 = QCheckBox("FS2", self)
        controls_layout.addWidget(self.checkbox_7)

        controls_layout.addWidget(x_length_label, 0, 0)
        controls_layout.addWidget(curve_label, 3, 0)   
        controls_layout.addWidget(curve_label2, 6, 0)
        controls_layout.addWidget(curve_label3, 7, 0)
        controls_layout.addWidget(curve_label4, 8, 0)
        controls_layout.addWidget(curve_label5, 9, 0)
        controls_layout.addWidget(self.checkbox_6, 4, 0)
        controls_layout.addWidget(self.checkbox_7, 5, 0)
        controls_layout.addWidget(self.button_1m_3, 1, 0)
        controls_layout.addWidget(self.button_10m_3, 1, 1)
        controls_layout.addWidget(self.button_30m_3, 2, 0)
        controls_layout.addWidget(self.button_All_3, 2, 1)
        return central_widget

    def update_plot(self):
        # Read the data of the csv (second link with the worker) and stored them
        with open(data_csv, "r") as file:
            csv_reader = csv.reader(file)
            first_row = next(csv_reader)

            self.x_data = []
            self.y_data = []
             
            for row in csv_reader:
                self.x_data.append((float(row[0])-float(first_row[0]))/1000)
                self.y_data.append([float(row[i]) for i in range(1, 8)])

        # Update RTP1 plot
        self.ax1.clear()
        # Check that checkbox is selected to display the plot (one color for each curves)
        if self.checkbox_1.isChecked():
            self.ax1.plot(self.x_data, [data[0] for data in self.y_data],color="blue", label="PS1")
            self.checkbox_1.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: blue; border: 2px solid blue; border-radius: 4px;}}")
        else:
            self.checkbox_1.setStyleSheet("")

        if self.checkbox_2.isChecked():
            self.ax1.plot(self.x_data, [data[1] for data in self.y_data],color="orange", label="PS2")
            self.checkbox_2.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: orange; border: 2px solid orange; border-radius: 4px;}}")
        else:
            self.checkbox_2.setStyleSheet("")

        if self.checkbox_3.isChecked():
            self.ax1.plot(self.x_data, [data[2] for data in self.y_data],color="green", label="PS3")
            self.checkbox_3.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: green; border: 2px solid green; border-radius: 4px;}}")
        else:
            self.checkbox_3.setStyleSheet("")
       
        # Adjust x-axis limits (depending on button selection)
        if self.x_axis_interval1==-1:
            self.ax1.set_xlim(0, max(self.x_data))
        else:
            self.ax1.set_xlim(max(0,max(self.x_data) - self.x_axis_interval1), max(self.x_data))
        
        # Responsivity only
        self.ax1.grid(True, which='both', linestyle='--')
        self.ax1.spines['bottom'].set_position('zero')
        self.ax1.tick_params(axis='both', which='both', length=2, width=2, direction='inout')
        self.canvas1.draw()

        # Update RTP2 plot (same thing as previously)
        self.ax2.clear()
        if self.checkbox_4.isChecked():
            self.ax2.plot(self.x_data, [data[3] for data in self.y_data],color="blue", label="TS1")
            self.checkbox_4.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: blue; border: 2px solid blue; border-radius: 4px;}}")
        else:
            self.checkbox_4.setStyleSheet("")

        if self.checkbox_5.isChecked():
            self.ax2.plot(self.x_data, [data[4] for data in self.y_data],color="orange", label="TS2")
            self.checkbox_5.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: orange; border: 2px solid orange; border-radius: 4px;}}")
        else:
            self.checkbox_5.setStyleSheet("")

        # Adjust x-axis limits
        if self.x_axis_interval2==-1:
            self.ax2.set_xlim(0, max(self.x_data))
        else:
            self.ax2.set_xlim(max(0,max(self.x_data) - self.x_axis_interval2), max(self.x_data))

        # Responsivity only
        self.ax2.spines['bottom'].set_position('zero')
        self.ax2.tick_params(axis='both', which='both', length=2, width=2, direction='inout')
        self.ax2.grid(True, which='both', linestyle='--')
        self.canvas2.draw()

        # Update RTP3 plot (same)
        self.ax3.clear()
        if self.checkbox_6.isChecked():
            self.ax3.plot(self.x_data, [data[5] for data in self.y_data],color='blue', label="FS1")
            self.checkbox_6.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: blue; border: 2px solid blue; border-radius: 4px;}}")
        else:
            self.checkbox_6.setStyleSheet("")

        if self.checkbox_7.isChecked():
            self.ax3.plot(self.x_data, [data[6] for data in self.y_data],color='orange', label="FS2")
            self.checkbox_7.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: orange; border: 2px solid orange; border-radius: 4px;}}")
        else:
            self.checkbox_7.setStyleSheet("")


        # Adjust x-axis limits
        if self.x_axis_interval3==-1:
            self.ax3.set_xlim(0, max(self.x_data))
        else:
            self.ax3.set_xlim(max(0,max(self.x_data) - self.x_axis_interval3), max(self.x_data))
    
        # Responsivity only
        self.ax3.spines['bottom'].set_position('zero')
        self.ax3.tick_params(axis='both', which='both', length=2, width=2, direction='inout')
        self.ax3.grid(True, which='both', linestyle='--')
        self.canvas3.draw()

    # Modify the x scale of the pressure plot
    def set_x_interval1(self, interval,id):
        self.x_axis_interval1 = interval
        button_list = [self.button_1m_1, self.button_10m_1, self.button_30m_1, self.button_All_1]

        for i, button in enumerate(button_list):
            if i == id - 1:
                button.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: grey;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
        background-color: lightblue;
        border-color: lightblue;
    }
""")
            else:
                button.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: white;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
        background-color: lightblue;
        border-color: lightblue;
    }
""")  # Set default background col
        self.update_plot()

    # Modify the x scale of the temperature plot
    def set_x_interval2(self, interval,id):
        self.x_axis_interval2 = interval
        button_list = [self.button_1m_2, self.button_10m_2, self.button_30m_2, self.button_All_2]

        for i, button in enumerate(button_list):
            if i == id - 1:
                button.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: grey;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
        background-color: lightblue;
        border-color: lightblue;
    }
""")
            else:
                button.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: white;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
        background-color: lightblue;
        border-color: lightblue;
    }
""") # Set default background col
        self.update_plot()

    # Modify the x scale of the force plot
    def set_x_interval3(self, interval,id):
        self.x_axis_interval3 = interval
        button_list = [self.button_1m_3, self.button_10m_3, self.button_30m_3, self.button_All_3]

        for i, button in enumerate(button_list):
            if i == id - 1:
                button.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: grey;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
        background-color: lightblue;
        border-color: lightblue;
    }
""")
            else:
                button.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        background-color: white;
        border-radius: 3px;
        height: 30px;
    }
    QPushButton:hover {
        background-color: lightblue;
        border-color: lightblue;
    }
""")  # Set default background col
        self.update_plot()

# This class generates a 7 segment display down counter
class CountdownWidget(QWidget):
    signal_activate = pyqtSignal()
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Countdown Timer")
        self.setGeometry(750, 490, 300, 150)

        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        # Define a start button (last barrier before no return)
        self.start_button = QPushButton("START COUNTDOWN", self)
        self.start_button.clicked.connect(self.start_countdown)
        self.button_layout.addWidget(self.start_button)
        font = QFont("Arial", 8, QFont.Bold)
        self.start_button.setFont(font)

        # Define a button to stop the timer
        self.stop_button = QPushButton("STOP", self)
        self.stop_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.stop_button)
        font = QFont("Arial", 9, QFont.Bold)
        self.stop_button.setFont(font)

        self.layout.addLayout(self.button_layout)

        # Define a countdown of 10s
        self.countdown_display = QLCDNumber(self)
        self.count_sec, self.count_msec= countdown_time
        self.countdown_display.setFixedSize(300, 100)  # Adjusted the size of the display
        self.countdown_display.display(f"{self.count_sec:02d}:{self.count_msec:03d}")

        self.layout.addWidget(self.countdown_display)
        
        self.setLayout(self.layout)

        # A label that will inform that the engine started
        self.engine_started_label = QLabel("")
        self.layout.addWidget(self.engine_started_label)
        self.engine_started_label.hide()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)

    def start_countdown(self):
        self.timer.start(10)

    # Update the seven segment display countdown until zero
    def update_display(self):
        if self.count_sec > 0 or self.count_msec > 0:
            self.count_msec -= 1
            if self.count_msec < 0:
                self.count_msec = 99
                self.count_sec -= 1
            self.countdown_display.display(f"{self.count_sec:02d}:{self.count_msec:02d}")
        else:
            # When reaching 0, the counter disappears and a label appears to inform that the engine started
            self.timer.stop()
            self.countdown_display.hide()
            self.engine_started_label.setText("\tEngine started")
            font = QFont("Arial", 12, QFont.Bold)
            self.engine_started_label.setFont(font)
            self.engine_started_label.adjustSize()
            self.engine_started_label.show()
            self.signal_activate.emit()
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    
    sys.exit(app.exec_())


