import os.path

from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import Qt, QRect, QEvent
from PyQt6.QtGui import QIcon, QCursor, QPainter
from PyQt6.QtWidgets import QWidget, QSlider, QLabel, QVBoxLayout, QGraphicsEffect


class Meter(QWidget):
    def __init__(self, values: list, current_value: int, avg: int) -> object:
        super().__init__()
        self.values = values
        self.current_value = current_value
        self.initUI()
    def initUI(self):
        print("it's meter")
        self.css_style = os.path.join(os.path.dirname(__file__), "meter.css")
        self.setStyleSheet(open(Path(__file__).parent/self.css_style).read())
        self.setWindowTitle('LinuxLog | meter')
        self.setWindowIcon(QIcon('logo.png'))
        #self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.meter_slider = QSlider()
        self.meter_slider.setOrientation(Qt.Orientation.Horizontal)
        self.meter_slider.setFixedHeight(30)
        self.meter_slider.setRange(1,100)
        self.meter_slider.setStyleSheet("QSlider{ background: #000000}")
        self.set_current_value(self.current_value)
        self.meter_label = QLabel(" | ".join(self.values))
        self.meter_lay = QVBoxLayout()
        self.meter_lay.addWidget(self.meter_slider)
        self.meter_lay.addWidget(self.meter_label)
        self.setLayout(self.meter_lay)
        self.show()

    def mousePressEvent(self, event):
        print("mousePressEvent")
        #self.setWindowFlags(Qt.WindowType.WindowTitleHint)

    def set_s_meter(self, dBm):
        self.set_current_value(round(self.dBm_to_value(dBm)))
    def dBm_to_value(self, level_s):
        percent_100 = (-13.0)
        percent_0 = (-121.0)
        return ((float(level_s) - percent_0)/(percent_100 - percent_0)) * 100

    def set_current_value(self, value):
        self.current_value = value
        self.show_current_value()

    def show_current_value(self):
        self.meter_slider.setSliderPosition(self.current_value)

class CustomMeter(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300, 100)
        self.setWindowTitle("Custom Meter")
        self.initUI()
    def initUI(self):
        self.rec = QRect()
        self.painter = QPainter()
        self.painter.begin(self)
        s_level = 100
        #self.set_s_meter(0)#
        self.painter.drawLine(0, round(self.rec.height() / 2), s_level, round(self.rec.height() / 2))
        self.painter.end()
    def paintEvent(self, event):

        if False:
            rec = QRect()


        ###
        #self.set_s_meter(0)
        #

    def set_s_meter(self, dBm):

        s_level = self.dBm_to_value(float(dBm))
        print(s_level)

        self.painter.drawLine(0, round(self.rec.height() / 2), s_level, round(self.rec.height() / 2))
        self.painter.end()
    def dBm_to_value(self, level_s):
        percent_100 = (-13.0)
        percent_0 = (-121.0)
        percent = ((float(level_s) - percent_0)/(percent_100 - percent_0)) * 100
        return round(percent * self.rec.width() / 100)