from PyQt6.QtWidgets import (
    QWidget,
    QGridLayout,
    QTimeEdit,
)
from PyQt6.QtCore import Qt, QTime
from qtrangeslider import QRangeSlider


class VideoWidget(QWidget):
    def __init__(self, max_time, height):
        super().__init__()

        self.layout = QGridLayout()

        # self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider = QRangeSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(max_time)
        self.slider.setValue((0, max_time))

        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm:ss")
        self.start_time_edit.setTime(QTime(0, 0, 0))  # 初始开始时间为0:00

        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("HH:mm:ss")
        self.end_time_edit.setTime(QTime(0, 0, 0))  # 初始结束时间为0:00

        self.slider.setFixedHeight(height)
        self.end_time_edit.setFixedHeight(height)
        self.start_time_edit.setFixedHeight(height)

        self.layout.addWidget(self.slider, 0, 0, 1, 1)
        self.layout.addWidget(self.start_time_edit, 0, 1, 1, 1)
        self.layout.addWidget(self.end_time_edit, 0, 2, 1, 1)

        self.slider.valueChanged.connect(self.on_slider_value_changed)

        self.setLayout(self.layout)

    def set_max_time(self, max_time):
        self.slider.setMaximum(max_time)

    def on_slider_value_changed(self):
        start_time, end_time = self.slider.value()

        self.start_time_edit.setTime(QTime(0, 0, 0).addSecs(start_time))
        self.end_time_edit.setTime(QTime(0, 0, 0).addSecs(end_time))

    def set_slider_value(self, start_time, end_time):
        self.slider.setValue((start_time, end_time))

    def get_start_time(self):
        midnight = QTime(0, 0, 0)
        return midnight.secsTo(self.start_time_edit.time())

    def get_end_time(self):
        midnight = QTime(0, 0, 0)
        return midnight.secsTo(self.end_time_edit.time())

    def set_start_time(self, time):
        self.start_time_edit.setTime(QTime(0, 0, 0).addSecs(time))

    def set_end_time(self, time):
        self.end_time_edit.setTime(QTime(0, 0, 0).addSecs(time))
