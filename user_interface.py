from serial import Serial, serialutil

import sys
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from scipy.fft import fft, fftfreq
from serial_read import Reader


class TimeSeriesCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.subplot_time_series = self.figure.add_subplot(211)
        self.subplot_frequency = self.figure.add_subplot(212)
        
        super(TimeSeriesCanvas, self).__init__(self.figure)
        if parent is not None:
            self.setParent(parent)


class MainWindow(QtWidgets.QMainWindow):

    N_PLOT_PER_SEC = 3
    N_HIST_SEC = 3
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.frame = QtWidgets.QFrame() 
        layout = QtWidgets.QHBoxLayout()
        central = QtWidgets.QWidget()
        
        self.plotting = False
        left_menu = self.construct_left_menu()
        layout.addLayout(left_menu, 1)
        self.canvas = TimeSeriesCanvas(parent=self.frame, 
                                       width=8, height=6, dpi=100)
        layout.addWidget(self.frame, 6)
        central.setLayout(layout);
        self.setCentralWidget(central)
        self.resize(500, 500)
        
        self.data_size = 256
        self.xdata = np.linspace(0, 5, num=self.data_size)
        self.ydata = np.zeros(self.data_size).ravel()
        
        self.start_reader_thread()
        
        self.timer = self.construct_timer()
        self.timer.start()
    
    def construct_left_menu(self):
        self.start_button = QtWidgets.QPushButton("start")
        self.stop_button = QtWidgets.QPushButton("stop")
        self.clear_button = QtWidgets.QPushButton("clear")
        self.autoscale_checkbox = QtWidgets.QCheckBox("auto-scale")
        self.start_button.clicked.connect(self.start_plotting)
        self.stop_button.clicked.connect(self.stop_plotting)
        
        secondary_layout_max, self.max_edit = self.create_named_value_box("max")
        secondary_layout_min, self.min_edit = self.create_named_value_box("min")

        left_menu = QtWidgets.QVBoxLayout()
        left_menu.addWidget(self.start_button)
        left_menu.addWidget(self.stop_button)
        left_menu.addWidget(self.autoscale_checkbox)
        left_menu.addLayout(secondary_layout_min)
        left_menu.addLayout(secondary_layout_max)
        
        self.autoscale_checkbox.toggled.connect(self.auto_scale_checkbox_toggled)
        self.autoscale_checkbox.setChecked(True)    
        return left_menu
    
    def construct_timer(self):
        timer = QtCore.QTimer()
        timer.setInterval(1000/self.N_PLOT_PER_SEC)
        timer.timeout.connect(self.update)
        return timer
    
    def create_named_value_box(self, name):
        value_edit_box = QtWidgets.QSpinBox()
        value_edit_box.setRange(0, 3000)
        secondary_layout_max = QtWidgets.QHBoxLayout()
        secondary_layout_max.addWidget(QtWidgets.QLabel(name))
        secondary_layout_max.addWidget(value_edit_box)
        return secondary_layout_max, value_edit_box
    
    def auto_scale_checkbox_toggled(self, checked):
        self.max_edit.setEnabled(not checked)
        self.min_edit.setEnabled(not checked)
       
    def start_plotting(self):
        self.plotting = True

    def stop_plotting(self):
        self.plotting = False
        
    def update(self):
        if not self.plotting:
            return
        self.canvas.figure.subplots_adjust(hspace=0.25)
        self.update_time_series_plot()
        self.update_frequency_domain_plot()
        self.canvas.draw()

    def update_time_series_plot(self):
        self.ydata = np.flip(self.worker.get_signals(self.data_size))
        self.xdata = np.flip(self.worker.get_timestamps(self.data_size))
        self.canvas.subplot_time_series.cla()  # Clear the canvas.
        self.canvas.subplot_time_series.set_title('Microphone stream')
        if not self.autoscale_checkbox.isChecked():
            self.canvas.subplot_time_series.set_ylim(self.min_edit.value(),
                                      self.max_edit.value())
        self.canvas.subplot_time_series.plot(self.xdata, self.ydata, 'b')
        self.canvas.subplot_time_series.grid(True)
        
    def update_frequency_domain_plot(self):
        yf = fft(self.ydata)
        N = 64
        dt = self.worker.get_avg_sampling_rate(10)
        xf = fftfreq(N, d=dt)[:N//2]
        self.canvas.subplot_frequency.cla()  # Clear the canvas.
        self.canvas.subplot_frequency.set_title('Frequency Analyis (FFT)')
        self.canvas.subplot_frequency.bar(xf[1:N//2],
                                           2.0/N * np.abs(yf[1:N//2]),
                                           color='b')
        self.canvas.subplot_frequency.grid(True)      

    def start_reader_thread(self):  
        self.thread = QThread()
        self.worker = Reader(self.data_size)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec_()
    
