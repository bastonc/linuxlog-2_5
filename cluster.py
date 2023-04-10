import socket
from time import sleep

from PyQt5.QtCore import QThread, pyqtSignal


class ClusterThread(QThread):
    reciev_spot_signal = pyqtSignal(object)

    def __init__(self, settings_dict, parent=None):
        super().__init__()
        self.settings_dict = settings_dict
        self.HOST = self.settings_dict['telnet-host']
        self.PORT = self.settings_dict['telnet-port']
        self.parent = parent
        self.telnet_socket = None
        self.connecting_telnet()

    def connecting_telnet(self):
        print("start Cluster")
        call = self.settings_dict['my-call']
        while 1:
            try:
                self.telnet_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.telnet_socket.connect((self.HOST, int(self.PORT)))
                break
            except:
                self.parent.set_telnet_wrong(text="Telnet --")
                QThread.sleep(3)
                continue
        message = (call + "\n").encode('ascii')
        while 1:
            in_message = self.telnet_socket.recv(1024)
            self.reciev_spot_signal.emit(in_message)
            if in_message.decode(self.settings_dict['encodeStandart']).lower().strip() == "login:":
                self.telnet_socket.send(message)
                break
        print('Starting Telnet cluster:', self.HOST, ':', self.PORT, '\nCall:', call, '\n')

    def send_to_telnet(self, message):
        self.telnet_socket.send((message + "\n").encode('ascii'))


    def run(self):
        while 1:
            try:
                read_string_telnet = self.telnet_socket.recv(1024)
                #print(read_string_telnet)
                if read_string_telnet != '':
                    self.parent.set_telnet_stat()
                    self.reciev_spot_signal.emit(read_string_telnet)
                sleep(0.2)
            except BaseException:
                self.parent.set_telnet_wrong(text="Telnet not connection")
                continue
