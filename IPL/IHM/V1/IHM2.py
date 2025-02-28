"""
Human-Machine Interface for 1kN rocket engine project

Creator : Mehdi Delouane

"""
import sys
import random
from socket import *
import csv

from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *

import time
import threading

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

# This class collects data sent y the Arduino. Acts also as a synchronizer the IRT plot
class Worker(QObject):
    update_signal = pyqtSignal(list)
    def __init__(self):
        super().__init__()

    def generate_random_values(self):
        i=0
        while True:
            # Generate random values and append them to the list
            values = [i]+[round(random.random(),2) for _ in range(15)]  # Adjust range as needed
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
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1922, 1237)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Set the background of the main window with the P&ID and a grey background
        self.background = QLabel(self.centralwidget)
        self.background.setGeometry(QRect(30, -40, 2000, 1080))
        self.background.setText("")
        self.background.setPixmap(QtGui.QPixmap("PID_IHM.png"))
        self.background.setObjectName("background")
        self.frame_13 = QFrame(self.centralwidget)
        self.frame_13.setGeometry(QRect(-31, -91, 1891, 1231))
        self.frame_13.setAutoFillBackground(True)
        self.frame_13.setFrameShape(QFrame.StyledPanel)
        self.frame_13.setFrameShadow(QFrame.Raised)
        self.frame_13.setObjectName("frame_13")

        # Set the IPL logo
        self.logo = QLabel(self.centralwidget)
        self.logo.setGeometry(QRect(1638, 23, 500, 100))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap("logo.png"))
        self.logo.setObjectName("logo")
        
        # Define the status table image (table to sum up all the status)
        self.table = QLabel(self.centralwidget)
        self.table.setGeometry(QRect(1250, 500, 271, 381))
        self.table.setText("")
        self.table.setPixmap(QtGui.QPixmap("table.png"))
        self.table.setObjectName("table")
        
        # Define all the objects linked to SV11
        self.status_SV11 = QLabel(self.centralwidget)
        self.status_SV11.setGeometry(QRect(620, 630, 111, 16))
        self.status_SV11.setObjectName("status_SV11")
        self.label_SV11 = QLabel(self.centralwidget)
        self.label_SV11.setGeometry(QRect(640, 650, 55, 16))
        self.label_SV11.setObjectName("label_SV11")
        self.open_SV11 = QPushButton(self.centralwidget)
        self.open_SV11.setGeometry(QRect(610, 670, 41, 28))
        self.open_SV11.setObjectName("open_SV11")
        self.closed_SV11 = QPushButton(self.centralwidget)
        self.closed_SV11.setGeometry(QRect(660, 670, 41, 28))
        self.closed_SV11.setObjectName("closed_SV11")
        
        # Define all the objects linked to SV12
        self.label_SV12 = QLabel(self.centralwidget)
        self.label_SV12.setGeometry(QRect(810, 570, 55, 16))
        self.label_SV12.setObjectName("label_SV12")
        self.status_SV12 = QLabel(self.centralwidget)
        self.status_SV12.setGeometry(QRect(790, 550, 111, 16))
        self.status_SV12.setObjectName("status_SV12")
        self.closed_SV12 = QPushButton(self.centralwidget)
        self.closed_SV12.setGeometry(QRect(830, 590, 41, 28))
        self.closed_SV12.setObjectName("closed_SV12")
        self.open_SV12 = QPushButton(self.centralwidget)
        self.open_SV12.setGeometry(QRect(780, 590, 41, 28))
        self.open_SV12.setObjectName("open_SV12")
        
        # Define all the objects linked to SV21
        self.label_SV21 = QLabel(self.centralwidget)
        self.label_SV21.setGeometry(QRect(640, 100, 55, 16))
        self.label_SV21.setObjectName("label_SV21")
        self.status_SV21 = QLabel(self.centralwidget)
        self.status_SV21.setGeometry(QRect(620, 80, 111, 16))
        self.status_SV21.setObjectName("status_SV21")
        self.closed_SV21 = QPushButton(self.centralwidget)
        self.closed_SV21.setGeometry(QRect(660, 120, 41, 28))
        self.closed_SV21.setObjectName("closed_SV21")
        self.open_SV21 = QPushButton(self.centralwidget)
        self.open_SV21.setGeometry(QRect(610, 120, 41, 28))
        self.open_SV21.setObjectName("open_SV21")
        
        # Define all the objects linked to SV22
        self.label_SV22 = QLabel(self.centralwidget)
        self.label_SV22.setGeometry(QRect(810, 220, 55, 16))
        self.label_SV22.setObjectName("label_SV22")
        self.status_SV22 = QLabel(self.centralwidget)
        self.status_SV22.setGeometry(QRect(790, 200, 111, 16))
        self.status_SV22.setObjectName("status_SV22")
        self.closed_SV22 = QPushButton(self.centralwidget)
        self.closed_SV22.setGeometry(QRect(830, 240, 41, 28))
        self.closed_SV22.setObjectName("closed_SV22")
        self.open_SV22 = QPushButton(self.centralwidget)
        self.open_SV22.setGeometry(QRect(780, 240, 41, 28))
        self.open_SV22.setObjectName("open_SV22")

        # Define all the objects linked to SV31
        self.label_SV31 = QLabel(self.centralwidget)
        self.label_SV31.setGeometry(QRect(200, 500, 55, 16))
        self.label_SV31.setObjectName("label_SV31")
        self.status_SV31 = QLabel(self.centralwidget)
        self.status_SV31.setGeometry(QRect(180, 480, 111, 16))
        self.status_SV31.setObjectName("status_SV31")
        self.closed_SV31 = QPushButton(self.centralwidget)
        self.closed_SV31.setGeometry(QRect(220, 520, 41, 28))
        self.closed_SV31.setObjectName("closed_SV31")
        self.open_SV31 = QPushButton(self.centralwidget)
        self.open_SV31.setGeometry(QRect(170, 520, 41, 28))
        self.open_SV31.setObjectName("open_SV31")
        
        # Define all the objects linked to SV32
        self.label_SV32 = QLabel(self.centralwidget)
        self.label_SV32.setGeometry(QRect(340, 220, 55, 16))
        self.label_SV32.setObjectName("label_SV32")
        self.status_SV32 = QLabel(self.centralwidget)
        self.status_SV32.setGeometry(QRect(320, 200, 111, 16))
        self.status_SV32.setObjectName("status_SV32")
        self.closed_SV32 = QPushButton(self.centralwidget)
        self.closed_SV32.setGeometry(QRect(360, 240, 41, 28))
        self.closed_SV32.setObjectName("closed_SV32")
        self.open_SV32 = QPushButton(self.centralwidget)
        self.open_SV32.setGeometry(QRect(310, 240, 41, 28))
        self.open_SV32.setObjectName("open_SV32")

        # Define all the objects linked to SV33
        self.label_SV33 = QLabel(self.centralwidget)
        self.label_SV33.setGeometry(QRect(340, 560, 55, 16))
        self.label_SV33.setObjectName("label_SV33")
        self.status_SV33 = QLabel(self.centralwidget)
        self.status_SV33.setGeometry(QRect(320, 540, 111, 16))
        self.status_SV33.setObjectName("status_SV33")
        self.closed_SV33 = QPushButton(self.centralwidget)
        self.closed_SV33.setGeometry(QRect(360, 580, 41, 28))
        self.closed_SV33.setObjectName("closed_SV33")
        self.open_SV33 = QPushButton(self.centralwidget)
        self.open_SV33.setGeometry(QRect(310, 580, 41, 28))
        self.open_SV33.setObjectName("open_SV33")

        # Define all the objects linked to SV34
        self.label_SV34 = QLabel(self.centralwidget)
        self.label_SV34.setGeometry(QRect(1020, 120, 55, 16))
        self.label_SV34.setObjectName("label_SV34")
        self.status_SV34 = QLabel(self.centralwidget)
        self.status_SV34.setGeometry(QRect(1000, 100, 111, 16))
        self.status_SV34.setObjectName("status_SV34")
        self.closed_SV34 = QPushButton(self.centralwidget)
        self.closed_SV34.setGeometry(QRect(1040, 140, 41, 28))
        self.closed_SV34.setObjectName("closed_SV34")
        self.open_SV34 = QPushButton(self.centralwidget)
        self.open_SV34.setGeometry(QRect(990, 140, 41, 28))
        self.open_SV34.setObjectName("open_SV34")
        
        # Define all the objects linked to SV35
        self.label_SV35 = QLabel(self.centralwidget)
        self.label_SV35.setGeometry(QRect(1020, 660, 55, 16))
        self.label_SV35.setObjectName("label_SV35")
        self.status_SV35 = QLabel(self.centralwidget)
        self.status_SV35.setGeometry(QRect(1000, 640, 111, 16))
        self.status_SV35.setObjectName("status_SV35")
        self.closed_SV35 = QPushButton(self.centralwidget)
        self.closed_SV35.setGeometry(QRect(1040, 680, 41, 28))
        self.closed_SV35.setObjectName("closed_SV35")
        self.open_SV35 = QPushButton(self.centralwidget)
        self.open_SV35.setGeometry(QRect(990, 680, 41, 28))
        self.open_SV35.setObjectName("open_SV35")

        # Define all the objects linked to SV51
        self.label_SV51 = QLabel(self.centralwidget)
        self.label_SV51.setGeometry(QRect(370, 810, 55, 16))
        self.label_SV51.setObjectName("label_SV51")
        self.status_SV51 = QLabel(self.centralwidget)
        self.status_SV51.setGeometry(QRect(350, 790, 111, 16))
        self.status_SV51.setObjectName("status_SV51")
        self.closed_SV51 = QPushButton(self.centralwidget)
        self.closed_SV51.setGeometry(QRect(390, 830, 41, 28))
        self.closed_SV51.setObjectName("closed_SV51")
        self.open_SV51 = QPushButton(self.centralwidget)
        self.open_SV51.setGeometry(QRect(340, 830, 41, 28))
        self.open_SV51.setObjectName("open_SV51")

        # Define all the objects linked to SV61
        self.label_SV61 = QLabel(self.centralwidget)
        self.label_SV61.setGeometry(QRect(600, 770, 55, 16))
        self.label_SV61.setObjectName("label_SV61")
        self.closed_SV61 = QPushButton(self.centralwidget)
        self.closed_SV61.setGeometry(QRect(620, 790, 41, 28))
        self.closed_SV61.setObjectName("closed_SV61")
        self.open_SV61 = QPushButton(self.centralwidget)
        self.open_SV61.setGeometry(QRect(570, 790, 41, 28))
        self.open_SV61.setObjectName("open_SV61")
        self.status_SV61 = QLabel(self.centralwidget)
        self.status_SV61.setGeometry(QRect(580, 750, 111, 16))
        self.status_SV61.setObjectName("status_SV61")

        # Define all the objects linked to SV62
        self.label_SV62 = QLabel(self.centralwidget)
        self.label_SV62.setGeometry(QRect(760, 800, 55, 16))
        self.label_SV62.setObjectName("label_SV62")
        self.status_SV62 = QLabel(self.centralwidget)
        self.status_SV62.setGeometry(QRect(740, 780, 111, 16))
        self.status_SV62.setObjectName("status_SV62")
        self.closed_SV62 = QPushButton(self.centralwidget)
        self.closed_SV62.setGeometry(QRect(780, 820, 41, 28))
        self.closed_SV62.setObjectName("closed_SV62")
        self.open_SV62 = QPushButton(self.centralwidget)
        self.open_SV62.setGeometry(QRect(730, 820, 41, 28))
        self.open_SV62.setObjectName("open_SV62")
        
        
        # Define the left and right sliders of the actuator (and their labels)
        self.verticalSliderL = QSlider(self.centralwidget)
        self.verticalSliderL.setObjectName(u"verticalSliderL")
        self.verticalSliderL.setGeometry(QRect(1670, 650, 22, 160))
        self.verticalSliderL.setOrientation(Qt.Vertical)
        self.verticalSliderL.setMinimum(0)
        self.verticalSliderL.setMaximum(101)
        self.verticalSliderL.setStyleSheet(
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
        self.label_slider_left = QLabel(self.centralwidget)
        self.label_slider_left.setGeometry(QRect(1660, 600, 55, 16))
        self.label_slider_left.setObjectName("label_slider_left")

        self.verticalSliderR = QSlider(self.centralwidget)
        self.verticalSliderR.setObjectName(u"verticalSliderR")
        self.verticalSliderR.setGeometry(QRect(1720, 650, 22, 160))
        self.verticalSliderR.setOrientation(Qt.Vertical)
        self.verticalSliderR.setMinimum(0)
        self.verticalSliderR.setMaximum(101)
        self.verticalSliderR.setStyleSheet(
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
        self.label_slider_right = QLabel(self.centralwidget)
        self.label_slider_right.setGeometry(QRect(1710, 600, 55, 16))
        self.label_slider_right.setObjectName("label_slider_right")

        # Define the left and right spinbox of the actuator (and their labels)
        self.spinBoxL = QSpinBox(self.centralwidget)
        self.spinBoxL.setObjectName(u"spinBox")
        self.spinBoxL.setGeometry(QRect(1660, 620, 42, 22))
        self.spinBoxL.setMinimum(0)
        self.spinBoxL.setMaximum(100)

        self.spinBoxR = QSpinBox(self.centralwidget)
        self.spinBoxR.setObjectName(u"spinBoxR")
        self.spinBoxR.setGeometry(QRect(1710, 620, 42, 22))
        self.spinBoxR.setMinimum(0)
        self.spinBoxR.setMaximum(100)
        
        # Define a button used to send the selected values of the slider&spinbox
        self.actuator = QPushButton(self.centralwidget)
        self.actuator.setGeometry(QRect(1671, 820, 70, 40))
        self.actuator.setObjectName("actuator")
        
        # Define a button used to enable TVC
        self.TVC = QPushButton(self.centralwidget)
        self.TVC.setGeometry(QRect(1600,720, 70, 40))
        self.TVC.setObjectName("TVC")

        # Define a button to finish the entire program (to avoid closing windows unintentionally, the close button hint is disabled)
        self.close_all = QPushButton(self.centralwidget)
        self.close_all.setGeometry(QRect(1800, 900, 70, 40))
        self.close_all.setObjectName("close_all")

        # Define the label in the status table
        self.SV11 = QLabel(self.centralwidget)
        self.SV11.setGeometry(QRect(1428, 567, 55, 16))
        self.SV11.setObjectName("SV11")
        self.SV12 = QLabel(self.centralwidget)
        self.SV12.setGeometry(QRect(1428, 591, 55, 16))
        self.SV12.setObjectName("SV12")
        self.SV21 = QLabel(self.centralwidget)
        self.SV21.setGeometry(QRect(1428, 613, 55, 16))
        self.SV21.setObjectName("SV21")
        self.SV22 = QLabel(self.centralwidget)
        self.SV22.setGeometry(QRect(1428, 636, 55, 16))
        self.SV22.setObjectName("SV22")
        self.SV31 = QLabel(self.centralwidget)
        self.SV31.setGeometry(QRect(1428, 660, 55, 16))
        self.SV31.setObjectName("SV31")
        self.SV32 = QLabel(self.centralwidget)
        self.SV32.setGeometry(QRect(1428, 682, 55, 16))
        self.SV32.setObjectName("SV32")
        self.SV33 = QLabel(self.centralwidget)
        self.SV33.setGeometry(QRect(1428, 705, 55, 16))
        self.SV33.setObjectName("SV33")
        self.SV34 = QLabel(self.centralwidget)
        self.SV34.setGeometry(QRect(1428, 728, 55, 16))
        self.SV34.setObjectName("SV34")
        self.SV35 = QLabel(self.centralwidget)
        self.SV35.setGeometry(QRect(1428, 752, 55, 16))
        self.SV35.setObjectName("SV35")
        self.SV51 = QLabel(self.centralwidget)
        self.SV51.setGeometry(QRect(1428, 774, 55, 16))
        self.SV51.setObjectName("SV51")
        self.SV61 = QLabel(self.centralwidget)
        self.SV61.setGeometry(QRect(1428, 797, 55, 16))
        self.SV61.setObjectName("SV61")
        self.SV62 = QLabel(self.centralwidget)
        self.SV62.setGeometry(QRect(1428, 820, 55, 16))
        self.SV62.setObjectName("SV62")
        
        # Define the launch plot button (to open a second window with IRT plots)
        self.lplot = QPushButton(self.centralwidget)
        self.lplot.setGeometry(QRect(1330, 880, 100, 50))
        self.lplot.setObjectName("Launch Plot")

        # Definition of frames for a clearer HMI
        self.frame = QFrame(self.centralwidget)
        self.frame.setGeometry(QRect(160, 470, 111, 91))
        self.frame.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 3px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")    
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setObjectName("frame")

        self.frame_2 = QFrame(self.centralwidget)
        self.frame_2.setGeometry(QRect(300, 190, 111, 91))
        self.frame_2.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 3px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.frame_2.setObjectName("frame_2")

        self.frame_3 = QFrame(self.centralwidget)
        self.frame_3.setGeometry(QRect(770, 190, 111, 91))
        self.frame_3.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 3px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.frame_3.setObjectName("frame_3")

        self.frame_4 = QFrame(self.centralwidget)
        self.frame_4.setGeometry(QRect(600, 70, 111, 91))
        self.frame_4.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 3px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.frame_4.setObjectName("frame_4")

        self.frame_5 = QFrame(self.centralwidget)
        self.frame_5.setGeometry(QRect(980, 90, 111, 91))
        self.frame_5.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 3px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.frame_5.setObjectName("frame_5")

        self.frame_6 = QFrame(self.centralwidget)
        self.frame_6.setGeometry(QRect(300, 530, 111, 91))
        self.frame_6.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 3px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")
        self.frame_6.setFrameShape(QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.frame_6.setObjectName("frame_6")

        self.frame_7 = QFrame(self.centralwidget)
        self.frame_7.setGeometry(QRect(600, 620, 111, 91))
        self.frame_7.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 3px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")
        self.frame_7.setFrameShape(QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.frame_7.setObjectName("frame_7")

        self.frame_8 = QFrame(self.centralwidget)
        self.frame_8.setGeometry(QRect(770, 540, 111, 91))
        self.frame_8.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 3px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")
        self.frame_8.setFrameShape(QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.frame_8.setObjectName("frame_8")

        self.frame_9 = QFrame(self.centralwidget)
        self.frame_9.setGeometry(QRect(980, 630, 111, 91))
        self.frame_9.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 3px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")
        self.frame_9.setFrameShape(QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QFrame.Raised)
        self.frame_9.setObjectName("frame_9")

        self.frame_10 = QFrame(self.centralwidget)
        self.frame_10.setGeometry(QRect(560, 740, 111, 91))
        self.frame_10.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 3px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")
        self.frame_10.setFrameShape(QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QFrame.Raised)
        self.frame_10.setObjectName("frame_10")

        self.frame_11 = QFrame(self.centralwidget)
        self.frame_11.setGeometry(QRect(720, 770, 111, 91))
        self.frame_11.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 3px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")
        self.frame_11.setFrameShape(QFrame.StyledPanel)
        self.frame_11.setFrameShadow(QFrame.Raised)
        self.frame_11.setObjectName("frame_11")

        self.frame_12 = QFrame(self.centralwidget)
        self.frame_12.setGeometry(QRect(330, 780, 111, 91))
        self.frame_12.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 3px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")
        self.frame_12.setFrameShape(QFrame.StyledPanel)
        self.frame_12.setFrameShadow(QFrame.Raised)
        self.frame_12.setObjectName("frame_12")

        self.frame_14 = QFrame(self.centralwidget)
        self.frame_14.setGeometry(QRect(1070, 280, 61, 41))
        self.frame_14.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 2px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")
        self.frame_14.setFrameShape(QFrame.StyledPanel)
        self.frame_14.setFrameShadow(QFrame.Raised)
        self.frame_14.setObjectName("frame_14")

        self.frame_15 = QFrame(self.centralwidget)
        self.frame_15.setGeometry(QRect(1180, 280, 61, 41))
        self.frame_15.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 2px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")
        self.frame_15.setFrameShape(QFrame.StyledPanel)
        self.frame_15.setFrameShadow(QFrame.Raised)
        self.frame_15.setObjectName("frame_15")

        self.frame_16 = QFrame(self.centralwidget)
        self.frame_16.setGeometry(QRect(910, 930, 61, 33))
        self.frame_16.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 2px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")
        self.frame_16.setFrameShape(QFrame.StyledPanel)
        self.frame_16.setFrameShadow(QFrame.Raised)
        self.frame_16.setObjectName("frame_16")
        
        self.frame_17 = QFrame(self.centralwidget)
        self.frame_17.setGeometry(QRect(1030, 930, 61, 33))
        self.frame_17.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 2px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")
        self.frame_17.setFrameShape(QFrame.StyledPanel)
        self.frame_17.setFrameShadow(QFrame.Raised)
        self.frame_17.setObjectName("frame_17")
        self.frame_18 = QFrame(self.centralwidget)
        self.frame_18.setGeometry(QRect(913, 839, 61, 38))
        self.frame_18.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 2px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")
        self.frame_18.setFrameShape(QFrame.StyledPanel)
        self.frame_18.setFrameShadow(QFrame.Raised)
        self.frame_18.setObjectName("frame_18")

        self.frame_19 = QFrame(self.centralwidget)
        self.frame_19.setGeometry(QRect(1033, 839, 61, 38))
        self.frame_19.setStyleSheet("QFrame, QLabel, QToolTip {\n"
        "    border: 2px solid grey;\n"
        "    border-radius: 10px;\n"
        "    padding: 2px;\n"
        "}")
        self.frame_19.setFrameShape(QFrame.StyledPanel)
        self.frame_19.setFrameShadow(QFrame.Raised)
        self.frame_19.setObjectName("frame_19")

        # Define all the label sensors
        self.PS61_value = QLabel(self.centralwidget)
        self.PS61_value.setGeometry(QRect(491, 900, 41, 21))
        self.PS61_value.setObjectName("PS61_value")
        self.PS11_value = QLabel(self.centralwidget)
        self.PS11_value.setGeometry(QRect(508, 485, 41, 21))
        self.PS11_value.setObjectName("PS11_value")
        self.PS21_value = QLabel(self.centralwidget)
        self.PS21_value.setGeometry(QRect(508, 323, 41, 21))
        self.PS21_value.setObjectName("PS21_value")
        self.TS41_value = QLabel(self.centralwidget)
        self.TS41_value.setGeometry(QRect(1092, 280, 41, 21))
        self.TS41_value.setObjectName("TS41_value")
        self.TS42_value = QLabel(self.centralwidget)
        self.TS42_value.setGeometry(QRect(1194, 280, 41, 21))
        self.TS42_value.setObjectName("TS42_value")
        self.PS62_value = QLabel(self.centralwidget)
        self.PS62_value.setGeometry(QRect(933, 940, 31, 21))
        self.PS62_value.setObjectName("PS62_value")
        self.PS63_value = QLabel(self.centralwidget)
        self.PS63_value.setGeometry(QRect(1048, 940, 31, 21))
        self.PS63_value.setObjectName("PS63_value")
        self.TS62_value = QLabel(self.centralwidget)
        self.TS62_value.setGeometry(QRect(1048, 840, 31, 21))
        self.TS62_value.setObjectName("TS62_value")
        self.TS61_value = QLabel(self.centralwidget)
        self.TS61_value.setGeometry(QRect(933, 840, 31, 21))
        self.TS61_value.setObjectName("TS61_value")

        # Raise all the above objects
        self.frame_13.raise_()
        self.background.raise_()
        self.logo.raise_()
        self.table.raise_()
        self.frame_9.raise_()
        self.frame_11.raise_()
        self.frame_7.raise_()
        self.frame_2.raise_()
        self.frame.raise_()
        self.frame_3.raise_()
        self.frame_4.raise_()
        self.frame_12.raise_()
        self.frame_6.raise_()
        self.frame_8.raise_()
        self.frame_5.raise_()
        self.frame_10.raise_()
        self.status_SV11.raise_()
        self.label_SV11.raise_()
        self.open_SV11.raise_()
        self.closed_SV11.raise_()
        self.label_SV33.raise_()
        self.status_SV33.raise_()
        self.closed_SV33.raise_()
        self.open_SV33.raise_()
        self.label_SV31.raise_()
        self.status_SV31.raise_()
        self.closed_SV31.raise_()
        self.open_SV31.raise_()
        self.label_SV12.raise_()
        self.status_SV12.raise_()
        self.closed_SV12.raise_()
        self.open_SV12.raise_()
        self.label_SV35.raise_()
        self.status_SV35.raise_()
        self.closed_SV35.raise_()
        self.open_SV35.raise_()
        self.label_SV51.raise_()
        self.status_SV51.raise_()
        self.closed_SV51.raise_()
        self.open_SV51.raise_()
        self.label_SV22.raise_()
        self.status_SV22.raise_()
        self.closed_SV22.raise_()
        self.open_SV22.raise_()
        self.label_SV21.raise_()
        self.status_SV21.raise_()
        self.closed_SV21.raise_()
        self.open_SV21.raise_()
        self.label_SV34.raise_()
        self.status_SV34.raise_()
        self.closed_SV34.raise_()
        self.open_SV34.raise_()
        self.label_SV32.raise_()
        self.status_SV32.raise_()
        self.closed_SV32.raise_()
        self.open_SV32.raise_()
        self.label_SV61.raise_()
        self.closed_SV61.raise_()
        self.open_SV61.raise_()
        self.status_SV61.raise_()
        self.label_SV62.raise_()
        self.status_SV62.raise_()
        self.closed_SV62.raise_()
        self.open_SV62.raise_()
        self.SV11.raise_()
        self.SV22.raise_()
        self.SV34.raise_()
        self.SV31.raise_()
        self.SV32.raise_()
        self.SV51.raise_()
        self.SV61.raise_()
        self.SV21.raise_()
        self.SV35.raise_()
        self.SV33.raise_()
        self.SV12.raise_()
        self.SV62.raise_()
        self.PS61_value.raise_()
        self.PS11_value.raise_()
        self.PS21_value.raise_()
        self.frame_14.raise_()
        self.frame_15.raise_()
        self.TS42_value.raise_()
        self.TS41_value.raise_()
        self.PS62_value.raise_()
        self.PS63_value.raise_()
        self.frame_18.raise_()
        self.TS61_value.raise_()
        self.frame_19.raise_()
        self.TS62_value.raise_()
        self.frame_17.raise_()
        self.frame_16.raise_()
        self.lplot.raise_()
        self.verticalSliderL.raise_()
        self.verticalSliderR.raise_()
        self.spinBoxL.raise_()
        self.spinBoxR.raise_()
        self.label_slider_right.raise_()
        self.label_slider_left.raise_()
        self.actuator.raise_()
        self.TVC.raise_()
        self.close_all.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setWindowFlags(MainWindow.windowFlags() & ~Qt.WindowCloseButtonHint)
    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate

        self.adress='192.168.0.101'

        # Set the text of multiple objects
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.status_SV11.setText(_translate("MainWindow", "SV11 status:"))
        self.label_SV11.setText(_translate("MainWindow", "Open"))
        self.open_SV11.setText(_translate("MainWindow", "Open"))
        self.closed_SV11.setText(_translate("MainWindow", "Close"))
        self.label_SV12.setText(_translate("MainWindow", "Open"))
        self.status_SV12.setText(_translate("MainWindow", "SV12 status:"))
        self.closed_SV12.setText(_translate("MainWindow", "Close"))
        self.open_SV12.setText(_translate("MainWindow", "Open"))
        self.label_SV21.setText(_translate("MainWindow", "Open"))
        self.status_SV21.setText(_translate("MainWindow", "SV21 status:"))
        self.closed_SV21.setText(_translate("MainWindow", "Close"))
        self.open_SV21.setText(_translate("MainWindow", "Open"))
        self.label_SV22.setText(_translate("MainWindow", "Open"))
        self.status_SV22.setText(_translate("MainWindow", "SV22 status:"))
        self.closed_SV22.setText(_translate("MainWindow", "Close"))
        self.open_SV22.setText(_translate("MainWindow", "Open"))
        self.label_SV31.setText(_translate("MainWindow", "Open"))
        self.status_SV31.setText(_translate("MainWindow", "SV31 status:"))
        self.closed_SV31.setText(_translate("MainWindow", "Close"))
        self.open_SV31.setText(_translate("MainWindow", "Open"))
        self.label_SV32.setText(_translate("MainWindow", "Open"))
        self.status_SV32.setText(_translate("MainWindow", "SV32 status:"))
        self.closed_SV32.setText(_translate("MainWindow", "Close"))
        self.open_SV32.setText(_translate("MainWindow", "Open"))
        self.label_SV33.setText(_translate("MainWindow", "Open"))
        self.status_SV33.setText(_translate("MainWindow", "SV33 status:"))
        self.closed_SV33.setText(_translate("MainWindow", "Close"))
        self.open_SV33.setText(_translate("MainWindow", "Open"))
        self.label_SV34.setText(_translate("MainWindow", "Open"))
        self.status_SV34.setText(_translate("MainWindow", "SV34 status:"))
        self.closed_SV34.setText(_translate("MainWindow", "Close"))
        self.open_SV34.setText(_translate("MainWindow", "Open"))      
        self.label_SV35.setText(_translate("MainWindow", "Open"))
        self.status_SV35.setText(_translate("MainWindow", "SV35 status:"))
        self.closed_SV35.setText(_translate("MainWindow", "Close"))
        self.open_SV35.setText(_translate("MainWindow", "Open"))
        self.label_SV51.setText(_translate("MainWindow", "Open"))
        self.status_SV51.setText(_translate("MainWindow", "SV51 status:"))
        self.closed_SV51.setText(_translate("MainWindow", "Close"))
        self.open_SV51.setText(_translate("MainWindow", "Open"))
        self.label_SV61.setText(_translate("MainWindow", "Open"))
        self.closed_SV61.setText(_translate("MainWindow", "Close"))
        self.open_SV61.setText(_translate("MainWindow", "Open"))
        self.status_SV61.setText(_translate("MainWindow", "SV61 status:"))
        self.label_SV62.setText(_translate("MainWindow", "Open"))
        self.status_SV62.setText(_translate("MainWindow", "SV62 status:"))
        self.closed_SV62.setText(_translate("MainWindow", "Close"))
        self.open_SV62.setText(_translate("MainWindow", "Open"))
        self.lplot.setText(_translate("MainWindow", "Launch Plot"))
        self.actuator.setText(_translate("MainWindow", "actuator"))
        self.TVC.setText(_translate("MainWindow", "TVC"))
        self.close_all.setText(_translate("MainWindow", "Close_all"))
        self.SV62.setText(_translate("MainWindow", "Open"))
        self.SV11.setText(_translate("MainWindow", "Open"))
        self.SV12.setText(_translate("MainWindow", "Open"))
        self.SV21.setText(_translate("MainWindow", "Open"))
        self.SV22.setText(_translate("MainWindow", "Open"))
        self.SV31.setText(_translate("MainWindow", "Open"))
        self.SV33.setText(_translate("MainWindow", "Open"))
        self.SV32.setText(_translate("MainWindow", "Open"))
        self.SV34.setText(_translate("MainWindow", "Open"))
        self.SV35.setText(_translate("MainWindow", "Open"))
        self.SV61.setText(_translate("MainWindow", "Open"))
        self.SV51.setText(_translate("MainWindow", "Open"))
        self.PS61_value.setText(_translate("MainWindow", "1000"))
        self.PS11_value.setText(_translate("MainWindow", "1000"))
        self.PS21_value.setText(_translate("MainWindow", "1000"))
        self.TS41_value.setText(_translate("MainWindow", "1000"))
        self.TS42_value.setText(_translate("MainWindow", "1000"))
        self.PS62_value.setText(_translate("MainWindow", "100"))
        self.PS63_value.setText(_translate("MainWindow", "100"))
        self.TS61_value.setText(_translate("MainWindow", "100"))
        self.TS62_value.setText(_translate("MainWindow", "100"))

        # Set the color and text of SV11
        self.SV11.setText(_translate("MainWindow", "Open"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.darkGreen)
        self.SV11.setGraphicsEffect(self.color_effect)
        self.label_SV11.setText(_translate("MainWindow", "Open"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.darkGreen)
        self.label_SV11.setGraphicsEffect(self.color_effect)

        # Set the color and text of SV12
        self.SV12.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)
        self.SV12.setGraphicsEffect(self.color_effect)
        self.label_SV12.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)
        self.label_SV12.setGraphicsEffect(self.color_effect)

        # Set the color and text of SV21
        self.SV21.setText(_translate("MainWindow", "Open"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.darkGreen)
        self.SV21.setGraphicsEffect(self.color_effect)
        self.label_SV21.setText(_translate("MainWindow", "Open"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.darkGreen)
        self.label_SV21.setGraphicsEffect(self.color_effect)

        # Set the color and text of SV22
        self.SV22.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)  
        self.SV22.setGraphicsEffect(self.color_effect)
        self.label_SV22.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)      
        self.label_SV22.setGraphicsEffect(self.color_effect)

        # Set the color and text of SV31
        self.SV31.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)  
        self.SV31.setGraphicsEffect(self.color_effect) 
        self.label_SV31.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)     
        self.label_SV31.setGraphicsEffect(self.color_effect)

        # Set the color and text of SV32
        self.SV32.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)
        self.SV32.setGraphicsEffect(self.color_effect)
        self.label_SV32.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)
        self.label_SV32.setGraphicsEffect(self.color_effect)

        # Set the color and text of SV33
        self.SV33.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)
        self.SV33.setGraphicsEffect(self.color_effect)
        self.label_SV33.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)
        self.label_SV33.setGraphicsEffect(self.color_effect)

        # Set the color and text of SV34
        self.SV34.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)
        self.SV34.setGraphicsEffect(self.color_effect)
        self.label_SV34.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)
        self.label_SV34.setGraphicsEffect(self.color_effect)

        # Set the color and text of SV35
        self.SV35.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)
        self.SV35.setGraphicsEffect(self.color_effect)
        self.label_SV35.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)
        self.label_SV35.setGraphicsEffect(self.color_effect)

        # Set the color and text of SV51
        self.SV51.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)
        self.SV51.setGraphicsEffect(self.color_effect)
        self.label_SV51.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)
        self.label_SV51.setGraphicsEffect(self.color_effect)
        
        # Set the color and text of SV61
        self.SV61.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)
        self.SV61.setGraphicsEffect(self.color_effect)
        self.label_SV61.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)
        self.label_SV61.setGraphicsEffect(self.color_effect)
        
        # Set the color and text of SV62
        self.SV62.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)
        self.SV62.setGraphicsEffect(self.color_effect)
        self.label_SV62.setText(_translate("MainWindow", "Closed"))
        self.color_effect = QGraphicsColorizeEffect()
        self.color_effect.setColor(Qt.red)
        self.label_SV62.setGraphicsEffect(self.color_effect)

        self.label_slider_left.setText(_translate("MainWindow", "actuator L"))
        self.label_slider_right.setText(_translate("MainWindow", "actuator R"))
        self.existence=0
        self.state_TVC=0
        # Link the buttons to the open/close_valve
        self.open_SV11.clicked.connect(lambda: self.open_valve(11,self.label_SV11,self.SV11))
        self.closed_SV11.clicked.connect(lambda: self.close_valve(11,self.label_SV11,self.SV11))

        self.open_SV12.clicked.connect(lambda: self.open_valve(12,self.label_SV12,self.SV12))
        self.closed_SV12.clicked.connect(lambda: self.close_valve(12,self.label_SV12,self.SV12))

        self.open_SV21.clicked.connect(lambda: self.open_valve(21,self.label_SV21,self.SV21))
        self.closed_SV21.clicked.connect(lambda: self.close_valve(21,self.label_SV21,self.SV21))

        self.open_SV22.clicked.connect(lambda: self.open_valve(22,self.label_SV22,self.SV22))
        self.closed_SV22.clicked.connect(lambda: self.close_valve(22,self.label_SV22,self.SV22))

        self.open_SV31.clicked.connect(lambda: self.open_valve(31,self.label_SV31,self.SV31))
        self.closed_SV31.clicked.connect(lambda: self.close_valve(31,self.label_SV31,self.SV31))

        self.open_SV32.clicked.connect(lambda:self.open_valve(32,self.label_SV32,self.SV32))
        self.closed_SV32.clicked.connect(lambda:self.close_valve(32,self.label_SV32,self.SV32))

        self.open_SV33.clicked.connect(lambda:self.open_valve(33,self.label_SV33,self.SV33))
        self.closed_SV33.clicked.connect(lambda:self.close_valve(33,self.label_SV33,self.SV33))

        self.open_SV34.clicked.connect(lambda:self.open_valve(34,self.label_SV34,self.SV34))
        self.closed_SV34.clicked.connect(lambda:self.close_valve(34,self.label_SV34,self.SV34))
        
        self.open_SV35.clicked.connect(lambda:self.open_valve(35,self.label_SV35,self.SV35))
        self.closed_SV35.clicked.connect(lambda:self.close_valve(35,self.label_SV35,self.SV35))

        self.open_SV51.clicked.connect(lambda:self.open_valve(51,self.label_SV51,self.SV51))
        self.closed_SV51.clicked.connect(lambda:self.close_valve(51,self.label_SV51,self.SV51))

        self.open_SV61.clicked.connect(lambda:self.open_valve(61,self.label_SV61,self.SV61))
        self.closed_SV61.clicked.connect(lambda:self.close_valve(61,self.label_SV61,self.SV61))

        self.open_SV62.clicked.connect(lambda:self.open_valve(62,self.label_SV62,self.SV62))
        self.closed_SV62.clicked.connect(lambda:self.close_valve(62,self.label_SV62,self.SV62))

        # Connect the launch_button to the toggel_second_window
        self.lplot.clicked.connect(self.launch_plot)


        self.close_all.clicked.connect(self.close_all_program)


        self.worker = Worker()
        self.worker_thread = threading.Thread(target=self.worker.generate_random_values)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        self.worker.update_signal.connect(self.update_str)

        self.verticalSliderL.valueChanged.connect(self.sliderValueChanged)
        self.spinBoxL.valueChanged.connect(self.spinBoxValueChanged)
        self.verticalSliderR.valueChanged.connect(self.sliderValueChanged2)
        self.spinBoxR.valueChanged.connect(self.spinBoxValueChanged2)
        self.actuator.clicked.connect(lambda : self.control_actuator(self.spinBoxL.value(),self.spinBoxR.value()))
        self.TVC.clicked.connect(self.activate_TVC)

    def activate_TVC(self):
        _translate = QCoreApplication.translate
        if self.state_TVC==1: # Check if TVC ON (if 1 ON else OFF)
            try:
                address = (self.adress, 5000)
                self.client_socket = socket(AF_INET, SOCK_DGRAM)
                self.client_socket.settimeout(1)
                ver_send=f"TVC_OFF"
                self.client_socket.sendto(str.encode(ver_send), address)
                rec_data, addr = self.client_socket.recvfrom(1024)
                if rec_data == f"TVC_OFF_ok".encode():
                    self.TVC.setText(_translate("MainWindow", "TVC OFF"))
                    self.color_effect = QGraphicsColorizeEffect()
                    self.color_effect.setColor(Qt.red)
                    self.TVC.setGraphicsEffect(self.color_effect)
                    self.state_TVC=0 # No TVC during the test
            except:
                pass

        elif self.state_TVC==0: 
            try:
                address = (self.adress, 5000)
                self.client_socket = socket(AF_INET, SOCK_DGRAM)
                self.client_socket.settimeout(1)
                ver_send=f"TVC_ON"
                self.client_socket.sendto(str.encode(ver_send), address)
                rec_data, addr = self.client_socket.recvfrom(1024)
                if rec_data == f"TVC_ON_ok".encode():
                    self.TVC.setText(_translate("MainWindow", "TVC ON"))
                    self.color_effect = QGraphicsColorizeEffect()
                    self.color_effect.setColor(Qt.darkGreen)
                    self.TVC.setGraphicsEffect(self.color_effect)
                    self.state_TVC=1
            except:
                pass


    def control_actuator(self,value1,value2):
        try:
            address = (self.adress, 5000)
            self.client_socket = socket(AF_INET, SOCK_DGRAM)
            self.client_socket.settimeout(1)
            ver_send=f"ver_{value1}_{value2}"
            self.client_socket.sendto(str.encode(ver_send), address)
        except:
            pass

    def close_all_program(self):
        print("\n\n\nYou closed the program.\nDid it work bitch (ง'-̀'́)ง  Ϟ  ฝ('-'ฝ)\n\n\n")
        QCoreApplication.quit()

    def sliderValueChanged(self,value):
        self.spinBoxL.setValue(value)

    def spinBoxValueChanged(self,value):
        self.verticalSliderL.setValue(value)

    def sliderValueChanged2(self,value):
        self.spinBoxR.setValue(value)

    def spinBoxValueChanged2(self,value):
        self.verticalSliderR.setValue(value)   

    def update_str(self,values):
        _translate = QCoreApplication.translate
        widgets = [
            self.PS61_value, self.PS11_value, self.PS21_value,
            self.TS41_value, self.TS42_value, self.PS62_value,
            self.PS63_value, self.TS61_value, self.TS62_value
        ]
        for widget, value in zip(widgets, values[1:10]):
            widget.setText(_translate("MainWindow", str(value)))

    # Connect and send data to the arduino
    def send_command(self,command):
        address = (self.adress, 5000)  # Define who you are talking to (must match Arduino IP and port)
        self.client_socket = socket(AF_INET, SOCK_DGRAM)  # Set up the socket
        self.client_socket.settimeout(1)
        self.client_socket.sendto(str.encode(command), address)  # Send command to Arduino
        rec_data, addr = self.client_socket.recvfrom(1024)
        return rec_data

    # Change the color and text of the status of each valve
    def update_valve_status(self,valve_label, status_text, color):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        valve_label.setText(_translate("MainWindow", status_text))
        color_effect = QGraphicsColorizeEffect()
        color_effect.setColor(color)
        valve_label.setGraphicsEffect(color_effect)

    # Send a command, if the arduino open the valve, it receives a validation and appy the update_valve_status function
    def open_valve(self,valve_number, valve_label,valve_status):
        command = f"SV{valve_number}1"
        try:
            rec_data = self.send_command(command)
            if rec_data == f"SV{valve_number}1_ok".encode():
                self.update_valve_status(valve_label, "Open", Qt.darkGreen)
                self.update_valve_status(valve_status, "Open", Qt.darkGreen)
        except:
            pass

    # Send a command, if the arduino close the valve, it receives a validation and appy the update_valve_status function
    def close_valve(self,valve_number, valve_label,valve_status):
        command = f"SV{valve_number}0"
        try:
            rec_data = self.send_command(command)
            if rec_data == f"SV{valve_number}0_ok".encode():
                self.update_valve_status(valve_label, "Closed", Qt.red)
                self.update_valve_status(valve_status, "Closed", Qt.red)
        except:
            pass

    # Call the MultiRealTimePlot class
    def launch_plot(self):
        if self.existence == 0:
            self.second_window = MultiRealTimePlot()
            self.second_window.show()
            self.existence=1
        else:
            pass

# Main class for the IRT plot
class MultiRealTimePlot(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window parameters
        self.setWindowTitle("Multi Real-Time Plot")
        self.setFixedSize(1910, 990)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create three instances of RealTimePlot and arrange them vertically
        self.real_time_plots = [RealTimePlot1(),RealTimePlot2(),RealTimePlot3()]
        for plot in self.real_time_plots:
            layout.addWidget(plot)
            thread = threading.Thread(target=plot.update_plot(Figure(figsize=(18,6))))
            thread.daemon = True  # Daemonize the thread
            thread.start()

# First IRT plot class
class RealTimePlot1(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Real-Time Plot")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        self.fig = Figure(figsize=(18,6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.x_data = []
        self.y_data = []

        # Thread for generating random values
        self.thread = threading.Thread(target=self.read_val)
        self.thread.daemon = True  # Daemonize the thread
        self.thread.start()

        # Create a frame for x-axis interval and curves controls
        self.controls_frame = QFrame(self)
        self.controls_frame.setFrameShape(QFrame.StyledPanel)
        layout.addWidget(self.controls_frame)
        self.controls_frame.setFixedWidth(200)
        
        # Layout for x-axis interval and curves controls
        self.controls_layout = QGridLayout(self.controls_frame)

        self.x_length_label = QLabel("Time Interval:", self)
        self.controls_layout.addWidget(self.x_length_label)

        self.button_1m = QPushButton("1m", self)
        self.button_1m.clicked.connect(lambda: self.set_x_interval(1*60))
        self.controls_layout.addWidget(self.button_1m)

        self.button_10m = QPushButton("10m", self)
        self.button_10m.clicked.connect(lambda: self.set_x_interval(10*60))
        self.controls_layout.addWidget(self.button_10m)

        self.button_30m = QPushButton("30m", self)
        self.button_30m.clicked.connect(lambda: self.set_x_interval(30*60))
        self.controls_layout.addWidget(self.button_30m)

        self.button_All = QPushButton("All", self)
        self.button_All.clicked.connect(lambda: self.set_x_interval(-1))
        self.controls_layout.addWidget(self.button_All)

        self.curve_label = QLabel("Sensors:", self)
        self.controls_layout.addWidget(self.curve_label)

        self.checkbox_1 = QCheckBox("Curve 1", self)
        self.checkbox_1.setChecked(True)  # Default to show the first curve
        self.controls_layout.addWidget(self.checkbox_1)

        self.checkbox_2 = QCheckBox("Curve 2", self)
        self.controls_layout.addWidget(self.checkbox_2)

        self.checkbox_3 = QCheckBox("Curve 3", self)
        self.controls_layout.addWidget(self.checkbox_3)

        self.checkbox_4 = QCheckBox("Curve 4", self)
        self.controls_layout.addWidget(self.checkbox_4)

        self.checkbox_5 = QCheckBox("Curve 5", self)
        self.controls_layout.addWidget(self.checkbox_5)

        self.checkbox_6 = QCheckBox("Curve 6", self)
        self.controls_layout.addWidget(self.checkbox_6)

        self.checkbox_7 = QCheckBox("Curve 4", self)
        self.controls_layout.addWidget(self.checkbox_7)

        self.checkbox_8 = QCheckBox("Curve 8", self)
        self.controls_layout.addWidget(self.checkbox_8)

        self.checkbox_9 = QCheckBox("Curve 9", self)
        self.controls_layout.addWidget(self.checkbox_9)

        self.animation = FuncAnimation(self.fig, self.update_plot, interval=1000, cache_frame_data=False)
    def read_val(self):
        i=0
        while True:
            with open('random_data.csv', 'r') as file:
                # Create a CSV reader object
                csv_reader = csv.reader(file)
                
                # Initialize an empty list to store the selected indexes
                self.x_data=[]
                self.y_data=[]
                # Iterate over each row in the CSV file
                for row in csv_reader:
                    self.x_data.append(float(row[0]))
                    self.y_data.append([float(row[i]) for i in range(1,10)])
            time.sleep(1)
    def set_x_interval(self, interval):
        self.x_interval = interval

    def update_plot(self,frame):
        try:
            x_length = self.x_interval
        except AttributeError:
            x_length = 10

        checked_boxes = [self.checkbox_1, self.checkbox_2, self.checkbox_3, self.checkbox_4,self.checkbox_5,self.checkbox_6, self.checkbox_7,self.checkbox_8,self.checkbox_9]

        
        
        self.ax.clear()
        rows = 4
        cols = 1
        for i, checkbox in enumerate(checked_boxes):
            row = rows + i % 5
            col = cols * (i // 5)
            self.controls_layout.addWidget(checkbox, row, col)

        self.controls_layout.addWidget(self.x_length_label, 0, 0)
        self.controls_layout.addWidget(self.curve_label, 3, 0)
        self.controls_layout.addWidget(self.button_1m, 1, 0)
        self.controls_layout.addWidget(self.button_10m, 1, 1)
        self.controls_layout.addWidget(self.button_30m, 2, 0)
        self.controls_layout.addWidget(self.button_All, 2, 1)
        #self.controls_layout.addWidget(checkbox, row, col)
        num_checked_boxes = sum(1 for checkbox in checked_boxes if checkbox.isChecked())

        for i, checkbox in enumerate(checked_boxes):
            if num_checked_boxes == 1 and checkbox.isChecked():
                checkbox.setEnabled(False)
                self.ax.plot(self.x_data, [data[i] for data in self.y_data], label=f'Curve {i+1}')
            elif checkbox.isChecked():
                checkbox.setEnabled(True)
                self.ax.plot(self.x_data, [data[i] for data in self.y_data], label=f'Curve {i+1}')

        if x_length == -1:
            self.ax.set_xlim(min(self.x_data), max(self.x_data))
        elif max(self.x_data) - x_length < 0:
            self.ax.set_xlim(0, x_length)
        else:
            self.ax.set_xlim(max(self.x_data) - x_length, max(self.x_data))

        self.ax.grid()
        self.ax.legend(loc='upper left')

# Second IRT plot class
class RealTimePlot2(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Real-Time Plot")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        self.fig = Figure(figsize=(18,6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.x_data = []
        self.y_data = []
        self.thread = threading.Thread(target=self.read_val2)
        self.thread.daemon = True  # Daemonize the thread
        self.thread.start()
        # Create a frame for x-axis interval and curves controls
        self.controls_frame = QFrame(self)
        self.controls_frame.setFrameShape(QFrame.StyledPanel)
        layout.addWidget(self.controls_frame)
        self.controls_frame.setFixedWidth(200)

        # Layout for x-axis interval and curves controls
        self.controls_layout = QGridLayout(self.controls_frame)

        self.x_length_label = QLabel("Time Interval:", self)
        self.controls_layout.addWidget(self.x_length_label)

        self.button_1m = QPushButton("1m", self)
        self.button_1m.clicked.connect(lambda: self.set_x_interval(1*60))
        self.controls_layout.addWidget(self.button_1m)

        self.button_10m = QPushButton("10m", self)
        self.button_10m.clicked.connect(lambda: self.set_x_interval(10*60))
        self.controls_layout.addWidget(self.button_10m)

        self.button_30m = QPushButton("30m", self)
        self.button_30m.clicked.connect(lambda: self.set_x_interval(30*60))
        self.controls_layout.addWidget(self.button_30m)

        self.button_All = QPushButton("All", self)
        self.button_All.clicked.connect(lambda: self.set_x_interval(-1))
        self.controls_layout.addWidget(self.button_All)

        self.curve_label = QLabel("Sensors:", self)
        self.controls_layout.addWidget(self.curve_label)

        self.checkbox_1 = QCheckBox("Curve 1", self)
        self.checkbox_1.setChecked(True)  # Default to show the first curve
        self.controls_layout.addWidget(self.checkbox_1)

        self.checkbox_2 = QCheckBox("Curve 2", self)
        self.controls_layout.addWidget(self.checkbox_2)

        self.checkbox_3 = QCheckBox("Curve 3", self)
        self.controls_layout.addWidget(self.checkbox_3)

        self.checkbox_4 = QCheckBox("Curve 4", self)
        self.controls_layout.addWidget(self.checkbox_4)

        self.checkbox_5 = QCheckBox("Curve 5", self)
        self.controls_layout.addWidget(self.checkbox_5)

        self.animation = FuncAnimation(self.fig, self.update_plot, interval=1000, cache_frame_data=False)
    def read_val2(self):
        i=0
        while True:
            with open('random_data.csv', 'r') as file:
                # Create a CSV reader object
                csv_reader = csv.reader(file)
                
                # Initialize an empty list to store the selected indexes
                self.x_data=[]
                self.y_data=[]
                
                # Iterate over each row in the CSV file
                for row in csv_reader:
                    # Append the desired indexes to the selected_indexes_data list
                    
                    self.x_data.append(float(row[0]))
                    self.y_data.append([float(row[i]) for i in range(10,15)])
            time.sleep(1)

    def set_x_interval(self, interval):
        self.x_interval = interval

    def update_plot(self,frame):
        try:
            x_length = self.x_interval
        except AttributeError:
            x_length = 10

        checked_boxes = [self.checkbox_1, self.checkbox_2, self.checkbox_3, self.checkbox_4,self.checkbox_5]
  
        self.ax.clear()

        self.controls_layout.addWidget(self.x_length_label, 0, 0)
        self.controls_layout.addWidget(self.curve_label, 3, 0)
        self.controls_layout.addWidget(self.button_1m, 1, 0)
        self.controls_layout.addWidget(self.button_10m, 1, 1)
        self.controls_layout.addWidget(self.button_30m, 2, 0)
        self.controls_layout.addWidget(self.button_All, 2, 1)
        num_checked_boxes = sum(1 for checkbox in checked_boxes if checkbox.isChecked())

        for i, checkbox in enumerate(checked_boxes):
            if num_checked_boxes == 1 and checkbox.isChecked():
                checkbox.setEnabled(False)
                self.ax.plot(self.x_data, [data[i] for data in self.y_data], label=f'Curve {i+1}')
            elif checkbox.isChecked():
                checkbox.setEnabled(True)
                self.ax.plot(self.x_data, [data[i] for data in self.y_data], label=f'Curve {i+1}')

        if x_length == -1:
            self.ax.set_xlim(min(self.x_data), max(self.x_data))
        elif max(self.x_data) - x_length < 0:
            self.ax.set_xlim(0, x_length)
        else:
            self.ax.set_xlim(max(self.x_data) - x_length, max(self.x_data))

        self.ax.grid()
        self.ax.legend(loc='upper left')

# Third IRT plot class
class RealTimePlot3(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Real-Time Plot")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        self.fig = Figure(figsize=(18,6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.thread = threading.Thread(target=self.read_val3)
        self.thread.daemon = True  # Daemonize the thread
        self.thread.start()
        # Create a frame for x-axis interval and curves controls
        self.controls_frame = QFrame(self)
        self.controls_frame.setFrameShape(QFrame.StyledPanel)
        layout.addWidget(self.controls_frame)
        self.controls_frame.setFixedWidth(200)

        # Layout for x-axis interval and curves controls
        self.controls_layout = QGridLayout(self.controls_frame)

        self.x_length_label = QLabel("Time Interval:", self)
        self.controls_layout.addWidget(self.x_length_label)

        self.button_1m = QPushButton("1m", self)
        self.button_1m.clicked.connect(lambda: self.set_x_interval(1*60))
        self.controls_layout.addWidget(self.button_1m)

        self.button_10m = QPushButton("10m", self)
        self.button_10m.clicked.connect(lambda: self.set_x_interval(10*60))
        self.controls_layout.addWidget(self.button_10m)

        self.button_30m = QPushButton("30m", self)
        self.button_30m.clicked.connect(lambda: self.set_x_interval(30*60))
        self.controls_layout.addWidget(self.button_30m)

        self.button_All = QPushButton("All", self)
        self.button_All.clicked.connect(lambda: self.set_x_interval(-1))
        self.controls_layout.addWidget(self.button_All)

        self.curve_label = QLabel("Sensors:", self)
        self.controls_layout.addWidget(self.curve_label)
        
        self.curve_label1 = QLabel(" ", self)
        self.controls_layout.addWidget(self.curve_label1)
        self.curve_label2 = QLabel(" ", self)
        self.controls_layout.addWidget(self.curve_label2)
        self.curve_label3 = QLabel(" ", self)
        self.controls_layout.addWidget(self.curve_label3)
        self.curve_label4 = QLabel(" ", self)
        self.controls_layout.addWidget(self.curve_label4)
        self.curve_label5 = QLabel(" ", self)
        self.controls_layout.addWidget(self.curve_label5)

        self.checkbox_1 = QCheckBox("Curve 1", self)
        self.checkbox_1.setChecked(True)  # Default to show the first curve
        self.controls_layout.addWidget(self.checkbox_1)
        
        self.animation = FuncAnimation(self.fig, self.update_plot, interval=1000, cache_frame_data=False)
        
    def read_val3(self):
        i=0
        while True:
            with open('random_data.csv', 'r') as file:
                # Create a CSV reader object
                csv_reader = csv.reader(file)
                
                # Initialize an empty list to store the selected indexes
                self.x_data=[]
                self.y_data=[]
                # Iterate over each row in the CSV file
                for row in csv_reader:
                    # Append the desired indexes to the selected_indexes_data list
                    
                    self.x_data.append(float(row[0]))
                    self.y_data.append([float(row[-1])])
            time.sleep(1)
    def set_x_interval(self, interval):
        self.x_interval = interval

    def update_plot(self,frame):
        try:
            x_length = self.x_interval
        except AttributeError:
            x_length = 10

        checked_boxes = [self.checkbox_1]
        
        
        self.ax.clear()
        self.controls_layout.addWidget(self.x_length_label, 0, 0)
        self.controls_layout.addWidget(self.curve_label, 3, 0)
        self.controls_layout.addWidget(self.curve_label1, 5, 0)
        self.controls_layout.addWidget(self.curve_label2, 6, 0)
        self.controls_layout.addWidget(self.curve_label3, 7, 0)
        self.controls_layout.addWidget(self.curve_label4, 8, 0)
        self.controls_layout.addWidget(self.curve_label5, 9, 0)
        self.controls_layout.addWidget(self.checkbox_1, 4, 0)
        self.controls_layout.addWidget(self.button_1m, 1, 0)
        self.controls_layout.addWidget(self.button_10m, 1, 1)
        self.controls_layout.addWidget(self.button_30m, 2, 0)
        self.controls_layout.addWidget(self.button_All, 2, 1)
        num_checked_boxes = sum(1 for checkbox in checked_boxes if checkbox.isChecked())

        for i, checkbox in enumerate(checked_boxes):
            if num_checked_boxes == 1 and checkbox.isChecked():
                checkbox.setEnabled(False)
                self.ax.plot(self.x_data, [data[i] for data in self.y_data], label=f'Curve {i+1}')
            elif checkbox.isChecked():
                checkbox.setEnabled(True)
                self.ax.plot(self.x_data, [data[i] for data in self.y_data], label=f'Curve {i+1}')

        if x_length == -1:
            self.ax.set_xlim(min(self.x_data), max(self.x_data))
        elif max(self.x_data) - x_length < 0:
            self.ax.set_xlim(0, x_length)
        else:
            self.ax.set_xlim(max(self.x_data) - x_length, max(self.x_data))

        self.ax.grid()
        self.ax.legend(loc='upper left')
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    
    sys.exit(app.exec_())
