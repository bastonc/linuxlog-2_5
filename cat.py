#!/usr/bin/python3
# -*- coding: utf-8 -*-
import serial
import time
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

class Cat_reciever(QThread):

    data_cat_signal = pyqtSignal(bytes)
    error_cat_signal = pyqtSignal(str)

    def __init__(self, settingsDict, serial_port):
        super().__init__()
        self.settingsDict = settingsDict
        self.status_flag_reciever = 1
        self.request_list = [b"FA;", b"MD;"]
        self.ser = serial_port
    def run(self):


        print("Ser:_>", self.ser)
        while self.status_flag_reciever == 1:
            # Get freq from cat port
            for key in self.request_list:
                self.ser.write(key)                  # send request into port (transciever)
                time.sleep(0.2)                 # wait 0.2 sec (while transciever formed answer)
                line_ser = self.ser.read(100)        # read from cat port
                if line_ser != '':
                    self.data_cat_signal.emit(line_ser)
                time.sleep(0.3)



            #print("string from cat port:_>", line_ser)
            time.sleep(2)
        self.ser.close()

class Cat_start(QObject):
    def __init__(self, settingsDict, parent_window):
        super().__init__()
        self.settingsDict = settingsDict
        self.parent_window = parent_window
        self.ser = serial.Serial('/dev/' + self.settingsDict['cat-port'],
                                 int(self.settingsDict['speed-cat']),
                                 timeout=int(self.settingsDict['timeout-cat']),
                                 parity=serial.PARITY_NONE, rtscts=1)

        self.start_reciever_cat()

    def start_reciever_cat(self):
        self.reciever_cat = Cat_reciever(self.settingsDict, self.ser)
        self.reciever_cat.data_cat_signal.connect(self.set_freq_cat)
        self.reciever_cat.start()

    @pyqtSlot(bytes)
    def set_freq_cat(self, data_byte):
        freq_str = data_byte.decode("utf-8").replace(';','')
        if freq_str[:2] == "FA" and len(freq_str) <= 14:
            freq = freq_str.replace('FA','')
            self.parent_window.set_freq(freq.lstrip('0'))
            print ("Frequency:_>", freq_str)
        elif freq_str[:2] == "MD":
            print("Mode:_>", freq_str)

    def sender_cat(self, freq=None, mode=None):
        if freq != None: # if we have freq
            if len(freq) < 11:                          # for cat len freq = 11 digit
                freq = freq.zfill(11)                   # add '0' before freq
                #print("freq:_>", freq)
            self.ser.write(b'FA'+freq.encode("utf-8")+b";")



