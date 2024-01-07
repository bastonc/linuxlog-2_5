import socket

from PyQt6.QtCore import pyqtSignal, QObject

class Rigctl_sender(QObject):

    error_send_signal = pyqtSignal(object)

    def __init__(self, rigctl_socket: socket.socket):
        super().__init__()
        self.rigctl_socket = rigctl_socket
        self.command = None

    def send_command(self, command):
        self.command = command
        try:
            self.rigctl_socket.send(bytes(str(self.command+"\n").encode("ascii")))
            read_string = self.rigctl_socket.recv(1024)
            return bytes.decode(read_string, "utf-8").replace("\n", "")
        except BaseException:
            self.error_send_signal.emit(self.command)
