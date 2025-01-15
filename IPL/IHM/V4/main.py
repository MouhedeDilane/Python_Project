from socket import *
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
import sys
import time 

from data_engine import engine_object

uC_connection = False
adress = ('192.168.0.149', 12345)
nbr_SV_engine = 12
nbr_sensor_engine = 12


class Main(object):
    def setupUi(self, MainWindow):
        # Set window size and style
        MainWindow.resize(1922, 1237)
        MainWindow.setWindowFlags(MainWindow.windowFlags() & ~Qt.WindowCloseButtonHint)
        MainWindow.setStyleSheet("background-color: rgb(236,236,236)")
        
        # Central widget and tab widget
        self.centralwidget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)
        self.tab_widget = QTabWidget(self.centralwidget)
        self.tab_widget.setGeometry(QRect(0, 0, 2000, 1080))
        self.tab_widget.setStyleSheet("""
            QTabBar::tab {
                height: 40px;
                width: 150px;
            }
        """)

        tab_names = ["Engine cycle", "Cooling cycle", "Test", "Plot", "Options"]
        self.tabs = [QWidget() for _ in tab_names]
        for tab, name in zip(self.tabs, tab_names):
            self.tab_widget.addTab(tab, name)
        self.tab1()

    def tab1(self):

        # Set up background picture (PID_Engine)
        self.background_engine = QLabel(self.tabs[0])
        self.background_engine.setGeometry(QRect(-30, 50, 2100, 900))
        self.background_engine.setPixmap(QPixmap("Synoptique_Arrax_Engine.png"))

        # Dimensions of the control objects
        width1, width2, width3, height1, height2, height3 = 111, 55, 41, 91, 16, 28

        # Control objects stored in list for efficiency
        self.SV_frame_engine = [QFrame(self.tabs[0]) for _ in range(nbr_SV_engine)]
        self.SV_frame_engine_status=[QLabel(self.tabs[0]) for _ in range(nbr_SV_engine)] 
        self.SV_frame_engine_label=[QLabel(self.tabs[0]) for _ in range(nbr_SV_engine)]  
        self.SV_button_ouvert_engine=[QPushButton(self.tabs[0]) for _ in range(nbr_SV_engine)] 
        self.SV_button_ferme_engine=[QPushButton(self.tabs[0]) for _ in range(nbr_SV_engine)] 
        
        # Link the lists using zip
        engine_array = zip(self.SV_frame_engine,self.SV_frame_engine_status, self.SV_frame_engine_label, self.SV_button_ouvert_engine, self.SV_button_ferme_engine)

        for (frame,frame_engine, label_engine, open_SV_engine, close_SV_engine), (valve_name, attributes) in zip(engine_array, engine_object.items()):
            # Unpack attributes of data_engine.py
            x, y = attributes['frame_dim']
            x1, y1 = attributes['status_dim']
            x2, y2 = attributes['label_dim']
            x3, y3 = attributes['ouvert_button_dim']
            x4, y4 = attributes['ferme_button_dim']
            
            # Set geometries for the frames, labels and buttons
            frame.setGeometry(QRect(x, y, width1, height1))
            frame_engine.setGeometry(QRect(x1, y1, width1, height2))
            label_engine.setGeometry(QRect(x2, y2, width2, height2))
            open_SV_engine.setGeometry(QRect(x3, y3, width3, height3))
            close_SV_engine.setGeometry(QRect(x4, y4, width3 + 7, height3))
            
            # Set fonts for the frames, labels, and buttons
            font = QFont("Arial", 8, QFont.Bold)
            frame_engine.setFont(font)
            label_engine.setFont(font)
            open_SV_engine.setFont(font)
            close_SV_engine.setFont(font)

            # Temporary variable that must be replace by either an overwrite to init or set the init here
            status_="Open"
            
            # Set label and styles for widgets
            frame_engine.setText(f"<u>{valve_name} status:</u>")
            label_engine.setText(f"{status_}")
            color = Qt.darkGreen
            color_effect = QGraphicsColorizeEffect()
            color_effect.setColor(color)  # You can replace with actual color logic if needed
            label_engine.setGraphicsEffect(color_effect)
            
            # Adjust size of widgets after setting text
            frame_engine.adjustSize()
            label_engine.adjustSize()

            # Set style for the frames
            frame.setStyleSheet("""QFrame, QLabel, QToolTip {
            background-color: rgb(230, 230, 230);
            border: 3px solid grey;
            border-radius: 10px;
            padding: 2px;
            }""")

            # Set text and style for open and close buttons
            open_SV_engine.setText("Open")
            open_SV_engine.setStyleSheet("""
                QPushButton {
                    border: 1px solid black;
                    background-color: white;
                    border-radius: 3px;
                    height: 30px;
                }
                QPushButton:hover {
                    background-color: #ADADAD;
                    border: 2px rgb(255,200,200);
                }
            """)
            
            close_SV_engine.setText("Close")
            close_SV_engine.setStyleSheet("""
                QPushButton {
                    border: 1px solid black;
                    background-color: white;
                    border-radius: 3px;
                    height: 30px;
                }
                QPushButton:hover {
                    background-color: #ADADAD;
                    border: 2px rgb(255,200,200);
                }
            """)

            # Raise the widgets to ensure correct display layering
            frame.raise_()
            frame_engine.raise_()
            label_engine.raise_()
            open_SV_engine.raise_()
            close_SV_engine.raise_()
    engine_object = {
    'SV11': {
        'frame_dim': (891, 690),
        'status_dim': (910, 700),
        'label_dim': (930, 720),
        'ouvert_button_dim': (901, 740),
        'ferme_button_dim': (947, 740)
    },
    'SV12': {
        'frame_dim': (1289, 585),
        'status_dim': (1305, 595),
        'label_dim': (1325, 615),
        'ouvert_button_dim': (1299, 635),
        'ferme_button_dim': (1345, 635)
    },
    'SV13': {
        'frame_dim': (1289, 758),
        'status_dim': (1305, 768),
        'label_dim': (1325, 788),
        'ouvert_button_dim': (1299, 808),
        'ferme_button_dim': (1345, 808)
    },
    'SV21': {
        'frame_dim': (891, 205),
        'status_dim': (910, 215),
        'label_dim': (930, 235),
        'ouvert_button_dim': (901, 255),
        'ferme_button_dim': (947, 255)
    },
    'SV22': {
        'frame_dim': (1239, 315),
        'status_dim': (1258, 325),
        'label_dim': (1279, 345),
        'ouvert_button_dim': (1249, 365),
        'ferme_button_dim': (1295, 365)
    },
    'SV24': {
        'frame_dim': (1289, 148),
        'status_dim': (1305, 158),
        'label_dim': (1325, 178),
        'ouvert_button_dim': (1299, 198),
        'ferme_button_dim': (1345, 198)
    },
    'SV31': {
        'frame_dim': (145, 356),
        'status_dim': (164, 366),
        'label_dim': (184, 386),
        'ouvert_button_dim': (155, 406),
        'ferme_button_dim': (201, 406)
    },
    'SV32': {
        'frame_dim': (403, 327),
        'status_dim': (422, 337),
        'label_dim': (442, 357),
        'ouvert_button_dim': (413, 377),
        'ferme_button_dim': (459, 377)
    },
    'SV33': {
        'frame_dim': (658, 312),
        'status_dim': (677, 322),
        'label_dim': (697, 342),
        'ouvert_button_dim': (668, 362),
        'ferme_button_dim': (714, 362)
    },
    'SV34': {
        'frame_dim': (658, 590),
        'status_dim': (677, 600),
        'label_dim': (697, 620),
        'ouvert_button_dim': (668, 640),
        'ferme_button_dim': (714, 640)
    },
    'SV35': {
        'frame_dim': (1600, 290),
        'status_dim': (1629, 300),
        'label_dim': (1649, 320),
        'ouvert_button_dim': (1610, 340),
        'ferme_button_dim': (1656, 340)
    },
    'SV36': {
        'frame_dim': (1600, 609),
        'status_dim': (1629, 619),
        'label_dim': (1649, 639),
        'ouvert_button_dim': (1610, 659),
        'ferme_button_dim': (1656, 659)
    }
}










    def End_program(self):  
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        reply = msgBox.warning(MainWindow, "Warning", 
            "Are you sure to quit?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.worker.stop()
            if self.worker_thread.is_alive():
                self.worker_thread.join()
            print("\n\n\nYou closed the program.\nDid it work bitch (ง'-̀'́)ง  Ϟ  ฝ('-'ฝ)\n\n\n")
            QCoreApplication.quit()
    
    # Data sending function
    def send_data(self, text):
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.sendto(bytes(text,'utf-8'), adress)

class SplashScreen(QSplashScreen):
    def __init__(self, pixmap):
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.SplashScreen)

        self.setStyleSheet("background-color: white;")

        self.pixmap = pixmap

        self.splash_width = pixmap.width()
        self.splash_height = pixmap.height() + 50

        self.setFixedSize(self.splash_width, self.splash_height)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(10, pixmap.height() + 10, pixmap.width() - 20, 20)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: #1a75ff;
                width: 20px;
                height: 20px;
            }
        """)
        self.percent_label = QLabel('0%')
        self.percent_label.setFont(QFont('Arial', 16))
        self.percent_label.setAlignment(Qt.AlignCenter)

    def drawContents(self, painter):
        painter.drawPixmap(QRect(0, 0, self.pixmap.width(), self.pixmap.height()), self.pixmap)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.percent_label.setText(f"{value}%")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    splash_pix = QPixmap('Logo_Arrax.png')
    splash = SplashScreen(splash_pix)

    screen = app.primaryScreen()
    screen_geometry = screen.geometry()
    x = (screen_geometry.width() - splash.splash_width) // 2
    y = (screen_geometry.height() - splash.splash_height) // 2
    splash.move(x, y)

    splash.show()

    for i in range(1, 101):
        time.sleep(0.01)    
        splash.update_progress(i)
        app.processEvents()

    MainWindow = QMainWindow()
    ui = Main()
    ui.setupUi(MainWindow)

    splash.finish(MainWindow)

    MainWindow.showFullScreen()

    sys.exit(app.exec_())