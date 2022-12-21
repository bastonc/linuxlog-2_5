import os
import subprocess
import sys
import time
from time import sleep

import requests
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QPushButton, QCheckBox, QTableWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QSize
from bs4 import BeautifulSoup

import internetworker
import main
import parse
import std



class ConnectionToEqsl(QThread):
    get_base_html = pyqtSignal(object)
    get_adi_file = pyqtSignal(object)
    get_html_img_eqsl = pyqtSignal(object)
    get_img_eqsl = pyqtSignal(object)
    error_connection = pyqtSignal()

    def __init__(self, parrent_window):
        super().__init__(parrent_window)
        self.url = ""
        self.signal = ""

    def set_attribute(self, url, signal):
        self.url = url
        self.signal = signal

    def run(self):
        try:
            response_from_server = requests.get(self.url)
            if self.signal == "base_html":
                self.get_base_html.emit(response_from_server)
            elif self.signal == "adi_file":
                self.get_adi_file.emit(response_from_server)
            elif self.signal == "get_eqsl_html_img":
                self.get_html_img_eqsl.emit(response_from_server)
            elif self.signal == "get_img_eqsl":
                self.get_img_eqsl.emit(response_from_server)

        except BaseException:
            self.error_connection.emit()


class EqslWindow(QWidget):
    def __init__(self, settings_dict, db, log_window):
        super().__init__()
        self.db = db
        self.settings_dict = settings_dict
        self.log_window = log_window
        self.base_url_eqsl = "https://www.eQSL.cc"
        self.url_get_link_to_adi = f"/qslcard/DownloadInBox.cfm?UserName={self.settings_dict['eqsl_user']}&Password={self.settings_dict['eqsl_password']}"
        uic.loadUi("eqsl_inbox.ui", self)
        style = "background-color:" + self.settings_dict['background-color'] + "; color:" + settings_dict[
            'color'] + ";"
        self.setStyleSheet(style)
        self.setWindowTitle("eQSL Inbox")
        self.tableWidget.setFixedWidth(775)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowOpacity(float(self.settings_dict['logWindow-opacity']))
        self.setWindowIcon(QIcon('logo.png'))
        self.status_lbl.setText("")
        self.chek_btn.clicked.connect(self.get_new_eqsl)
        self.img_name = "default"
        self.path = os.path.join(os.getcwd(), "eqsl")
        self.date_chkbx.stateChanged.connect(self.state_date)
        self.date_start_lbl.hide()
        self.date_finish_lbl.hide()
        self.calendar_start.hide()
        self.calendar_start.setFixedWidth(300)
        self.calendar_finish.hide()
        self.calendar_finish.setFixedWidth(300)
        self.unconfirmed_chkbx.stateChanged.connect(self.unconfirmed_activate)
        self.confirmed_chkbx.stateChanged.connect(self.confirmed_activate)
        self.date_start = None
        self.date_finish = None
        self.add_btn.setEnabled(False)
        self.add_btn.clicked.connect(self.add_to_log_action)
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.clicked.connect(self.confirm_action)
        self.all_confirm = True
        self.all_add = True
        self.all_qso_list = []
        self.close_btn.clicked.connect(self.close)
        self.show()

    def connection_to_eqsl_thread(self, url, signal="base_html"):
        """
        Method for start new thread where connecting to eqsl server
        :param url:
        :param signal:
        :return:
        """
        self.thread_connection = ConnectionToEqsl(self)
        self.thread_connection.set_attribute(url=url, signal=signal)
        #self.check_run_thread()
        self.thread_connection.get_base_html.connect(self.processing_answer_eqsl)
        self.thread_connection.get_adi_file.connect(self.processing_adi_file)
        self.thread_connection.get_html_img_eqsl.connect(self.processing_html_img_eqsl)
        self.thread_connection.get_img_eqsl.connect(self.processing_img_eqsl)
        self.thread_connection.error_connection.connect(self.error_connection_processing)
        self.thread_connection.start()

    # Slot for processing html with links to ADI file
    @pyqtSlot(object)
    def processing_answer_eqsl(self, answer_from_eqsl):
        self.thread_connection.destroyed
        if answer_from_eqsl.status_code == 200:
            self.status_lbl.setStyleSheet(f"color: {self.settings_dict['color']}")
            self.status_lbl.setText("Complete")
            adi_url = self.get_url_adi_file(answer_from_eqsl)
            self.connection_to_eqsl_thread(adi_url, signal="adi_file")
        else:
            self.status_lbl.setStyleSheet("color: #885555;")
            self.status_lbl.setText("Not connected")
            self.chek_btn.setEnabled(True)

    # Slot for processing ADI file
    @pyqtSlot(object)
    def processing_adi_file(self, answer_from_eqsl):
        self.thread_connection.destroyed
        if answer_from_eqsl.status_code == 200:
            self.status_lbl.setStyleSheet(f"color: {self.settings_dict['color']}")
            self.status_lbl.setText("Complete")
            with open("eqsl_import.adi", "w") as f:
                f.write(answer_from_eqsl.text)
            self.output_adi_to_table(answer_from_eqsl.text)
        else:
            self.status_lbl.setStyleSheet("color: #BB4444;")
            self.status_lbl.setText("Not connected")

    # Slot fo processing html with link to image of eQSL
    @pyqtSlot(object)
    def processing_html_img_eqsl(self, response):
        self.thread_connection.destroyed
        img_url = f"{self.base_url_eqsl}{self.get_url_img_eqsl(response)}"
        self.connection_to_eqsl_thread(img_url, signal="get_img_eqsl")

    # Slot fo processing image of eQSL
    @pyqtSlot(object)
    def processing_img_eqsl(self, response):
        self.thread_connection.exit(0)

        with open(f'{self.path}/{self.img_name}', 'wb') as f:
            f.write(response.content)
        self.show_image_eqsl(f'{self.path}/{self.img_name}')

    # slot for processing connection error
    @pyqtSlot()
    def error_connection_processing(self):
        self.thread_connection.exit(0)
        self.chek_btn.setEnabled(True)
        self.status_lbl.setStyleSheet("color: #BB4444;")
        self.status_lbl.setText("Connection error")

    def get_new_eqsl(self):
        # self.tableWidget.clear()
        self.chek_btn.setEnabled(False)
        self.status_lbl.setStyleSheet(f"color: {self.settings_dict['color']}")
        self.status_lbl.setText("Connecting to eQSL.cc")
        if self.unconfirmed_chkbx.isChecked():
            url_eqsl = f"{self.base_url_eqsl}{self.url_get_link_to_adi}&UnconfirmedOnly=1"
        elif self.confirmed_chkbx.isChecked():
            url_eqsl = f"{self.base_url_eqsl}{self.url_get_link_to_adi}&ConfirmedOnly=1"
        else:
            url_eqsl = f"{self.base_url_eqsl}{self.url_get_link_to_adi}"
        if self.date_chkbx.isChecked():
            self.date_start = self.calendar_start.selectedDate()
            self.date_finish = self.calendar_finish.selectedDate()
            # ММ/ДД/ГГГГ
            date_parameter = f"&LimitDateLo={str(self.date_start.month()) if int(self.date_start.month()) > 10 else '0' + str(self.date_start.month())}"
            date_parameter += f"%2F{str(self.date_start.day()) if int(self.date_start.day()) > 10 else '0' + str(self.date_start.day())}"
            date_parameter += f"%2F{str(self.date_start.year())}"
            date_parameter += f"&LimitDateHi={str(self.date_finish.month()) if int(self.date_finish.month()) > 10 else '0' + str(self.date_finish.month())}"
            date_parameter += f"%2F{str(self.date_finish.day()) if int(self.date_finish.day()) > 10 else '0' + str(self.date_finish.day())}"
            date_parameter += f"%2F{str(self.date_finish.year())}"
            url_eqsl += date_parameter
        print(f"URL with date: {url_eqsl}")
        self.connection_to_eqsl_thread(url_eqsl)

    def get_url_adi_file(self, answer_form_eqsl):
        soup = BeautifulSoup(answer_form_eqsl.text, 'html.parser')
        links = soup.findAll("a")
        for link in links:
            if str(link).find(".adi") != -1:
                return str(link["href"]).replace("../", self.base_url_eqsl + "/")

    def output_adi_to_table(self, answer_from_eqsl, mode='eqsl_server'):

        self.all_confirm_chkbox = QCheckBox("All")
        self.all_confirm_chkbox.stateChanged.connect(self.all_state_confirm)
        self.all_confirm_chkbox.setChecked(self.all_confirm)
        self.all_add_chkbox = QCheckBox("All")
        self.all_add_chkbox.stateChanged.connect(self.all_state_add)
        self.all_add_chkbox.setChecked(self.all_add)
        self.tableWidget.setRowCount(0)
        self.tableWidget.insertRow(0)

        self.tableWidget.setCellWidget(0, 5, self.all_confirm_chkbox)
        self.tableWidget.setCellWidget(0, 6, self.all_add_chkbox)
        #self.tableWidget.horizontalHeader().setWidget(5, self.all_confirm_chkbox)

        # table = QTableWidget()
        # table.removeRow(2)
        if mode == 'eqsl_server':
            self.all_confirm_chkbox.setChecked(True)
            self.all_add_chkbox.setChecked(True)
            self.all_confirm = self.get_confirm_chkbx_state()
            self.all_add = self.get_add_chkbx_state()
            strings = str(answer_from_eqsl).split("\n")
            self.all_qso_list.clear()
            for string in strings:
                qso_dict = parse.parseStringAdi(string)
                if qso_dict.get("CALL"):
                    self.all_qso_list.append(qso_dict) if qso_dict is not None else None
        for row, qso in enumerate(self.all_qso_list, start=1):
            show_btn = QPushButton("Show QSL")
            show_btn.clicked.connect(lambda button_show_eqsl, qso_dict=qso: self.get_image_eqsl(qso_dict))
            add_in_base_checkbox = QCheckBox()
            add_in_base_checkbox.setChecked(self.all_add)
            confirm_checkbox = QCheckBox()
            confirm_checkbox.setChecked(self.all_confirm)
            date = qso['QSO_DATE'][:4] + "-" + qso['QSO_DATE'][4:6] + "-" + qso['QSO_DATE'][6:]
            records = self.db.search_qso_by_full_data(call=qso['CALL'], date=date, band=qso['BAND'],
                                            mode=qso['MODE'])
            self.tableWidget.insertRow(self.tableWidget.rowCount())
            self.tableWidget.setItem(row, 0, QTableWidgetItem(qso['QSO_DATE']))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(qso['CALL']))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(qso['BAND']))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(qso['MODE']))
            self.tableWidget.setCellWidget(row, 4, show_btn)
            if self.confirmed_chkbx.isChecked():
                self.tableWidget.setItem(row, 5, QTableWidgetItem("Confirmed"))
            elif self.unconfirmed_chkbx.isChecked() and qso.get("EQSL_QSL_SENT") == "Y":
                self.tableWidget.setItem(row, 5, QTableWidgetItem("Confirmed"))
            elif self.unconfirmed_chkbx.isChecked():
                self.tableWidget.setCellWidget(row, 5, confirm_checkbox)
            elif not self.confirmed_chkbx.isChecked() and \
                    not self.unconfirmed_chkbx.isChecked() and \
                    records != () and records[0]["EQSL_QSL_SENT"] == "Y":
                self.tableWidget.setItem(row, 5, QTableWidgetItem("Confirmed"))

            else:
                self.tableWidget.setCellWidget(row, 5, confirm_checkbox)
            if records != ():
                self.tableWidget.setItem(row, 6, QTableWidgetItem("In log"))
            else:
                self.tableWidget.setCellWidget(row, 6, add_in_base_checkbox)
        self.add_btn.setEnabled(True)
        self.confirm_btn.setEnabled(True)
        self.chek_btn.setEnabled(True)

    def get_image_eqsl(self, qso: dict):
        self.img_name = f"{str(qso['CALL']).replace('/', '_')}_{qso['MODE']}_{qso['BAND']}_{qso['QSO_DATE']}.jpg"
        if os.path.exists(os.path.join(self.path, self.img_name)):
            self.show_image_eqsl(os.path.join(self.path, self.img_name))
        else:
            print("Show eQSL", qso)
            get_img_url = f"{self.base_url_eqsl}/qslcard/GeteQSL.cfm?Username={self.settings_dict['eqsl_user']}"
            get_img_url += f"&Password={self.settings_dict['eqsl_password']}&CallsignFrom={qso['CALL']}&QSOBand={qso['BAND']}"
            get_img_url += f"&QSOMode={qso['MODE']}&QSOYear={qso['QSO_DATE'][:4]}&QSOMonth={qso['QSO_DATE'][4:6]}&QSODay={qso['QSO_DATE'][6:]}"
            get_img_url += f"&QSOHour={qso['TIME_ON'][:2]}&QSOMinute={qso['TIME_ON'][2:]}"
            self.connection_to_eqsl_thread(get_img_url, signal="get_eqsl_html_img")

    def get_url_img_eqsl(self, answer_form_eqsl):
        soup = BeautifulSoup(answer_form_eqsl.text, 'html.parser')
        img = soup.find("img")
        return img["src"]

    def show_image_eqsl(self, path):
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, path])

    def check_run_thread(self):
        if self.thread_connection.isRunning():
            print("close thread", self.thread_connection.currentThreadId())
            self.thread_connection.exit(0)
            print("after exit", self.thread_connection.currentThreadId())

    def state_date(self):
        if self.date_chkbx.isChecked():
            date_start = self.calendar_start.selectedDate()
            date_finish = self.calendar_finish.selectedDate()
            self.date_chkbx.setText(
                f"Use data:\n{date_start.month()}/{date_start.day()}/{date_start.year()} - {date_finish.month()}/{date_finish.day()}/{date_finish.year()}")
            self.calendar_start.show()
            self.calendar_finish.show()
            self.date_start_lbl.show()
            self.date_finish_lbl.show()
            self.calendar_start.selectionChanged.connect(self.set_date_event)
            self.calendar_finish.selectionChanged.connect(self.set_date_event)

        else:
            self.date_chkbx.setText("Use data")
            self.calendar_start.hide()
            self.date_start_lbl.hide()
            self.calendar_finish.hide()
            self.date_finish_lbl.hide()

    def unconfirmed_activate(self):
        if self.unconfirmed_chkbx.isChecked():
            self.confirmed_chkbx.setChecked(False)

    def confirmed_activate(self):
        if self.confirmed_chkbx.isChecked():
            self.unconfirmed_chkbx.setChecked(False)

    def set_date_event(self):
        date_start = self.calendar_start.selectedDate()
        date_finish = self.calendar_finish.selectedDate()
        self.date_chkbx.setText(f"Use data:\n{date_start.month()}/{date_start.day()}/{date_start.year()} - {date_finish.month()}/{date_finish.day()}/{date_finish.year()}")

    def add_to_log_action(self):
        qso_for_add = self.get_checked_qso(index_cell=6)
        for qso in qso_for_add:
            if self.confirmed_chkbx.isChecked() or qso.get("EQSL_QSL_SENT") == "Y":
                qso["EQSL_QSL_SENT"] = "Y"
            else:
                qso["EQSL_QSL_SENT"] = "N"
            self.db.record_qso_to_base(qso_dict=qso, mode="import")
        self.output_adi_to_table(self.all_qso_list, mode='refresh')
        self.log_window.refresh_data()

    def confirm_action(self):
        self.status_lbl.setStyleSheet(f"color: {self.settings_dict['color']}")
        self.status_lbl.setText("Confirmation")
        file_name = "eqsl_c.adi"
        self.all_confirm_qso_list = self.get_checked_qso(5)
        print(self.all_confirm_qso_list)
        main.Adi_file(self.settings_dict['APP_VERSION'], self.settings_dict).record_dict_qso(self.all_confirm_qso_list,
                                                                                             self.settings_dict['adi_fields'],
                                                                                             file_name)
        send_thread = internetworker.Eqsl_send_file(self, file_name, self.settings_dict)
        send_thread.eqsl_send_file_answer.connect(self.processing_row)
        send_thread.error_connection.connect(self.error_eqsl)
        send_thread.start()

    @pyqtSlot(object)
    def processing_row(self, input_object):
        """
        set checkbox confirm into "Confirmed"
        :return:
        """
        self.status_lbl.setStyleSheet(f"color: {self.settings_dict['color']}")
        self.status_lbl.setText("Complited")
        for qso in self.all_qso_list:
            for qso_confirmed in self.all_confirm_qso_list:
                if qso == qso_confirmed:
                    qso["EQSL_QSL_SENT"] = "Y"
        print("all QSO", self.all_qso_list)
        self.output_adi_to_table(self.all_qso_list, mode="refresh")


    @pyqtSlot(object)
    def error_eqsl(self, error_msg):
        """
        set checkbox confirm in to chekable checkbox
        :return:
        """
        self.status_lbl.setStyleSheet("color: #BB4444;")
        self.status_lbl.setText(error_msg)

    def get_checked_qso(self, index_cell):
        """
        Method return list with all full data qso who checked in QTableWidget
        :param index_cell: num of collumn with checkbox
        :return: list with checked qso
        """
        all_qso = []
        for row in range(1, self.tableWidget.rowCount()):
            add_ckbx = self.tableWidget.cellWidget(row, index_cell)
            if add_ckbx is not None and add_ckbx.isChecked():
                for qso in self.all_qso_list:
                    if qso["CALL"] == self.tableWidget.item(row, 1).text() and \
                        qso["QSO_DATE"] == self.tableWidget.item(row, 0).text() and \
                        qso["MODE"] == self.tableWidget.item(row, 3).text() and \
                        qso["BAND"] == self.tableWidget.item(row, 2).text():
                        all_qso.append(qso)
        return all_qso

    def all_state_confirm(self):
        if self.all_confirm_chkbox.isChecked():
            self.all_confirm = True
            self.all_set_checked(5)
        else:
            self.all_confirm = False
            self.all_set_unchecked(5)

    def all_state_add(self):
        if self.all_add_chkbox.isChecked():
            self.all_add = True
            self.all_set_checked(6)
        else:
            self.all_add = False
            self.all_set_unchecked(6)


    def all_set_checked(self, cell_index):
        for row in range(self.tableWidget.rowCount()):
            chkbx = self.tableWidget.cellWidget(row, cell_index)
            if chkbx is not None and not chkbx.isChecked():
                chkbx.setChecked(True)

    def all_set_unchecked(self, cell_index):
        for row in range(self.tableWidget.rowCount()):
            chkbx = self.tableWidget.cellWidget(row, cell_index)
            if chkbx is not None and chkbx.isChecked():
                chkbx.setChecked(False)

    def get_add_chkbx_state(self):
        if self.all_add_chkbox.isChecked():
            return True
        return False

    def get_confirm_chkbx_state(self):
        if self.all_confirm_chkbox.isChecked():
            return True
        return False
