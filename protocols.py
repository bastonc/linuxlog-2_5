import std
from PyQt6.QtCore import QObject
class Kenwood(QObject):
    def __init__(self, settingsDict, parent_window, serial_port):
        super().__init__()
        self.settingsDict = settingsDict
        self.parent_window = parent_window
        self.ser = serial_port

    def get_freq_mod_list(self):
        list = [b"FA;", b"MD;"]
        return list
    def decoder_data(self, data_byte: bytes):
        freq_str = data_byte.decode("utf-8").replace(';', '')
        if freq_str[:2] == "FA" and len(freq_str) <= 14:
            freq = freq_str.replace('FA', '')
            self.parent_window.set_freq(freq.lstrip('0'))
            #print("Frequency:_>", freq_str)
        elif freq_str[:2] == "MD":
            if freq_str[2:] == '1':
                self.parent_window.set_mode_tci("lsb")
            if freq_str[2:] == '2':
                self.parent_window.set_mode_tci("usb")
            if freq_str[2:] == '3':
                self.parent_window.set_mode_tci("cw")
            if freq_str[2:] == '4':
                self.parent_window.set_mode_tci("nfm")
            if freq_str[2:] == '5':
                self.parent_window.set_mode_tci("am")
            if freq_str[2:] == '6':
                self.parent_window.set_mode_tci("digl")
            if freq_str[2:] == '7':
                self.parent_window.set_mode_tci("cw")
            if freq_str[2:] == '9':
                self.parent_window.set_mode_tci("digu")
        #print("Mode MD:_>", freq_str[2:])
    def set_freq_rig(self, freq):
        if len(freq) < 11:  # for cat len freq = 11 digit
            freq = freq.zfill(11)  # add '0' before freq
            # print("freq:_>", freq)
        self.ser.write(b'FA' + freq.encode("utf-8") + b";")
    def set_mode_rig(self, mode):

        if mode == 'LSB':
            mode_bytes = b"MD1;"
        elif mode == 'USB':
            mode_bytes = b"MD2;"
        elif mode == 'CW':
            mode_bytes = b"MD3;"
        elif mode == 'NFM':
            mode_bytes = b"MD4;"
        elif mode == 'AM':
            mode_bytes = b"MD5;"
        elif mode == 'DIGL':
            mode_bytes = b"MD6;"
        #if mode == 'CW':
         #   mode_bytes = b"MD7;"
        elif mode == 'DIGU':
            mode_bytes = b"MD9;"
        elif mode == 'ERROR':
            mode_bytes = b"MD1;"

        self.ser.write(mode_bytes)

class Icom(QObject):
    def __init__(self, settingsDict, parent_window, serial_port):
        super().__init__()
        self.settingsDict = settingsDict
        self.parent_window = parent_window
        self.ser = serial_port

    def get_freq_mod_list(self):
        list = [b"FEFE6C0003FD", b"FEFE6C0004FD"]  # 1-st bytecode for request frequency, 2-nd bytecode for request mode
        return list

    def freq_to_bcd(self, i):
        i = i.zfill(9)
        out = r'\x' + i[8] + '2' + r'\x' + i[6] + i[7] + r'\x' + i[4] + i[5] + r'\x' + i[2] + i[3] + r'\x' + i[0] + i[1]
        return out

    def decoder_data(self, data_byte: bytes):
        freq_str = data_byte.decode("utf-8").replace(';', '')
        if freq_str[:4] == "FEFE" and len(freq_str) <= 14:
            if freq_str[9:10] == '03':
                freq_in_hex = freq_str[10:20]
                freq = int(freq_in_hex, 16)
            self.parent_window.set_freq(freq)
            #print("Frequency:_>", freq_str)
            if freq_str[9:10] == "06":
                if freq_str[10:11] == '00':
                    self.parent_window.set_mode_tci("lsb")
                if freq_str[10:11] == '01':
                    self.parent_window.set_mode_tci("usb")
                if freq_str[10:11] == '03':
                    self.parent_window.set_mode_tci("cw")
                if freq_str[10:11] == '05':
                    self.parent_window.set_mode_tci("nfm")
                if freq_str[10:11] == '02':
                    self.parent_window.set_mode_tci("am")
                if freq_str[10:11] == '08' or freq_str[10:11] == '11' \
                        or freq_str[10:11] == '12' or freq_str[10:11] == '04':
                    self.parent_window.set_mode_tci("digl")


    def set_freq_rig(self, freq):
        freq_in_hex = self.freq_to_bcd(freq)
        self.ser.write(b'FEFE6C0000' + freq_in_hex.encode("utf-8") + b"FD")

    def set_mode_rig(self, mode):

        if mode == 'LSB':
            mode_bytes = b"00"
        elif mode == 'USB':
            mode_bytes = b"01"
        elif mode == 'CW':
            mode_bytes = b"03"
        elif mode == 'NFM':
            mode_bytes = b"05"
        elif mode == 'AM':
            mode_bytes = b"02"
        elif mode == 'DIGL':
            mode_bytes = None
        #if mode == 'CW':
         #   mode_bytes = b"MD7;"
        elif mode == 'DIGU':
            mode_bytes = None
        else:
            mode_bytes = b"00"

        if mode_bytes != None:
            self.ser.write(b"FEFE6C0004" + mode_bytes + b"FD")
