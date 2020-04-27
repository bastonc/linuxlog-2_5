# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

import urllib
import std
import requests
import shutil
import os
from os.path import expanduser
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap
# import urllib.request
# import urllib.parse
from urllib.request import urlretrieve
from urllib.parse import quote
from PyQt5.QtCore import QThread
from PyQt5 import QtCore
from PyQt5.QtWidgets import  QWidget
import main


class internetWorker(QThread):

    def __init__(self, window, callsign, settings, parrent=None):
        super().__init__()
        self.internet_search_window = window
        self.callsign = callsign
        self.settings = settings

    def run(self):
        # print (self.callsign)
        info_from_internet_array = internetWorker.get_image_from_server(self)
        print (info_from_internet_array)
        if info_from_internet_array != {}:
            pixmap = QPixmap(info_from_internet_array.get('img'))
            #pixmap_resized = pixmap.scaled(int(self.settings['search-internet-width']) - 8,
            #                              int(self.settings['search-internet-height']) - 8,
            #                              QtCore.Qt.KeepAspectRatio)
            pixmap_resized = pixmap.scaledToWidth(int(self.settings['image-width']) - 8)

            pixmap_resized_height = pixmap_resized.scaledToHeight(int(self.settings['image-height']) - 8)
            self.internet_search_window.labelImage.setPixmap(pixmap_resized_height)
            # return info_from_internet_array

    def get_image_from_server(self):
        '''
        метод загружает изображение с qrz.com
        принимает callsign - позывной
        '''
        url_found = "https://www.qrz.com/lookup"
        print(self.callsign)
        parameter_request = "tquery=" + self.callsign + "&mode: callsign"
        parameter_to_byte = bytearray(parameter_request, "utf-8")
        data_dictionary = {}
        try:
            response = urllib.request.urlopen(url_found, parameter_to_byte)
            html = response.read().decode("utf-8")
            soup = BeautifulSoup(html, 'html.parser')
        except Exception:
            print("get_image_from_server: Don't connection")

        img = soup.find(id="mypic")

        file_name = self.callsign.replace("/", "_")
        print("file_name, img:_>", file_name, img)


        try:
            if img != None:
                urllib.request.urlretrieve(img['src'], "image/" + file_name + ".jpg")
                data_dictionary.update({'img': "image/" + file_name + ".jpg"})
            print(data_dictionary)
        except Exception:
            print("Exception:", Exception)

        return data_dictionary


class Eqsl_services (QThread):

    def __init__(self, settingsDict, recordObject, std, parent_window):
        super().__init__()
        self.recordObject = recordObject
        self.settingsDict = settingsDict
        self.std = std
        self.parrent_window = parent_window

    def send_qso_to_qrz(self):
        server_url_post = 'https://logbook.qrz.com/api'
        key_account = "KEY=81FE-08CA-D97D-8709&"
        action = "ACTION=INSERT&ADIF=<band:3>80m<mode:3>SSB<call:5>RN6XC<qso_date:8>20140121<station_callsign:6>UR4LGA<time_on:4>0346<eor>"
        print ("key+action", key_account + action)
        response = requests.post(server_url_post, data=key_account + action)

        print ("send_to_qrz", response.text)

    def run(self):

        api_url_eqsl = 'https://www.eQSL.cc/qslcard/importADIF.cfm?ADIFData=LinLog upload'
        data_qso_string = '<BAND:'+str(len(self.recordObject['BAND']))+'>'+str(self.recordObject['BAND'])+' <CALL:'+str(len(self.recordObject['CALL']))+'>'+str(self.recordObject['CALL'])+' <MODE:'+str(len(self.recordObject['MODE']))+'>'+str(self.recordObject['MODE'])+' <QSO_DATE:'+str(len(self.recordObject['QSO_DATE']))+'>'+str(self.recordObject['QSO_DATE'])+' <RST_RCVD:'+str(len(self.recordObject['RST_RCVD']))+'>'+str(self.recordObject['RST_RCVD'])+' <RST_SENT:'+str(len(self.recordObject['RST_SENT']))+'>'+str(self.recordObject['RST_SENT'])+' <TIME_ON:'+str(len(self.recordObject['TIME_ON']))+'>'+str(self.recordObject['TIME_ON'])+' <EOR>'
        data_string_code_to_url = urllib.parse.quote(data_qso_string)
        user_pasword_eqsl = '&EQSL_USER='+self.settingsDict['eqsl_user']+'&EQSL_PSWD='+self.settingsDict['eqsl_password']
        #data_qso_string = 'ADIFData=LinLog%20upload%20%3CBAND%3A'+str(len(band))+'%3AC%3E'+str(band)+'%20%2D%20%3CCALL%3A'+str(len(call))+'%3AC%3'+str(call)+'%20%3CMODE%3A'+str(len(mode))+'%3AC%3E'+str(mode)+'%20%3CQSO%5FDATE%3A'+str(len(qso_date))+'%3AD%3E'+str(qso_date)+'%20%3CRST%5FRCVD%3A'+str(len(rst_rsvd))+'%3AC%3E'+str(rst_rsvd)+'%20%3CRST%5FSENT%3A'+str(len(rst_send))+'%3AC%3E'+str(rst_send)+'%20%2D%20%3CTIME%5FON%3A'+str(len(time_on))+'%3AC%3E'+str(time_on)+'%20%3CEOR%3E&EQSL_USER='+self.settingsDict['eqsl_user']+'&EQSL_PSWD='+self.settingsDict['eqsl_password']
        print ("end_qso_to_eqsl", api_url_eqsl+data_string_code_to_url)

        request_eqsl = requests.get(api_url_eqsl+data_string_code_to_url+user_pasword_eqsl)

        if request_eqsl.status_code != 200:

            std.std().message("Can't send to eQSL", "")
            print("request_eqsl.status_code", request_eqsl.status_code)
        else:
            soup = BeautifulSoup(request_eqsl.text, 'html.parser')
            response = soup.body.contents[0]
            print ("SOUP", soup.body.contents[0].strip())
            if (response.find('Warning')!= -1) or (response.find('Error')!= -1):
                message = QMessageBox(self.parrent_window)
                #message.setFixedHeight(200)
                #message.setGeometry(500, 300, 1000, 500)
                message.setStyleSheet("font: 12px;")
                message.setWindowTitle("Warning!")
                message.setText("Can't send to eQSL.cc")
                #message.setText(soup.body.contents[0].strip())
                message.setInformativeText(soup.body.contents[0].strip())
                message.setStandardButtons(QMessageBox.Ok)
                message.exec_()
            #print(request_eqsl.text)
        


        #request_eqsl = requests.get(
         #   'https://www.eQSL.cc/qslcard/importADIF.cfm?ADIFData=LinLog%20upload%20%3CADIF%5FVER%3A4%3E1%2E00%20%3CEOH%3E%20%3CBAND%3A3%3AC%3E30M%20%2D%20%3CCALL%3A6%3AC%3EWB4WXX%20%3CMODE%3A3%3AC%3ESSB%20%3CQSO%5FDATE%3A8%3AD%3E20010503%20%3CRST%5FRCVD%3A2%3AC%3E52%20%3CRST%5FSENT%3A2%3AC%3E59%20%2D%20%3CTIME%5FON%3A6%3AC%3E122500%20%3CEOR%3E&EQSL_USER=ur4lga&EQSL_PSWD=a9minx3m')

class check_update (QThread):

    def __init__(self, APP_VERSION, settingsDict, parrentWindow):
        super().__init__()
        self.version = APP_VERSION
        self.settingsDict = settingsDict
        self.parrent = parrentWindow


    def run(self):

        server_url_get = 'http://357139-vds-bastonsv.gmhost.pp.ua'
        path_directory_updater_app = "/upd/"

        action = server_url_get+path_directory_updater_app+self.version+"/"+self.settingsDict['my-call']
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
                                     "Found new version "+version+" install it?",
                                     buttons=QMessageBox.Yes | QMessageBox.No,
                                     defaultButton=QMessageBox.Yes)
                if update_result == QMessageBox.Yes:
                    print("Yes")
                    #try:
                    self.parrent.check_update.setText("Updating")
                    adi_name_list = []
                    for file in os.listdir():
                        if file.endswith(".adi"):
                            adi_name_list.append(file)
                    rules_name_list = []
                    for file in os.listdir():
                        if file.endswith(".rules"):
                            rules_name_list.append(file)
                    print("Rules name List:_>", rules_name_list)
                    print("Adi name List:_>", adi_name_list)
                    home = expanduser("~")
                    print("Home path:_>", home)
                    os.mkdir(home+"/linuxlog-backup")
                    for i in range(len(adi_name_list)):
                        os.system("cp '"+adi_name_list[i]+"' "+home+"/linuxlog-backup")
                    for i in range(len(rules_name_list)):
                        os.system("cp  '" + rules_name_list[i] + "' " + home + "/linuxlog-backup")
                    os.system("cp settings.cfg " + home+"/linuxlog-backup")
                    # archive dir
                    if os.path.isdir(home+'/linlog-old'):
                     pass
                    else:
                        os.system("mkdir "+home+"/linlog-old")
                    os.system("tar -cf "+home+"/linlog-old/linlog"+version+".tar.gz " + home + "/linlog/")

                    # delete dir linlog
                    os.system("rm -rf " + home + "/linlog/")
                    # clone from git repository to ~/linlog
                    os.system("git clone " + git_path + " " + home + "/linlog")

                    # copy adi and rules file from linuxlog-backup to ~/linlog
                    for i in range(len(adi_name_list)):
                        os.system("cp '"+home+"/linuxlog-backup/" + adi_name_list[i] + "' '" + home + "/linlog'")
                    for i in range(len(rules_name_list)):
                        os.system("cp '" + home + "/linuxlog-backup/" + rules_name_list[i] + "' '" + home + "/linlog'")

                    # read and replace string in new settings.cfg

                    file = open(home+"/linlog/settings.cfg", "r")
                    settings_list = {}
                    for configstring in file:
                        if configstring != '' and configstring != ' ' and configstring[0] != '#':
                            configstring = configstring.strip()
                            configstring = configstring.replace("\r", "")
                            configstring = configstring.replace("\n", "")
                            splitString = configstring.split('=')
                            settings_list.update({splitString[0]: splitString[1]})
                    file.close()
                    settings_list['diploms-json'] = self.settingsDict['diploms-json']
                    settings_list['background-color'] = self.settingsDict['background-color']
                    settings_list['form-background'] = self.settingsDict['form-background']
                    settings_list['color'] = self.settingsDict['color']
                    settings_list['solid-color'] = self.settingsDict['solid-color']
                    settings_list['my-call'] = self.settingsDict['my-call']
                    print("settings list^_>", settings_list)

                    filename = home+"/linlog/settings.cfg"
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

                    #delete backup dir
                    os.system("rm -rf " + home + "/linuxlog-backup")

                    std.std.message(self.parrent, "Update to v."+version+" \nCOMPLITED \n "
                                                                         "Please restart LinuxLog", "UPDATER")
                    self.version = version
                    self.parrent.check_update.setText("> Check update <")
                    self.parrent.check_update.setEnabled(True)
                    self.parrent.text.setText("Version:"+version+"\n\nBaston Sergey\nbastonsv@gmail.com")
                #except Exception:
                        #std.std.message(self.parrent, "Don't found adi/rules files", "Oops")


                                #print("Files names:_>", file)
                            #    inp = open(os.path.join(dirpath, file_name), 'r')
                            #    for line in inp:
                            #        if pattern in line:
                            #            print(inp)


                else:
                    print("No")
                    self.parrent.check_update.setText("> Check update <")
                    self.parrent.check_update.setEnabled(True)

        else:
            std.std.message(self.parrent, "Sorry\ntimeout server.", "UPDATER")
        #std.std.message(self.parrent, "Found new version: "+version+" \n Date:"+date, "UPDATER")
       # print("SOUP", version,"\n", git_path,"\n", date)
        #except Exception:
        #    print("Exception in chek_update:_>", Exception)
         #   std.std.message(self.parrent, "You have latest version", "UPDATER")


        #if (response.find('Warning') != -1) or (response.find('Error') != -1):
         #   message = QMessageBox(self.parrent_window)
            # message.setFixedHeight(200)
            # message.setGeometry(500, 300, 1000, 500)
        #    message.setStyleSheet("font: 12px;")
        #    message.setWindowTitle("Warning!")
        #    message.setText("Can't send to eQSL.cc")
            # message.setText(soup.body.contents[0].strip())
        #    message.setInformativeText(soup.body.contents[0].strip())
         #   message.setStandardButtons(QMessageBox.Ok)
         #   message.exec_()
        # print(request_eqsl.text)
        #print("Check_update:_>",response, "\n", response.text)
