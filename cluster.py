import re
import socket
from time import sleep

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from threads_lib import Set_connect_thread


class ClusterThread(QThread):
    reciev_spot_signal = pyqtSignal(object)
    reciev_string_signal = pyqtSignal(object)

    def __init__(self, settings_dict, parent=None):
        super().__init__()
        self.settings_dict = settings_dict
        self.HOST = self.settings_dict['telnet-host']
        self.PORT = self.settings_dict['telnet-port']
        self.parent = parent
        self.telnet_socket = None
        self.cluster_connect_flag = False
        self.connecting_telnet()
        self.reciev_string = ""

    def connecting_telnet(self):
        # print("start Cluster")

        self.connect = Set_connect_thread(self.HOST, int(self.PORT))
        self.connect.connect_socket_signal.connect(self.connect_ok)
        self.connect.error_connect_signal.connect(self.connect_error)
        self.connect.start()

    @pyqtSlot(object)
    def connect_ok(self, connect_object: socket.socket):
        message = (self.settings_dict['my-call'] + "\n").encode('ascii')
        self.telnet_socket = connect_object
        while 1:
            in_message = self.telnet_socket.recv(1024)
            print("Reciever circle", in_message.decode(self.settings_dict['encodeStandart']).lower().strip())

            self.reciev_spot_signal.emit(in_message)
            if in_message.decode(self.settings_dict['encodeStandart']).lower().strip().find("login:") or \
                in_message.decode(self.settings_dict['encodeStandart']).lower().strip().find("please enter your call:"):
                    self.telnet_socket.send(message)
                    self.parent.set_telnet_stat()
                    print(f"send message")
                    break
            sleep(0.1)
        self.start()
        print('Starting Telnet cluster:', self.HOST, ':', self.PORT, '\nCall:', self.settings_dict['my-call'], '\n')

    @pyqtSlot(object)
    def connect_error(self, inbox_message):
        self.parent.set_telnet_wrong(text="Telnet --")

    def send_to_telnet(self, message):
        print(f"Message to telnet server")
        self.telnet_socket.send(bytes(message + "\n", "ascii"))

    def get_cluster_connect_status(self):
        return self.cluster_connect_flag


    def run(self):
        # print("start main loop cluster")
        while 1:
            try:
                print(f"cluster Loop")

                read_string_telnet = self.telnet_socket.recv(1024)
                print(read_string_telnet)
                if bytes.decode(read_string_telnet, self.settings_dict['encodeStandart'], errors="ignore") not in ('', None):
                    reciev_fragment = bytes.decode(read_string_telnet, self.settings_dict['encodeStandart'], errors="ignore").split("\r\n")
                    # print(f"reciev_fragment{reciev_fragment[0]}")
                    reciev_fragment[0] = re.search(r'.*Z', reciev_fragment[0])
                    if reciev_fragment[0] is not None:
                        reciev_fragment[0] = reciev_fragment[0].group()
                    #print(f"String strip {reciev_fragment[0]}")
                    for sub_string in reciev_fragment:
                        # print(f"Sub_string: {sub_string} sub_st[0:2]: {sub_string[:2]} sub_str[:-1]: {sub_string[-1:]}")
                        if sub_string is not None and sub_string[:2] == "DX" and sub_string[-1:] == "Z":
                            self.reciev_string = sub_string
                            # print(f"reciever_string: {self.reciev_string}")
                            self.parent.set_telnet_stat()
                            self.reciev_spot_signal.emit(self.reciev_string)
                            self.reciev_string = ""
                        else:
                            self.reciev_string_signal.emit(read_string_telnet)                                           # if self.reciev_string[:2] == "DX" and self.reciev_string[:-1] == "Z":
                        #     self.parent.set_telnet_stat()
                        #     self.reciev_spot_signal.emit(self.reciev_string)
                        #     self.reciev_string = ""

                sleep(0.2)
            except BaseException:
                #self.telnet_socket.close()
                self.parent.set_telnet_wrong(text="· Telnet")
                self.connecting_telnet()
                continue
