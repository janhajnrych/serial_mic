from serial import Serial, serialutil
from PyQt5.QtCore import QMutex, QObject, pyqtSignal
import numpy as np

class Reader(QObject):
    finished = pyqtSignal()
    mutex = QMutex()
    
    def __init__(self, buffer_size): 
        super().__init__()
        self.__serial_device = self.try_open()
        self.__serial_device.flushInput()
        self.__buffer_size = buffer_size
        self.signal_data = np.zeros(self.__buffer_size).ravel()
        self.time_data = np.zeros(self.__buffer_size).ravel()
        self.first_timestamp = None
        self.should_run = False

    def try_open(self):
        try:
            device = Serial('/dev/ttyACM0')
        except serialutil.SerialException as e:
            print("Serial device not ready", str(e))
            exit(1)
        return device
    
    def run(self):
        self.should_run = True
        print("start reading")
        while self.should_run:
            timestamp, data = self.__get_next_serial_data_point()
            if data is None or timestamp is None:
                continue
            self.mutex.lock()
            self.signal_data = np.roll(self.signal_data, 1)
            self.signal_data[0] = data
            if self.first_timestamp is None:
                self.first_timestamp = timestamp
            self.time_data = np.roll(self.time_data, 1)
            self.time_data[0] = (timestamp - self.first_timestamp)/1000.0
            self.mutex.unlock()
        print("finished reading")
        self.finished.emit()

    def get_signals(self, n_elem):
        return self.signal_data[:n_elem]

    def get_timestamps(self, n_elem):
        return self.time_data[:n_elem]
    
    def get_avg_sampling_rate(self, n_elem):
        diff = self.time_data[1:n_elem+1] - self.time_data[:n_elem]
        return np.abs(np.mean(diff))

    def __get_next_serial_data_point(self):
        try:
            serial_bytes = self.__serial_device.readline()
            decoded_bytes = serial_bytes.decode("utf-8")
            tokens = decoded_bytes.split("/")
            if len(tokens) < 2:
                return None, None
            timestamp = int(tokens[0])
            value = int(tokens[1])
        except ValueError as value_error:
            print(str(value_error))
            return None, None
        except serialutil.SerialException as serial_error:
            print(str(serial_error))
            self.should_run = False
            return None, None
        return timestamp, value
