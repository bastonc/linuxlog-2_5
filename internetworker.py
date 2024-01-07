# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

import urllib
import std
import requests
import datetime

import shutil
import os
from os.path import expanduser
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt6.QtGui import QPixmap, QColor
# import urllib.request
# import urllib.parse
from urllib.request import urlretrieve
from urllib.parse import quote
from PyQt6.QtCore import QThread
from PyQt6 import QtCore
import PyQt6.QtCore

from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QApplication
import main


class internetWorker(QThread):

    def __init__(self, window, settings, parrent=None):
        super().__init__()
        self.internet_search_window = window
        self.callsign = None
        self.settings = settings

    def set_callsign_for_search(self, callsign):
        self.callsign = callsign

    def run(self):
        # print (self.callsign)
        info_from_internet_array = internetWorker.get_image_from_server(self)
        print(info_from_internet_array)
        if info_from_internet_array != {}:
            pixmap = QPixmap(info_from_internet_array.get('img'))
            pixmap_resized = pixmap.scaled(int(self.settings['search-internet-width']) - 20,
                                           int(self.settings['search-internet-height']) - 20,
                                           QtCore.Qt.AspectRatioMode.KeepAspectRatio)

            self.internet_search_window.labelImage.setPixmap(pixmap_resized)
            # return info_from_internet_array

    def get_image_from_server(self):
        '''
        метод загружает изображение с qrz.com
        принимает self.callsign - как позывной
        '''
        url_found = self.settings['qrz-com']

        # print(self.callsign)
        parameter_request = "tquery=" + self.callsign + "&mode: callsign"
        parameter_to_byte = bytearray(parameter_request, "utf-8")
        data_dictionary = {}
        try:
            response = urllib.request.urlopen(url_found, parameter_to_byte)
            #print("request status:", response.code)
            html = response.read().decode("utf-8")
            soup = BeautifulSoup(html, 'html.parser')
            img = soup.find(id="mypic")
            file_name = self.callsign.replace("/", "_")
            if img['src'].split('/')[-1] == self.settings['qrz-none']:
                img = None
            print("file name:", file_name, img['src'].split('/')[-1])
        except Exception:
            print("get_image_from_server: Don't connection")
            img = None

        try:
            if img != None:
                urllib.request.urlretrieve(img['src'], "image/" + file_name + ".jpg")
                data_dictionary.update({'img': "image/" + file_name + ".jpg"})
            else:
                dict_qrz_ru = self.search_qrz_ru()
                data_dictionary.update({'name': dict_qrz_ru['name'], 'qth': dict_qrz_ru['qth'], 'loc': dict_qrz_ru['loc']})

        # print(data_dictionary)
        except Exception:
            print("Exception:", Exception)

        return data_dictionary

    def get_id_qrz_ru(self):
        response = urllib.request.urlopen("http://api.qrz.ru/login", "u=<username>&p=<password>&agent=LinuxLog")
        print("QRZ_RU status:", response.code)
        html = response.read().decode("utf-8")
        "http: // api.qrz.ru / login?u = < username > & p = < password > & agent = < agent >"
        soup = BeautifulSoup(html, 'xml')
        id_qrz = soup.session_id
        return id_qrz

    def search_qrz_ru(self):

        self.id_rqz_ru = self.get_id_qrz_ru()

        out_dict={}
        url_found_qrz_ru = self.settings['qrz-ru']
        parameter_request = "id=" + self.id_rqz_ru + "&callsign=" + self.callsign.replace("/", "_")
        parameter_to_byte = bytearray(parameter_request, "utf-8")

        response = urllib.request.urlopen(url_found_qrz_ru, parameter_to_byte)
        print("QRZ_RU status:", response.code)
        html = response.read().decode("utf-8")
        #print("QRZ_RU html:", html)
        soup = BeautifulSoup(html, 'html.parser')
        info_block = soup.find(id="infoBlock")
        name_clear = info_block.b.text.split(" ")[0]
        print("QRZ_RU html:", name_clear)
        content_div_dirty = info_block.div.text.split(" ")
        content_div=[]
        for content_elem in content_div_dirty:
            if content_elem !='':
                content_div.append(content_elem)

        print("QRZ_RU QTH:", content_div)
        qth_clear = content_div[3].replace(',','')
        loc_clear = content_div[6].replace("#", '').replace("\n", '')
        out_dict.update({'name': name_clear, 'qth': qth_clear, 'loc': loc_clear})
        return out_dict

class Eqsl_send(QtCore.QObject):
    error_message = QtCore.pyqtSignal(str)
    sent_ok = QtCore.pyqtSignal()

    def __init__(self, settingsDict, recordObject, std, parent_window):
        super().__init__()
        self.recordObject = recordObject
        self.settingsDict = settingsDict
        self.std = std
        self.parrent_window = parent_window

    def run(self):

        api_url_eqsl = 'https://www.eQSL.cc/qslcard/importADIF.cfm?ADIFData=LinuxLog upload'
        data_qso_string = '<BAND:' + str(len(self.recordObject['BAND'])) + '>' + str(
            self.recordObject['BAND']) + ' <CALL:' + str(len(self.recordObject['CALL'])) + '>' + str(
            self.recordObject['CALL']) + ' <MODE:' + str(len(self.recordObject['MODE'])) + '>' + str(
            self.recordObject['MODE']) + ' <QSO_DATE:' + str(len(self.recordObject['QSO_DATE'])) + '>' + str(
            self.recordObject['QSO_DATE']) + ' <RST_RCVD:' + str(len(self.recordObject['RST_RCVD'])) + '>' + str(
            self.recordObject['RST_RCVD']) + ' <RST_SENT:' + str(len(self.recordObject['RST_SENT'])) + '>' + str(
            self.recordObject['RST_SENT']) + ' <TIME_ON:' + str(len(self.recordObject['TIME_ON'])) + '>' + str(
            self.recordObject['TIME_ON']) + ' <EOR>'
        data_string_code_to_url = urllib.parse.quote(data_qso_string)
        user_pasword_eqsl = '&EQSL_USER=' + self.settingsDict['eqsl_user'] + '&EQSL_PSWD=' + self.settingsDict[
            'eqsl_password']

        try:
            request_eqsl = requests.get(api_url_eqsl + data_string_code_to_url + user_pasword_eqsl)

            if request_eqsl.status_code != 200:

                self.error_message.emit("Can't sent eQSL (server not 200)")

            else:
                soup = BeautifulSoup(request_eqsl.text, 'html.parser')
                response = soup.body.contents[0]
                # print ("SOUP", soup.body.contents[0].strip())
                if (response.find('Warning') != -1) or (response.find('Error') != -1):
                    self.error_message.emit(soup.body.contents[0].strip())
                else:
                    self.sent_ok.emit()
        except Exception:
            print("Can't send eQSL")
            self.error_message.emit("Can't sent eQSL\nCheck internet connection")


class Eqsl_services(QtCore.QObject):
    send_ok = QtCore.pyqtSignal()
    error_signal = QtCore.pyqtSignal()

    def __init__(self, settingsDict, recordObject, std, parent_window):
        super().__init__()
        self.recordObject = recordObject
        self.settingsDict = settingsDict
        self.std = std
        self.parrent_window = parent_window
        self.check_auth_data()
        self.input_form_key = 0

    def send_qso_to_qrz(self):
        server_url_post = 'https://logbook.qrz.com/api'
        key_account = "KEY=81FE-08CA-D97D-8709&"
        action = "ACTION=INSERT&ADIF=<band:3>80m<mode:3>SSB<call:5>RN6XC<qso_date:8>20140121<station_callsign:6>UR4LGA<time_on:4>0346<eor>"
        # print ("key+action", key_account + action)
        response = requests.post(server_url_post, data=key_account + action)

    # print ("send_to_qrz", response.text)

    def check_auth_data(self):
        if self.settingsDict['eqsl_user'] == '' or self.settingsDict['eqsl_password'] == '':
            self.enter_auth_data()
        else:
            self.start_sending()

    def enter_auth_data(self):
        desktop = QApplication.desktop()
        self.window_auth = QWidget()
        self.window_auth.setGeometry(int(desktop.width() / 2) - 100, int(desktop.height() / 2) - 50, 200, 100)
        self.window_auth.setWindowTitle("Enter eQSL auth data")
        styleform = "background :" + self.settingsDict['form-background'] + "; font-weight: bold; color:" + \
                    self.settingsDict['color-table'] + ";"

        style = "QWidget{background-color:" + self.settingsDict['background-color'] + "; color:" + self.settingsDict[
            'color'] + ";}"
        self.window_auth.setStyleSheet(style)

        # Login element
        self.login_label = QLabel("login")
        self.login_input = QLineEdit()
        self.login_input.setFixedWidth(100)
        self.login_input.setFixedHeight(30)
        self.login_input.setStyleSheet(styleform)

        login_layer = QHBoxLayout()
        login_layer.addWidget(self.login_label)
        login_layer.addWidget(self.login_input)
        # Password element
        self.password_label = QLabel("Password")
        self.password_input = QLineEdit()
        self.password_input.setFixedWidth(100)
        self.password_input.setFixedHeight(30)
        self.password_input.setStyleSheet(styleform)
        password_layer = QHBoxLayout()
        password_layer.addWidget(self.password_label)
        password_layer.addWidget(self.password_input)

        # Button elements
        ok_button = QPushButton("Ok")
        ok_button.setFixedWidth(70)
        ok_button.setFixedHeight(30)
        ok_button.setStyleSheet(style)
        ok_button.clicked.connect(self.return_data)
        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedWidth(70)
        cancel_button.setFixedHeight(30)
        cancel_button.setStyleSheet(style)
        cancel_button.clicked.connect(self.window_auth.close)
        buttons_layer = QHBoxLayout()
        buttons_layer.addWidget(cancel_button)
        buttons_layer.addWidget(ok_button)
        main_layout = QVBoxLayout()
        main_layout.addLayout(login_layer)
        main_layout.addLayout(password_layer)
        main_layout.addLayout(buttons_layer)
        self.window_auth.setLayout(main_layout)
        self.window_auth.show()

    def return_data(self):
        self.settingsDict['eqsl_user'] = self.login_input.text().strip()
        self.settingsDict['eqsl_password'] = self.password_input.text().strip()
        # main.Settings_file().update_file_to_disk()
        self.window_auth.close()
        self.input_form_key = 1
        self.start_sending()

    def start_sending(self):
        self.send_thread = QtCore.QThread()
        self.send_eqsl = Eqsl_send(settingsDict=self.settingsDict,
                                   recordObject=self.recordObject,
                                   std=self.std,
                                   parent_window=self.parrent_window)
        self.send_eqsl.moveToThread(self.send_thread)
        self.send_eqsl.error_message.connect(self.show_message)
        self.send_eqsl.sent_ok.connect(self.send_complited)
        self.send_thread.started.connect(self.send_eqsl.run)
        self.send_thread.start()

    @QtCore.pyqtSlot(str)
    def show_message(self, string: str):
        std.std.message(self.parrent_window, string, "<p style='color: red;'>ERROR</p>")
        if self.input_form_key == 1:
            self.settingsDict['eqsl_user'] = ''
            self.settingsDict['eqsl_password'] = ''
        self.error_signal.emit()
        self.send_thread.exec()

    @QtCore.pyqtSlot()
    def send_complited(self):
        if self.input_form_key == 1:
            main.settings_file.save_all_settings(main.settings_file, self.settingsDict)
        self.send_ok.emit()
        self.send_thread.exec()


class Eqsl_send_file(QThread):
    eqsl_send_file_answer = QtCore.pyqtSignal(object)
    error_connection = QtCore.pyqtSignal(object)
    def __init__(self, parent, file_name, settings_dict):
        super().__init__(parent)
        self.file_name = file_name
        self.settings_dict = settings_dict
        self.url_post = "https://www.eQSL.cc/qslcard/ImportADIF.cfm"

    def run(self):
        files = {'Filename': open(self.file_name, 'rb')}
        values = {'EQSL_USER': self.settings_dict['eqsl_user'],
                  'EQSL_PSWD': self.settings_dict['eqsl_password']}
        try:
            answer = requests.post(self.url_post, files=files, data=values)
            if answer.status_code == 200:
                self.eqsl_send_file_answer.emit(answer)
            else:
                self.error_connection.emit("Connection error")
        except BaseException:
            self.error_connection.emit("Network error (Exception)")


class check_update(QThread):

    def __init__(self, APP_VERSION, settingsDict, parrentWindow):
        super().__init__()
        self.version = APP_VERSION
        self.settingsDict = settingsDict
        self.parrent = parrentWindow

    def run(self):

        server_url_get = 'http://357139-vds-bastonsv.gmhost.pp.ua'
        path_directory_updater_app = "/upd/"

        action = server_url_get + path_directory_updater_app + self.version + "/" + self.settingsDict['my-call']
        flag = 0
        data_flag = 0
        try:
            response = requests.get(action)
            flag = 1
        except Exception:
            flag = 0

        if flag == 1:
            soup = BeautifulSoup(response.text, 'html.parser')
            try:
                version = soup.find(id="version").get_text()
                git_path = soup.find(id="git_path").get_text()
                date = soup.find(id="date").get_text()
                data_flag = 1
            except Exception:
                std.std.message(self.parrent, "You have latest version", "UPDATER")
                self.parrent.check_update.setText("> Check update <")
                self.parrent.check_update.setEnabled(True)
            if data_flag == 1:
                update_result = QMessageBox.question(self.parrent, "LinuxLog | Updater",
                                                     "Found new version " + version + " install it?",
                                                     buttons=QMessageBox.Yes | QMessageBox.No,
                                                     defaultButton=QMessageBox.Yes)
                if update_result == QMessageBox.Yes:
                    # print("Yes")
                    # try:
                    self.parrent.check_update.setText("Updating")
                    adi_name_list = []
                    for file in os.listdir():
                        if file.endswith(".adi"):
                            adi_name_list.append(file)
                    rules_name_list = []
                    for file in os.listdir():
                        if file.endswith(".rules"):
                            rules_name_list.append(file)
                    # print("Rules name List:_>", rules_name_list)
                    # print("Adi name List:_>", adi_name_list)
                    home = expanduser("~")
                    # print("Home path:_>", home)
                    os.mkdir(home + "/linuxlog-backup")
                    for i in range(len(adi_name_list)):
                        os.system("cp '" + adi_name_list[i] + "' " + home + "/linuxlog-backup")
                    for i in range(len(rules_name_list)):
                        os.system("cp  '" + rules_name_list[i] + "' " + home + "/linuxlog-backup")
                    os.system("cp settings.cfg " + home + "/linuxlog-backup")
                    # archive dir
                    if os.path.isdir(home + '/linlog-old'):
                        pass
                    else:
                        os.system("mkdir " + home + "/linlog-old")
                    os.system("tar -cf " + home + "/linlog-old/linlog" + version + ".tar.gz " + home + "/linlog/")

                    # delete dir linlog
                    os.system("rm -rf " + home + "/linlog/")
                    # clone from git repository to ~/linlog
                    os.system("git clone " + git_path + " " + home + "/linlog")

                    # copy adi and rules file from linuxlog-backup to ~/linlog
                    for i in range(len(adi_name_list)):
                        os.system("cp '" + home + "/linuxlog-backup/" + adi_name_list[i] + "' '" + home + "/linlog'")
                    for i in range(len(rules_name_list)):
                        os.system("cp '" + home + "/linuxlog-backup/" + rules_name_list[i] + "' '" + home + "/linlog'")

                    # read and replace string in new settings.cfg

                    file = open(home + "/linlog/settings.cfg", "r")
                    settings_list = {}
                    for configstring in file:
                        if configstring != '' and configstring != ' ' and configstring[0] != '#':
                            configstring = configstring.strip()
                            configstring = configstring.replace("\r", "")
                            configstring = configstring.replace("\n", "")
                            splitString = configstring.split('=')
                            settings_list.update({splitString[0]: splitString[1]})
                    file.close()
                    for key_new in settings_list:
                        for key_old in self.settingsDict:
                            if key_new == key_old:
                                settings_list[key_new] = self.settingsDict[key_old]

                    # print("settings list^_>", settings_list)

                    filename = home + "/linlog/settings.cfg"
                    with open(filename, 'r') as f:
                        old_data = f.readlines()
                    for index, line in enumerate(old_data):
                        key_from_line = line.split('=')[0]
                        # print ("key_from_line:",key_from_line)
                        for key in settings_list:

                            if key_from_line == key:
                                # print("key",key , "line", line)
                                old_data[index] = key + "=" + settings_list[key] + "\n"
                    with open(filename, 'w') as f:
                        f.writelines(old_data)
                    # done!

                    # delete backup dir
                    os.system("rm -rf " + home + "/linuxlog-backup")

                    std.std.message(self.parrent, "Update to v." + version + " \nCOMPLITED \n "
                                                                             "Please restart LinuxLog", "UPDATER")
                    self.version = version
                    self.parrent.check_update.setText("> Check update <")
                    self.parrent.check_update.setEnabled(True)
                    self.parrent.text.setText("Version:" + version + "\n\nBaston Sergey\nbastonsv@gmail.com")


                else:
                    #  print("No")
                    self.parrent.check_update.setText("> Check update <")
                    self.parrent.check_update.setEnabled(True)

        else:
            std.std.message(self.parrent, "Sorry\ntimeout server.", "UPDATER")


class Clublog(QtCore.QObject):

    sent_qso_ok = QtCore.pyqtSignal(object)
    sent_qso_no = QtCore.pyqtSignal(object)
    del_qso_ok = QtCore.pyqtSignal(object)
    del_qso_no = QtCore.pyqtSignal(object)
    network_error = QtCore.pyqtSignal()

    def __init__(self, settingsDict, adi_string=None):
        super().__init__()
        self.key = "1262ee63ad3b25917b695cb78b3d3bdcfd8e2ff8"
        self.adi_string = adi_string
        #self.data = data_for_tx
        self.settingsDict = settingsDict
        self.upload_file_url = "https://clublog.org/putlogs.php"
        self.add_record_url = "https://clublog.org/realtime.php"
        self.delete_record_url = "https://clublog.org/delete.php"

    def export_file(self, file, clear=None):
        '''
         Export ADI file to Club log
         url -  https://clublog.org/putlogs.php
         method POST
         data in request:
            email: A registered email address in Club Log
            password: The password to authenticate the email login
            callsign: Optionally, the callsign into which the logs should be uploaded.
                        If not set, the primary callsign of the account is used.
            clear: If a value of 1 is given, the log will be flushed before the new upload is processed. In all other cases, including if this field is absent, the log will be merged.
            file: A multipart/form-data upload which is used to POST the ADIF file with the form. The filename should be an ADIF, LGS or a ZIP file containing one of those.
            api: An API key to access this interface (protecting it from abuse), which you can obtain by emailing the helpdesk.

        :return: result 0 - Ok, 1 - error
        '''
        if clear != None:
            clear = "1"

            multipart_data = {
                "email": self.settingsDict['email-clublog'],
                "password": self.settingsDict['pass-clublog'],
                "callsign": self.settingsDict['my-call'],
                "clear": clear,
                "api": self.key
            }
        else:
            multipart_data = {
                "email": self.settingsDict['email-clublog'],
                "password": self.settingsDict['pass-clublog'],
                "callsign": self.settingsDict['my-call'],
                "api": self.key
            }
            file_data = {"file": ('log.ADI', open(file, 'rb'),'text/plain')}

            #print(multipart_data)
        response = requests.post(self.upload_file_url, files=file_data, data=multipart_data, headers={'enctype': 'multipart/form-data' })
        return response

    def add_record(self):
        #print("data_record", self.adi_string)
        multipart_data = {
            "email": self.settingsDict['email-clublog'],
            "password": self.settingsDict['pass-clublog'],
            "callsign": self.settingsDict['my-call'],
            "adif": self.adi_string,
            "api": self.key
        }
        try:
            response = requests.post(self.add_record_url, data=multipart_data)
            print("Type response:_>", type(response))
            if response.status_code == 200:
                self.sent_qso_ok.emit(response)
            if response.status_code != 200:
                self.sent_qso_no.emit(response)
            return response
        except Exception:
            self.network_error.emit()

    def del_record(self, record_object):
        '''
        Delete record from club log
        :param record_object: dict - object with data about QSO
        All data in dict: records_number, QSO_DATE, TIME_ON, FREQ, CALL, MODE, RST_RCVD, RST_SENT
        NAME, QTH, OPERATOR, BAND, COMMENTS, TIME_OFF, EQSL_QSL_SENT
        :return: response from server
        '''
        date = record_object['date']
        date_formated = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
        time = std.std.std_time(self,record_object['time'])

        time_formated = time[0:2] +':' + time[2:4] + ':' + time[4:]
        date_time = date_formated + " " + time_formated
        print ("Band:_>", record_object['band'].replace("M",'').strip(), "\nDate time:", date_time)
        multipart_data = {
            "email": self.settingsDict['email-clublog'],
            "password": self.settingsDict['pass-clublog'],
            "callsign": self.settingsDict['my-call'],
            "dxcall": record_object['call'],
            "datetime": date_time,
            "bandid": record_object['band'].replace("M",'').strip(),
            "api": self.key
        }
        try:
            response = requests.post(self.delete_record_url, data=multipart_data)

            if response.status_code == 200:
                self.del_qso_ok.emit(response)
            if response.status_code != 200:
                self.del_qso_no.emit(response)
            return response
        except Exception:
            self.network_error.emit()
