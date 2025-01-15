import sys
import csv
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QTimer
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from serial import Serial, SerialException

# Define the number of inputs as a global variable
NUM_INPUTS = 1

class SerialPlotter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.initSerial()
        self.initPlot()
        self.startTimer()
        self.initCSV()

    def initUI(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        self.button_layout = QHBoxLayout()
        for i in range(1, 6):
            button = QPushButton(f'Button {i}', self)
            self.button_layout.addWidget(button)
        self.layout.addLayout(self.button_layout)

    def initSerial(self):
        try:
            self.serial_port = Serial('COM4', 9600, timeout=1)
            print("Serial port opened successfully.")
        except SerialException as e:
            print(f"Error opening serial port: {e}")
            sys.exit(1)

    def initPlot(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_ylim(0, 5)  # Set y-axis range
        self.x_data = []
        self.y_data = [[] for _ in range(NUM_INPUTS)]  # Initialize for NUM_INPUTS values

    def startTimer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.updatePlot)
        self.timer.start(50)  # Update every 50 milliseconds (increase if needed)

    def initCSV(self):
        self.csv_file = open('data.csv', 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow([f'Value {i+1}' for i in range(NUM_INPUTS)])  # Write headers for NUM_INPUTS values

    def updatePlot(self):
        try:
            line = self.serial_port.readline().decode('utf-8').strip()
            if line:
                print(f"Received line: {line}")  # Debugging statement
                values = self.extract_values_from_line(line)
                
                if values and len(values) == NUM_INPUTS:
                    self.csv_writer.writerow(values)
                    
                    self.x_data.append(self.x_data[-1] + 1 if self.x_data else 0)
                    if len(self.x_data) > 50:
                        self.x_data = self.x_data[-50:]
                    
                    for i in range(NUM_INPUTS):
                        self.y_data[i].append(values[i])
                        self.y_data[i] = self.y_data[i][-50:]
                    
                    self.ax.clear()
                    for i in range(NUM_INPUTS):
                        self.ax.plot(self.x_data[-len(self.y_data[i]):], self.y_data[i], label=f'Value {i + 1}')
                    self.ax.set_ylim(0, 5)  # Set y-axis range
                    self.ax.legend()
                    self.canvas.draw()
        except (ValueError, SerialException) as e:
            print(f"Error reading line: {e}")

    def extract_values_from_line(self, line):
        try:
            values = [float(line)]  # Assume the line is a single float value
            print(f"Extracted values: {values}")  # Debugging statement
            return values
        except ValueError as e:
            print(f"Error extracting values from line: {e}")
            return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = SerialPlotter()
    main_win.show()
    sys.exit(app.exec_())