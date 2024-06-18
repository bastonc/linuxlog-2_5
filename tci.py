#!/usr/bin/python3
# -*- coding: utf-8 -*-

#from websocket import WebSocket
import time

import websocket
import std
import traceback
from PyQt6.QtCore import QThread,  pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication
from PyQt6 import QtCore



class tci_connect:

    def __init__(self, settingsDict, log_form, parent=None):
        super().__init__()
        self.settingsDict = settingsDict
        self.log_form = log_form
        self.settingsDisct = settingsDict


    def get_mode(self):
        return self.log_form.get_mode()

    def start_tci(self, host, port):
        self.tci_reciever = Tci_reciever(host + ":" + port,
                                         log_form=self.log_form, settingsDict=self.settingsDict)
        self.tci_reciever.set_flag("run")
        self.tci_reciever.start()
        # self.tci_reciever_stream_port = Tci_reciever(host + ":" + "50040", log_form=self.log_form, settingsDict=self.settingsDict)
        # self.tci_reciever_stream_port.set_flag("run")
        # self.tci_reciever_stream_port.start()

    def stop_tci(self):
        try:
            print ("Tci stop 1", self.tci_reciever.currentThreadId())
            self.tci_reciever.set_flag("stop")
            if self.tci_reciever.isFinished():
                print("Tci stop 2", self.tci_reciever.currentThreadId())
            #self.log_form.set_tci_stat(' ')
        except Exception:
            print("TCI don't started")


class Tci_reciever(QThread):
    tx_flag = QtCore.pyqtSignal(str)
    tx = "Disable"

    def __init__(self, uri, log_form, settingsDict, parent=None):
        super().__init__()
        self.uri = uri
        self.log_form = log_form
        #print("uri:_>", self.uri)
        self.active_rx = 0
        self.active_vfo = 0
        self.ws = websocket.WebSocket()
        self.settingsDict = settingsDict
        self.mode = self.settingsDict['mode']

    def set_flag(self, flag):
        #print("set_flag:", flag)
        self.flag = flag

    def get_mode(self):
        return self.mode

    def tci_send_command(self, string_command):
        try:
            self.ws.send(string_command)
        except BaseException:
            print(f"Error send command: {string_command}")

    def run(self):

        while self.flag == "run":
            try:

                self.ws.connect(self.uri)
                self.log_form.tx_tci("restart")
                self.log_form.set_tci_stat('•TCI')

                break
                #time.sleep(3)
            except Exception:
                # self.log_form.set_tci_label_found()
                # print("Tci_reciever: Except connection")
                # self.log_form.set_tci_stat('--', "#ff5555")
                QThread.sleep(2)

                continue
        old_reciever = ""
        while self.flag == "run":
            try:
                #print("Connect to ")
                #
                reciever = self.ws.recv()
                # print("Tci_reciever.run: from socket (esdr):_>", reciever)
                if reciever != old_reciever:
                    # print("Tci_reciever.run: from socket (esdr):_>", reciever)
                    tci_string=reciever.split(":")
                    # reciev vfo (freq)
                    if tci_string[0] == "ready;":
                        #print("send RX_SENSOR_ENABLE")
                        #if bool(self.settingsDict["rs-from-tci"]):
                         self.tci_send_command("RX_SENSORS_ENABLE:" + self.settingsDict["rs-from-tci"] + "," + self.settingsDict["rs-time-update"] + ";")

                    if tci_string[0] == "ecoder_switch_rx":
                        self.active_rx = str(tci_string[1]).split(",")[-1].replace(";","")
                        self.active_vfo = str(tci_string[1]).split(",")[0]
                        self.tci_send_command(f"VFO:{self.active_rx},{self.active_vfo};")

                    if tci_string[0] == "ecoder_switch_channel":
                        self.active_vfo = str(tci_string[1]).split(",")[-1].replace(";","")
                        self.tci_send_command(f"VFO:{self.active_rx},{self.active_vfo};")
                        #self.active_rx = str(tci_string[1]).split(",")[0]

                    if tci_string[0] == "rx_channel_sensors":
                        dBm = str(tci_string[1]).split(",")[-1].replace(";","")
                        rx = str(tci_string[1]).split(",")[0]
                        vfo = str(tci_string[1]).split(",")[1]
                        if rx == self.active_rx and vfo == self.active_vfo:
                        #print(f"dBm: {dBm}")
                            self.log_form.set_rs_s(dBm)

                    if tci_string[0] == 'trx':
                        #self.tx = 'Enable'
                        values = tci_string[1].split(",")
                        #print("TRX:_>", values[1])
                        if values[1] == 'true;':
                            #print(values[1])
                            self.log_form.trx_enable('tx')

                        elif values[1] == 'false;':
                            #print(values[1])
                            self.log_form.trx_enable('rx')


                    if tci_string[0] == 'vfo':
                        values = tci_string[1].split(",")
                        if values[1] == self.active_vfo and values[0] == self.active_rx:
                            #print("set freq:")
                            self.log_form.set_freq(values[2].replace(';', ''))

                    # reciev protocol
                            #print("Частота:", values[2])
                    if tci_string[0] == 'protocol':
                        self.version_tci = tci_string[1].split(",")[1].replace(";","")

                        values = tci_string[1].replace(',', ' ')
                        values = values.replace(";", "")

                        #print("Version protocol:", self.version_tci)
                        self.log_form.set_tci_stat('•TCI: '+ values)

                    # reciev mode
                    if tci_string[0] == 'modulation':
                         values = tci_string[1].split(",")
                         if values[0] == '0':
                            #if self.version_tci == "1.4":
                            self.log_form.set_mode_tci(values[1].replace(';', ''))
                            self.mode = values[1].replace(';', '')
                            #if self.version_tci == '1.5':
                            #    self.log_form.set_mode_tci(values[1].replace(';', ''))
                            #    self.mode = values[1].replace(';', '')

                            print(">", tci_string)

                    #if tci_string[0] == 'ready':
                    #     print("server: ready;")
                    #     self.log_form.sendMesageToTCI("ready;")


                    # reciev spot call
                    if tci_string[0] == 'clicked_on_spot':
                        print("clicked_on_spot:_>", tci_string)
                        values = tci_string[1].split(",")
                        print("clicked_on_spot:_>", values)
                        self.log_form.set_call(call=values[0].strip())
                        band = std.std().get_std_band(values[1].strip().replace(";",""))
                        print("band>", band)
                        mode = std.std().mode_band_plan(band, values[1].strip().replace(";",""))
                        print("mode>", mode)
                        self.log_form.set_mode_tci(mode.lower())
                        Tci_sender(self.settingsDict['tci-server']+":"+self.settingsDict['tci-port']).set_mode("0",mode)
                    old_reciever = reciever



                time.sleep(0.002)

            except Exception:
                print("Tci_reciever: Exception in listen port loop", Exception)
                self.log_form.set_tci_stat('')
                #self.log_form.set_tci_label_found()
                try:
                    self.ws.close()
                    self.ws = websocket.WebSocket()
                    self.ws.connect(self.uri)
                    self.log_form.set_tci_stat("•TCI")
                    self.log_form.tx_tci("restart")

                except:
                    QThread.sleep(2)
                    # self.log_form.set_tci_label_found()
                    #time.sleep(2)
                    continue

        #else:
            #self.ws.close()


class Tci_sender (QtCore.QObject):

    def __init__(self, uri, tx_flag, log_form, settings_dict):
        super().__init__()
        self.log_form = log_form
        self.settings_dict = settings_dict
        self.tx_flag = tx_flag
        self.uri = uri
        self.ws = websocket.WebSocket()
        self.web_socket_init(self.uri)
        #self.rs_from_tci()

    def web_socket_init(self, uri):
        try:
            self.ws.connect(uri)
            # self.ws.send("READY;")
        except ConnectionError:
            self.log_form.set_tci_stat('· TCI', color="#aaaaaa")
            result = traceback.format_exc()
            print("> Tci_sender: Not connect", uri)


    def update_tx_tci(self):
        try:
            self.ws.connect(self.uri)
        except Exception:
            result = traceback.format_exc()
            print(result)

    def send_command(self, string_command):
        if self.tx_flag != "Enable":
            try:
                print(f"SEND COMMAND TO TCI: {string_command}")
                self.ws.send(string_command)
            except Exception:
                print(f"Exception send command: {string_command}")
                pass

    def rs_from_tci(self):
        print(f"rs-from-tci: {self.settings_dict['rs-from-tci'], type(self.settings_dict['rs-from-tci'])}")
        if bool(self.settings_dict["rs-from-tci"]):
            if 30 < int(self.settings_dict["rs-time-update"]) < 1000:
                self.send_command("RX_SENSORS_ENABLE:true;")
                print(f"time_update: {self.settings_dict['rs-time-update']}")
            else:
                print(f"time_update not in range (30 - 1000): {self.settings_dict['rs-time-update']}")


    def set_freq(self, freq):
        print("set_freq:", freq)
        freq_string = str(freq)
        if len(str(freq)) < 8 and len(str(freq))>=5:
            freq_string = str(freq)+"00"
        if len(str(freq)) < 5:
            freq_string = str(freq)+"000"
        string_command = "VFO:0,0,"+str(freq_string)+";"
        self.ws.send(string_command)

 ### spots

    def set_spot(self, call, freq, color="12711680"):
        #print("TX stat:", self.tx_flag)
        # check enable TX mode
        if self.tx_flag != "Enable":
            try:
                string_command = "SPOT:"+str(call)+", ,"+str(freq)+","+color+", ;"
                self.ws.send(string_command)
            except BaseException:
                #result = traceback.format_exc()
                #print("Cant set spot. Connect object:", result)
                pass

    def del_spot(self, call):
        if self.tx_flag != "Enable":
            string_command = "SPOT_DELETE:"+str(call)+";"
            self.ws.send(string_command)

    def change_color_spot(self, call, freq, color="21711680"):
        if self.tx_flag != "Enable":
            string_command = "SPOT_DELETE:"+str(call)+";"
            self.ws.send(string_command)
            string_command = "SPOT:"+str(call)+", ,"+str(freq)+","+color+", ;"
            self.ws.send(string_command)

##########

    def set_mode(self, reciever, mode):
        string_command = "MODULATION:"+str(reciever)+","+str(mode)+";"
        self.ws.send(string_command)

