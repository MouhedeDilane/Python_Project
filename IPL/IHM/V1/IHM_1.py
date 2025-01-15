"""
Human-Machine Interface for 1kN rocket engine project

Creator : Mehdi Delouane

"""
import sys
import random
from socket import *
import csv

from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
from PyQt5.Qt import QPainter, QPen

import time
import threading
import functools
import json

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# This class collects data sent y the Arduino. Acts also as a synchronizer the IRT plot
class Worker(QObject):
    update_signal = pyqtSignal(list)
    def __init__(self):
        super().__init__()

    def generate_random_values(self):
        i=0
        while True:
            # Generate random values and append them to the list
            values = [i]+[int(10000*random.random()) for _ in range(16)]  # Adjust range as needed
            self.update_signal.emit(values)
            # Sleep for a while before generating next set of values
            # You can adjust the sleep duration as needed
            with open('random_data.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(values)     
            i+=1
            time.sleep(1)

# Main class of the program
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        # Set the main window and its size
        MainWindow.resize(1922, 1237)
        self.centralwidget = QWidget(MainWindow)

        # Set the background of the main window with the P&ID and a grey background
        self.background = QLabel(self.centralwidget)
        self.background.setGeometry(QRect(30, -40, 2000, 1080))
        self.background.setPixmap(QPixmap("PID_IHM.png"))
        self.frame1 = QFrame(self.centralwidget)
        self.frame1.setGeometry(QRect(-31, -91, 1891, 1231))
        self.frame1.setAutoFillBackground(True)
        self.frame1.setFrameShape(QFrame.StyledPanel)
        self.frame1.setFrameShadow(QFrame.Raised)

        # Set the IPL logo
        self.logo = QLabel(self.centralwidget)
        self.logo.setGeometry(QRect(1620, 50, 500, 100))
        self.logo.setPixmap(QPixmap("logo.png"))
        self.table = QLabel(self.centralwidget)
        self.table.setGeometry(QRect(1250, 500, 271, 381))
        self.table.setPixmap(QPixmap("table.png"))

        self.frame1.raise_()
        self.background.raise_()
        self.logo.raise_()
        self.table.raise_()

        self.frames = [QFrame(self.centralwidget) for _ in range(12)]
        self.dims_frame=[(600, 620, 111, 91),(770, 540, 111, 91),(600, 70, 111, 91),
              (770, 190, 111, 91),(160, 470, 111, 91),(300, 190, 111, 91),
              (300, 530, 111, 91),(980, 90, 111, 91),(980, 630, 111, 91),
              (330, 780, 111, 91),(560, 740, 111, 91),(720, 770, 111, 91)
              ]
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
        self.status=[QLabel(self.centralwidget) for _ in range(12)]
        self.labels=[QLabel(self.centralwidget) for _ in range(12)]
        self.ouverts=[QPushButton(self.centralwidget) for _ in range(12)]
        self.fermes=[QPushButton(self.centralwidget) for _ in range(12)]
        self.ids=[QLabel(self.centralwidget) for _ in range(12)]
        
        self.names=['SV11','SV12','SV21',
               'SV22','SV31','SV32',
               'SV33','SV34','SV35',
               'SV51','SV61','SV62']
        self.nums=[11,12,21,
               22,31,32,
               33,34,35,
               51,61,62]
        self.dims_status=[(620, 630, 111, 16),(790, 550, 111, 16),(620, 80, 111, 16),
                          (790, 200, 111, 16),(180, 480, 111, 16),(320, 200, 111, 16),
                          (320, 540, 111, 16),(1000, 100, 111, 16),(1000, 640, 111, 16),
                          (350, 790, 111, 16),(580, 750, 111, 16),(740, 780, 111, 16)]
        self.dims_label=[(640, 650, 55, 16),(810, 570, 55, 16),(640, 100, 55, 16),
                         (810, 220, 55, 16),(200, 500, 55, 16),(340, 220, 55, 16),
                         (340, 560, 55, 16),(1020, 120, 55, 16),(1020, 660, 55, 16),
                         (370, 810, 55, 16),(600, 770, 55, 16),(760, 800, 55, 16)]    
        self.dims_ouvert=[(610, 670, 41, 28),(780, 590, 41, 28),(610, 120, 41, 28),
                          (780, 240, 41, 28),(170, 520, 41, 28),(310, 240, 41, 28),
                          (310, 580, 41, 28),(990, 140, 41, 28),(990, 680, 41, 28),
                          (340, 830, 41, 28),(570, 790, 41, 28),(730, 820, 41, 28)]       
        self.dims_ferme=[(660, 670, 41, 28),(830, 590, 41, 28),(660, 120, 41, 28),
                         (830, 240, 41, 28),(220, 520, 41, 28),(360, 240, 41, 28),
                         (360, 580, 41, 28),(1040, 140, 41, 28),(1040, 680, 41, 28),
                         (390, 830, 41, 28),(620, 790, 41, 28),(780, 820, 41, 28)]
        self.dims_idd=[(1428, 567, 55, 16),(1428, 591, 55, 16),(1428, 613, 55, 16),
                        (1428, 636, 55, 16),(1428, 660, 55, 16),(1428, 682, 55, 16),
                        (1428, 705, 55, 16),(1428, 728, 55, 16),(1428, 752, 55, 16),
                        (1428, 774, 55, 16),(1428, 797, 55, 16),(1428, 820, 55, 16)]
        for widget,label,ouvert,ferme,idd,dim_status,dim_label,dim_ouvert,dim_ferme,dim_idd in zip(self.status,self.labels,self.ouverts,self.fermes,self.ids,self.dims_status,self.dims_label,self.dims_ouvert,self.dims_ferme,self.dims_idd):
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
            font = QFont("Arial", 8, QFont.Bold)
            widget.setFont(font)
            label.setFont(font)
            font = QFont("Arial", 7, QFont.Bold)
            ouvert.setFont(font)
            ferme.setFont(font)
            widget.raise_()
            label.raise_()
            ouvert.raise_()
            ferme.raise_()      
            idd.raise_()  
        
        self.sliders=[QSlider(self.centralwidget) for _ in range(2)]
        self.dims_slider=[(1644, 703, 22, 160),(1844, 703, 22, 160)]
        self.spinboxes=[QSpinBox(self.centralwidget) for _ in range(2)]
        self.dims_spinbox=[(1635, 673, 42, 22),(1835, 673, 42, 22)]
        
        self.frames2 = [QFrame(self.centralwidget) for _ in range(5)]
        self.dims_frame2=[(1575, 200, 336, 1000),(1575, 603, 184, 280),(1756, 603, 184, 280),(1575, 603, 336, 383),(1575, 880, 336, 102)]
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
        self.frames2[1].setStyleSheet("QFrame, QLabel, QToolTip {\n"
            "    background-color: rgba(0, 0, 0, 0);\n"
            "    border: 3px dashed grey;\n"
            "    border-radius: 1px;\n"
            "    padding: 2px;\n"
            "}")
        self.frames2[2].setStyleSheet("QFrame, QLabel, QToolTip {\n"
            "    background-color: rgba(0, 0, 0, 0);\n"
            "    border: 3px dashed grey;\n"
            "    border-radius: 1px;\n"
            "    padding: 2px;\n"
            "}")

        self.labs=[QLabel(self.centralwidget) for _ in range(2)]
        self.dims_lab=[(1620, 653, 60, 16),(1820, 653, 60, 16)]
        self.actuator_name=["Actuator L","Actuator R"]
        for slider,dim_slider,spinbox,dim_spinbox,lab,dim_lab in zip(self.sliders,self.dims_slider,self.spinboxes,self.dims_spinbox,self.labs,self.dims_lab):
            x,y,h,w,= dim_slider
            slider.setGeometry(QRect(x,y,h,w))
            slider.setOrientation(Qt.Vertical)
            slider.setMinimum(0)
            slider.setValue(50)
            slider.setMaximum(101)       
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

            x,y,h,w,= dim_spinbox
            spinbox.setGeometry(QRect(x,y,h,w))
            spinbox.setMinimum(0)
            spinbox.setValue(50)
            spinbox.setMaximum(100)
            idd=self.spinboxes.index(spinbox)
            spinbox.valueChanged.connect(functools.partial(self.spinboxval,idd))
            spinbox.raise_()

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

        self.sensors = [QLabel(self.centralwidget) for _ in range(10)]
        self.dims_sensor=[(503, 485, 37, 21),(503, 323, 37, 21),(209, 272, 37, 21),
                          (486, 900, 37, 21),(926, 945, 37, 21),(1043, 945, 37, 21),          
                          (1084, 280, 37, 21),(1186, 280, 37, 21),(926, 840, 37, 21),
                          (1043, 840, 37, 21)]
        for sensor,dim in zip(self.sensors,self.dims_sensor):
            x,y,h,w=dim
            sensor.setGeometry(QRect(x,y,h,w))
            sensor.raise_()
        
        self.lplot.raise_()
        self.actuator.raise_()
        self.close_all.raise_()

        
        self.comboBox = QComboBox(self.centralwidget)
        self.load_json()
        self.comboBox.setGeometry(QRect(1590,230,200,25))
        self.comboBox.currentIndexChanged.connect(self.update_json_text)
        self.comboBox.raise_()

        self.viewButton = QPushButton("View selection",self.centralwidget)
        self.viewButton.setGeometry(QRect(1800,228,100,30))
        self.viewButton.adjustSize()
        self.viewButton.clicked.connect(self.view_json)
        self.viewButton.raise_()
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setWindowFlags(MainWindow.windowFlags() & ~Qt.WindowCloseButtonHint)
        MainWindow.setStyleSheet("background-color: rgb(236,236,236)")

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate

        self.adress='192.168.0.101'

        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        for widget,label,name,ouvert,ferme,idd,num in zip(self.status,self.labels,self.names,self.ouverts,self.fermes,self.ids,self.nums):
            if widget==self.status[0] or widget==self.status[2]:
                widget.setText(_translate("MainWindow", "<u>"+name+" status:</u>"))
                widget.adjustSize()
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
                label.adjustSize()
                color_effect = QGraphicsColorizeEffect()
                color_effect.setColor(Qt.darkGreen)
                idd.setText(_translate("MainWindow", "Open"))
                font = QFont("Arial", 8, QFont.Bold)
                idd.setFont(font)
                idd.setGraphicsEffect(color_effect)
                idd.adjustSize()
            else:
                widget.setText(_translate("MainWindow", "<u>"+name+" status:</u>"))
                widget.setStyleSheet("QFrame, QLabel, QToolTip {\n"
                "    background-color: rgb(230, 230, 230);\n"
                "}")
                widget.adjustSize()             
                color_effect = QGraphicsColorizeEffect()
                color_effect.setColor(Qt.red)
                label.setText(_translate("MainWindow", "Closed"))
                label.setStyleSheet("QFrame, QLabel, QToolTip {\n"
                "    background-color: rgb(230, 230, 230);\n"
                "}")
                label.setGraphicsEffect(color_effect)
                label.adjustSize()
                color_effect = QGraphicsColorizeEffect()
                color_effect.setColor(Qt.red)
                idd.setText(_translate("MainWindow", "Closed"))
                idd.setGraphicsEffect(color_effect)
                font = QFont("Arial", 8, QFont.Bold)
                idd.setFont(font)
                idd.adjustSize()
                
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
            ferme.setText(_translate("MainWindow", "Close"))
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
            
            ouvert.clicked.connect(functools.partial(self.open_valve, num, label, idd))
            ferme.clicked.connect(functools.partial(self.close_valve, num, label, idd))
        for lab, act in zip(self.labs,self.actuator_name):
            lab.setText(_translate("MainWindow", "<u>"+act+"</u>"))
            lab.adjustSize()

        self.lplot.setText(_translate("MainWindow", "Launch Plot"))
        font = QFont("Arial", 9, QFont.Bold)
        self.lplot.setFont(font)

        self.actuator.setText(_translate("MainWindow", "actuator"))

        self.close_all.setText(_translate("MainWindow", "End program"))
        font = QFont("Arial", 9, QFont.Bold)
        self.close_all.setFont(font)
        self.lplot.clicked.connect(self.launch_plot)
        self.close_all.clicked.connect(self.close_all_program)

        
        self.actuator.clicked.connect(lambda : self.control_actuator(self.spinboxes[0].value(),self.spinboxes[1].value()))

        self.worker = Worker()
        self.worker_thread = threading.Thread(target=self.worker.generate_random_values)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        self.worker.update_signal.connect(self.update_str)

    def control_actuator(self,value1,value2):
        try:
            address = (self.adress, 5000)
            self.client_socket = socket(AF_INET, SOCK_DGRAM)
            self.client_socket.settimeout(1)
            ver_send=f"ver_{value1}_{value2}"
            self.client_socket.sendto(str.encode(ver_send), address)
            print(value1,value2)
        except:
            pass

    def close_all_program(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        reply = msgBox.warning(MainWindow, "Warning", 
            "Are you sure to quit?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            print("\n\n\nYou closed the program.\nDid it work bitch (ง'-̀'́)ง  Ϟ  ฝ('-'ฝ)\n\n\n")
            QCoreApplication.quit()

    def sliderval(self,idd,value):
        self.spinboxes[idd].setValue(value)

    def spinboxval(self,idd,value):
        self.sliders[idd].setValue(value)   

    def update_str(self,values):
        _translate = QCoreApplication.translate
        
        val = [values[1],values[3],values[5],
                   values[8],values[9],values[10],
                   values[12],values[13],values[14],
                   values[15]]
        for widget, value in zip(self.sensors, val):
            widget.setText(_translate("MainWindow", str(value)))
            font = QFont("Arial", 9, QFont.Bold)
            widget.setFont(font)
            widget.setStyleSheet("background-color: #dcdcdc")
            widget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.sensors[0].setStyleSheet("background-color: #d2d2fa")
        self.sensors[1].setStyleSheet("background-color: #f8b4b4")
        self.sensors[3].setStyleSheet("background-color: #ffe682")
    
    def send_command(self,command):
        address = (self.adress, 5000)  # Define who you are talking to (must match Arduino IP and port)
        self.client_socket = socket(AF_INET, SOCK_DGRAM)  # Set up the socket
        self.client_socket.settimeout(1)
        self.client_socket.sendto(str.encode(command), address)  # Send command to Arduino
        rec_data, addr = self.client_socket.recvfrom(1024)
        return rec_data

    def update_valve_status(self,valve_label, status_text, color):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        valve_label.setText(_translate("MainWindow", status_text))
        color_effect = QGraphicsColorizeEffect()
        color_effect.setColor(color)
        valve_label.setGraphicsEffect(color_effect)

    def open_valve(self,valve_number, valve_label,valve_status):
        command = f"SV{valve_number}1"
        try:
            rec_data = self.send_command(command)
            if rec_data == f"SV{valve_number}1_ok".encode():
                self.update_valve_status(valve_label, "Open", Qt.darkGreen)
                self.update_valve_status(valve_status, "Open", Qt.darkGreen)
        except:
            pass

    def close_valve(self,valve_number, valve_label,valve_status):
        command = f"SV{valve_number}0"
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

    def load_json(self):
        with open("data.json", "r") as f:
            self.data = json.load(f)
            for key in self.data.keys():
                self.comboBox.addItem(key) 

    def update_json_text(self):
        key = self.comboBox.currentText()
    
    def view_json(self):                # Arrangement et Bouton de validation
        dialog = QDialog(MainWindow)
        dialog.setWindowTitle("JSON Parameters")
        dialog.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout(dialog)
        key = self.comboBox.currentText()
        json_string = json.dumps(self.data[key], indent=4)
        jsonText = QTextEdit()
        jsonText.setPlainText(json_string)
        layout.addWidget(jsonText)

        dialog.exec_()

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
        self.x_axis_interval1 = 10  # Default x-axis interval
        self.x_axis_interval2 = 10  # Default x-axis interval
        self.x_axis_interval3 = 10  # Default x-axis interval
        for plot in self.real_time_plots:
            layout.addWidget(plot)

        # Start the timer to update the plots
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1000)  # Update every second

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

        # Layout for x-axis interval and curves controls
        controls_layout = QGridLayout(controls_frame)

        x_length_label = QLabel("Time Interval:", self)
        controls_layout.addWidget(x_length_label)

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

        self.checkbox_1 = QCheckBox("PS11", self)
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

    def RTP2(self):
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)

        self.fig2 = Figure(figsize=(18, 6))
        self.ax2 = self.fig2.add_subplot(111)
        self.canvas2 = FigureCanvas(self.fig2)
        layout.addWidget(self.canvas2)

        # Create a frame for x-axis interval and curves controls
        controls_frame = QFrame(self)
        controls_frame.setFrameShape(QFrame.StyledPanel)
        layout.addWidget(controls_frame)
        controls_frame.setFixedWidth(200)

        # Layout for x-axis interval and curves controls
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
        self.checkbox_11.setChecked(True)  # Default to show the first curve
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

    def RTP3(self):
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)

        self.fig3 = Figure(figsize=(18, 6))
        self.ax3 = self.fig3.add_subplot(111)
        self.canvas3 = FigureCanvas(self.fig3)
        layout.addWidget(self.canvas3)

        # Create a frame for x-axis interval and curves controls
        controls_frame = QFrame(self)
        controls_frame.setFrameShape(QFrame.StyledPanel)
        layout.addWidget(controls_frame)
        controls_frame.setFixedWidth(200)

        # Layout for x-axis interval and curves controls
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
        self.checkbox_16.setChecked(True)  # Default to show the first curve
        controls_layout.addWidget(self.checkbox_16)

        controls_layout.addWidget(x_length_label, 0, 0)
        controls_layout.addWidget(curve_label, 3, 0)
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
        with open("random_data.csv", "r") as file:
            # Create a CSV reader object
            csv_reader = csv.reader(file)

            # Initialize empty lists to store the selected indexes
            self.x_data = []
            self.y_data = []
            # Iterate over each row in the CSV file
            for row in csv_reader:
                self.x_data.append(float(row[0]))
                self.y_data.append([float(row[i]) for i in range(1, 17)])

        # Update RTP1 plot
        self.ax1.clear()
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
        self.ax1.grid()
        # Adjust x-axis limits
        if self.x_axis_interval1==-1:
            self.ax1.set_xlim(0, max(self.x_data))
        else:
            self.ax1.set_xlim(max(0,max(self.x_data) - self.x_axis_interval1), max(self.x_data))
        self.canvas1.draw()

        # Update RTP2 plot
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
        self.ax2.grid()
        # Adjust x-axis limits
        if self.x_axis_interval2==-1:
            self.ax2.set_xlim(0, max(self.x_data))
        else:
            self.ax2.set_xlim(max(0,max(self.x_data) - self.x_axis_interval2), max(self.x_data))
        self.canvas2.draw()

        # Update RTP3 plot
        self.ax3.clear()
        if self.checkbox_16.isChecked():
            self.ax3.plot(self.x_data, [data[15] for data in self.y_data],color='blue', label="FS11")
            self.checkbox_16.setStyleSheet(f"QCheckBox::indicator:checked {{background-color: blue; border: 2px solid blue; border-radius: 4px;}}")
        else:
            self.checkbox_16.setStyleSheet("")
        self.ax3.grid()
        # Adjust x-axis limits
        if self.x_axis_interval3==-1:
            self.ax3.set_xlim(0, max(self.x_data))
        else:
            self.ax3.set_xlim(max(0,max(self.x_data) - self.x_axis_interval3), max(self.x_data))
        self.canvas3.draw()
        t1 = time.perf_counter()
        # Calculate the time taken for the update process
        update_time = (t1 - t0) * 1000  # Convert to milliseconds
        # Adjust the timer to ensure a delay of one second between updates
        self.timer.start(max(0, int(1000 - update_time)))  # Delay is at least one second

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    
    sys.exit(app.exec_())
