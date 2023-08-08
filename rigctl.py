import socket
from time import sleep

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, QObject

from threads_lib import Set_connect_thread

class Rigctl_sender:

    string_send = pyqtSignal(str)

    def __init__(self, rigctl_socket: socket.socket):
        super().__init__()
        self.rigctl_socket = rigctl_socket
        self.command = None

    def send_command(self, command):
        self.command = command
        self.rigctl_socket.send(bytes(str(self.command+"\n").encode("ascii")))
        while 1:
            read_string = self.rigctl_socket.recv(1024)
            if read_string is not None and read_string != "":
                return bytes.decode(read_string, "utf-8").replace("\n", "")
            sleep(0.01)



class Rigctl(QObject):

    rigctl_incoming_string = pyqtSignal(object)
    rigctl_ready_signal = pyqtSignal(object)

    def __init__(self, uri, port):
        super().__init__()
        self.uri = uri
        self.port = port
        self.rigctl_status = None
        self.reciever = None
        self.sender = None
        self.rigctl_socket = None
        self.create_socket()

    def get_rigctl_status(self):
        return self.rigctl_status

    def create_socket(self):
        self.rigctl_socket = Set_connect_thread(self.uri, self.port)
        self.rigctl_socket.connect_socket_signal.connect(self.rigctl_connect_ok)
        self.rigctl_socket.error_connect_signal.connect(self.rigctl_connect_error)
        self.rigctl_socket.start()

    @pyqtSlot(object)
    def rigctl_connect_ok(self, socket_object):
        self.rigctl_socket=socket_object
        self.start_sender_rigctl()
        self.rigctl_status = True
        self.rigctl_ready_signal.emit("Ready")

    @pyqtSlot(object)
    def rigctl_connect_error(self, incoming_message):
        self.rigctl_status = False
        print(f"Error connect to rig control {self.uri}:{self.port}")

    def send(self, command):
        if self.sender:
            self.answer = self.sender.send_command(command)
            return self.answer
    @QtCore.pyqtSlot(object)
    def incoming_string_process(self, incoming_string):
        self.rigctl_incoming_string.emit(incoming_string)


    def start_sender_rigctl(self):
        self.sender = Rigctl_sender(self.rigctl_socket)

    @QtCore.pyqtSlot(str)
    def string_send_report(self, send_string):
        print(f"String {send_string} - OK")