import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, QFrame, QCheckBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation


class RealTimePlot(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Real-Time Plot")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.x_data = []
        self.y_data = []

        # Create a frame for x-axis interval and curves controls
        self.controls_frame = QFrame(self)
        self.controls_frame.setFrameShape(QFrame.StyledPanel)
        layout.addWidget(self.controls_frame)

        # Layout for x-axis interval and curves controls
        controls_layout = QVBoxLayout(self.controls_frame)

        self.x_length_label = QLabel("X-Axis Interval:", self)
        controls_layout.addWidget(self.x_length_label)

        self.button_10 = QPushButton("10", self)
        self.button_10.clicked.connect(lambda: self.set_x_interval(10))
        controls_layout.addWidget(self.button_10)

        self.button_50 = QPushButton("50", self)
        self.button_50.clicked.connect(lambda: self.set_x_interval(50))
        controls_layout.addWidget(self.button_50)

        self.button_100 = QPushButton("100", self)
        self.button_100.clicked.connect(lambda: self.set_x_interval(100))
        controls_layout.addWidget(self.button_100)

        self.curve_label = QLabel("Number of Curves:", self)
        controls_layout.addWidget(self.curve_label)

        self.checkbox_1 = QCheckBox("Curve 1", self)
        self.checkbox_1.setChecked(True)  # Default to show the first curve
        controls_layout.addWidget(self.checkbox_1)

        self.checkbox_2 = QCheckBox("Curve 2", self)
        controls_layout.addWidget(self.checkbox_2)

        self.checkbox_3 = QCheckBox("Curve 3", self)
        controls_layout.addWidget(self.checkbox_3)

        self.checkbox_4 = QCheckBox("Curve 4", self)
        controls_layout.addWidget(self.checkbox_4)

        self.checkbox_5 = QCheckBox("Curve 5", self)
        controls_layout.addWidget(self.checkbox_5)

        self.checkbox_6 = QCheckBox("Curve 6", self)
        controls_layout.addWidget(self.checkbox_6)

        self.animation = FuncAnimation(self.fig, self.update_plot, interval=1000)

    def set_x_interval(self, interval):
        self.x_interval = interval

    def update_plot(self, frame):
        try:
            x_length = self.x_interval
        except AttributeError:
            x_length = 10

        checked_boxes = [self.checkbox_1, self.checkbox_2, self.checkbox_3, self.checkbox_4,self.checkbox_5,self.checkbox_6]
        
        self.x_data.append(len(self.x_data))
        self.y_data.append([random.random() for _ in range(len(checked_boxes))])  # Generate 4 random values for each curve
        self.ax.clear()

        num_checked_boxes = sum(1 for checkbox in checked_boxes if checkbox.isChecked())

        for i, checkbox in enumerate(checked_boxes):
            if num_checked_boxes == 1 and checkbox.isChecked():
                checkbox.setEnabled(False)
                self.ax.plot(self.x_data, [data[i] for data in self.y_data], label=f'Curve {i+1}')
            elif checkbox.isChecked():
                checkbox.setEnabled(True)
                self.ax.plot(self.x_data, [data[i] for data in self.y_data], label=f'Curve {i+1}')

        if max(self.x_data) - x_length < 0:
            self.ax.set_xlim(0, x_length)
        else:
            self.ax.set_xlim(max(self.x_data) - x_length, max(self.x_data))
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Value')
        self.ax.set_title('Real-Time Plot')
        self.ax.legend(loc='upper left')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RealTimePlot()
    window.show()
    sys.exit(app.exec_())

    