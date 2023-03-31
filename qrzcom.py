import xml.dom.minidom
from time import sleep

import requests
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot


class RequestToServer(QObject):
    answer_data = pyqtSignal(object)
    key_data = pyqtSignal(object)
    error_connection = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        #self.password = parent_data.password
        #self.username = parent_data.username
        self.url = None
        self.signal = None
        self.stop_flag = False

    def stop(self):
        self.stop_flag = True

    def set_attributes(self, url, signal):
        self.url = url
        self.signal = signal

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





class QrzCom(QObject):
    data_info = pyqtSignal(object)
    qrz_com_error = pyqtSignal(object)
    qrz_com_connect = pyqtSignal(bool)

    def __init__(self, username, password, parent_widget):
        super().__init__()
        self.username = username
        self.password = password
        self.parent_widget = parent_widget
        self.get_actual_key()
        self.callsign = None

    def start_thread(self, url, signal):
        print(f"Start thread {url}, {signal}")
        self.worker_thread = QThread()
        self.worker_class = RequestToServer()
        self.worker_class.set_attributes(url, signal)
        self.worker_class.moveToThread(self.worker_thread)
        self.worker_class.answer_data.connect(self.reciever_data)
        self.worker_class.key_data.connect(self.set_key)
        self.worker_class.error_connection.connect(self.error_connection)
        self.worker_thread.started.connect(self.worker_class.get_to_server)
        self.worker_thread.finished.connect(self.worker_class.stop)
        self.worker_thread.finished.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def stop_thread(self):
        if self.worker_thread.isRunning():
            self.worker_class.stop()
            #self.worker_thread.wait()
            #self.worker_thread.quit()
            self.worker_thread.quit()
            #self.worker_thread.wait()




    def get_callsign_info(self, callsign):

        if callsign != self.callsign:
            self.callsign = callsign
            print(f"get callsign info from qrz.com{callsign}")
            if self.key is not None:
                url = f"https://xmldata.qrz.com/xml/current/?s={self.key};callsign={self.callsign}"
                # 8c7dd40a60b5010a1f1d1cf66cc91c06 {self.key}
                self.start_thread(url, "callsign_info")
            else:
                print("qrz.com key is None")


    @pyqtSlot(object)
    def reciever_data(self, data):
        self.stop_thread()
        print(data.text)
        result_dict = self.xml_parse_info(data.text)
        if result_dict is not None and "error" in result_dict and result_dict["error"] == "Invalid key":
            sleep(3)
            self.get_actual_key()
            self.qrz_com_connect.emit(False)

        else:
            self.data_info.emit(result_dict)
        print(f"Reciver_data Worker thread running: {self.worker_thread.isRunning()}, finished: {self.worker_thread.isFinished()}")

    @pyqtSlot(object)
    def set_key(self, data):
        self.stop_thread()
        print(f"key_query_answer: {data.text}")
        xml_dom = xml.dom.minidom.parseString(data.content)
        self.key = xml_dom.getElementsByTagName('Key')[0].childNodes[0].data
        self.qrz_com_connect.emit(True)
        print(f"QRZ.com key: {self.key}")
        print(f"Set key Worker thread running: {self.worker_thread.isRunning()}, finished: {self.worker_thread.isFinished()}")

    @pyqtSlot(object)
    def error_connection(self, error_maessage):
        self.stop_thread()
        print(f"qrz.com error: {error_maessage}")
        self.qrz_com_connect.emit(False)
        print(f"Error slot Worker thread running: {self.worker_thread.isRunning()}, finished: {self.worker_thread.isFinished()}")

    def get_actual_key(self):
        url = f"https://xmldata.qrz.com/xml/?username={self.username};password={self.password};agent=Linuxlog"
        self.start_thread(url, "key")

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