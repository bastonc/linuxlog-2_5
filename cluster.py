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
        self.reciev_string = ""

    def connecting_telnet(self):
        print("start Cluster")
        call = self.settings_dict['my-call']
        while 1:
            try:
                self.telnet_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.telnet_socket.connect((self.HOST, int(self.PORT)))
                print("Telnet is connected")
                break
            except:
                self.parent.set_telnet_wrong(text="Telnet --")
                QThread.sleep(3)
                continue
        message = (call + "\n").encode('ascii')
        while 1:
            in_message = self.telnet_socket.recv(1024)
            # print("Reciever circle", in_message.decode(self.settings_dict['encodeStandart']).lower().strip())

            self.reciev_spot_signal.emit(in_message)
            if in_message.decode(self.settings_dict['encodeStandart']).lower().strip().find("login:") or \
                in_message.decode(self.settings_dict['encodeStandart']).lower().strip().find("please enter your call:"):
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
                    reciev_fragment = read_string_telnet.decode(self.settings_dict['encodeStandart'], errors='ignore').split("\r\n")
                    for sub_string in reciev_fragment:
                        # print(f"Sub_string: {sub_string} sub_st[0:2]: {sub_string[:2]} sub_str[:-1]: {sub_string[-1:]}")
                        if sub_string[:2] == "DX" and sub_string[-1:] == "Z":
                            self.reciev_string = sub_string
                            # print(f"reciever_string: {self.reciev_string}")
                            self.parent.set_telnet_stat()
                            self.reciev_spot_signal.emit(self.reciev_string)
                            self.reciev_string = ""
                        # elif sub_string[:2] == "DX" and sub_string[:-1] != "Z":
                        #     self.reciev_string += sub_string
                        # elif sub_string[:2] != "DX" and sub_string[:-1] !="Z":
                        #     self.reciev_string += sub_string
                        #print(f"reciever_string: {self.reciev_string}")
                        if self.reciev_string[:2] == "DX" and self.reciev_string[:-1] == "Z":
                            self.parent.set_telnet_stat()
                            self.reciev_spot_signal.emit(self.reciev_string)
                            self.reciev_string = ""
                sleep(0.2)
            except BaseException:
                self.parent.set_telnet_wrong(text="Telnet not connection")
                continue
