#!/usr/bin/python3
# -*- coding: utf-8 -*-
import serial
import time
import std
import protocols
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

class Cat_reciever(QThread):

    data_cat_signal = pyqtSignal(bytes)
    error_cat_signal = pyqtSignal(str)

    def __init__(self, settingsDict, serial_port, protocol_list):
        super().__init__()
        self.settingsDict = settingsDict
        self.status_flag_reciever = 1
        self.request_list = protocol_list
        self.ser = serial_port
    def run(self):


        print("Ser:_>", self.ser)
        while self.status_flag_reciever == 1:
            # Get freq from cat port
            for key in self.request_list:
                try:
                    self.ser.write(key)                  # send request into port (transciever)
                    time.sleep(0.2)                 # wait 0.2 sec (while transciever formed answer)
                    line_ser = self.ser.read(100)        # read from cat port
                    if line_ser != '':
                        self.data_cat_signal.emit(line_ser)
                except Exception:
                    print("CAT system:_> Can't read/write to TRX")
                time.sleep(0.2)



            #print("string from cat port:_>", line_ser)
            time.sleep(2)
        self.ser.close()
    def stop_cat_reciever(self):
        self.status_flag_reciever = 0


class Cat_start(QObject):
    def __init__(self, settingsDict, parent_window):
        super().__init__()
        self.settingsDict = settingsDict
        self.parent_window = parent_window
        if self.settingsDict['cat-parity'] == 'None':
            parity = serial.PARITY_NONE
        elif self.settingsDict['cat-parity'] == 'Odd':
            parity = serial.PARITY_ODD
        elif self.settingsDict['cat-parity'] == 'Even':
            parity = serial.PARITY_EVEN
        elif self.settingsDict['cat-parity'] == 'Mark':
            parity = serial.PARITY_MARK
        elif self.settingsDict['cat-parity'] == 'Space':
            parity = serial.PARITY_SPACE

        try:
            self.ser = serial.Serial('/dev/' + self.settingsDict['cat-port'],
                                 int(self.settingsDict['speed-cat']),
                                 timeout=int(self.settingsDict['timeout-cat']),
                                 parity=parity, rtscts=1)
            self.protocol_command_list = self.protocol_cat() # list of commands for models TRX
            self.start_reciever_cat()
            self.parent_window.set_cat_label(True)

        except Exception:
            std.std.message(self.parent_window, "Can't open "+self.settingsDict['cat-port'], "Error CAT system")
            self.parent_window.set_cat_label(False)

    def protocol_cat(self):
        if self.settingsDict['cat-protocol'] == 'Kenwood' or \
            self.settingsDict['cat-protocol'] == "ExpertSDR":
                self.protocol_decoder = protocols.Kenwood(self.settingsDict, self.parent_window, self.ser)
        elif self.settingsDict['cat-protocol'] == "Icom":
            self.protocol_decoder = protocols.Icom(self.settingsDict, self.parent_window, self.ser)

        comand_list = self.protocol_decoder.get_freq_mod_list()


        return comand_list

    def start_reciever_cat(self):
        self.reciever_cat = Cat_reciever(self.settingsDict, self.ser, self.protocol_command_list)
        self.reciever_cat.data_cat_signal.connect(self.set_freq_cat)
        self.reciever_cat.start()

    def stop_cat(self):
        self.reciever_cat.stop_cat_reciever()
        #self.parent_window.set_cat_label(False)

    @pyqtSlot(bytes)
    def set_freq_cat(self, data_byte):
        self.protocol_decoder.decoder_data(data_byte)

    def sender_cat(self, freq=None, mode=None):
        if freq != None: # if we have freq

            self.protocol_decoder.set_freq_rig(freq)
            std_value = std.std()
            band = std_value.get_std_band(freq)
            mode = std_value.mode_band_plan(band, freq)
            print(mode)
            time.sleep(0.2)
            self.protocol_decoder.set_mode_rig(mode)








