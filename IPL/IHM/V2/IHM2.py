"""
Human-Machine Interface for 1kN rocket engine project

Creator : Mehdi Delouane

"""
import sys      # Used for system manipulation ( system error,...)
from socket import *    # Has a buffer (any delay doesn't mean loss of data)
import csv      # Store data received from the arduino
import time     # Used to ensure synchronisation
import threading    # Used to get data and plot them at the same time
import functools    # Link functions to button
import json     # Store the test profile data
import numpy as np  # Used to generate data when there's no arduino

# PyQT5 library to construct the interface
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *

# MatPlotLib library for in-real-time plot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# This class collects data sent by the Arduino. Acts also as a synchronizer for the IRT plot
class Worker(QObject):
    update_signal = pyqtSignal(list)    # Define a signal used for synchronisation

    def __init__(self):
        super().__init__()

        # Allows to run program in test mode whithout needing a connected Arduino (set to 0 to go in test mode)
        self.arduino = 0        
        # Define the frequency at which you received data
        self.freq=1

    # Collect the data sent by the arduino (or generate values)
    def write_csv_arduino(self):
        i = 0

        # Connect the program to the Arduino
        address = ('192.168.0.101', 5000)  # define server IP and port
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.settimeout(1)
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
                            t = (
                                int(data[4]) << 24
                                | int(data[5]) << 16
                                | int(data[6]) << 8
                                | int(data[7])
                            )
                            a.append(t)

                            # Values of the sensors (pressure, temperature, force, flowrate)
                            for i in range(8, len(data), 2):
                                a1 = (int(data[i]) << 8
                                    | int(data[i + 1]))
                                a1 = (25 / 4.5) * (a1 * (5 / 4096) - 0.5)
                                a.append(round(a1, 2))

                            # Get the ID of the array to ensure no loss
                            a.append(round(int(data[2]) << 8 | int(data[3]), 2))
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

# Main class of the program
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        # Allows to run program in test mode whithout needing a connected Arduino (set to 0 to go in test mode)
        self.arduino=0

        # Create the MainWindow object and set its size
        MainWindow.resize(1922, 1237)
        self.centralwidget = QWidget(MainWindow)

        # Create the background of the main window with the P&ID and a grey background
        self.background = QLabel(self.centralwidget)
        self.background.setGeometry(QRect(30, -40, 2000, 1080))
        self.background.setPixmap(QPixmap("PID_IHM.png"))
        self.frame1 = QFrame(self.centralwidget)
        self.frame1.setGeometry(QRect(-31, -91, 1891, 1231))
        self.frame1.setAutoFillBackground(True)
        self.frame1.setFrameShape(QFrame.StyledPanel)
        self.frame1.setFrameShadow(QFrame.Raised)
        self.frame1.raise_()
        self.background.raise_()

        # Insert the IPL logo
        self.logo = QLabel(self.centralwidget)
        self.logo.setGeometry(QRect(1620, 50, 500, 100))
        self.logo.setPixmap(QPixmap("logo.png"))
        self.logo.raise_()

        # Insert a table (used to sum up the valve status)
        self.table = QLabel(self.centralwidget)
        self.table.setGeometry(QRect(1250, 500, 271, 381))
        self.table.setPixmap(QPixmap("table.png"))
        self.table.raise_()

        # The status display is a square (frame) with two buttons and two labels that indicates to the user the status of the valve (open/close)
        # Create all the frames for the status valves display
        self.frames = [QFrame(self.centralwidget) for _ in range(12)]
        self.dims_frame=[(600, 620, 111, 91),(770, 540, 111, 91),(600, 70, 111, 91), 
              (770, 190, 111, 91),(160, 470, 111, 91),(300, 190, 111, 91),
              (300, 530, 111, 91),(980, 90, 111, 91),(980, 630, 111, 91),
              (330, 780, 111, 91),(560, 740, 111, 91),(720, 770, 111, 91)
              ]
        
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
        self.status=[QLabel(self.centralwidget) for _ in range(12)]     # Indicates the status of the valve
        self.labels=[QLabel(self.centralwidget) for _ in range(12)]     # Indicates the name of the valve
        self.ouverts=[QPushButton(self.centralwidget) for _ in range(12)]   # Button to open valve
        self.fermes=[QPushButton(self.centralwidget) for _ in range(12)]    # Button to close valve
        self.ids=[QLabel(self.centralwidget) for _ in range(12)]    # Label placed in the sum up table 
        
        # Define specifically the name and number of the valve
        self.names=['SV11','SV12','SV21',
               'SV22','SV31','SV32',
               'SV33','SV34','SV35',
               'SV51','SV61','SV62']
        self.nums=[11,12,21,
               22,31,32,
               33,34,35,
               51,61,62]
        
        # Dimension and localisation of the status display objects
        self.dims_status=[(618, 630, 111, 16),(788, 550, 111, 16),(618, 80, 111, 16),
                          (788, 200, 111, 16),(178, 480, 111, 16),(318, 200, 111, 16),
                          (318, 540, 111, 16),(998, 100, 111, 16),(998, 640, 111, 16),
                          (348, 790, 111, 16),(578, 750, 111, 16),(738, 780, 111, 16)]
        self.dims_label=[(638, 650, 55, 16),(808, 570, 55, 16),(638, 100, 55, 16),
                         (808, 220, 55, 16),(198, 500, 55, 16),(338, 220, 55, 16),
                         (338, 560, 55, 16),(1018, 120, 55, 16),(1018, 660, 55, 16),
                         (368, 810, 55, 16),(600, 770, 55, 16),(760, 800, 55, 16)]    
        self.dims_ouvert=[(609, 670, 41, 28),(779, 590, 41, 28),(609, 120, 41, 28),
                          (779, 240, 41, 28),(169, 520, 41, 28),(309, 240, 41, 28),
                          (309, 580, 41, 28),(989, 140, 41, 28),(989, 680, 41, 28),
                          (339, 830, 41, 28),(569, 790, 41, 28),(729, 820, 41, 28)]       
        self.dims_ferme=[(655, 670, 48, 28),(825, 590, 48, 28),(655, 120, 48, 28),
                         (825, 240, 48, 28),(215, 520, 48, 28),(355, 240, 48, 28),
                         (355, 580, 48, 28),(1035, 140, 48, 28),(1035, 680, 48, 28),
                         (385, 830, 48, 28),(615, 790, 48, 28),(775, 820, 48, 28)]
        self.dims_idd=[(1428, 567, 55, 16),(1428, 591, 55, 16),(1428, 613, 55, 16),
                        (1428, 636, 55, 16),(1428, 660, 55, 16),(1428, 682, 55, 16),
                        (1428, 705, 55, 16),(1428, 728, 55, 16),(1428, 752, 55, 16),
                        (1428, 774, 55, 16),(1428, 797, 55, 16),(1428, 820, 55, 16)]
        
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
        
        # Create actuator related object (spinbox, slider, frame, label, button)
        self.sliders=[QSlider(self.centralwidget) for _ in range(2)]    # Define the sliders
        self.dims_slider=[(1644, 703, 22, 160),(1844, 703, 22, 160)]    # Define the dimensions and localisation of the slider
        self.spinboxes=[QSpinBox(self.centralwidget) for _ in range(2)]     # Define the spinboxes
        self.dims_spinbox=[(1635, 673, 42, 22),(1835, 673, 42, 22)]     # Define the dimensions and localisation of the spinbox
        self.frames2 = [QFrame(self.centralwidget) for _ in range(5)]   # Define the frames
        self.dims_frame2=[(1575, 200, 336, 1000),(1575, 603, 184, 280), (1575, 603, 336, 383),
                          (1575, 880, 336, 102),(1575, 200, 336, 70)]     # Define the dimensions and localisation of the frame
        self.labs=[QLabel(self.centralwidget) for _ in range(2)]
        self.dims_lab=[(1620, 653, 60, 16),(1820, 653, 60, 16)]
        self.actuator_name=["Actuator L","Actuator R"]

        # Loop to place each frame (these frame delimit different section on the right part of the screen)
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

        # Set a frame with dashed border for responsivity
        self.frames2[1].setStyleSheet("QFrame, QLabel, QToolTip {\n"
            "    background-color: rgba(0, 0, 0, 0);\n"
            "    border: 3px dashed grey;\n"
            "    border-radius: 1px;\n"
            "    padding: 2px;\n"
            "}")

        # Loop to place each above object (except frames)
        for slider,dim_slider,spinbox,dim_spinbox,lab,dim_lab in zip(self.sliders,self.dims_slider,self.spinboxes,self.dims_spinbox,self.labs,self.dims_lab):
            # Set position and dimension of the sliders
            x,y,h,w,= dim_slider
            slider.setGeometry(QRect(x,y,h,w))
            slider.setOrientation(Qt.Vertical)  # Set orientation of the slider
            slider.setMinimum(0)    # Set minimum value of the slider
            slider.setValue(50)     # Set default value of the slider
            slider.setMaximum(101)  # Set maximum value of the slider (put N+1 to get N as a max value)    
            slider.setStyleSheet(
            """
            QSlider::groove:vertical {
                border: 1px solid #999999;
                background: #E0E0E0;
                width: 10px; /* adjust width */
                margin: 5px 5px; /* adjust margin */
            }
            QSlider::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f6f7fa, stop:1 #dadbde);
                border: 1px solid #5c5c5c;
                width: 20px; /* adjust width */
                height: 12px; /* adjust height */
                margin: -1px -5px; /* adjust margin */
                border-radius: 10px; /* adjust border radius */
            }
            """
            )
            idd=self.sliders.index(slider)
            slider.valueChanged.connect(functools.partial(self.sliderval,idd))
            slider.raise_()

            # Set position and dimension of the spinboxes
            x,y,h,w,= dim_spinbox
            spinbox.setGeometry(QRect(x,y,h,w))
            spinbox.setMinimum(0)   # Set minimum value of the spinbox
            spinbox.setValue(50)    # Set default value of the spinbox
            spinbox.setMaximum(100) # Set maximum value of the spinbox (put N to get N as a max value)    
            idd=self.spinboxes.index(spinbox)
            spinbox.valueChanged.connect(functools.partial(self.spinboxval,idd))
            spinbox.raise_()

            # Set position, dimension and font of the sliders
            x,y,h,w,= dim_lab
            lab.setGeometry(QRect(x,y,h,w))
            font = QFont("Arial", 8, QFont.Bold)
            lab.setFont(font)
            lab.raise_()
        

        # Define a button used to send the selected values of the slider&spinbox
        self.actuator = QPushButton(self.centralwidget)
        self.actuator.setGeometry(QRect(1720, 753, 70, 40))
        font = QFont("Arial", 8, QFont.Bold)
        self.actuator.setFont(font)
        self.actuator.setStyleSheet("""
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
        
        # Define a button to finish the entire program (to avoid closing windows unintentionally, the close button hint is disabled)
        self.close_all = QPushButton(self.centralwidget)
        self.close_all.setGeometry(QRect(1690, 915, 120, 40))
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
        self.lplot.setGeometry(QRect(1330, 880, 100, 50))
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
        self.sensors = [QLabel(self.centralwidget) for _ in range(10)]
        self.dims_sensor=[(503, 485, 37, 21),(503, 323, 37, 21),(209, 272, 37, 21),
                          (486, 900, 37, 21),(926, 945, 37, 21),(1043, 945, 37, 21),          
                          (1084, 280, 37, 21),(1186, 280, 37, 21),(926, 840, 37, 21),
                          (1043, 840, 37, 21)]
        for sensor,dim in zip(self.sensors,self.dims_sensor):
            x,y,h,w=dim
            sensor.setGeometry(QRect(x,y,h,w))
            sensor.raise_()
        
        # The raise method is used to define the view localisation (foreground, background,...). 
        # These objects are updated here to make sure they are usable
        self.lplot.raise_()
        self.actuator.raise_()
        self.close_all.raise_()

        # Define a combobox to choose the test profile
        self.comboBox = QComboBox(self.centralwidget)
        self.load_json()
        self.comboBox.setGeometry(QRect(1590,285,200,25))
        self.comboBox.currentIndexChanged.connect(self.update_json_text)
        self.comboBox.raise_()

        # Define a button to view the test profile selected
        self.viewButton = QPushButton("View selection",self.centralwidget)
        self.viewButton.setGeometry(QRect(1800,283,100,30))
        self.viewButton.adjustSize()
        self.viewButton.clicked.connect(self.view_json)
        self.viewButton.raise_()

        # Labels used to display the test profile parameters
        self.title=QLabel(self.centralwidget)
        self.title.setGeometry(QRect(1610, 325, 70, 40))
        font = QFont("Arial", 10, QFont.Bold)
        self.title.setFont(font)

        self.label_preselect=[QLabel(self.centralwidget) for _ in range(15)]
        self.dim_preselect=[(1610,366,10,10),(1610,398,10,10),(1610,430,10,10),
             (1610,462,10,10),(1610,494,10,10),(1610,526,10,10),
             (1610,558,10,10)]
        
        # Define a button to view a checklist (registered as an image)
        self.checklist= QPushButton("View Checklist",self.centralwidget)
        self.checklist.setGeometry(QRect(1700,220,100,30))
        self.checklist.adjustSize()
        self.checklist.clicked.connect(self.view_checklist)
        self.checklist.raise_()

        # Define a button to start a coutdown and start the engine
        self.launch= QPushButton("START",self.centralwidget)
        self.launch.setGeometry(QRect(1700,560,100,30))
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

        self.adress='192.168.0.101'     # Define the IP adress to connect the arduino

        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

        # Loop for responsivity purpose and set the default status of the valve
        for widget,label,name,ouvert,ferme,idd,num in zip(self.status,self.labels,self.names,self.ouverts,self.fermes,self.ids,self.nums):
            # Set valve to open mode and define the design of each other object
            if widget==self.status[0] or widget==self.status[2]:
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

        # Display the title of each display frame    
        for lab, act in zip(self.labs,self.actuator_name):
            lab.setText(_translate("MainWindow", "<u>"+act+"</u>"))
            lab.adjustSize()

        # Set the font,fontsize etc of some objects
        self.lplot.setText(_translate("MainWindow", "Launch Plot"))
        font = QFont("Arial", 9, QFont.Bold)
        self.lplot.setFont(font)

        self.checklist.setText(_translate("MainWindow", "View checklist"))
        font = QFont("Arial", 9, QFont.Bold)
        self.checklist.setFont(font)
        self.checklist.adjustSize()

        self.actuator.setText(_translate("MainWindow", "Set position"))
        self.actuator.adjustSize()
        self.close_all.setText(_translate("MainWindow", "End program"))
        
        font = QFont("Arial", 9, QFont.Bold)
        self.close_all.setFont(font)

        # Connect button to function
        self.lplot.clicked.connect(self.launch_plot)
        self.close_all.clicked.connect(self.close_all_program)
        self.actuator.clicked.connect(lambda : self.control_actuator(self.spinboxes[0].value(),self.spinboxes[1].value()))

        # Linked the worker to the main class and launch it in a thread
        self.worker = Worker()
        self.worker_thread = threading.Thread(target=self.worker.write_csv_arduino)    # Put the worker in a thread
        # Separate the worker from the main (if main crashes but not the program, the worker still collects data)
        self.worker_thread.daemon = True    
        self.worker_thread.start()
        self.worker.update_signal.connect(self.update_str)  # Only link between main and worker

    # Send the selection of actutor to the arduino
    def control_actuator(self,value1,value2):
        _translate = QCoreApplication.translate
        if self.arduino==0:
            self.position_sent = QLabel(self.centralwidget)
            self.position_sent.setText(_translate("MainWindow", "Position sent"))
            self.position_sent.setGeometry(QRect(1720, 810, 70, 40))
                    
            font = QFont("Arial", 9, QFont.Bold)
            self.position_sent.setFont(font)
            self.position_sent.adjustSize()
            self.position_sent.show()

            self.animation = QVariantAnimation()
            self.animation.valueChanged.connect(self.change_opacity)
            self.animation.setStartValue(255)
            self.animation.setEndValue(0)
            self.animation.setDuration(10000)  # Duration in milliseconds
            self.animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.animation.start()

            print(ver_send)
        else:
            try:
                # Send the data and wait for an asnwer before indicating that the data has been sent
                address = (self.adress, 5000)
                self.client_socket = socket(AF_INET, SOCK_DGRAM)
                self.client_socket.settimeout(1)
                ver_send=f"ver_{value1}_{value2}"
                self.client_socket.sendto(str.encode(ver_send), address)
                rec_data, addr = self.client_socket.recvfrom(1024)
                if rec_data=="position_received".encode():
                    self.position_sent = QLabel(self.centralwidget)
                    self.position_sent.setText(_translate("MainWindow", "Set position"))
                    self.position_sent.setGeometry(QRect(1720, 810, 70, 40))
                        
                    font = QFont("Arial", 9, QFont.Bold)
                    self.position_sent.setFont(font)
                    self.position_sent.adjustSize()
                    self.position_sent.show()

                    # Fancy animation (responsivity only)
                    self.animation = QVariantAnimation()
                    self.animation.valueChanged.connect(self.change_opacity)
                    self.animation.setStartValue(255)
                    self.animation.setEndValue(0)
                    self.animation.setDuration(10000)
                    self.animation.setEasingCurve(QEasingCurve.InOutQuad)
                    self.animation.start()
            except:
                pass
    
    # Change opacity of the label related to the actuators (responsivity purpose only)
    def change_opacity(self, value):
        self.position_sent.setStyleSheet("color: rgba(0, 100, 255, {});".format(value))
        if value <30:
            self.position_sent.hide()

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

    # Link spinbox value to the slider one
    def sliderval(self,idd,value):
        self.spinboxes[idd].setValue(value)

    # Link slider value to the spinbox one
    def spinboxval(self,idd,value):
        self.sliders[idd].setValue(value)   

    # Update the label sensor value to see them IRT
    def update_str(self,values):
        _translate = QCoreApplication.translate
        
        # Store the wanted value
        val = [values[1],values[3],values[5],
                   values[8],values[9],values[10],
                   values[12],values[13],values[14],
                   values[15]]
        # Loop to print the value
        for widget, value in zip(self.sensors, val):
            # Indicate if no data has beeen received
            if value==None:
                widget.setText(_translate("MainWindow", "No data"))
                font = QFont("Arial", 5, QFont.Bold)
                widget.setFont(font)
            else:
                widget.setText(_translate("MainWindow", str(value)))
                font = QFont("Arial", 9, QFont.Bold)
                widget.setFont(font)
            widget.setStyleSheet("background-color: #dcdcdc")
            widget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            # Define color for the tank sensors
            self.sensors[0].setStyleSheet("background-color: rgb(218,232,252)")
            self.sensors[1].setStyleSheet("background-color: rgb(248,206,204)")
            self.sensors[3].setStyleSheet("background-color: rgb(255,230,204)")

    # Send a data to the arduino (called by many function)             IMPROVMENT : can be used for more functions (ex: control_actuator)
    def send_command(self,command):
        address = (self.adress, 5000)
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        self.client_socket.settimeout(1)
        self.client_socket.sendto(str.encode(command), address)
        rec_data, addr = self.client_socket.recvfrom(1024)
        return rec_data

    # Change the status of the valve if a button is clicked
    def update_valve_status(self,valve_label, status_text, color):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        valve_label.setText(_translate("MainWindow", status_text))
        color_effect = QGraphicsColorizeEffect()
        color_effect.setColor(color)
        valve_label.setGraphicsEffect(color_effect)
        valve_label.adjustSize()

    # Change the label if it receives a signal from the arduino
    def open_valve(self,valve_number, valve_label,valve_status):
        command = f"SV{valve_number}1"
        if self.arduino==0:
            self.update_valve_status(valve_label, "Open", Qt.darkGreen)
            self.update_valve_status(valve_status, "Open", Qt.darkGreen)
        else:
            try:
                rec_data = self.send_command(command)
                if rec_data == f"SV{valve_number}1_ok".encode():
                    self.update_valve_status(valve_label, "Open", Qt.darkGreen)
                    self.update_valve_status(valve_status, "Open", Qt.darkGreen)
            except:
                pass

    # Change the label if it receives a signal from the arduino
    def close_valve(self,valve_number, valve_label,valve_status):
        command = f"SV{valve_number}0"
        if self.arduino==0:
            self.update_valve_status(valve_label, "Closed", Qt.red)
            self.update_valve_status(valve_status, "Closed", Qt.red)
        else:
            try:
                rec_data = self.send_command(command)
                if rec_data == f"SV{valve_number}0_ok".encode():
                    self.update_valve_status(valve_label, "Closed", Qt.red)
                    self.update_valve_status(valve_status, "Closed", Qt.red)
            except:
                pass

    def launch_plot(self):
        self.second_window = MultiRealTimePlot()
        self.second_window.show()

# Not sure I understand the difference between both
####################################################################
    def load_json(self):
        with open("data.json", "r") as f:
            self.data_json = json.load(f)
            for key in self.data_json.keys():
                self.comboBox.addItem(key) 

    def update_json_text(self):
        key = self.comboBox.currentText()

####################################################################    
    
    # Display the selected test profil
    def view_json(self): 
        _translate = QCoreApplication.translate 
        
        if self.comboBox.currentText()=="---":
            self.title.setText(_translate("MainWindow",self.comboBox.currentText()))
        else:
            self.title.setText(_translate("MainWindow","<u>"+self.comboBox.currentText()+"</u>"))
        self.title.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.title.adjustSize()
        self.title.show()
        names=["Test duration : ",
        "LOX tank pressure : ",
        "ETH tank pressure : ",
        "H2O tank pressure : ",
        "TVC pattern : ",
        "Opening interval : "]
        units=[" s"," bar"," bar"," bar",""," ms"]
        json=[value for key, value in self.data_json[self.comboBox.currentText()].items()]
        for value,l,dim,name,unit in zip(json,self.label_preselect[7:],self.dim_preselect,names,units):
            x,y,w,h=dim
            l.setGeometry(QRect(x,y,w,h))
            l.setText(_translate("MainWindow",name + value + unit))
            l.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            font = QFont("Arial", 9)
            l.setFont(font)
            l.adjustSize()
            l.show()

    # Display the checklist
    def view_checklist(self):
        self.third_window = QWidget()
        self.third_window.setWindowTitle("Checklist")

        pixmap = QPixmap("image.png")

        image_label = QLabel()
        image_label.setPixmap(pixmap)

        # Create scroll area                                    
        scroll_area = QScrollArea()
        scroll_area.setWidget(image_label)

        # Check if image height is bigger than screen height
        screen_height = QApplication.desktop().screenGeometry().height()
        if pixmap.height() > screen_height:
            scroll_area.setVerticalScrollBarPolicy(1)

        layout = QVBoxLayout()
        layout.addWidget(scroll_area)
        self.third_window.setLayout(layout)

        # Resize window
        self.third_window.resize(pixmap.width() + 20, min(pixmap.height() + 20, screen_height))

        self.third_window.show()

    # Launch the countdown window (in CountdownWidget class)  
    # IMPROVMENT: add a verification?? (button doesn't work until all the checklist is done (actuator tested, valve open, ...))
    def launch_engine(self):
        self.fourth_window = CountdownWidget()
        self.fourth_window.show()

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
        self.timer.start(1000)  # Update every second

    # Pressure plot
    def RTP1(self):
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)

        self.fig1 = Figure(figsize=(18, 6))
        self.ax1 = self.fig1.add_subplot(111)
        self.canvas1 = FigureCanvas(self.fig1)
        layout.addWidget(self.canvas1)

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
        self.button_1m_1 = QPushButton("1m", self)
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
        self.button_1m_1.clicked.connect(lambda: self.set_x_interval1(60,1))
        controls_layout.addWidget(self.button_1m_1)

        # Last 10 min data
        self.button_10m_1 = QPushButton("10m", self)
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
        self.button_10m_1.clicked.connect(lambda: self.set_x_interval1(600,2))
        controls_layout.addWidget(self.button_10m_1)

        # Last 30 min data     
        self.button_30m_1 = QPushButton("30m", self)
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
        self.button_30m_1.clicked.connect(lambda: self.set_x_interval1(1800,3))
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
        # Define checkboxes to show specific curves                     IMPROVMENT: loop
        self.checkbox_1 = QCheckBox("PS11", self)
        for i in range(1):
        self.checkbox_1.setChecked(True)  # Default to show the first curve
        controls_layout.addWidget(self.checkbox_1)

        self.checkbox_2 = QCheckBox("PS12", self)
        controls_layout.addWidget(self.checkbox_2)

        self.checkbox_3 = QCheckBox("PS21", self)
        controls_layout.addWidget(self.checkbox_3)

        self.checkbox_4 = QCheckBox("PS22", self)
        controls_layout.addWidget(self.checkbox_4)

        self.checkbox_5 = QCheckBox("PS31", self)
        controls_layout.addWidget(self.checkbox_5)

        self.checkbox_6 = QCheckBox("PS41", self)
        controls_layout.addWidget(self.checkbox_6)

        self.checkbox_7 = QCheckBox("PS42", self)
        controls_layout.addWidget(self.checkbox_7)

        self.checkbox_8 = QCheckBox("PS61", self)
        controls_layout.addWidget(self.checkbox_8)

        self.checkbox_9 = QCheckBox("PS62", self)
        controls_layout.addWidget(self.checkbox_9)

        self.checkbox_10 = QCheckBox("PS63", self)
        controls_layout.addWidget(self.checkbox_10)
        checked_boxes = [self.checkbox_1, self.checkbox_2, self.checkbox_3, self.checkbox_4,self.checkbox_5,self.checkbox_6, self.checkbox_7,self.checkbox_8,self.checkbox_9,self.checkbox_10]

        # Responsivity (put the checbox in columns)
        rows = 4
        cols = 1
        for i, checkbox in enumerate(checked_boxes):
            row = rows + i % 5
            col = cols * (i // 5)
            controls_layout.addWidget(checkbox, row, col)

        controls_layout.addWidget(x_length_label, 0, 0)
        controls_layout.addWidget(curve_label, 3, 0)
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

        self.button_1m_2 = QPushButton("1m", self)
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
        self.button_1m_2.clicked.connect(lambda: self.set_x_interval2(60,1))
        controls_layout.addWidget(self.button_1m_2)
        
        self.button_10m_2 = QPushButton("10m", self)
        self.button_10m_2.clicked.connect(lambda: self.set_x_interval2(600,2))
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

        self.button_30m_2 = QPushButton("30m", self)
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
        self.button_30m_2.clicked.connect(lambda: self.set_x_interval2(1800,3))
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

        self.checkbox_11 = QCheckBox("TS11", self)
        self.checkbox_11.setChecked(True)
        controls_layout.addWidget(self.checkbox_11)

        self.checkbox_12 = QCheckBox("TS41", self)
        controls_layout.addWidget(self.checkbox_12)

        self.checkbox_13 = QCheckBox("TS42", self)
        controls_layout.addWidget(self.checkbox_13)

        self.checkbox_14 = QCheckBox("TS61", self)
        controls_layout.addWidget(self.checkbox_14)

        self.checkbox_15 = QCheckBox("TS62", self)
        controls_layout.addWidget(self.checkbox_15)

        controls_layout.addWidget(x_length_label, 0, 0)
        controls_layout.addWidget(curve_label, 3, 0)
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

        self.button_1m_3 = QPushButton("1m", self)
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
        self.button_1m_3.clicked.connect(lambda: self.set_x_interval3(60,1))
        controls_layout.addWidget(self.button_1m_3)

        self.button_10m_3 = QPushButton("10m", self)
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
        self.button_10m_3.clicked.connect(lambda: self.set_x_interval3(600,2))
        controls_layout.addWidget(self.button_10m_3)

        self.button_30m_3 = QPushButton("30m", self)
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
        self.button_30m_3.clicked.connect(lambda: self.set_x_interval3(1800,3))
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

        self.checkbox_16 = QCheckBox("FS11", self)
        self.checkbox_16.setChecked(True)
        controls_layout.addWidget(self.checkbox_16)

        controls_layout.addWidget(x_length_label, 0, 0)
        controls_layout.addWidget(curve_label, 3, 0)    # These labels are invisible but are used for responsivity
        controls_layout.addWidget(curve_label1, 5, 0)   
        controls_layout.addWidget(curve_label2, 6, 0)
        controls_layout.addWidget(curve_label3, 7, 0)
        controls_layout.addWidget(curve_label4, 8, 0)
        controls_layout.addWidget(curve_label5, 9, 0)
        controls_layout.addWidget(self.checkbox_16, 4, 0)
        controls_layout.addWidget(self.button_1m_3, 1, 0)
        controls_layout.addWidget(self.button_10m_3, 1, 1)
        controls_layout.addWidget(self.button_30m_3, 2, 0)
        controls_layout.addWidget(self.button_All_3, 2, 1)
        return central_widget

    def update_plot(self):
        t0 = time.perf_counter()
        # Read the data of the csv (second link with the worker) and stored them
        with open("data.csv", "r") as file:
            csv_reader = csv.reader(file)

            self.x_data = []
            self.y_data = []
             
            for row in csv_reader:
                self.x_data.append(float(row[0]))
                self.y_data.append([float(row[i]) for i in range(1, 17)])

        
        # Update RTP1 plot
        self.ax1.clear()
        # Check that checkbox is selected to display the plot (one color for each curves)
        if self.checkbox_1.isChecked():
            self.ax1.plot(self.x_data, [data[0] for data in self.y_data],color="blue", label="PS11")
            self.checkbox_1.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: blue; border: 2px solid blue; border-radius: 4px;}}")
        else:
            self.checkbox_1.setStyleSheet("")

        if self.checkbox_2.isChecked():
            self.ax1.plot(self.x_data, [data[1] for data in self.y_data],color="orange", label="PS12")
            self.checkbox_2.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: orange; border: 2px solid orange; border-radius: 4px;}}")
        else:
            self.checkbox_2.setStyleSheet("")

        if self.checkbox_3.isChecked():
            self.ax1.plot(self.x_data, [data[2] for data in self.y_data],color="green", label="PS21")
            self.checkbox_3.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: green; border: 2px solid green; border-radius: 4px;}}")
        else:
            self.checkbox_3.setStyleSheet("")

        if self.checkbox_4.isChecked():
            self.ax1.plot(self.x_data, [data[3] for data in self.y_data],color="red", label="PS22")
            self.checkbox_4.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: red; border: 2px solid red; border-radius: 4px;}}")
        else:
            self.checkbox_4.setStyleSheet("")

        if self.checkbox_5.isChecked():
            self.ax1.plot(self.x_data, [data[4] for data in self.y_data],color="purple", label="PS31")
            self.checkbox_5.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: purple; border: 2px solid purple; border-radius: 4px;}}")
        else:
            self.checkbox_5.setStyleSheet("")

        if self.checkbox_6.isChecked():
            self.ax1.plot(self.x_data, [data[5] for data in self.y_data],color="brown", label="PS41")
            self.checkbox_6.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: brown; border: 2px solid brown; border-radius: 4px;}}")
        else:
            self.checkbox_6.setStyleSheet("")

        if self.checkbox_7.isChecked():
            self.ax1.plot(self.x_data, [data[6] for data in self.y_data],color="pink", label="PS42")
            self.checkbox_7.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: pink; border: 2px solid pink; border-radius: 4px;}}")
        else:
            self.checkbox_7.setStyleSheet("")

        if self.checkbox_8.isChecked():
            self.ax1.plot(self.x_data, [data[7] for data in self.y_data],color="olive", label="PS61")
            self.checkbox_8.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: olive; border: 2px solid olive; border-radius: 4px;}}")
        else:
            self.checkbox_8.setStyleSheet("")

        if self.checkbox_9.isChecked():
            self.ax1.plot(self.x_data, [data[8] for data in self.y_data],color="grey", label="PS62")
            self.checkbox_9.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: grey; border: 2px solid grey; border-radius: 4px;}}")
        else:
            self.checkbox_9.setStyleSheet("")

        if self.checkbox_10.isChecked():
            self.ax1.plot(self.x_data, [data[9] for data in self.y_data],color="cyan", label="PS63")
            self.checkbox_10.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: cyan; border: 2px solid cyan; border-radius: 4px;}}")
        else:
            self.checkbox_10.setStyleSheet("")
        
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
        if self.checkbox_11.isChecked():
            self.ax2.plot(self.x_data, [data[10] for data in self.y_data],color="blue", label="TS11")
            self.checkbox_11.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: blue; border: 2px solid blue; border-radius: 4px;}}")
        else:
            self.checkbox_11.setStyleSheet("")

        if self.checkbox_12.isChecked():
            self.ax2.plot(self.x_data, [data[11] for data in self.y_data],color="orange", label="TS41")
            self.checkbox_12.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: orange; border: 2px solid orange; border-radius: 4px;}}")
        else:
            self.checkbox_12.setStyleSheet("")

        if self.checkbox_13.isChecked():
            self.ax2.plot(self.x_data, [data[12] for data in self.y_data],color="green", label="TS42")
            self.checkbox_13.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: green; border: 2px solid green; border-radius: 4px;}}")
        else:
            self.checkbox_13.setStyleSheet("")

        if self.checkbox_14.isChecked():
            self.ax2.plot(self.x_data, [data[13] for data in self.y_data],color="red", label="TS61")
            self.checkbox_14.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: red; border: 2px solid red; border-radius: 4px;}}")
        else:
            self.checkbox_14.setStyleSheet("")

        if self.checkbox_15.isChecked():
            self.ax2.plot(self.x_data, [data[14] for data in self.y_data],color="purple", label="TS62")
            self.checkbox_15.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: purple; border: 2px solid purple; border-radius: 4px;}}")
        else:
            self.checkbox_15.setStyleSheet("")
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
        if self.checkbox_16.isChecked():
            self.ax3.plot(self.x_data, [data[15] for data in self.y_data],color='blue', label="FS11")
            self.checkbox_16.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: blue; border: 2px solid blue; border-radius: 4px;}}")
        else:
            self.checkbox_16.setStyleSheet("")
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
        
        t1 = time.perf_counter()
        # Calculate the time taken for the update process
        update_time = (t1 - t0) * 1000
        # Adjust the timer to ensure a delay of one second between updates
        self.timer.start(max(0, int(1000 - update_time)))  # Delay is at least one second

    # Modify the x scale of the pressure plot                                   IMPROVMENT : one set_x_interval instead of three?? use id?
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
        self.count_sec = 10
        self.count_msec = 0
        self.countdown_display.setFixedSize(300, 100)  # Adjusted the size of the display
        self.countdown_display.display(f"{self.count_sec:02d}:{self.count_msec:02d}")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    
    sys.exit(app.exec_())


