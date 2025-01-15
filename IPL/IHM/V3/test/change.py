import sys
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QComboBox, QPushButton
from PyQt5.QtGui import QPainter, QPen, QBrush, QPaintEvent
from PyQt5.QtCore import Qt, QRect

class ShapeLabel(QLabel):
    def __init__(self, parent=None):
        super(ShapeLabel, self).__init__(parent)
        self.shape = None

    def setShape(self, shape):
        self.shape = shape
        self.update()

    def paintEvent(self, event):
        super(ShapeLabel, self).paintEvent(event)
        if self.shape:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            if self.shape == "Square":
                rect_pen = QPen(Qt.black, 2)
                painter.setPen(rect_pen)
                painter.setBrush(QBrush(Qt.green, Qt.SolidPattern))
                painter.drawRect(QRect(75, 75, 100, 100))
            elif self.shape == "Circle":
                circle_pen = QPen(Qt.red, 2)
                painter.setPen(circle_pen)
                painter.setBrush(QBrush(Qt.blue, Qt.SolidPattern))
                painter.drawEllipse(75, 75, 100, 100)

class ShapeWidget(QWidget):
    def __init__(self):
        super(ShapeWidget, self).__init__()

        # Create control frame
        self.TVC_control_frame = QFrame(self)
        self.TVC_control_frame.setFrameShape(QFrame.StyledPanel)
        self.TVC_control_frame.setGeometry(QRect(10, 500, 250, 100))
        # Main vertical layout for the frame
        self.frame_TVC_control = QVBoxLayout(self.TVC_control_frame)
        self.frame_TVC_control.setAlignment(Qt.AlignCenter)

        # Create a QLabel for the title
        self.TVC_label = QLabel("Sequence control", self.TVC_control_frame)
        self.TVC_label.setAlignment(Qt.AlignCenter)
        self.TVC_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        self.frame_TVC_control.addWidget(self.TVC_label)

        # Create a horizontal layout for the combo box and button
        self.hbox_layout_TVC = QHBoxLayout()
        self.hbox_layout_TVC.setAlignment(Qt.AlignCenter)

        # Add combo box to the horizontal layout
        self.comboBox_TVC = QComboBox(self.TVC_control_frame)
        self.comboBox_TVC.setFixedSize(120, 30)
        self.comboBox_TVC.addItems(['None', 'Square', 'Circle', 'Up-Down', 'Left-Right'])
        self.comboBox_TVC.setStyleSheet("""
            QComboBox {
                border: 2px solid #000000; /* Blue border */
                border-radius: 5px; /* Rounded corners */
                padding: 5px 10px; /* Padding inside the box */
                background-color: #F0F0F0; /* Light grey background */
                color: #333; /* Dark grey text color */
            }
            QComboBox QAbstractItemView {
                border: 2px solid #000000; /* Border around the dropdown list */
                selection-background-color: #F0F0F0; /* Background color of the selected item */
                selection-color: black; /* Text color of the selected item */
                background-color: #F0F0F0; /* Background color of the dropdown list */
            }
        """)
        self.hbox_layout_TVC.addWidget(self.comboBox_TVC)

        # Add a spacer item to push the button to the right
        self.hbox_layout_TVC.addStretch()

        # Customize the button
        self.viewButton_TVC = QPushButton("View TVC shape", self.TVC_control_frame)
        self.viewButton_TVC.setFixedSize(100, 30)  # Custom size
        self.viewButton_TVC.setStyleSheet("""
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
        self.hbox_layout_TVC.addWidget(self.viewButton_TVC)

        # Add the horizontal layout to the vertical layout
        self.frame_TVC_control.addLayout(self.hbox_layout_TVC)

        # Create a custom QLabel for drawing
        self.TVC_drawing = ShapeLabel(self)
        self.TVC_drawing.setMinimumSize(250, 250)
        self.frame_TVC_control.addWidget(self.TVC_drawing)

        # Connect the button click to the shape drawing logic
        self.viewButton_TVC.clicked.connect(self.updateShape)

    def updateShape(self):
        shape = self.comboBox_TVC.currentText()
        self.TVC_drawing.setShape(shape)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ShapeWidget()
    window.setGeometry(100, 100, 300, 650)  # Set a larger window size to see the whole content
    window.show()
    sys.exit(app.exec_())