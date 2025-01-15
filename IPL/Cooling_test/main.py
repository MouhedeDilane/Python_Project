import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QComboBox,
    QPushButton, QFileDialog, QSizePolicy, QLineEdit, QLabel, QGridLayout, QSpinBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig, self.axs = plt.subplots(2, 2, figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

    def plot_data(self, time, PS1, PS2, PS3, PS1_avg, PS2_avg, PS3_avg, window_size):
        self.axs[0][0].clear()
        self.axs[0][0].plot(time, PS1, label='PS1')
        self.axs[0][0].plot(time, PS2, label='PS2')
        self.axs[0][0].plot(time, PS3, label='PS3')
        self.axs[0][0].set_title('Original Data')
        self.axs[0][0].set_xlabel('Time')
        self.axs[0][0].set_ylabel('Pressure')
        self.axs[0][0].legend()
        self.axs[0][0].grid(True)

        self.axs[0][1].clear()
        self.axs[0][1].plot(time, PS1_avg, label='PS1 (Avg)')
        self.axs[0][1].plot(time, PS2_avg, label='PS2 (Avg)')
        self.axs[0][1].plot(time, PS3_avg, label='PS3 (Avg)')
        self.axs[0][1].set_title('Sliding Average')
        self.axs[0][1].set_xlabel('Time')
        self.axs[0][1].set_ylabel('Pressure')
        self.axs[0][1].legend()
        self.axs[0][1].grid(True)

        self.axs[1][0].clear()
        self.axs[1][0].plot(time, abs(PS2 - PS3), label='|PS2 - PS3|')
        self.axs[1][0].set_title('Absolute Difference')
        self.axs[1][0].set_xlabel('Time')
        self.axs[1][0].set_ylabel('Absolute Difference')
        self.axs[1][0].legend()
        self.axs[1][0].grid(True)

        self.axs[1][1].clear()
        self.axs[1][1].plot(time, (abs(PS2 - PS3)).rolling(window=window_size).mean(), label='Avg |PS2 - PS3|')
        self.axs[1][1].set_title('Average Absolute Difference')
        self.axs[1][1].set_xlabel('Time')
        self.axs[1][1].set_ylabel('Average Absolute Difference')
        self.axs[1][1].legend()
        self.axs[1][1].grid(True)

        self.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CSV Plotter")
        self.resize(1920, 1080)
        self.main_layout = QVBoxLayout()

        self.grid_layout = QGridLayout()

        self.combo_box = QComboBox()
        self.combo_box.addItem("Select CSV File")
        self.combo_box.activated[str].connect(self.on_combobox_activated)
        self.grid_layout.addWidget(self.combo_box, 0, 0, 1, 3)

        self.xmin_label = QLabel("X min:")
        self.grid_layout.addWidget(self.xmin_label, 1, 0)

        self.xmin_input = QLineEdit()
        self.grid_layout.addWidget(self.xmin_input, 1, 1)

        self.xmax_label = QLabel("X max:")
        self.grid_layout.addWidget(self.xmax_label, 1, 2)

        self.xmax_input = QLineEdit()
        self.grid_layout.addWidget(self.xmax_input, 1, 3)

        self.window_size_label = QLabel("Window Size:")
        self.grid_layout.addWidget(self.window_size_label, 1, 4)

        self.window_size_spinbox = QSpinBox()
        self.window_size_spinbox.setMinimum(5)  # Set minimum value to 5
        self.window_size_spinbox.setMaximum(100)
        self.window_size_spinbox.setValue(3)  # Default value
        self.window_size_spinbox.valueChanged.connect(self.update_window_size)  # Connect signal
        self.grid_layout.addWidget(self.window_size_spinbox, 1, 6)

        self.apply_button = QPushButton("Apply X Limits")
        self.apply_button.clicked.connect(self.apply_x_limits)
        self.grid_layout.addWidget(self.apply_button, 1, 5)

        self.main_layout.addLayout(self.grid_layout)

        self.canvas = MplCanvas(self, width=8, height=8, dpi=100)  # Square plot
        self.main_layout.addWidget(self.canvas)

        self.container = QWidget()
        self.container.setLayout(self.main_layout)
        self.setCentralWidget(self.container)

        # Set directory here
        self.directory = os.path.join(os.path.dirname(__file__), "Pressure_data")

        self.load_csv_files(self.directory)

        self.xmin = None
        self.xmax = None

    def load_csv_files(self, directory):
        self.combo_box.clear()
        self.combo_box.addItem("Select CSV File")
        self.csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
        for file in self.csv_files:
            self.combo_box.addItem(file)
        self.directory = directory

    def on_combobox_activated(self, text):
        if text != "Select CSV File":
            file_path = os.path.join(self.directory, text)
            self.load_and_plot_csv(file_path)
            self.current_file_path = file_path  # Save current file path

    def load_and_plot_csv(self, file_path):
        self.data = pd.read_csv(file_path)
        time = self.data['time']
        PS1 = self.data['PS1']
        PS2 = self.data['PS2']
        PS3 = self.data['PS3']
        
        window_size = self.window_size_spinbox.value()  # Get the window size from the spinbox
        PS1_avg = PS1.rolling(window=window_size).mean()
        PS2_avg = PS2.rolling(window=window_size).mean()
        PS3_avg = PS3.rolling(window=window_size).mean()

        self.canvas.plot_data(time, PS1, PS2, PS3, PS1_avg, PS2_avg, PS3_avg, window_size)

        # Set default values of xmin and xmax
        self.xmin_input.setText(str(time.min()))
        self.xmax_input.setText(str(time.max()))

    def apply_x_limits(self):
        xmin = self.xmin_input.text()
        xmax = self.xmax_input.text()

        if xmin and xmax:
            try:
                xmin = float(xmin)
                xmax = float(xmax)
                if xmin > xmax:
                    xmin, xmax = xmax, xmin
                if xmin < self.data['time'].iloc[0]:
                    xmin = self.data['time'].iloc[0]
                if xmax > self.data['time'].iloc[-1]:
                    xmax = self.data['time'].iloc[-1]

                self.xmin_input.setText(str(xmin))
                self.xmax_input.setText(str(xmax))

                self.xmin = xmin
                self.xmax = xmax

                self.canvas.axs[0][0].set_xlim([self.xmin, self.xmax])
                self.canvas.axs[0][1].set_xlim([self.xmin, self.xmax])
                self.canvas.axs[1][0].set_xlim([self.xmin, self.xmax])
                self.canvas.axs[1][1].set_xlim([self.xmin, self.xmax])
                self.canvas.draw()
            except ValueError:
                pass  # Ignore invalid input

    def update_window_size(self):
        # Get the new window size from the spin box
        window_size = self.window_size_spinbox.value()

        # Reload and plot the CSV data with the new window size
        if hasattr(self, 'current_file_path'):
            self.load_and_plot_csv(self.current_file_path)

            # Set x-limits if they were previously defined
            if self.xmin is not None and self.xmax is not None:
                self.canvas.axs[0][0].set_xlim([self.xmin, self.xmax])
                self.canvas.axs[0][1].set_xlim([self.xmin, self.xmax])
                self.canvas.axs[1][0].set_xlim([self.xmin, self.xmax])
                self.canvas.axs[1][1].set_xlim([self.xmin, self.xmax])
                self.canvas.draw()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())