import re
import socket
from time import sleep

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

#from rigctl import Rigctl


class Set_connect_thread(QThread):

    connect_socket_signal = pyqtSignal(object)
    error_connect_signal = pyqtSignal(object)

    def __init__(self, host, port):
        super().__init__()
        self.HOST = host
        self.PORT = port

    def run(self):
        while 1:
            try:
                self.telnet_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.telnet_socket.connect((self.HOST, int(self.PORT)))
                print(f"Connected to {self.HOST}:{self.PORT}")
                self.connect_socket_signal.emit(self.telnet_socket)
                break
            except:
                self.error_connect_signal.emit("Error")
                print(f"Except connect to {self.HOST}:{self.PORT}")
                QThread.sleep(3)
                continue

class RigctlLoop(QThread):

    frequency_signal = pyqtSignal(object)
    vfo_signal = pyqtSignal(object)
    mode_signal = pyqtSignal(object)
    ptt_signal = pyqtSignal(object)
    def __init__(self, rx1, rx2, sleep_time):
        super().__init__()
        self.incoming_string = None
        self.freq_cache = None
        self.vfo_cache = None
        self.mode_cache = None
        self.ptt_cache = None
        self.sleep_time = sleep_time
        self.rx1 = rx1
        self.rx1.rigctl_incoming_string.connect(self.rigctl_incoming_string)
        self.rx2 = rx2

    # def clean_str(self, input_bytes):
    #     if input_bytes is not None:
    #         return bytes.decode(input_bytes, "utf-8").replace("\n", "")

    def is_frequency(self, input_string):
        if input_string is not None and input_string.isdigit():
            return True

    def is_vfo(self, input_string):
        # print(self.incoming_string)
        if input_string is not None and input_string in ("VFOA", "VFOB"):
            return True

    def is_mode(self, input_string):
        # print(f"MODE: {input_string}")
        if input_string is not None and input_string in ("USB", "LSB", "AM", "CWR", "CW", "FM",
                                                         "PKTUSB", "PKTLSB",  "DIGI"):
            return True

    def get_frequency(self):
        freq = self.rx1.send("f")
        if self.is_frequency(freq) and freq != self.freq_cache:
            self.frequency_signal.emit(freq)
            self.freq_cache = freq
            # print(freq )
        # if self.is_frequency() and self.incoming_string != self.freq_cache:
        #     self.frequency_signal.emit(self.incoming_string)
        #     self.freq_cache = self.incoming_string
        #     print(self.incoming_string)

    def get_vfo(self):
        vfo = self.rx1.send("v")
        if self.is_vfo(vfo) and vfo != self.vfo_cache:
            self.vfo_signal.emit(vfo)
            self.vfo_cache = vfo
            # print(f"VFO: {vfo}")


    def get_mode(self):
        mode = self.rx1.send("m")
        mode = re.sub(r"\d*", "", mode).strip()
        if self.is_mode(mode) and mode != self.mode_cache:
            self.mode_signal.emit(mode)
            self.mode_cache = mode
            # print(f"MODE: {mode}")

    def get_ptt(self):
        ptt = self.rx1.send("t")
        # print(f"ptt: {ptt}")
        if ptt in ("0", "1") and ptt != self.ptt_cache:
            self.ptt_signal.emit(ptt)
            self.ptt_cache = ptt
            # print(f"MODE: {mode}")


    @pyqtSlot(object)
    def rigctl_incoming_string(self, incoming_string):
        self.incoming_string = incoming_string
        # print(self.incoming_string)

    def run(self):
        while 1:
            self.get_vfo()
            self.get_frequency()
            self.get_mode()
            self.get_ptt()

            sleep(self.sleep_time)
