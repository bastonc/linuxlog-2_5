import xml.dom.minidom
from time import sleep

import requests
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

import std


class RequestToServer(QObject):
    answer_data = pyqtSignal(object)
    key_data = pyqtSignal(object)
    error_connection = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.url = None
        self.signal = None
        self.stop_flag = False

    def stop(self):
        self.stop_flag = True

    def set_attributes(self, url, signal, post_data={}):
        self.url = url
        self.signal = signal
        self.post_data = post_data

    def get_to_server(self):
        try:
            print("Thread get_to_server")
            answer = requests.get(self.url, timeout=30)
            if answer.status_code == 200:
                if self.signal == "callsign_info":
                    self.answer_data.emit(answer)
                elif self.signal == "key":
                    self.key_data.emit(answer)
            else:
                self.error_connection.emit("Error connection to qrz.com")
        except BaseException:
            self.error_connection.emit("Error connection to qrz.com")
        finally:
            self.stop_flag = True
            self.deleteLater()

    def post_to_server(self):
        try:
            answer = requests.post(self.url, data=self.post_data)
            if answer.status_code == 200:
                self.answer_data.emit(answer)
            else:
                self.error_connection.emit(answer)
        except:
            self.error_connection.emit("Error connection")


class QrzComApiThread(QThread):

    data_reciev_signal = pyqtSignal(object)
    answer_data = pyqtSignal(object)
    key_data = pyqtSignal(object)
    error_connection = pyqtSignal(object)

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
        self.qrz_key = None
        self.callsign = None
        self.cache_callsign = None
        self.url = None
        self.signal = None
        self.post_data = None
        self.run_signal = True
        #self.worker_class = RequestToServer()

    def get_to_server(self):
        try:
            print("Thread get_to_server")
            answer = requests.get(self.url, timeout=30)
            if answer.status_code == 200:
                if self.signal == "callsign_info":
                    self.cache_callsign = self.callsign
                    self.answer_data.emit(answer)
                elif self.signal == "key":
                    self.key_data.emit(answer)
            else:
                self.error_connection.emit("Not 200 (HTTPS) from qrz.com")
        except BaseException:
            self.error_connection.emit("Network error to qrz.com")
        finally:
            self.stop_flag = True
            #self.deleteLater()
    def get_actual_key(self):
        url = f"https://xmldata.qrz.com/xml/?username={self.username};password={self.password};agent=Linuxlog"
        self.set_attrubute(url, "key")
        self.get_to_server()

    def set_attrubute(self, url: str, signal: str, post_data={}):
        self.url = url
        self.signal = signal
        self.post_data = post_data

    def get_callsign_info(self, callsign):
        # if callsign != self.cache_callsign:
        #     self.callsign = callsign
            if self.qrz_key is not None:
                url = f"https://xmldata.qrz.com/xml/current/?s={self.qrz_key};callsign={self.callsign}"
                # 8c7dd40a60b5010a1f1d1cf66cc91c06 {self.key}
                self.set_attrubute(url, "callsign_info")
                self.get_to_server()
            else:
                print("qrz.com key is None")

    def get_callsign_info_auto(self, callsign):
        self.callsign = callsign
    def set_run_signal(self, run_signal: bool):
        self.run_signal = run_signal

    def set_key(self, key):
        self.qrz_key = key
    def run(self):
        while self.run_signal:
            # print("running qrz_com thread")
            if self.qrz_key is None:
                self.get_actual_key()
            if self.callsign != self.cache_callsign:
                print("get callsign info in mainloop qthread")
                self.get_callsign_info(self.callsign)
            #self.get_callsign_info(self.callsign)
            sleep(0.01)


class QrzComApi(QObject):
    data_info = pyqtSignal(object)
    qrz_com_error = pyqtSignal(object)
    qrz_com_connect = pyqtSignal(bool)

    def __init__(self, username: str, password: str):
        super().__init__()
        self.username = username
        self.password = password
        self.qrz_com_thread = QrzComApiThread(self.username, self.password)
        self.qrz_com_thread.answer_data.connect(self.reciever_data)
        self.qrz_com_thread.key_data.connect(self.set_key)
        self.qrz_com_thread.error_connection.connect(self.error_connection)
        self.qrz_com_thread.start()

    def get_callsign_info(self, callsign):
        self.qrz_com_thread.get_callsign_info_auto(callsign)

    def stop_thread(self):
        self.qrz_com_thread.set_run_signal(False)
        self.qrz_com_thread.set_key(None)
        self.qrz_com_thread.terminate()

    @pyqtSlot(object)
    def reciever_data(self, data):
        self.worker_thread = None
        result_dict = self.xml_parse_info(data.text)
        if result_dict is not None and "error" in result_dict and result_dict["error"] == "Invalid key":
            self.qrz_com_thread.set_key(None)
            self.qrz_com_connect.emit(False)
        else:
            self.data_info.emit(result_dict)

    @pyqtSlot(object)
    def set_key(self, data):
        xml_dom = xml.dom.minidom.parseString(data.content)
        if xml_dom.getElementsByTagName('Error'):
            self.qrz_com_thread.set_run_signal(False)
            std.std().message(xml_dom.getElementsByTagName('Error')[0].childNodes[0].data, "QRZ.COM ERROR")
        else:
            self.key = xml_dom.getElementsByTagName('Key')[0].childNodes[0].data
            self.qrz_com_thread.set_key(self.key)
            self.qrz_com_connect.emit(True)

    @pyqtSlot(object)
    def error_connection(self, error_maessage):
        #self.stop_thread()
        print(f"qrz.com error: {error_maessage}")
        self.qrz_com_connect.emit(False)
        print(
            f"Error slot Worker thread running: {self.worker_thread.isRunning()}, finished: {self.worker_thread.isFinished()}")

    @staticmethod
    def xml_parse_info(xml_string):
        xml_dom = xml.dom.minidom.parseString(xml_string)
        f_name = None
        s_name = None
        qth = None
        if not xml_dom.getElementsByTagName('Error'):
            if xml_dom.getElementsByTagName('fname'):
                f_name = xml_dom.getElementsByTagName('fname')[0].childNodes[0].data
            if xml_dom.getElementsByTagName('name'):
                s_name = xml_dom.getElementsByTagName('name')[0].childNodes[0].data
            if xml_dom.getElementsByTagName('addr2'):
                qth = xml_dom.getElementsByTagName('addr2')[0].childNodes[0].data
            return {"f_name": f_name,
                    "s_name": s_name,
                    "qth": qth}
        if str(xml_dom.getElementsByTagName('Error')[0].childNodes[0].data).find("Timeout") != -1 or \
                str(xml_dom.getElementsByTagName('Error')[0].childNodes[0].data).find("Invalid") != -1:
            return {"error": "Invalid key"}
        return None

class QrzLogbook(QObject):
    def __init__(self, settings_dict):
        super(QrzLogbook, self).__init__()
        self.settings_dict = settings_dict
        self.api_url_post = "https://logbook.qrz.com/api"

    def request_to_server(self, post_data):
        self.worker_thread = QThread()
        self.worker_class = RequestToServer()
        self.worker_class.set_attributes(self.api_url_post, post_data["ACTION"], post_data=post_data)
        self.worker_class.moveToThread(self.worker_thread)
        self.worker_class.answer_data.connect(self.reciever_data)
        self.worker_class.error_connection.connect(self.error_connection)
        self.worker_thread.started.connect(self.worker_class.post_to_server)
        self.worker_thread.finished.connect(self.worker_class.stop)
        self.worker_thread.finished.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def send_qso_to_logbook(self, qso_adi_string):
        print(f"String ADI to qrz.com logbook: {str(qso_adi_string).replace(' ', '')}\n{self.settings_dict['qrz-com-app-key']}")
        post_data = {"KEY": self.settings_dict['qrz-com-app-key'],
                     "ACTION": "INSERT",
                     "ADIF": str(qso_adi_string).replace(' ', '')}
        self.request_to_server(post_data)

    @pyqtSlot(object)
    def reciever_data(self, obj):
        print(f"Reciever POST answer: {obj.text}")

    @pyqtSlot(object)
    def error_connection(self, obj):
        print(f"Reciever POST error_connection: {obj}")
