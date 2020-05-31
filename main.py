#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
import parse
import re
import os
import datetime
import telnetlib
import internetworker
import time
import tci
import std
import settings
import subprocess
import ext
import json
import requests
# import cat # for version 1.262
from os.path import expanduser
from bs4 import BeautifulSoup
from gi.repository import Notify, GdkPixbuf
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QStyle, QCheckBox, QMenu, QMessageBox, QAction, QWidget, QMainWindow, QTableView, QTableWidget, QTableWidgetItem, QTextEdit, \
    QLineEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QComboBox
from PyQt5.QtCore import pyqtSignal, QObject, QEvent, QRect, QPoint, QSize
from PyQt5.QtGui import QIcon, QFont, QPalette, QBrush, QPixmap, QColor, QStandardItemModel
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread
from time import gmtime, strftime, localtime


class Settings_file:

    def update_file_to_disk(self):
        #self.settingsDict = self
        filename = 'settings.cfg'
        with open(filename, 'r') as f:
            old_data = f.readlines()
        for index, line in enumerate(old_data):
            key_from_line = line.split('=')[0]
            # print ("key_from_line:",key_from_line)
            for key in self.settingsDict:

                if key_from_line == key:
                    # print("key",key , "line", line)
                    old_data[index] = key + "=" + self.settingsDict[key] + "\n"
        with open(filename, 'w') as f:
            f.writelines(old_data)
        #print("Update_to_disk: ", old_data)
        return True

class Adi_file:

    def __init__(self):

        self.filename = 'log.adi'

        with open(self.filename, 'r') as file: #read all strings

            self.strings_in_file = file.readlines()

    def get_last_string(self):
        return len(self.strings_in_file)

    def rename_adi(self, old_name, new_name):
        os.rename(old_name, new_name)

    def store_changed_qso(self, object):
        '''
        1. Function recived object in format (ch.1)
        2. Building string for log.adi file
        3. Read all strings
        4. ReWrite string in log.adi file
        chapter 1
        :param object: {'BAND': '40M', 'CALL': 'UR4LGA', 'FREQ': 'Freq: 7028500', 'MODE': 'ESSB',
        'OPERATOR': 'UR4LGA', 'QSO_DATE': '20191109', 'TIME_ON': '224058', 'RST_RCVD': '59',
         'RST_SENT': '59', 'NAME': '', 'QTH': '', 'COMMENTS': '', 'TIME_OFF': '224058',
         'eQSL_QSL_RCVD': 'Y', 'EOR': 'R\n',
         'string_in_file': '186', 'records_number': '89'}

        :return:
        '''

        #print("hello  store_changed_qso method in Adi_file class\n", object)
        stringToAdiFile = "<BAND:" + str(len(object['BAND'])) + ">" + object['BAND'] + "<CALL:" + str(
            len(object['CALL'])) + ">"

        stringToAdiFile = stringToAdiFile + object['CALL'] + "<FREQ:" + str(len(object['FREQ'])) + ">" + \
                          object['FREQ']
        stringToAdiFile = stringToAdiFile + "<MODE:" + str(len(object['MODE'])) + ">" + object[
            'MODE'] + "<OPERATOR:" + str(len(object['OPERATOR']))
        stringToAdiFile = stringToAdiFile + ">" + object['OPERATOR'] + "<QSO_DATE:" + str(
            len(object['QSO_DATE'])) + ">"
        stringToAdiFile = stringToAdiFile + object['QSO_DATE'] + "<TIME_ON:" + str(
            len(object['TIME_ON'])) + ">"
        stringToAdiFile = stringToAdiFile + object['TIME_ON'] + "<RST_RCVD:" + \
                          str(len(object['RST_RCVD'])) + ">" + object['RST_RCVD']
        stringToAdiFile = stringToAdiFile + "<RST_SENT:" + str(len(object['RST_SENT'])) + ">" + \
                          object['RST_SENT'] + "<NAME:" + str(len(object['NAME'])) + ">" + object['NAME'] + \
                          "<QTH:" + str(len(object['QTH'])) + ">" + object['QTH'] + "<COMMENTS:" + \
                          str(len(object['COMMENTS'])) + ">" + object['COMMENTS'] + "<TIME_OFF:" + \
                          str(len(object['TIME_OFF'])) + ">" + object['TIME_OFF'] + "<EQSL_QSL_SENT:"+ \
                          str(len(object['EQSL_QSL_SENT']))+">"+object['EQSL_QSL_SENT']+"<EOR>\n"
        print("store_changed_qso: stringToAdiFile", stringToAdiFile)

        self.strings_in_file[int(object['string_in_file'])-1] = stringToAdiFile
        with open(self.filename, 'w') as file:
            #file.seek(0, 2)
            file.writelines(self.strings_in_file)


        #print("this:", self.strings_in_file[int(object['string_in_file'])-1])

    def delete_qso_from_file(self, row_in_file):
        with open(self.filename, 'r') as file:
            # file.seek(0, 2)
            lines_in_file = file.readlines()

        print ("Delete QSO from file \nAll lines", len(lines_in_file), "\nrow_in_files:_>", row_in_file)
        lines_in_file[int(row_in_file)-1] = ''
        with open(self.filename, 'w') as file:
            # file.seek(0, 2)
            file.writelines(lines_in_file)


    def get_header(self):

        '''
        This function returned string with cariage return
        :return: string header with cariage return
        '''

        self.header_string="ADIF from LinLog Light v."+APP_VERSION+" \n"
        self.header_string +="Copyright 2019-"+strftime("%Y", gmtime())+"  Baston V. Sergey\n"
        self.header_string +="Header generated on "+strftime("%d/%m/%y %H:%M:%S", gmtime())+" by "+settingsDict['my-call']+"\n"
        self.header_string +="File output restricted to QSOs by : All Operators - All Bands - All Modes \n"
        self.header_string +="<PROGRAMID:6>LinLog\n"
        self.header_string += "<PROGRAMVERSION:"+str(len(APP_VERSION))+">"+APP_VERSION+"\n"
        self.header_string += "<EOH>\n\n"
        return self.header_string

    def get_all_qso(self):
        try:
            with  open(self.filename, 'r') as file:
                lines = file.readlines()
                #print (lines)
        except Exception:
            print ("Adi_file: Exception. Don't open or read"+self.filename)

    def record_dict_qso (self, list_data):
        '''
        This function recieve List (list_data) with Dictionary with QSO-data
        Dictionary including:
        call
        name
        qth
        rst_send
        rst_reciev
        band
        mode
        comment
        :param list_data: List with Dictionary with QSO-data
        :return:
        '''
        index = len(list_data)
        with open ('log.adi', 'a') as file:
            for i in range(index):
               # print(i,list_data[i]['BAND'])
                stringToAdiFile = "<BAND:" + str(len(list_data[i]['BAND'])) + ">" + list_data[i]['BAND'] + "<CALL:" + str(
                    len(list_data[i]['CALL'])) + ">"

                stringToAdiFile = stringToAdiFile + list_data[i]['CALL'] + "<FREQ:" + str(len(list_data[i]['FREQ'])) + ">" + \
                                  list_data[i]['FREQ']
                stringToAdiFile = stringToAdiFile + "<MODE:" + str(len(list_data[i]['MODE'])) + ">" + list_data[i][
                    'MODE'] + "<OPERATOR:" + str(len(list_data[i]['OPERATOR']))
                stringToAdiFile = stringToAdiFile + ">" + list_data[i]['OPERATOR'] + "<QSO_DATE:" + str(
                    len(list_data[i]['QSO_DATE'])) + ">"
                stringToAdiFile = stringToAdiFile + list_data[i]['QSO_DATE'] + "<TIME_ON:" + str(
                    len(list_data[i]['TIME_ON'])) + ">"
                stringToAdiFile = stringToAdiFile + list_data[i]['TIME_ON'] + "<RST_RCVD:" + \
                                  str(len(list_data[i]['RST_RCVD'])) + ">" + list_data[i]['RST_RCVD']
                stringToAdiFile = stringToAdiFile + "<RST_SENT:" + str(len(list_data[i]['RST_SENT'])) + ">" + \
                                  list_data[i]['RST_SENT'] + "<NAME:" + str(len(list_data[i]['NAME'])) + ">" + list_data[i]['NAME'] + \
                                  "<QTH:" + str(len(list_data[i]['QTH'])) + ">" + list_data[i]['QTH'] + "<COMMENTS:" + \
                                  str(len(list_data[i]['COMMENTS'])) + ">" + list_data[i]['COMMENTS'] + "<TIME_OFF:" + \
                                  str(len(list_data[i]['TIME_OFF'])) + ">" + list_data[i]['TIME_OFF'] + "<eQSL_QSL_RCVD:1>Y<EOR>\n"
                file.write(stringToAdiFile)



        #print(list_data[0]['call'])
        #header = self.get_header()
        #with open('aditest.adi', 'w') as file:
          #  file.writelines(header)
            #file.writelines(list_data)

    def create_adi(self, name):
        with open(name, 'w') as f:
            f.writelines(self.get_header())

class Filter(QObject):

    previous_call = ''



    def eventFilter(self, widget, event):


        if event.type() == QEvent.FocusOut:

                textCall = logForm.inputCall.text()
                foundList = self.searchInBase(textCall)

                logSearch.overlap(foundList)

                freq = logForm.get_freq()

                if textCall != '' and textCall != Filter.previous_call:
                    if settingsDict['search-internet-window'] == 'true':

                        Filter.previous_call = textCall
                        self.isearch = internetworker.internetWorker(window=internetSearch, callsign=textCall, settings=settingsDict)
                        self.isearch.start()
                        if settingsDict['tci'] == 'enable':
                            try:
                                tci.Tci_sender(settingsDict['tci-server']+":"+settingsDict['tci-port']).set_spot(textCall, freq)
                            except:
                                print("Filter: Can't connect to TCI-server")

                if textCall == '' or textCall == ' ':
                    pixmap = QPixmap('logo.png')




                return False

        if event.type() == QEvent.FocusIn:

                if logForm.inputCall.text() == '':
                    if settingsDict['mode-swl'] != 'enable':
                        logForm.inputRstS.setText('59')
                        logForm.inputRstR.setText('59')
                    else:
                        logForm.inputRstR.setText('SWL')
                    # return False so that the widget will also handle the event
                    # otherwise it won't focus out
                return False
        else:
                # we don't care about other events
                return False



    def searchInBase(self, call):
        #print ("search_in Base:_>", call)
        foundList = []  # create empty list for result list
        All_records = logWindow.get_all_record()
        lenRecords = len(All_records)  # get count all Records
        #print("Search InBase: lenRecords: _>", All_records)
        for counter in range(lenRecords):  # start cicle where chek all elements at equivivalent at input call
            if All_records[counter]['CALL'].strip() == call.strip():
                foundList.append(All_records[counter])

        #print("search_in Base:_>",foundList)
        return foundList
        # print (foundList)
        #

class Communicate(QObject):
    signalComplited = pyqtSignal(list)

class Fill_table(QThread):

    fill_complite = QtCore.pyqtSignal()

    def __init__(self, all_column, window, all_record, communicate, settingsDict, parent=None):
        super().__init__()
        self.all_collumn = all_column
        self.window = window
        self.all_record = all_record
        self.c = communicate
        self.settingsDict = settingsDict

    def run(self):

        self.allRecord = parse.getAllRecord(self.all_collumn, "log.adi")
        self.all_record = self.allRecord
        self.c = Communicate()
        self.c.signalComplited.connect(Reciev_allRecords)
        self.c.signalComplited.emit(self.allRecord)

        self.allRows = len(self.allRecord)
        print(" self.allRecords:_> ",  len(self.allRecord))
        self.window.tableWidget_qso.setRowCount(self.allRows)
        allCols = len(self.all_collumn)
        for row in range(self.allRows):
           # if self.allRecord[(self.allRows - 1) - row]['EQSL_QSL_SENT'] == 'Y':
           #     color = QColor(settingsDict['eqsl-sent-color'])
          #  else:
          #      color = QColor(200, 200, 200, 0)
            for col in range(allCols):
                #print("col -", col, self.all_collumn[col])
                pole = self.all_collumn[col]
                # print(self.allRows, row, self.allRows - row )
                # print("Number record:", self.allRecord[row][pole])

                if self.allRecord[(self.allRows - 1) - row][pole] != ' ' or \
                        self.allRecord[(self.allRows - 1) - row][pole] != '':
                    if col == 0:
                       self.window.tableWidget_qso.setItem(row, col,
                                                 self.protectionItem(self.allRecord[(self.allRows - 1) - row][pole],
                                                                     Qt.ItemIsSelectable | Qt.ItemIsEnabled))
                       self.window.tableWidget_qso.item(row, col).setForeground(QColor(self.settingsDict["color-table"]))


                        # QTableWidgetItem(self.allRecord[(self.allRows - 1) - row][pole]))
                    elif col == 1:
                        date = str(self.allRecord[(self.allRows - 1) - row][pole])
                        date_formated = date[:4] + "-" + date[4:6] + "-" + date[6:]
                        #print(time_formated)
                        self.window.tableWidget_qso.setItem(row, col,
                                                        QTableWidgetItem(date_formated))
                        self.window.tableWidget_qso.item(row, col).setForeground(QColor(self.settingsDict["color-table"]))

                    elif col == 2:
                        time = str(self.allRecord[(self.allRows - 1) - row][pole])
                        time_formated = time[:2] + ":" + time[2:4] + ":" + time[4:]
                        #print(time_formated)
                        self.window.tableWidget_qso.setItem(row, col,
                                                        QTableWidgetItem(time_formated))
                        self.window.tableWidget_qso.item(row, col).setForeground(
                            QColor(self.settingsDict["color-table"]))



                    else:
                        self.window.tableWidget_qso.setItem(row, col,
                                                 QTableWidgetItem(self.allRecord[(self.allRows - 1) - row][pole]))
                        self.window.tableWidget_qso.item(row, col).setForeground(
                            QColor(self.settingsDict["color-table"]))

                    if self.allRecord[(self.allRows - 1) - row]['EQSL_QSL_SENT'] == 'Y':
                        self.window.tableWidget_qso.item(row, col).setBackground(QColor(self.settingsDict['eqsl-sent-color']))
        self.fill_complite.emit()
        #self.window.tableWidget.resizeColumnsToContents()
        #self.window.tableWidget.resizeRowsToContents()

    def update_All_records(self, all_records_list):
        self.all_records_list = all_records_list
        All_records = self.all_records_list
        #print("update_All_records > All_records:_>", All_records)

    def protectionItem(self, text, flags):
        tableWidgetItem = QTableWidgetItem(text)
        tableWidgetItem.setFlags(flags)
        return tableWidgetItem

class Reciev_allRecords:
    def __init__(self, allRecords):
        self.allRecords = allRecords
        All_records.clear()
        for i in range(len(self.allRecords)):
            All_records.append(self.allRecords[i])

        #print("Reciev_allRecords: _>", allRecords)
        #print("Reciev_allRecords: _>", All_records)

class log_Window(QWidget):

        def __init__(self):
            super().__init__()
            self.filename = "log.adi"
            if os.path.isfile(self.filename):
                pass
            else:
                with open(self.filename, "w") as file:
                    file.write(Adi_file().get_header())

            self.allCollumn = ['records_number', 'QSO_DATE', 'TIME_ON', 'BAND', 'CALL', 'MODE', 'RST_RCVD', 'RST_SENT',
                               'NAME', 'QTH', 'COMMENTS', 'TIME_OFF', 'EQSL_QSL_SENT']
            # self.allRecord = parse.getAllRecord(self.allCollumn, self.filename)

            self.initUI()


        def initUI(self):
                '''
                    Design of log window

                '''

                self.setGeometry(int(settingsDict['log-window-left']),
                                 int(settingsDict['log-window-top']),
                                 int(settingsDict['log-window-width']),
                                 int(settingsDict['log-window-height']))
                self.setWindowTitle('LinuxLog | All QSO')
                self.setWindowIcon(QIcon('logo.png'))
                self.setWindowOpacity(float(settingsDict['logWindow-opacity']))
                style = "background-color:" + settingsDict['background-color'] + "; color:" + settingsDict[
                    'color'] + ";"

                self.setStyleSheet(style)

                # print ('%10s %5s %10s %16s %8s %8s %8s %15s %15s' % ('QSO_DATE', 'TIME', 'FREQ', 'CALL',
                #			'MODE', 'RST_RCVD', 'RST_SENT',	'NAME', 'QTH')
                #		   )

                self.tableWidget_qso = QTableWidget()
                self.tableWidget_qso.move(0, 0)
                self.tableWidget_qso.verticalHeader().hide()
                style_table = "background-color:" + settingsDict['form-background'] + "; color:" + settingsDict[
                    'color-table'] + "; font: 12px;  gridline-color: " + settingsDict['solid-color'] + ";"
                self.tableWidget_qso.setStyleSheet(style_table)
                #self.tableWidget_qso.item().
                fnt = self.tableWidget_qso.font()
                fnt.setPointSize(9)
                self.tableWidget_qso.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                self.tableWidget_qso.customContextMenuRequested.connect(self.context_menu)
                self.tableWidget_qso.setSortingEnabled(True)
                self.tableWidget_qso.setFont(fnt)
                self.tableWidget_qso.setColumnCount(13)
                #self.tableWidget.resizeRowsToContents()

                self.tableWidget_qso.itemActivated.connect(self.store_change_record)

                self.layout = QVBoxLayout()
                self.layout.addWidget(self.tableWidget_qso)
                #self.layout.addWidget(self.label)
                self.setLayout(self.layout)
                #self.show()
                if self.isEnabled():
                    self.refresh_data()

        def context_menu(self, point):
            context_menu = QMenu()
            style_table = "font: 12px"
            #context_menu.setStyleSheet(style_table)
            #context_menu.setFixedWidth(0)
            #context_menu.set
            if self.tableWidget_qso.itemAt(point):
                index_row = self.tableWidget_qso.currentItem().row()
                call  = self.tableWidget_qso.item(index_row, 4).text()
                delete_record = QAction("Delete QSO with " + call, context_menu)
                delete_record.triggered.connect(lambda:
                                                self.delete_qso(self.tableWidget_qso.currentItem().row()))
                edit_record = QAction ("Edit QSO with " + call, context_menu)
                edit_record.triggered.connect(lambda:
                                              self.edit_qso(self.tableWidget_qso.currentItem().row()))
                send_eqsl = QAction("Send eQSL for " + call, context_menu)
                send_eqsl.triggered.connect(lambda:
                                            self.send_eqsl_for_call(self.tableWidget_qso.currentItem().row()))
                if self.tableWidget_qso.item(index_row, 12).text() == "Y":
                    send_eqsl.setEnabled(False)
                else:
                    send_eqsl.setEnabled(True)
                context_menu.addAction(edit_record)
                context_menu.addAction(send_eqsl)
                context_menu.addAction(delete_record)
            context_menu.exec(self.tableWidget_qso.mapToGlobal(point))

        def send_eqsl_for_call(self, row):
            #row = self.tableWidget.currentItem().row()
            record_number = self.tableWidget_qso.item(row, 0).text()
            date = self.tableWidget_qso.item(row, 1).text().replace("-","")
            time = self.tableWidget_qso.item(row, 2).text().replace(":","")
            call = self.tableWidget_qso.item(row, 4).text()
            freq = All_records[int(record_number) - 1]['FREQ']
            rstR = self.tableWidget_qso.item(row, 6).text()
            rstS = self.tableWidget_qso.item(row, 7).text()
            name = self.tableWidget_qso.item(row, 8).text()
            qth = self.tableWidget_qso.item(row, 9).text()
            self.operator = All_records[int(record_number) - 1]['OPERATOR']
            band = self.tableWidget_qso.item(row, 3).text()
            comment = self.tableWidget_qso.item(row, 10).text()
            time_off = self.tableWidget_qso.item(row, 11).text()
            EQSL_QSL_SENT = self.tableWidget_qso.item(row, 12).text()
            mode = self.tableWidget_qso.item(row, 5).text()
            self.string_in_file_edit = All_records[int(record_number) - 1]['string_in_file']
            self.records_number_edit = All_records[int(record_number) - 1]['records_number']

            recordObject = {'records_number': str(record_number), 'QSO_DATE': date, 'TIME_ON': time, 'FREQ': freq,
                            'CALL': call, 'MODE': mode,
                            'RST_RCVD': rstR, 'RST_SENT': rstS, 'NAME': name, 'QTH': qth, 'OPERATOR': self.operator,
                            'BAND': band, 'COMMENTS': comment, 'TIME_OFF': time,
                            'EQSL_QSL_SENT': EQSL_QSL_SENT}

            self.eqsl_send = internetworker.Eqsl_services(settingsDict=settingsDict, recordObject=recordObject, std=std.std,
                                                     parent_window=self)
            self.eqsl_send.send_ok.connect(self.procesing_row)

        @QtCore.pyqtSlot(name='send_eqsl_ok')
        def procesing_row(self):
            row = self.tableWidget_qso.currentItem().row()
            cols = self.tableWidget_qso.columnCount()
            self.tableWidget_qso.setItem(row, 12, QTableWidgetItem("Y"))
            for i in range(cols):
                self.tableWidget_qso.item(row, i).setBackground(QColor(settingsDict['eqsl-sent-color']))
            self.store_change_record()
            print("It's slot processing_row")

        def edit_qso(self, row):
            row = self.tableWidget_qso.currentItem().row()
            record_number = self.tableWidget_qso.item(row, 0).text()
            print("record_number", record_number)
            date = self.tableWidget_qso.item(row, 1).text()
            time = self.tableWidget_qso.item(row, 2).text()
            call = self.tableWidget_qso.item(row, 4).text()
            freq = All_records[int(record_number) - 1]['FREQ']
            rstR = self.tableWidget_qso.item(row, 6).text()
            rstS = self.tableWidget_qso.item(row, 7).text()
            name = self.tableWidget_qso.item(row, 8).text()
            qth = self.tableWidget_qso.item(row, 9).text()
            self.operator_edit = All_records[int(record_number) - 1]['OPERATOR']
            band = self.tableWidget_qso.item(row, 3).text()
            comment = self.tableWidget_qso.item(row, 10).text()
            time_off = self.tableWidget_qso.item(row, 11).text()
            EQSL_QSL_SENT = self.tableWidget_qso.item(row, 12).text()
            mode = self.tableWidget_qso.item(row, 5).text()
            self.string_in_file_edit = All_records[int(record_number) - 1]['string_in_file']
            self.records_number_edit = All_records[int(record_number) - 1]['records_number']
            print("self.string_in_file_edit", self.string_in_file_edit)


            # GUI for edit window
            self.edit_window = QWidget()
            self.edit_window.setGeometry(int(settingsDict['log-window-left']),
                             int(settingsDict['log-window-top']),
                             300,
                             500)
            self.edit_window.setWindowTitle('Edit QSO with ' + call)

            style = "background-color:" + settingsDict['background-color'] + "; color:" + \
                    settingsDict['color'] + ";"
            style_table = "background-color:" + settingsDict['form-background'] + \
                          "; color:" + settingsDict['color-table'] + "; font: 12px; "
            self.edit_window.setStyleSheet(style)
            self.edit_window.setWindowOpacity(0.98)
            # Call element 1
            self.call_label = QLabel("Call")
            self.call_input = QLineEdit()
            self.call_input.setStyleSheet(style_table)
            self.call_input.setFixedWidth(100)
            self.call_input.setFixedHeight(30)
            self.call_input.setText(call)
            call_layer = QHBoxLayout()
            call_layer.addWidget(self.call_label)
            call_layer.addWidget(self.call_input)
            # Date element 2
            self.date_label = QLabel("Date")
            self.date_input = QLineEdit()
            self.date_input.setStyleSheet(style_table)
            self.date_input.setFixedWidth(100)
            self.date_input.setFixedHeight(30)
            self.date_input.setText(date)
            date_layer = QHBoxLayout()
            date_layer.addWidget(self.date_label)
            date_layer.addWidget(self.date_input)
            # Time element 3
            self.time_label = QLabel("Time")
            self.time_input = QLineEdit()
            self.time_input.setStyleSheet(style_table)
            self.time_input.setFixedWidth(100)
            self.time_input.setFixedHeight(30)
            self.time_input.setText(time)
            time_layer = QHBoxLayout()
            time_layer.addWidget(self.time_label)
            time_layer.addWidget(self.time_input)
            # Freq element 4
            self.freq_label = QLabel("Frequency")
            self.freq_input = QLineEdit()
            self.freq_input.setStyleSheet(style_table)
            self.freq_input.setFixedWidth(100)
            self.freq_input.setFixedHeight(30)
            self.freq_input.setText(freq)
            freq_layer = QHBoxLayout()
            freq_layer.addWidget(self.freq_label)
            freq_layer.addWidget(self.freq_input)
            # RstR element 5
            self.rstr_label = QLabel("RSt reciev")
            self.rstr_input = QLineEdit()
            self.rstr_input.setStyleSheet(style_table)
            self.rstr_input.setFixedWidth(100)
            self.rstr_input.setFixedHeight(30)
            self.rstr_input.setText(rstR)
            rstr_layer = QHBoxLayout()
            rstr_layer.addWidget(self.rstr_label)
            rstr_layer.addWidget(self.rstr_input)
            # RstS element 6
            self.rsts_label = QLabel("RSt sent")
            self.rsts_input = QLineEdit()
            self.rsts_input.setStyleSheet(style_table)
            self.rsts_input.setFixedWidth(100)
            self.rsts_input.setFixedHeight(30)
            self.rsts_input.setText(rstS)
            rsts_layer = QHBoxLayout()
            rsts_layer.addWidget(self.rsts_label)
            rsts_layer.addWidget(self.rsts_input)
            # Name element 7
            self.name_label = QLabel("Name")
            self.name_input = QLineEdit()
            self.name_input.setStyleSheet(style_table)
            self.name_input.setFixedWidth(100)
            self.name_input.setFixedHeight(30)
            self.name_input.setText(name)
            name_layer = QHBoxLayout()
            name_layer.addWidget(self.name_label)
            name_layer.addWidget(self.name_input)
            # QTH element 8
            self.qth_label = QLabel("QTH")
            self.qth_input = QLineEdit()
            self.qth_input.setStyleSheet(style_table)
            self.qth_input.setFixedWidth(100)
            self.qth_input.setFixedHeight(30)
            self.qth_input.setText(qth)
            qth_layer = QHBoxLayout()
            qth_layer.addWidget(self.qth_label)
            qth_layer.addWidget(self.qth_input)
            # Mode element 9
            self.mode_label = QLabel("Mode")
            self.mode_input = QLineEdit()
            self.mode_input.setStyleSheet(style_table)
            self.mode_input.setFixedWidth(100)
            self.mode_input.setFixedHeight(30)
            self.mode_input.setText(mode)
            mode_layer = QHBoxLayout()
            mode_layer.addWidget(self.mode_label)
            mode_layer.addWidget(self.mode_input)
            # Band element 10
            self.band_label = QLabel("Band")
            self.band_input = QLineEdit()
            self.band_input.setStyleSheet(style_table)
            self.band_input.setFixedWidth(100)
            self.band_input.setFixedHeight(30)
            self.band_input.setText(band)
            band_layer = QHBoxLayout()
            band_layer.addWidget(self.band_label)
            band_layer.addWidget(self.band_input)
            # time_off element 11
            self.timeoff_label = QLabel("Time OFF")
            self.timeoff_input = QLineEdit()
            self.timeoff_input.setStyleSheet(style_table)
            self.timeoff_input.setFixedWidth(100)
            self.timeoff_input.setFixedHeight(30)
            self.timeoff_input.setText(time_off)
            timeoff_layer = QHBoxLayout()
            timeoff_layer.addWidget(self.timeoff_label)
            timeoff_layer.addWidget(self.timeoff_input)
            # Eqsl recvd element 12
            self.eslrcvd_input = QCheckBox("eQSL Recieved")
            self.eslrcvd_input.setStyleSheet(style)

            if EQSL_QSL_SENT == "Y":
                self.eslrcvd_input.setChecked(True)
            else:
                self.eslrcvd_input.setChecked(False)
            eslrcvd_layer = QHBoxLayout()
            eslrcvd_layer.addWidget(self.eslrcvd_input)
            # Comment element 13
            self.comment_label = QLabel("Comment")
            self.comment_input = QLineEdit()
            self.comment_input.setStyleSheet(style_table)
            self.comment_input.setFixedWidth(100)
            self.comment_input.setFixedHeight(30)
            self.comment_input.setText(comment)
            comment_layer = QHBoxLayout()
            comment_layer.addWidget(self.comment_label)
            comment_layer.addWidget(self.comment_input)
            # Set Button
            self.save_button = QPushButton("Save QSO")
            self.save_button.setFixedHeight(30)
            self.save_button.setFixedWidth(100)
            self.save_button.clicked.connect(self.apply_edit_window)

            self.cancel_button = QPushButton("Cancel")
            self.cancel_button.setFixedHeight(30)
            self.cancel_button.setFixedWidth(100)
            self.cancel_button.clicked.connect(self.edit_window_close)
            button_layer = QHBoxLayout()
            button_layer.addWidget(self.cancel_button)
            button_layer.addWidget(self.save_button)
            # Setup all elements
            vertical_box = QVBoxLayout()
            vertical_box.addLayout(call_layer)
            vertical_box.addLayout(name_layer)
            vertical_box.addLayout(qth_layer)
            vertical_box.addLayout(rstr_layer)
            vertical_box.addLayout(rsts_layer)
            vertical_box.addLayout(mode_layer)
            vertical_box.addLayout(band_layer)
            vertical_box.addLayout(freq_layer)
            vertical_box.addLayout(date_layer)
            vertical_box.addLayout(time_layer)
            vertical_box.addLayout(timeoff_layer)
            vertical_box.addLayout(eslrcvd_layer)
            vertical_box.addLayout(comment_layer)
            vertical_box.addLayout(button_layer)
            # Setup vertical to widget
            self.edit_window.setLayout(vertical_box)
            self.edit_window.show()

        def edit_window_close(self):
            self.edit_window.close()

        def apply_edit_window(self):
            if self.eslrcvd_input.isChecked():
                eqsl = "Y"
            else:
                eqsl = "N"
            print("eqsl:_>", eqsl)
            time_format = self.time_input.text().strip().replace(":", '')
            print("Time format:_>", time_format)
            date_format = self.date_input.text().strip().replace("-", '')
            new_object = {'BAND': self.band_input.text().strip(),
                          'CALL': self.call_input.text().strip(),
                          'FREQ': self.freq_input.text().strip(),
                          'MODE': self.mode_input.text().strip(),
                          'OPERATOR': self.operator_edit,
                          'QSO_DATE': date_format,
                          'TIME_ON': time_format,
                          'RST_RCVD': self.rstr_input.text().strip(),
                          'RST_SENT': self.rsts_input.text().strip(),
                          'NAME': self.name_input.text().strip(),
                          'QTH': self.qth_input.text().strip(),
                          'COMMENTS': self.comment_input.text().strip(),
                          'TIME_OFF': self.timeoff_input.text().strip(),
                          'EQSL_QSL_SENT': eqsl,
                          'EOR': 'R\n',
                          'string_in_file': self.string_in_file_edit,
                          'records_number': self.records_number_edit}
            Adi_file().store_changed_qso(new_object)
            All_records[int(self.records_number_edit) - 1] = new_object
            print("Object for edit:_>", new_object)
            self.refresh_data()
            self.edit_window.close()

        def delete_qso(self, row):
            record_number = self.tableWidget_qso.item(row, 0).text()
            string_in_file = All_records[int(record_number) - 1]['string_in_file']
            print("delete_qso number:_>", record_number)
            Adi_file().delete_qso_from_file(string_in_file)
            self.tableWidget_qso.removeRow(row)
            self.refresh_data()


        def changeEvent(self, event):

            if event.type() == QtCore.QEvent.WindowStateChange:
                if self.isMinimized():
                    settingsDict['log-window'] = 'false'
                    #print("log-window: changeEvent:_>", settingsDict['log-window'])
                    # telnetCluster.showMinimized()
                elif self.isVisible():
                    settingsDict['log-window'] = 'true'
                    #print("log-window: changeEvent:_>", settingsDict['log-window'])
                QWidget.changeEvent(self, event)

        def refresh_data(self):
            #print("refresh_data:_>", All_records)
            self.tableWidget_qso.clear()
            #self.tableWidget.insertRow()

            self.tableWidget_qso.setHorizontalHeaderLabels(
                ["No", "     Date     ", "   Time   ", "Band", "   Call   ", "Mode", "RST r",
                 "RST s", "      Name      ", "      QTH      ", " Comments ",
                 " Time off ", " eQSL Sent "])
            #self.tableWidget_qso.resizeRowsToContents()
            #self.tableWidget_qso.resizeColumnsToContents()
            self.allRecords = Fill_table(all_column=self.allCollumn, window=self, all_record=All_records, communicate=signal_complited, settingsDict=settingsDict)
            self.allRecords.fill_complite.connect(self.fill_complited)
            self.allRecords.start()


            self.allRows = len(All_records)

        @QtCore.pyqtSlot(name='fill_complited')
        def fill_complited(self):
            print("All_records", len(All_records))
            self.tableWidget_qso.resizeRowsToContents()
            self.tableWidget_qso.resizeColumnsToContents()



        def get_all_record(self):
            return All_records

        def protectionItem(self, text, flags):
            tableWidgetItem = QTableWidgetItem(text)
            tableWidgetItem.setFlags(flags)
            return tableWidgetItem

        def store_change_record(self, row_arg=''):

            #print("store_change_record")
            if row_arg == '':
                row = self.tableWidget_qso.currentItem().row()
            else:
                row = int(row_arg)
            record_number = self.tableWidget_qso.item(row, 0).text()
            date = str(self.tableWidget_qso.item(row, 1).text())
            date_formated = date.replace("-", "")
            time = str(self.tableWidget_qso.item(row, 2).text())
            time_formated = time.replace(":", "")
            call = self.tableWidget_qso.item(row, 4).text()
            freq = All_records[int(record_number) - 1]['FREQ']
            rstR = self.tableWidget_qso.item(row, 6).text()
            rstS = self.tableWidget_qso.item(row, 7).text()
            name = self.tableWidget_qso.item(row, 8).text()
            qth = self.tableWidget_qso.item(row, 9).text()
            operator = All_records[int(record_number) - 1]['OPERATOR']
            band = self.tableWidget_qso.item(row, 3).text()
            comment = self.tableWidget_qso.item(row, 10).text()
            time_off = self.tableWidget_qso.item(row, 11).text()
            EQSL_QSL_SENT = self.tableWidget_qso.item(row, 12).text()
            mode = self.tableWidget_qso.item(row, 5).text()
            string_in_file = All_records[int(record_number) - 1]['string_in_file']
            records_number = All_records[int(record_number) - 1]['records_number']

           # if 'string_in_file' in self.allRecord:
           #     pass

            #else:
            #    pass

            new_object = {'BAND': band, 'CALL': call, 'FREQ': freq, 'MODE': mode, 'OPERATOR': operator,
                          'QSO_DATE': date_formated, 'TIME_ON': time_formated, 'RST_RCVD': rstR, 'RST_SENT': rstS,
                          'NAME': name, 'QTH': qth, 'COMMENTS': comment, 'TIME_OFF': time_off,
                          'EQSL_QSL_SENT': EQSL_QSL_SENT,
                          'EOR': 'R\n', 'string_in_file': string_in_file, 'records_number': records_number}

           # print("store_change_record: NEW Object", new_object)
            Adi_file().store_changed_qso(new_object)
            All_records[int(record_number) - 1] = new_object

        def refresh_interface(self):

            self.update_color_schemes()

        def update_color_schemes(self):
            style = "background-color:" + settingsDict['background-color'] + "; color:" + \
                    settingsDict['color'] + ";"

            style_form = "background-color:" + settingsDict['form-background'] + "; color:" + settingsDict[
                'color-table'] + "; font: 12px; gridline-color:"+settingsDict['solid-color']+";"
            self.tableWidget_qso.setStyleSheet(style_form)
            all_rows = self.tableWidget_qso.rowCount()
            all_cols = self.tableWidget_qso.columnCount()
            print("All_rows", all_rows, "All_cols", all_cols)
            for row in range(all_rows):
                for col in range(all_cols):
                    self.tableWidget_qso.item(row, col).setForeground(QColor(settingsDict["color-table"]))

            self.setStyleSheet(style)
            self.refresh_data()

        def addRecord(self, recordObject):
            # <BAND:3>20M <CALL:6>DL1BCL <FREQ:9>14.000000
            # <MODE:3>SSB <OPERATOR:6>UR4LGA <PFX:3>DL1 <QSLMSG:19>TNX For QSO TU 73!.
            # <QSO_DATE:8:D>20131011 <TIME_ON:6>184700 <RST_RCVD:2>57 <RST_SENT:2>57 <TIME_OFF:6>184700
            # <eQSL_QSL_RCVD:1>Y <APP_LOGGER32_QSO_NUMBER:1>1  <EOR>
            # record to file
            if settingsDict['eqsl'] == 'enable':
                try:
                    self.sync_eqsl = internetworker.Eqsl_services(settingsDict=settingsDict, recordObject=recordObject,
                                                                  std=std.std, parent_window=self)
                    self.sync_eqsl.send_ok.connect(self.eqsl_ok)
                    self.sync_eqsl.error_signal.connect(self.eqsl_error)
                except Exception:
                    print("Don't sent eQSL")


            stringToAdiFile = "<BAND:" + str(len(recordObject['BAND'])) + ">" + recordObject['BAND'] + "<CALL:" + str(
                len(recordObject['CALL'])) + ">"

            stringToAdiFile = stringToAdiFile + recordObject['CALL'] + "<FREQ:" + str(len(recordObject['FREQ'])) + ">" + \
                              recordObject['FREQ']
            stringToAdiFile = stringToAdiFile + "<MODE:" + str(len(recordObject['MODE'])) + ">" + recordObject[
                'MODE'] + "<OPERATOR:" + str(len(recordObject['OPERATOR']))
            stringToAdiFile = stringToAdiFile + ">" + recordObject['OPERATOR'] + "<QSO_DATE:" + str(
                len(recordObject['QSO_DATE'])) + ">"
            stringToAdiFile = stringToAdiFile + recordObject['QSO_DATE'] + "<TIME_ON:" + str(
                len(recordObject['TIME_ON'])) + ">"
            stringToAdiFile = stringToAdiFile + recordObject['TIME_ON'] + "<RST_RCVD:" + str(
                len(recordObject['RST_RCVD'])) + ">" + recordObject['RST_RCVD']
            stringToAdiFile = stringToAdiFile + "<RST_SENT:" + str(len(recordObject['RST_SENT'])) + ">" + recordObject[
                'RST_SENT'] + "<NAME:" + str(
                len(recordObject['NAME'])) + ">" + recordObject['NAME'] + "<QTH:" + str(
                len(recordObject['QTH'])) + ">" + recordObject['QTH'] + "<COMMENTS:" + str(
                len(recordObject['COMMENTS'])) + ">" + recordObject[
                                  'COMMENTS'] + "<TIME_OFF:" + str(len(recordObject['TIME_OFF'])) + ">" + recordObject[
                                  'TIME_OFF'] + "<EQSL_QSL_SENT:"+str(len(recordObject['EQSL_QSL_SENT']))+">"+str(recordObject['EQSL_QSL_SENT'])+"<EOR>\n"
            # print(stringToAdiFile)
            recordObject['string_in_file'] = Adi_file().get_last_string() + 1

            file = open(self.filename, 'a')
            resultWrite = file.write(stringToAdiFile)
            # print(resultWrite)
            if resultWrite > 0:
                file.close()
            else:
                print("QSO not write in logfile")
                file.close()
            #####

            # record to allRecord
            #print(recordObject)

            All_records.append(recordObject)
            all_rows = len(All_records)
            # record to table
            allCols = len(self.allCollumn)
            # row = self.allRows + 1
            # print(recordObject)
            # print (row)
            #self.tableWidget_qso.setRowCount(all_rows)
            self.tableWidget_qso.insertRow(0)
            self.tableWidget_qso.resizeRowsToContents()

            for col in range(allCols):
                if col == 1:
                    date = str(recordObject[self.allCollumn[col]])
                    date_formated = date[:4] + "-" + date[4:6] + "-" + date[6:]
                    self.tableWidget_qso.setItem(0, col, QTableWidgetItem(date_formated))

                elif col == 2:
                    time = str(recordObject[self.allCollumn[col]])
                    time_formated = time[:2] + ":" + time[2:4] + ":" + time[4:]
                    self.tableWidget_qso.setItem(0, col, QTableWidgetItem(time_formated))

                else:
                    self.tableWidget_qso.setItem(0, col, QTableWidgetItem(recordObject[self.allCollumn[col]]))
                self.tableWidget_qso.item(0, col).setForeground(QColor(settingsDict['color-table']))


        @QtCore.pyqtSlot(name='eqsl_ok')
        def eqsl_ok(self):
            self.tableWidget_qso.setItem (0,12, QTableWidgetItem('Y'))
            allCols = len(self.allCollumn)
            for col in range(allCols):
                self.tableWidget_qso.item(0, col).setBackground(QColor(settingsDict['eqsl-sent-color']))

            self.store_change_record(row_arg=0)

        @QtCore.pyqtSlot()
        def eqsl_error(self):
            # self.recordObject['EQSL_QSL_SENT'] = 'Y'
            pass

        def search_in_table(self, call):
            list_dict = []
            if self.tableWidget_qso.rowCount() > 0:
                for rows in range(self.tableWidget_qso.rowCount()):
                    #print(self.tableWidget.item(rows, 4).text())
                    try:
                        if self.tableWidget_qso.item(rows, 4).text() == call:
                            row_in_dict = {"No":self.tableWidget_qso.item(rows,0).text(),
                                            "Date":self.tableWidget_qso.item(rows,1).text(),
                                            "Time":self.tableWidget_qso.item(rows,2).text(),
                                            "Band":self.tableWidget_qso.item(rows,3).text(),
                                            "Call":self.tableWidget_qso.item(rows,4).text(),
                                            "Mode":self.tableWidget_qso.item(rows,5).text(),
                                            "Rstr":self.tableWidget_qso.item(rows,6).text(),
                                            "Rsts":self.tableWidget_qso.item(rows,7).text(),
                                            "Name":self.tableWidget_qso.item(rows,8).text(),
                                            "Qth":self.tableWidget_qso.item(rows,9).text(),
                                            "Comments":self.tableWidget_qso.item(rows,10).text(),
                                            "Time_off":self.tableWidget_qso.item(rows,11).text(),
                                            "Eqsl_sent":self.tableWidget_qso.item(rows,12).text()}
                            list_dict.append(row_in_dict)
                    except Exception:
                        print("Search in table > Don't Load text from table")
                return list_dict

class logSearch(QWidget):
    def __init__(self):
        super().__init__()
        self.foundList = []
        self.initUI()

    def initUI(self):

        self.setGeometry(int(settingsDict['log-search-window-left']), int(settingsDict['log-search-window-top']),
                         int(settingsDict['log-search-window-width']), int(settingsDict['log-search-window-height']))
        self.setWindowTitle('LinuxLog | Search')
        self.setWindowIcon(QIcon('logo.png'))
        self.setWindowOpacity(float(settingsDict['logSearch-opacity']))
        style = "background-color:" + settingsDict['background-color'] + "; color:" + settingsDict[
            'color'] + "; font: 12px;"
        self.setStyleSheet(style)

        # print ('%10s %5s %10s %16s %8s %8s %8s %15s %15s' % ('QSO_DATE', 'TIME', 'FREQ', 'CALL',
        #			'MODE', 'RST_RCVD', 'RST_SENT',	'NAME', 'QTH')
        #		   )
        self.tableWidget = QTableWidget()
        style_table = "background-color:" + settingsDict['form-background'] + "; color:" + settingsDict[
            'color-table'] + "; font: 12px;  gridline-color: " + settingsDict['solid-color'] + ";"
        self.tableWidget.setStyleSheet(style_table)
        fnt = self.tableWidget.font()
        fnt.setPointSize(9)
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.setFont(fnt)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
        #self.show()

    def changeEvent(self, event):

        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.isMinimized():
                settingsDict['log-search-window'] = 'false'
                #print("log-search-window: changeEvent:_>", settingsDict['log-search-window'])
                    #telnetCluster.showMinimized()
            elif self.isVisible():
                settingsDict['log-search-window'] = 'true'
               # print("log-search-window: changeEvent:_>", settingsDict['log-search-window'])
            QWidget.changeEvent(self, event)

    def overlap(self, foundList):
        if foundList != "":
            allRows = len(foundList)
            #print("overlap", foundList)
            self.tableWidget.setRowCount(allRows)
            self.tableWidget.setColumnCount(10)
            self.tableWidget.setHorizontalHeaderLabels(
                ["No", "   Date   ", " Time ", "Band", "   Call   ", "Mode", "RST r",
                 "RST s", "      Name      ", "      QTH      "])
            self.tableWidget.resizeColumnsToContents()
            allCols = self.tableWidget.columnCount()
            # print(foundList[0]["CALL"])
            for row in range(allRows):
                for col in range(allCols):
                    pole = logWindow.allCollumn[col]
                    self.tableWidget.setItem(row, col, QTableWidgetItem(foundList[row][pole]))
                    self.tableWidget.item(row, col).setForeground(QColor(settingsDict["color-table"]))
            self.tableWidget.resizeRowsToContents()
            self.tableWidget.resizeColumnsToContents()
            self.foundList = foundList
        else:
            self.tableWidget.clearContents()
        # print(self.foundList)

    def refresh_interface(self):

        self.update_color_schemes()

    def update_color_schemes(self):
        style = "background-color:" + settingsDict['background-color'] + "; color:" + \
                settingsDict['color'] + ";"

        style_form = "background-color:" + settingsDict['form-background'] + "; color:" + settingsDict[
            'color-table'] + "; font: 12px"
        self.tableWidget.setStyleSheet(style_form)
        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()
        for row in range(rows):
            for col in range(cols):
                self.tableWidget.item(row, col).setForeground(QColor(settingsDict['color-table']))

        self.setStyleSheet(style)

class check_update ():



    def __init__(self, APP_VERSION, settingsDict, parrentWindow):
        super().__init__()
        self.version = APP_VERSION
        self.settingsDict = settingsDict
        self.parrent = parrentWindow
        self.run()


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
                git_path_param = soup.find(id="git_path").get_text()
                parameters = git_path_param.split('|')
                git_path = parameters[0]
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
                   # print("Yes")
                    #try:
                    self.parrent.check_update.setText("Updating")
                    adi_name_list = []
                    for file in os.listdir():
                        if file.endswith(".adi"):
                            adi_name_list.append(file)
                    print("found all .adi file")
                    rules_name_list = []
                    for file in os.listdir():
                        if file.endswith(".rules"):
                            rules_name_list.append(file)
                    print("found all .rules file")
                   # print("Rules name List:_>", rules_name_list)
                   # print("Adi name List:_>", adi_name_list)
                    home = expanduser("~")
                    print("Home path:_>", home)
                    if os.path.isdir(home+'/linuxlog-backup'):
                        os.system("rm -rf "+home+"/linuxlog-backup")
                    else:
                        pass
                    print("Create buckup folder (linuxlog-buckup)")
                    os.mkdir(home+"/linuxlog-backup")
                    for i in range(len(adi_name_list)):
                        os.system("cp '"+adi_name_list[i]+"' "+home+"/linuxlog-backup")
                    print("Copy all .adi file to backup folder")
                    for i in range(len(rules_name_list)):
                        os.system("cp  '" + rules_name_list[i] + "' " + home + "/linuxlog-backup")
                    print("Copy all .rules file to backup folder")
                    os.system("cp settings.cfg " + home+"/linuxlog-backup")
                    print("Copy settings.cfg to backup folder")

                    # archive dir
                    if os.path.isdir(home+'/linlog-old'):
                     pass
                    else:
                        os.system("mkdir "+home+"/linlog-old")
                    os.system("tar -cf "+home+"/linlog-old/linlog"+version+".tar.gz " + home + "/linlog/")
                    print("Create archive with linlog folder")
                    print("Delete Linlog folder")
                    # delete dir linlog
                    #os.system("rm -rf " + home + "/linlog")
                    # clone from git repository to ~/linlog
                    print("Git clone to new linlog folder")
                    os.system("git clone " + git_path + " " + home + "/linlog_"+version)

                    # copy adi and rules file from linuxlog-backup to ~/linlog

                    for i in range(len(adi_name_list)):
                        os.system("cp '"+home+"/linuxlog-backup/" + adi_name_list[i] + "' '" + home + "/linlog_"+version+"'")
                    for i in range(len(rules_name_list)):
                        os.system("cp '" + home + "/linuxlog-backup/" + rules_name_list[i] + "' '" + home + "/linlog_"+version+"'")

                    # read and replace string in new settings.cfg

                    file = open(home+"/linlog_"+version+"/settings.cfg", "r")
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

                    filename = home+"/linlog_"+version+"/settings.cfg"
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

                    os.system("chmod +x "+home+"/linlog_"+version+"/linlog")
                    with open(home+"/linlog/linlog", "w") as f:
                       string_to_file = ['#! /bin/bash\n', 'cd '+home+'/linlog_'+version+'\n', 'python3 main.py\n']
                       f.writelines(string_to_file)

                    #delete backup dir
                    os.system("rm -rf " + home + "/linuxlog-backup")

                    os.system("rm -rf " + home + "/linlog_"+self.version)
                if len(parameters) > 1:
                    pip_install_string = 'pip3 install '
                    for i in range(1, len(parameters), 1):
                        if parameters[i] != "" and parameters[i] != " ":
                            pip_install_string += parameters[i] + ' '
                    if pip_install_string != "pip3 install ":
                        result = os.system(pip_install_string)
                    else:
                        result = 0
                    if result != 0:
                        std.std.message(self.parrent, "Can't install module(s)\nPlease install modules in Terminal.\n \
                                                      Command: " + pip_install_string + " maybe use 'sudo'\n","ERROR install modules\n")

                    std.std.message(self.parrent, "Update to v."+version+" \nCOMPLITED \n "
                                                                         "Please restart LinuxLog", "UPDATER")

                    self.version = version
                    self.parrent.check_update.setText("> Check update <")
                    self.parrent.check_update.setEnabled(True)
                    self.parrent.text.setText("Version:"+version+"\n<a href='http://linixlog.su'>http://linixlog.su</a>\nBaston Sergey\nbastonsv@gmail.com")


                else:
                  #  print("No")
                    self.parrent.check_update.setText("> Check update <")
                    self.parrent.check_update.setEnabled(True)

        else:
            std.std.message(self.parrent, "Sorry\ntimeout server.", "UPDATER")

class Check_update_thread(QtCore.QObject):

    update_response = QtCore.pyqtSignal(object)
   # error_request = QtCore.pyqtSignal()

    def __init__(self, url_query):
        super().__init__()
        self.url_query = url_query

    def run(self):
            #print("Test")
            try:
                self.response_upd_server = requests.get(self.url_query)
                self.update_response.emit(self.response_upd_server)
            except Exception:
                print ("Can't check update")
           # if response_upd_server.status_code == 200:
            #    self.update_response.emit(response_upd_server)
           # else:
            #    self.error_request.emit()

class update_after_run(QObject):

    def __init__(self, version, settings_dict):
        super().__init__()
        self.version = version
        self.settingsDict = settings_dict
        self.update_check()

    def update_check(self):

        server_url_get = 'http://357139-vds-bastonsv.gmhost.pp.ua'
        path_directory_updater_app = "/upd/"

        self.action = server_url_get + path_directory_updater_app + self.version + "/" + self.settingsDict['my-call']
        flag = 0
        data_flag = 0
        self.thread_update = QThread()
        self.check_in_thread = Check_update_thread(self.action)
        self.check_in_thread.moveToThread(self.thread_update)
        self.check_in_thread.update_response.connect(self.answer_from_upd_server)
        #self.check_in_thread.start()
        #
        #
        self.thread_update.started.connect(self.check_in_thread.run)

        self.thread_update.start()
        ###############

    @QtCore.pyqtSlot(object)
    def answer_from_upd_server(self, object_reciev):
        soup = BeautifulSoup(object_reciev.text, 'html.parser')
        try:
            version = soup.find(id="version").get_text()
            #git_path = soup.find(id="git_path").get_text()
            date = soup.find(id="date").get_text()
            self.show_message(str(version), str(date))
        except Exception:
            pass

        ###############


    def show_message(self, str_version, str_date):
        de = os.environ['XDG_CURRENT_DESKTOP']
        button_upd = QPushButton("Update now")

        if de == "GNOME":
            Notify.init("LinuxLog")
            summary = "LinuxLog update"
            body = "New version released:  v " + str_version + ".  Please update LinuxLog"
            notification = Notify.Notification.new(
                summary,
                body,  # Optional
            )
            image = GdkPixbuf.Pixbuf.new_from_file("logo.png")
            # notification.set_icon_from_pixbuf(image)
            notification.set_image_from_pixbuf(image)
            notification.show()
        else:
            self.tray_icon = QSystemTrayIcon(app)
            self.tray_icon.setIcon(QIcon("logo.png"))

            self.tray_icon.show()
            self.tray_icon.showMessage(
                "LinuxLog",
                "New version released:  v " + str_version + ".  Please update LinuxLog",
                QSystemTrayIcon.Information,
                10000
            )

class About_window(QWidget):
    def __init__(self, capture, text):
        super().__init__()
        self.capture_string = capture
        self.text_string = text
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        #self.setGeometry(100,100,210,100)
        width_coordinate = (desktop.width() / 2) - 100
        height_coordinate = (desktop.height() / 2) - 100
        #self.setWindowModified(False)
        self.setFixedHeight(270)
        self.setFixedWidth(320)

        self.setGeometry(int(width_coordinate), int(height_coordinate), 200, 300)
        self.setWindowIcon(QIcon('logo.png'))
        self.setWindowTitle('About | LinuxLog')
        style = "QWidget{background-color:" + settingsDict['background-color'] + "; color:" + settingsDict[
            'color'] + ";}"
        self.setStyleSheet(style)
        self.capture = QLabel(self.capture_string)
        self.capture.setStyleSheet("font-size: 18px")
        self.capture.setFixedHeight(30)
        self.text = QLabel(self.text_string)
        #self.text.setFixedHeight(200)
        self.text.setStyleSheet("font-size: 12px")
        self.about_layer = QVBoxLayout()
        self.image = QPixmap("logo.png")
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setPixmap(self.image)
        #about_layer.setAlignment(Qt.AlignCenter)
        self.check_update = QPushButton()
        self.check_update.setFixedWidth(130)
        self.check_update.setFixedHeight(60)
        self.check_update.setText("> Check update <")
        self.check_update.setStyleSheet("size: 10px;")

        self.check_update.clicked.connect(self.updater)
        self.about_layer.addWidget(self.capture)
        self.about_layer.addSpacing(5)
        self.about_layer.addWidget(self.check_update)
        self.about_layer.addWidget(self.text)
        self.horizontal_lay = QHBoxLayout()
        self.horizontal_lay.addWidget(self.image_label)
        self.horizontal_lay.addLayout(self.about_layer)

        self.setLayout(self.horizontal_lay)

    def updater(self):
        self.check_update.setEnabled(False)
        self.check_update.setText("Found update")
        self.check = check_update(APP_VERSION, settingsDict=settingsDict, parrentWindow=self)
        #self.check.start()

class realTime(QThread):

    def __init__(self, logformwindow, parent=None):
        super().__init__()
        self.logformwindow = logformwindow

    def run(self):

        while 1:
            self.logformwindow.labelTime.setText("Loc: "+strftime("%H:%M:%S", localtime())+
                                                 "  |  GMT: "+strftime("%H:%M:%S", gmtime()))
            time.sleep(0.5)

class ClikableLabel(QLabel):
    click_signal = QtCore.pyqtSignal()
    change_value_signal = QtCore.pyqtSignal()
    def __init__(self, parrent=None):
        QLabel.__init__(self, parrent)


    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.click_signal.emit()

class FreqWindow(QWidget):
    figure = QtCore.pyqtSignal(str)
    def __init__(self, settings_dict):
        super().__init__()
        self.settings_dict = settings_dict
        self.memory_list = []
        self.active_memory_element = "0"
        self.label_style  = "background:"+self.settings_dict['form-background']+ \
                                      "; color:"+self.settings_dict['color-table']+"; font: 25px"
        self.style_mem_label = "background:" + self.settings_dict['form-background'] + \
                               "; color:" + self.settings_dict['color-table'] + "; font: 12px"
        self.style = "background:" + self.settings_dict['background-color'] + "; color:" \
                + self.settings_dict['color'] + "; font: 12px;"
        self.style_window = "background:"+self.settings_dict['background-color']+"; color:"\
                           +self.settings_dict['color']+";"
        self.freq_status = 0
        self.initUI()

        if self.isEnabled():
            self.init_data()

    def keyPressEvent(self, e):

        if e.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self.enter_freq()
        if e.key() == QtCore.Qt.Key_F12:
            self.close()

    def initUI(self):
        self.setGeometry(int(self.settings_dict['log-form-window-left'])+logForm.width(),
                         int(self.settings_dict['log-form-window-top']),
                         200, int(self.settings_dict['log-form-window-height']))
        self.setFixedHeight(320)
        self.setWindowOpacity(float(self.settings_dict['freq-input-window-opacity']))
        self.setWindowTitle('Frequency | LinLog')
        self.setStyleSheet(self.style_window)
        ##### Create elements

        # create button 1
        self.button_1 = QPushButton("1")
        self.button_1.setStyleSheet(self.style)
        self.button_1.setFixedSize(40, 40)
        self.button_1.clicked.connect(self.num_clicked)
        self.button_1.setShortcut('1')
        # create button 2
        self.button_2 = QPushButton("2")
        self.button_2.setStyleSheet(self.style)
        self.button_2.setFixedSize(40, 40)
        self.button_2.clicked.connect(self.num_clicked)
        self.button_2.setShortcut('2')
        # create button 3
        self.button_3 = QPushButton("3")
        self.button_3.setStyleSheet(self.style)
        self.button_3.setFixedSize(40, 40)
        self.button_3.clicked.connect(self.num_clicked)
        self.button_3.setShortcut('3')
        # create button 4
        self.button_4 = QPushButton("4")
        self.button_4.setStyleSheet(self.style)
        self.button_4.setFixedSize(40, 40)
        self.button_4.clicked.connect(self.num_clicked)
        self.button_4.setShortcut('4')
        # create button 5
        self.button_5 = QPushButton("5")
        self.button_5.setStyleSheet(self.style)
        self.button_5.setFixedSize(40, 40)
        self.button_5.clicked.connect(self.num_clicked)
        self.button_5.setShortcut('5')
        # create button 6
        self.button_6 = QPushButton("6")
        self.button_6.setStyleSheet(self.style)
        self.button_6.setFixedSize(40, 40)
        self.button_6.clicked.connect(self.num_clicked)
        self.button_6.setShortcut('6')
        # create button 7
        self.button_7 = QPushButton("7")
        self.button_7.setStyleSheet(self.style)
        self.button_7.setFixedSize(40, 40)
        self.button_7.clicked.connect(self.num_clicked)
        self.button_7.setShortcut('7')
        # create button 8
        self.button_8 = QPushButton("8")
        self.button_8.setStyleSheet(self.style)
        self.button_8.setFixedSize(40, 40)
        self.button_8.clicked.connect(self.num_clicked)
        self.button_8.setShortcut('8')
        # create button 9
        self.button_9 = QPushButton("9")
        self.button_9.setStyleSheet(self.style)
        self.button_9.setFixedSize(40, 40)
        self.button_9.clicked.connect(self.num_clicked)
        self.button_9.setShortcut('9')
        # create button 1
        self.button_0 = QPushButton("0")
        self.button_0.setStyleSheet(self.style)
        self.button_0.setFixedSize(40, 40)
        self.button_0.clicked.connect(self.num_clicked)
        self.button_0.setShortcut('0')
        # create button Point
        self.button_p = QPushButton("<-")
        self.button_p.setStyleSheet(self.style)
        self.button_p.setFixedSize(40, 40)
        self.button_p.clicked.connect(self.delete_symbol_freq)
        self.button_p.setShortcut('Backspace')
        # create button CLR
        self.button_clear = QPushButton("CLR")
        self.button_clear.setStyleSheet(self.style)
        self.button_clear.setFixedSize(40, 40)
        self.button_clear.clicked.connect(self.clear_freq_label)
        self.button_clear.setShortcut('Esc')
        # create button Ent
        self.button_ent = QPushButton("Enter")
        self.button_ent.setStyleSheet(self.style)
        self.button_ent.setFixedSize(60, 40)
        self.button_ent.clicked.connect(self.enter_freq)
        #self.button_ent.setShortcut('Enter')
        #self.button_ent.setShortcut('Return')
        # create button Save in memory
        self.button_sm = QPushButton("+memory")
        self.button_sm.setStyleSheet(self.style)
        self.button_sm.setFixedSize(60, 25)
        self.button_sm.clicked.connect(self.save_freq_to_memory)
        # create button up in memory
        self.button_up = QPushButton("▲")
        self.button_up.setStyleSheet(self.style)
        self.button_up.setFixedSize(60, 20)
        self.button_up.clicked.connect(self.change_memory_element)
        # create button down in memory
        self.button_dn = QPushButton("▼")
        self.button_dn.setStyleSheet(self.style)
        self.button_dn.setFixedSize(60, 20)
        self.button_dn.clicked.connect(self.change_memory_element)
        # create recall from memory
        self.button_all_rm = QPushButton("memory>")
        self.button_all_rm.setStyleSheet(self.style)
        self.button_all_rm.setFixedSize(60, 25)
        self.button_all_rm.clicked.connect(self.recal_from_memory)
        # delete from memory
        self.button_dm = QPushButton("- memory")
        self.button_dm.setStyleSheet(self.style)
        self.button_dm.setFixedSize(60, 25)
        self.button_dm.clicked.connect(self.delete_from_memory)
        # create button up in memory
        self.button_all_m = QPushButton("Show \n memory")
        self.button_all_m.setStyleSheet(self.style)
        self.button_all_m.setFixedSize(60, 40)
        # create label with memory
        self.memory_label = QLabel()
        self.memory_label.setStyleSheet(self.style)
        self.memory_label.setFixedHeight(10)
        # Create freq Label
        self.freq_label = QLabel()
        freq = logForm.get_freq()
        if freq.isnumeric():
            freq_to_label = self.freq_to_sting(freq)
            self.freq_label.setText(freq_to_label + " Hz")
        self.freq_label.setAlignment(Qt.AlignRight)
        self.freq_label.setStyleSheet(self.label_style)
        self.freq_label.setFixedHeight(50)
        self.freq_label.setFixedWidth(200)
        # create memory label Show
        self.memory_label_show = QLabel()
        self.memory_label_show.setStyleSheet(self.style_mem_label)
        self.memory_label_show.setFixedWidth(200)
        self.memory_label_show.setFixedHeight(20)
        # create Close chekbox element
        self.close_checkbox = QCheckBox("Close after enter freq")
        self.close_checkbox.setStyleSheet(self.style)
        if self.settings_dict['freq-wnd'] == "enable":
            self.close_checkbox.setChecked(True)



        #####################
        ### Setup to lay
        # 1-3
        self.buttons1_3_lay = QHBoxLayout()
        self.buttons1_3_lay.addWidget(self.button_1)
        self.buttons1_3_lay.addWidget(self.button_2)
        self.buttons1_3_lay.addWidget(self.button_3)
        # 4-6
        self.buttons4_6_lay = QHBoxLayout()
        self.buttons4_6_lay.addWidget(self.button_4)
        self.buttons4_6_lay.addWidget(self.button_5)
        self.buttons4_6_lay.addWidget(self.button_6)
        # 7-9
        self.buttons7_9_lay = QHBoxLayout()
        self.buttons7_9_lay.addWidget(self.button_7)
        self.buttons7_9_lay.addWidget(self.button_8)
        self.buttons7_9_lay.addWidget(self.button_9)
        # clr - 0 - point
        self.buttons0_lay = QHBoxLayout()
        self.buttons0_lay.addWidget(self.button_clear)
        self.buttons0_lay.addWidget(self.button_0)
        self.buttons0_lay.addWidget(self.button_p)
        # memory lay & enter button
        self.buttons_memory_lay = QVBoxLayout()
        self.buttons_memory_lay.addSpacing(10)
        self.buttons_memory_lay.setAlignment(Qt.AlignCenter)
        self.buttons_memory_lay.addWidget(self.button_sm)
        self.buttons_memory_lay.addWidget(self.button_up)
        self.memory_bank_num = QHBoxLayout()
        self.memory_bank_num.setAlignment(Qt.AlignCenter)
        self.memory_bank_num.addWidget(self.memory_label)
        self.buttons_memory_lay.addLayout(self.memory_bank_num)
        self.buttons_memory_lay.addWidget(self.button_dn)
        self.buttons_memory_lay.addWidget(self.button_dm)
        self.buttons_memory_lay.addWidget(self.button_all_rm)
        #self.buttons_memory_lay.addWidget(self.button_all_m)
        self.buttons_memory_lay.addWidget(self.button_ent)
        self.buttons_memory_lay.addSpacing(15)
        # create NUM layer
        self.num_buttons_lay = QVBoxLayout()
        #self.num_buttons_lay.setAlignment(Qt.AlignCenter)
        self.num_buttons_lay.addLayout(self.buttons1_3_lay)
        self.num_buttons_lay.addLayout(self.buttons4_6_lay)
        self.num_buttons_lay.addLayout(self.buttons7_9_lay)
        self.num_buttons_lay.addLayout(self.buttons0_lay)
        self.num_buttons_lay.addWidget(self.close_checkbox)
        # create all button layer
        self.button_layer = QHBoxLayout()
        #self.button_layer.setGeometry(QRect(0, 0, 100, 100))
        self.button_layer.addLayout(self.num_buttons_lay)
        self.button_layer.addLayout(self.buttons_memory_lay)
        #
        self.general_lay = QVBoxLayout()
        self.general_lay.setAlignment(Qt.AlignVCenter)
        #self.general_lay.
        self.general_lay.addWidget(self.memory_label_show)
        self.general_lay.addWidget(self.freq_label)
        self.general_lay.addLayout(self.button_layer)
        #self.general_lay.
        self.general_lay.addStretch()
        #setup general lay to form
        self.setLayout(self.general_lay)
        self.show()

    def init_data(self):
        self.memory_list = json.loads(self.settings_dict['memory-freq'])
        len_memory_list = len(self.memory_list)
        if len_memory_list > 0:
            self.memory_label.setText(str(len_memory_list))

            self.memory_label_show.setText("Mem: " + str(len_memory_list) + " Frq: "+ str(self.memory_list[len_memory_list-1]))
        else:
            self.memory_label.setText('')
            self.memory_label_show.setText('')
        #self.init_data()

    def clear_freq_label(self):
        self.freq_label.clear()

    def num_clicked(self):
        button = self.sender()
        freq = self.freq_label.text()
        digit_freq = self.freq_label.text().replace('.','')
        digit_freq = digit_freq.replace(' Hz','')
        if self.freq_status == 0:
            digit_freq=''
            self.freq_status = 1
        future_freq = digit_freq + button.text()
        if int(future_freq) < 146000000:
            freq_string_to_label = self.freq_to_sting(future_freq)
            self.freq_label.setText(freq_string_to_label+" Hz")
        else:
            self.freq_label.setText("146.000.000 Hz")
        #if len(digit_freq) == 0:
        #    digit_freq = '0'

    def freq_to_sting(self, freq):
        len_freq = len(freq)
        if len_freq <= 3:
            freq_to_label = freq
        elif len_freq > 3 and len_freq <=6:
            freq_to_label = freq[0:len_freq-3]+'.'+freq[len_freq-3:]
        elif len_freq > 6 and len_freq <= 8:
            freq_to_label = freq[0:len_freq-6]+'.'+freq[len_freq-6:len_freq-3]+'.'+freq[len_freq-3:]
        elif len_freq > 8 and len_freq <= 9:
            freq_to_label = freq[0:len_freq - 6] + '.' + freq[len_freq - 6:len_freq - 3] + '.' + freq[len_freq - 3:]

        #freq_to_label = freq[0:len_freq - 6] + "." + freq[len_freq - 6:len_freq - 3] + "." + freq[len_freq - 3:len_freq]
        #print("freq_to_label", freq_to_label)

        return freq_to_label

    def enter_freq(self):
        std_value = std.std()
        frequency = self.freq_label.text().replace(" Hz", '')
        frequency = frequency.replace('.','')
        if len(frequency) > 3 and int(frequency) > 0:
            logForm.set_freq(frequency)
            if (self.settings_dict['tci'] == 'enable'):
                #if len(frequency) <= 8:
                frequency = frequency.zfill(8)
                band = std_value.get_std_band(frequency)
                mode = std_value.mode_band_plan(band, frequency)
                try:
                    tci.Tci_sender(settingsDict['tci-server'] + ":" + settingsDict['tci-port']).set_freq(frequency)
                    tci.Tci_sender(settingsDict['tci-server'] + ":" + settingsDict['tci-port']).set_mode("0", mode)
                except Exception:
                   print("enter_freq:_> Can't setup tci_freq")
        if self.close_checkbox.isChecked():
            self.close()

    def delete_symbol_freq(self):
        self.freq_status = 1
        freq_str = self.freq_label.text()
            #.replace(".","")
        freq_str = freq_str.replace(" Hz","")
        freq_str_del = freq_str[:len(freq_str)-1]
        #freq_str_formated = self.freq_to_sting(freq_str_del)

        self.freq_label.setText(freq_str_del+" Hz")

    def save_freq_to_memory(self):
        self.memory_list.append(self.freq_label.text())
        self.active_memory_element = str(len(self.memory_list))
        self.memory_label.setText(self.active_memory_element)
        self.memory_label_show.setText("Mem: "+self.active_memory_element+ \
                                       " Frq: "+str(self.memory_list[int(self.active_memory_element) - 1]))

    def set_freq(self, freq):
        freq_formated = self.freq_to_sting(freq)
        self.freq_label.setText(freq_formated+" Hz")


    def change_memory_element(self):
        button = self.sender()
        if button.text() == "▲" and self.memory_label.text()!='':

            if int(self.memory_label.text()) - 1 == 0:
                self.index = len(self.memory_list)
                #index_to_label = 1
                self.memory_label.setText(str(self.index))
            else:
                self.index = int(self.memory_label.text()) - 1
                self.memory_label.setText(str(self.index))


        if button.text() == "▼" and self.memory_label.text()!='':
            if int(self.memory_label.text()) + 1 > len(self.memory_list):
                self.index = 1
                self.memory_label.setText(str(self.index))
            else:
                self.index = int(self.memory_label.text()) + 1
                self.memory_label.setText(str(self.index))
        if self.memory_label.text()!='':
            self.memory_label_show.setText("Mem: " + str(self.index) +
                                       " Frq: " + self.memory_list[self.index-1])

    def delete_from_memory(self):
        if self.memory_label.text() != '':
            index = int(self.memory_label.text()) - 1
            del self.memory_list[index]
            if len(self.memory_list) == 0:
                self.memory_label.setText('')
                self.memory_label_show.setText('No freq in memory')
            elif index == 0:
                self.memory_label.setText(str(index+1))
            else:
                self.memory_label.setText(str(index))

    def recal_from_memory(self):
        if self.memory_label.text() != '':
            index = int(self.memory_label.text()) - 1
            self.freq_label.setText(self.memory_list[index])
            self.enter_freq()

    def refresh_interface(self):
        self.label_style = "background:"+self.settings_dict['form-background']+ \
                                      "; color:"+self.settings_dict['color-table']+"; font: 25px"
        self.style = "background:" + self.settings_dict['background-color'] + "; color:" \
                + self.settings_dict['color'] + "; font: 12px;"
        self.style_window = "background:"+self.settings_dict['background-color']+"; color:"\
                           +self.settings_dict['color']+";"
        self.style_mem_label = "background:"+self.settings_dict['form-background']+ \
                                      "; color:"+self.settings_dict['color-table']+"; font: 12px"
        self.updatesEnabled()

    def closeEvent(self, event):
        self.settings_dict['memory-freq'] = json.dumps(self.memory_list)
        self.settings_dict['band'] = logForm.get_band()
        if self.close_checkbox.isChecked():
            self.settings_dict['freq-wnd'] = 'enable'
        else:
            self.settings_dict['freq-wnd'] = 'disable'

        self.settingsDict = self.settings_dict
        Settings_file.update_file_to_disk(self)
        self.close()

class logForm(QMainWindow):

    def __init__(self):
        super().__init__()
        self.diploms_init()
        #self.diploms = self.get_diploms()
        #self.freq_window_status = 0
        self.updater = update_after_run(version=APP_VERSION, settings_dict=settingsDict)

        self.initUI()



        #print("self.Diploms in logForm init:_>", self.diploms)

    def start_cat(self):
        self.cat_system = cat.Cat_start(settingsDict, self)

    def set_cat_label(self, flag: bool):
        if flag:
            self.labelStatusCat_cat.setStyleSheet("font-weight: bold; color: #57BD79;")
            self.labelStatusCat_cat.setText('CAT')
        else:
            self.labelStatusCat_cat.setStyleSheet("font-weight: bold; color: #FF6C49;")
            self.labelStatusCat_cat.setText('--')


    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_F5:
            self.full_clear_form()
        if e.key() == QtCore.Qt.Key_F12:
            self.freq_window()

    def menu(self):

        logSettingsAction = QAction('&Settings', self)
        #logSettingsAction.setStatusTip('Name, Call and other of station')
        logSettingsAction.triggered.connect(self.logSettings)
        #
        window_cluster_action = QAction('Cluster', self)
        #windowAction.setStatusTip('Name, Call and other of station')
        window_cluster_action.triggered.connect(self.stat_cluster)
        #
        window_inet_search_action = QAction ('Internet search', self)
        window_inet_search_action.triggered.connect(self.stat_internet_search)
        #
        window_repeat_qso_action = QAction ('Repeat QSO', self)
        window_repeat_qso_action.triggered.connect(self.stat_repeat_qso)


        self.menuBarw = self.menuBar()
        self.menuBarw.setStyleSheet("QWidget{font: 12px;}")
      #  settings_menu = menuBar.addMenu('Settings')
        self.menuBarw.addAction(logSettingsAction)
        WindowMenu = self.menuBarw.addMenu('&Window')
        #WindowMenu.triggered.connect(self.logSettings)
        WindowMenu.addAction(window_cluster_action)
        WindowMenu.addAction(window_inet_search_action)
        WindowMenu.addAction(window_repeat_qso_action)

        self.otherMenu = self.menuBarw.addMenu('&Diploms')
        window_form_diplom = QAction('New diploma', self)
        window_form_diplom.triggered.connect(self.new_diplom)
        self.otherMenu.addAction(window_form_diplom)
        #
        aboutAction = QAction('&About', self)
        # logSettingsAction.setStatusTip('Name, Call and other of station')
        aboutAction.triggered.connect(self.about_window)
        self.menuBarw.addAction(aboutAction)

        if self.diploms != []:

            for i in range(len(self.diploms)):
                diplom_data = self.diploms[i].get_data()
                #print("self.diploms:_>", diplom_data[0]['name'])
                self.menu_add(diplom_data[0]['name'])

        '''
        catSettingsAction = QAction(QIcon('logo.png'), 'Cat settings', self)
        catSettingsAction.setStatusTip('Name, Call and other of station')
        catSettingsAction.triggered.connect(self.logSettings)
        #
        logWindowAction = QAction(QIcon('logo.png'), 'All log Window', self)
        logWindowAction.setStatusTip('Name, Call and other of station')
        logWindowAction.triggered.connect(self.logSettings)
        #
        searchWindowAction = QAction(QIcon('logo.png'), 'Search window', self)
        searchWindowAction.setStatusTip('Name, Call and other of station')
        searchWindowAction.triggered.connect(self.searchWindow)
        #
        importAdiAction = QAction(QIcon('logo.png'), 'Import ADI', self)
        importAdiAction.setStatusTip('Name, Call and other of station')
        importAdiAction.triggered.connect(self.logSettings)
        #
        exportAdiAction = QAction(QIcon('logo.png'), 'Export ADI', self)
        exportAdiAction.setStatusTip('Name, Call and other of station')
        exportAdiAction.triggered.connect(self.logSettings)
        #

        telnetAction = QAction(QIcon('logo.png'), 'Cluster window', self)
        telnetAction.setStatusTip('Name, Call and other of station')
        telnetAction.triggered.connect(self.logSettings)
        #
        newDiplomEnvAction = QAction(QIcon('logo.png'), 'New Diplom Env', self)
        newDiplomEnvAction.setStatusTip('Name, Call and other of station')
        newDiplomEnvAction.triggered.connect(self.logSettings)
        #
        helpAction = QAction(QIcon('logo.png'), 'New Diplom Env', self)
        helpAction.setStatusTip('Name, Call and other of station')
        helpAction.triggered.connect(self.logSettings)
        #
        aboutAction = QAction(QIcon('logo.png'), 'New Diplom Env', self)
        aboutAction.setStatusTip('Name, Call and other of station')
        aboutAction.triggered.connect(self.logSettings)
        #
        exitAction = QAction(QIcon('logo.png'), '&Exit', self)
        exitAction.triggered.connect(QApplication.quit)

        menuBar = self.menuBar()
        mainMenu = menuBar.addMenu('&Menu')
        mainMenu.addAction(logSettingsAction)
        mainMenu.addAction(catSettingsAction)
        searchWindowMenu = mainMenu.addMenu('Window')
        searchWindowMenu.addAction(telnetAction)
        searchWindowMenu.addAction(logWindowAction)
        searchWindowMenu.addAction(searchWindowAction)
        mainMenu.addAction(importAdiAction)
        mainMenu.addAction(exportAdiAction)
        diplomMenu = mainMenu.addMenu('Diplom Env.')
        diplomMenu.addAction(newDiplomEnvAction)
        mainMenu.addAction(exitAction)
        ###
        helpMenu = menuBar.addMenu('Help')
        helpMenu.addAction(helpAction)
        helpMenu.addAction(aboutAction)
        '''
        #pass

    def menu_add(self, name_menu):
        # self.otherMenu = self.menuBarw.addMenu('&Other')

       # print(name_menu)
        self.item_menu = self.otherMenu.addMenu(name_menu)
        edit_diploma = QAction('Edit '+name_menu, self)
        edit_diploma.triggered.connect(lambda checked, name_menu=name_menu : self.edit_diplom(name_menu))
        show_stat = QAction('Show statistic', self)
        show_stat.triggered.connect(lambda checked, name_menu=name_menu : self.show_statistic_diplom(name_menu))
        del_diploma = QAction ("Delete "+name_menu, self)
        del_diploma.triggered.connect(lambda checked, name_menu=name_menu : self.del_diplom(name_menu))
        self.item_menu.addAction(show_stat)
        self.item_menu.addAction(edit_diploma)
        self.item_menu.addAction(del_diploma)

    def menu_rename_diplom(self):
        self.menuBarw.clear()
        #self.otherMenu.clear()

    def edit_diplom(self, name):
        all_data = ext.diplom.get_rules(self=ext.diplom, name=name+".rules")
        self.edit_window = ext.Diplom_form(settingsDict=settingsDict, log_form=self,
                        adi_file=adi_file, diplomname=name, list_data=all_data)
        self.edit_window.show()

        #print("edit_diplom:_>", name, "all_data:", all_data)

    def show_statistic_diplom(self, name):
        self.stat_diplom = ext.static_diplom(diplom_name=name, settingsDict=settingsDict)
        self.stat_diplom.show()
        #print("show_statistic_diplom:_>", name)

    def del_diplom (self, name):
        ext.diplom.del_dilpom(ext.diplom, name, settingsDict, self)
        #print("del_diplom:_>", name)

    def new_diplom(self):
        #new_diploma = ext.Diplom_form(settingsDict=settingsDict, log_form=logForm)

        #diploma.show()
        new_diploma.show()

    def about_window(self):
       # print("About_window")
        about_window.show()

    def searchWindow(self):

        logSearch.hide()

    def initUI(self):
        font = QFont("Cantarell Light", 10, QFont.Normal)
        QApplication.setFont(font)
        styleform = "background :" + settingsDict['form-background']+\
                    "; color: " + settingsDict['color-table'] + "; padding: 0em"
        self.setGeometry(int(settingsDict['log-form-window-left']), int(settingsDict['log-form-window-top']),
                         int(settingsDict['log-form-window-width']), int(settingsDict['log-form-window-height']))
        self.setWindowTitle('LinuxLog | Form')
        self.setWindowIcon(QIcon('logo.png'))
        style = "background-color:" + settingsDict['background-color'] + "; color:" + settingsDict[
            'color'] + ";"
        self.setStyleSheet(style)
        self.menu()

        # self.test()
        self.labelCall = QLabel("Call")
        self.labelCall.setFont(QtGui.QFont('SansSerif', 9))

        # labelCall.move(40,40)
        self.inputCall = QLineEdit()
        self.inputCall.setFocusPolicy(Qt.StrongFocus)
        self.inputCall.setStyleSheet(styleform)
        self.inputCall.setFixedWidth(108)
        self.inputCall.setFixedHeight(30)
        self.inputCall.textChanged[str].connect(
            self.onChanged)  # событие изминения текста, привязываем в слот функцию onChanged
        self._filter = Filter()
        # adjust for your QLineEdit
        self.inputCall.installEventFilter(self._filter)
        self.inputCall.returnPressed.connect(
            self.logFormInput)  # событие нажатия Enter, привязываем в слот функцию logSettings
        #self.inputCall.tabPressed.connect(self.internetWorker.get_internet_info)
        # inputCall.move(40,40)

        self.labelRstR = QLabel('RSTr')

        self.labelRstR.setFont(QtGui.QFont('SansSerif', 7))

        self.inputRstR = QLineEdit()

        self.inputRstR.setFixedWidth(35)
        self.inputRstR.setFixedHeight(35)
        self.inputRstR.setStyleSheet(styleform)

        if settingsDict['mode-swl'] == 'enable':
            self.inputRstR.setText('SWL')
           # fnt = self.inputRstR.font()
            #fnt.setPointSize(7)
            #self.inputRstR.setFont(fnt)
            self.inputRstR.setText('SWL')
            self.inputRstR.setEnabled(False)

        else:
            self.inputRstR.setText('59')
            self.inputRstR.setEnabled(True)

        self.inputRstR.returnPressed.connect(self.logFormInput)

        self.inputRstR.installEventFilter(self._filter)

        self.labelRstS = QLabel('RSTs')
        self.labelRstS.setFont(QtGui.QFont('SansSerif', 7))
        self.inputRstS = QLineEdit("59")
        self.inputRstS.setFixedWidth(35)
        self.inputRstS.setFixedHeight(35)
        self.inputRstS.setStyleSheet(styleform)
        self.inputRstS.returnPressed.connect(self.logFormInput)

        self.labelName = QLabel('Name')
        self.labelName.setFont(QtGui.QFont('SansSerif', 9))
        self.inputName = QLineEdit(self)
        self.inputName.setFixedWidth(137)
        self.inputName.setFixedHeight(30)
        self.inputName.setStyleSheet(styleform)
        self.inputName.returnPressed.connect(self.logFormInput)

        self.labelQth = QLabel("QTH  ")
        self.labelQth.setFont(QtGui.QFont('SansSerif', 9))

        self.inputQth = QLineEdit(self)
        self.inputQth.setFixedWidth(137)
        self.inputQth.setFixedHeight(30)
        self.inputQth.setStyleSheet(styleform)
        self.inputQth.returnPressed.connect(self.logFormInput)

        self.comboMode = QComboBox(self)
        self.comboMode.setFixedWidth(80)
        self.comboMode.setFixedHeight(30)
        self.comboMode.addItems(["SSB", "ESSB", "CW", "AM", "FM", "DSB", "DIGI"])
        indexMode = self.comboMode.findText(settingsDict['mode'])
        self.comboMode.setCurrentIndex(indexMode)
        self.comboMode.activated[str].connect(self.rememberMode)

        self.comboBand = QComboBox(self)
        self.comboBand.setFixedWidth(80)
        self.comboBand.setFixedHeight(30)
        self.comboBand.addItems(["160", "80", "40", "30", "20", "17", "15", "12", "10", "6", "2", "100", "200"])
        indexBand = self.comboBand.findText(settingsDict['band'])
        self.comboBand.setCurrentIndex(indexBand)
        #self.comboBand.activated[str].connect(self.rememberBand)
        self.comboBand.currentTextChanged.connect(self.rememberBand)

        self.labelStatusCat = QLabel('    ')
        self.labelStatusCat.setAlignment(Qt.AlignLeft)
        self.labelStatusCat.setFont(QtGui.QFont('SansSerif', 7))

        self.labelStatusCat_cat = QLabel('    ')
        self.labelStatusCat_cat.setAlignment(Qt.AlignLeft)
        self.labelStatusCat_cat.setFont(QtGui.QFont('SansSerif', 7))

        self.labelStatusTelnet = QLabel('')
        self.labelStatusTelnet.setAlignment(Qt.AlignLeft)
        self.labelStatusTelnet.setFont(QtGui.QFont('SansSerif', 7))

        self.labelTime = QLabel()
        self.labelTime.setFont(QtGui.QFont('SansSerif', 7))


        self.labelFreq = ClikableLabel()
        self.labelFreq.setFont(QtGui.QFont('SansSerif', 7))
        self.labelFreq.setText("Freq control (F12)")
        self.labelFreq.click_signal.connect(self.freq_window)
        self.labelFreq.change_value_signal.connect(self.change_freq_event)
        self.labelMyCall = QLabel(settingsDict['my-call'])
        self.labelMyCall.setFont(QtGui.QFont('SansSerif', 10))
        self.comments = QTextEdit()
        self.comments.setFontPointSize(10)
        self.comments.setFontWeight(3)
        self.comments.setPlaceholderText("Comment")
        self.comments.setFixedHeight(60)

        hBoxHeader = QHBoxLayout()
        hBoxHeader.addWidget(self.labelTime)

        #hBoxLeft = QHBoxLayout(self)
        #hBoxRight = QHBoxLayout(self)
        hBoxRst = QHBoxLayout(self)

        vBoxLeft = QVBoxLayout(self)

        vBoxRight = QVBoxLayout(self)
        vBoxMain = QVBoxLayout(self)
        # Build header line
        hBoxHeader.addStretch(20)
        hBoxHeader.addWidget(self.labelFreq)
        hBoxHeader.addWidget(self.labelMyCall)
        # Build Left block
        # vBoxLeft.addLayout(hBoxHeader)

        # set label Call
        # set input CALL
        hCall = QHBoxLayout(self)
        hCall.addWidget(self.labelCall)
        hCall.addWidget(self.inputCall)
        hCall.addStretch(1)
        vBoxLeft.addLayout(hCall)

        hBoxRst.addWidget(self.labelRstR)  # set label RSTr
        hBoxRst.addWidget(self.inputRstR)
        hBoxRst.addWidget(self.labelRstS)  # set input RSTr
        hBoxRst.addWidget(self.inputRstS)
        hBoxRst.addStretch(1)

        vBoxLeft.addLayout(hBoxRst)
        hName = QHBoxLayout(self)

        hName.addWidget(self.labelName)
        hName.addWidget(self.inputName)
        hName.addStretch(1)
        vBoxLeft.addLayout(hName)

        hQth = QHBoxLayout(self)
        hQth.addWidget(self.labelQth)
        hQth.addWidget(self.inputQth)
        hQth.addStretch(1)
        vBoxLeft.addLayout(hQth)

        # vBoxLeft.addWidget( labelName) #set label Name
        # vBoxLeft.addWidget( inputName) #set input Name
        # vBoxLeft.addWidget( labelQth)  #set label QTH
        # vBoxLeft.addWidget( inputQth)  #set input RSTr

        vBoxRight.addWidget(self.comboBand)
        vBoxRight.addWidget(self.comboMode)
        vBoxRight.addStretch(1)
        #vBoxRight.addWidget(self.labelStatusCat)
        #vBoxRight.addWidget(self.labelStatusTelnet)

        leftRight = QHBoxLayout()

        leftRight.addLayout(vBoxLeft)
        leftRight.addLayout(vBoxRight)
        # leftRight.setAlignment(Qt.AlignHCenter)

        vBoxMain.addLayout(hBoxHeader)
        vBoxMain.addLayout(leftRight)

        hBoxStatus = QHBoxLayout()
        hBoxStatus.setAlignment(Qt.AlignRight)
        hBoxStatus.addWidget(self.labelStatusTelnet)
        hBoxStatus.addWidget(self.labelStatusCat)
        hBoxStatus.addWidget(self.labelStatusCat_cat)

        vBoxMain.addWidget(self.comments)
        vBoxMain.addLayout(hBoxStatus)

        style = "QTextEdit{background:" + settingsDict['form-background'] + "; border: 1px solid " + settingsDict[
            'solid-color'] + ";}"
        self.comments.setStyleSheet(style)

        central_widget = QWidget()
        central_widget.setLayout(vBoxMain)
        self.setCentralWidget(central_widget)

       # self.show()

        # run time in Thread
        self.run_time = realTime(logformwindow=self) #run time in Thread
        self.run_time.start()

    def full_clear_form(self):
        self.inputCall.clear()
        if settingsDict['mode-swl'] == 'enable':
            #fnt = self.inputRstR.font()
            #fnt.setPointSize(7)
            #self.inputRstR.setFont(fnt)
            self.inputRstR.setText('SWL')
            self.inputRstR.setEnabled(False)
        else:
            self.inputRstR.setText('59')
        self.inputRstS.setText('59')
        self.inputName.clear()
        self.inputQth.clear()
        self.comments.clear()

    def change_freq_event(self):
        freq = self.labelFreq.text()
        print("Change_freq_event:_>", freq)

    def freq_window(self):
        print ("Click by freq label")
        self.freq_input_window = FreqWindow(settings_dict=settingsDict)

    def rememberBand(self, text):
        print("Band change value", self.comboBand.currentText())
        #settingsDict['band'] = self.comboBand.currentText().strip()
        with open('settings.cfg', 'r') as file:
            # read a list of lines into data
            data = file.readlines()
        for i in range(len(data)):
            string = data[i]
            string = string.strip()
            string = string.replace("\r", "")
            string = string.replace("\n", "")
            string = string.split('=')
            # print(string)
            if data[i][0] != "#":
                if string[0] == 'band':
                    string[1] = self.comboBand.currentText().strip()
                data[i] = string[0] + '=' + string[1] + '\n'
                with open('settings.cfg', 'w') as file:
                    file.writelines(data)

    def rememberMode(self, text):
        # print(self.comboMode.currentText())
        with open('settings.cfg', 'r') as file:
            # read a list of lines into data
            data = file.readlines()
        for i in range(len(data)):
            string = data[i]
            string = string.strip()
            string = string.replace("\r", "")
            string = string.replace("\n", "")
            string = string.split('=')
            # print(string)
            if data[i][0] != "#":
                if string[0] == 'mode':
                    string[1] = self.comboMode.currentText().strip()
                data[i] = string[0] + '=' + string[1] + '\n'
                with open('settings.cfg', 'w') as file:
                    file.writelines(data)

    def key_lay_reverse(self, string: str):
        '''
        This method reciev string on russian and reverse lay
        in equivalent to english keyboard lay. ЙЦУКЕН => QWERTY
        :param string: input original string
        :return:
        '''

        reverse_dict = {"Й":"Q", "Ц":"W", "У":"E", "К":"R", "Е":"T", "Н":"Y", "Г":"U",
                        "Ш":"I", "Щ":"O", "З":"P", "Х":"", "Ъ":"",
                        "Ф":"A", "Ы":"S", "В":"D", "А":"F", "П":"G", "Р":"H", "О":"J",
                        "Л":"K", "Д":"L", "Ж":":","Э":"",
                        "Я":"Z", "Ч":"X", "С":"C", "М":"V", "И":"B", "Т":"N", "Ь":"M",
                        "Б":"", "Ю":"",".":"/"}
        new_string = ""

        for char in string:
                if re.search('[А-Я]', char):
                    char_reverse = reverse_dict[char]
                else:
                    char_reverse = char
                new_string += char_reverse
        return new_string

    def onChanged(self, text):
        '''метод которій отрабатывает как только произошло изменение в поле ввода'''
        self.inputCall.setText(text.upper())

        if re.search('[А-Я]', text):

            string_old = self.inputCall.text()
            string_reverse = self.key_lay_reverse(string_old)
            self.inputCall.setText(string_reverse)

    def logFormInput(self):

        call = str(self.inputCall.text()).strip()
        # print(call+ "this")
        if call != '':
            recordObject = {}
            #freq = str(self.labelFreq.text()).strip()

            mode = str(self.comboMode.currentText()).strip()
            rstR = str(self.inputRstR.text()).strip()
            rstS = str(self.inputRstS.text()).strip()
            name = str(self.inputName.text()).strip()
            qth = str(self.inputQth.text()).strip()
            operator = str(self.labelMyCall.text()).strip()
            band = str(self.comboBand.currentText()).strip() + "M"
            comment = str(self.comments.toPlainText()).strip()
            comment = comment.replace("\r", " ")
            comment = comment.replace("\n", " ")
            freq = self.get_freq()

            self.EQSL_QSL_SENT = 'N'

            all_records = logWindow.get_all_record()            # print("'QSO_DATE':'20190703', 'TIME_ON':'124600', 'FREQ':"+freq+" 'CALL':"+cal+"'MODE'"+mode+" 'RST_RCVD':"+rstR+" 'RST_SENT':"+rstS+", 'NAME':"+name+", 'QTH':"+qth+"'OPERATOR':"+operator+"'BAND':"+band+"'COMMENT':"+comment)
            record_number = len(All_records) + 1

            print("record_number in logFrom:", len(All_records))
            datenow = datetime.datetime.now()
            date = datenow.strftime("%Y%m%d")
            time = str(strftime("%H%M%S", gmtime()))


            self.recordObject = {'records_number': str(record_number), 'QSO_DATE': date, 'TIME_ON': time, 'FREQ': freq, 'CALL': call, 'MODE': mode,
                            'RST_RCVD': rstR, 'RST_SENT': rstS, 'NAME': name, 'QTH': qth, 'OPERATOR': operator,
                            'BAND': band, 'COMMENTS': comment, 'TIME_OFF': time,
                            'EQSL_QSL_SENT': 'N'}

            logWindow.addRecord(self.recordObject)


            call_dict = {'call': call, 'mode': mode, 'band': band}
            #print ("call_dict:_>", call_dict)
            if settingsDict['diplom'] == 'enable':
                for diploms in self.diploms:
                    if diploms.filter(call_dict):
                        #print("filter true for:", diploms, "string:", recordObject)
                        diploms.add_qso(self.recordObject)


                #sync_eqsl.start()
            try:
                tci.Tci_sender(settingsDict['tci-server'] + ":" + settingsDict['tci-port']).change_color_spot(call, freq)
            except:
                print ("LogFormInput: can't connect to TCI server (set spot)")

            logForm.inputCall.setFocus(True)

            if settingsDict['mode-swl'] == 'enable':
                self.inputCall.clear()
                self.inputName.clear()
                self.inputQth.clear()
                #fnt = self.inputRstR.font()
                #fnt.setPointSize(7)
                #self.inputRstR.setFont(fnt)
                self.inputRstR.setText('SWL')
                self.inputRstR.setEnabled(False)
                self.inputRstS.setText('59')
            else:
                self.inputCall.clear()
                self.inputRstS.setText('59')
                self.inputRstR.setText('59')
                self.inputName.clear()
                self.inputQth.clear()
                self.comments.clear()
            try:
                logSearch.tableWidget.clearContents()
                internetSearch.update_photo()
            except Exception:
                pass

    def changeEvent(self, event):

        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.isMinimized():
                if settingsDict['search-internet-window'] == 'true':
                    internetSearch.showMinimized()
                    settingsDict['search-internet-window'] = 'true'
                if settingsDict['log-search-window'] == 'true':
                    logSearch.showMinimized()
                    settingsDict['log-search-window'] = 'true'
                if settingsDict['log-window'] == 'true':
                    logWindow.showMinimized()
                    settingsDict['log-window'] = 'true'
                if settingsDict['telnet-cluster-window'] == 'true':
                    telnetCluster.showMinimized()
                    settingsDict['telnet-cluster-window'] = 'true'
            QWidget.changeEvent(self, event)

    def showEvent(self, event):
        #print("Show Event", settingsDict['log-window'])
        if settingsDict['log-window'] == 'true':
            #print("Show Event", settingsDict['log-window'])
            logWindow.showNormal()

        if settingsDict['log-search-window'] == 'true':
            logSearch.showNormal()
        if settingsDict['telnet-cluster-window'] == 'true':
            telnetCluster.showNormal()
        if settingsDict['search-internet-window'] == 'true':
            internetSearch.showNormal()
        #print ("Show normal")

    def closeEvent(self, event):
        '''
        This function recieve signal close() from logSearch window
        Save coordinate and size all window
        Close app
        '''
        self.parameter={}
        if settingsDict['log-window'] == 'true':

            logWindow_geometry = logWindow.geometry()
            self.parameter.update({'log-window-left': str(logWindow_geometry.left()),
                              'log-window-top': str(logWindow_geometry.top()),
                              'log-window-width': str(logWindow_geometry.width()),
                              'log-window-height': str(logWindow_geometry.height())
                              })

        if settingsDict['search-internet-window'] == 'true':

            internetSearch_geometry = internetSearch.geometry()
            self.parameter.update({'search-internet-left': str(internetSearch_geometry.left()),
                              'search-internet-top': str(internetSearch_geometry.top()),
                              'search-internet-width': str(internetSearch_geometry.width()),
                              'search-internet-height': str(internetSearch_geometry.height())
                              })
        if settingsDict['log-search-window'] == 'true':

            logSearch_geometry = logSearch.geometry()
            self.parameter.update({'log-search-window-left': str(logSearch_geometry.left()),
                              'log-search-window-top': str(logSearch_geometry.top()),
                              'log-search-window-width': str(logSearch_geometry.width()),
                              'log-search-window-height': str(logSearch_geometry.height())
                              })
        if settingsDict['log-form-window'] == 'true':

            logForm_geometry = logForm.geometry()
            self.parameter.update({'log-form-window-left': str(logForm_geometry.left()),
                              'log-form-window-top': str(logForm_geometry.top()),
                              'log-form-window-width': str(logForm_geometry.width()),
                              'log-form-window-height': str(logForm_geometry.height())
                              })
        if settingsDict['telnet-cluster-window'] == 'true':

            telnetCluster_geometry = telnetCluster.geometry()
            self.parameter.update({'telnet-cluster-window-left': str(telnetCluster_geometry.left()),
                              'telnet-cluster-window-top': str(telnetCluster_geometry.top()),
                              'telnet-cluster-window-width': str(telnetCluster_geometry.width()),
                              'telnet-cluster-window-height': str(telnetCluster_geometry.height())
                              })
        #self.parameter.update({"band": settingsDict['band']})
        '''
        internetSearch_geometry = internetSearch.geometry()
        settingsDict['search-internet-left'] = str(internetSearch_geometry.left())
        settingsDict['search-internet-top'] = str(internetSearch_geometry.top())
        settingsDict['search-internet-width'] = str(internetSearch_geometry.width())
        settingsDict['search-internet-height'] = str(internetSearch_geometry.height())
        ###
        logWindow_geometry = logWindow.geometry()
        settingsDict['log-window-left'] = str(logWindow_geometry.left())
        settingsDict['log-window-top'] = str(logWindow_geometry.top())
        settingsDict['log-window-width'] = str(logWindow_geometry.width())
        settingsDict['log-window-height'] = str(logWindow_geometry.height())
        ###
        logSearch_geometry = logSearch.geometry()
        settingsDict['log-search-window-left'] = str(logSearch_geometry.left())
        settingsDict['log-search-window-top'] = str(logSearch_geometry.top())
        settingsDict['log-search-window-width'] = str(logSearch_geometry.width())
        settingsDict['log-search-window-height'] = str(logSearch_geometry.height())
        ###
        logForm_geometry = logForm.geometry()
        settingsDict['log-form-window-left'] = str(logForm_geometry.left())
        settingsDict['log-form-window-top'] = str(logForm_geometry.top())
        settingsDict['log-form-window-width'] = str(logForm_geometry.width())
        settingsDict['log-form-window-height'] = str(logForm_geometry.height())
        ###
        telnetCluster_geometry = telnetCluster.geometry()
        settingsDict['telnet-cluster-window-left'] = str(telnetCluster_geometry.left())
        settingsDict['telnet-cluster-window-top'] = str(telnetCluster_geometry.top())
        settingsDict['telnet-cluster-window-width'] = str(telnetCluster_geometry.width())
        settingsDict['telnet-cluster-window-height'] = str(telnetCluster_geometry.height())

        ###
        '''


        logWindow.close()
        internetSearch.close()
        logSearch.close()
        logForm.close()
        telnetCluster.close()


        #print(parameter)
        try:
            if self.menu.isEnabled():
                self.menu.close()
        except Exception:
            pass
        try:
            if self.freq_input_window.isEnabled():
                self.freq_input_window.close()
        except:
            pass

        if about_window.isEnabled():
            about_window.close()

        self.remember_in_cfg(self.parameter)

    def remember_in_cfg (self, parameter):
        '''
        This function reciev Dictionary parametr with key:value
        record key=value into config.cfg

        :param parameter:
        :return:
        '''
       # print(parameter)
        filename='settings.cfg'
        with open(filename,'r') as f:
            old_data = f.readlines()
        for line, string in enumerate(old_data):
            #print(line, string)
            for key in parameter:
                if key in string:
                    string = key+"="+parameter[key]+"\n"
                    old_data[line] = string
        with open(filename, 'w') as f:
            f.writelines(old_data)

    def empty(self):
        print('hi')

    def logSettings(self):
        print('logSettings')
        #menu_window.show()
        self.menu = settings.Menu(settingsDict,
                             telnetCluster,
                             logForm,
                             logSearch,
                             logWindow,
                             internetSearch,
                             tci_recv)
        self.menu.show()
        # logSearch.close()

    def stat_cluster(self):

        if telnetCluster.isHidden():
            print('statTelnet')
            telnetCluster.show()
        elif telnetCluster.isEnabled():
            telnetCluster.hide()

    def stat_internet_search(self):
        if internetSearch.isHidden():
            print('internet_search')
            internetSearch.show()
        elif internetSearch.isEnabled():
            internetSearch.hide()

    def stat_repeat_qso(self):
        if logSearch.isHidden():
            print('internet_search')
            logSearch.show()
        elif logSearch.isEnabled():
            logSearch.hide()

    def set_band(self, band):
        #print("LogForm.set_band. input band:", band)
        indexMode = self.comboBand.findText(band)
        self.comboBand.setCurrentIndex(indexMode)

    def set_freq(self, freq):
        freq_string = str(freq)
        freq_string = freq_string.replace('.', '')
        len_freq=len(freq)
        #print ("set_freq:_>", freq_string)
        freq_to_label = freq[0:len_freq - 6] + "." + freq[len_freq - 6:len_freq - 3] + "." + freq[len_freq - 3:]
        self.labelFreq.setText("Freq: "+str(freq_to_label))
        band = std.std().get_std_band(freq)
        #print(band)
        index_band = self.comboBand.findText(band)
        self.comboBand.setCurrentIndex(index_band)
        try:
            if self.freq_input_window.isEnabled():
                if settingsDict['cat'] != "enable":
                    self.freq_input_window.set_freq(freq)
                else:
                    pass
        except Exception:
            pass


    def set_call(self, call):
        self.inputCall.setText(str(call))

    def set_mode_tci(self, mode):
        if mode == "lsb" or mode == "usb":
            mode_string = 'SSB'
        if mode == "am" or mode == "sam":
            mode_string = 'AM'
        if mode == "dsb":
            mode_string = 'DSB'
        if mode == "cw":
            mode_string = 'CW'
        if mode == "nfm" or mode == "wfm":
            mode_string = 'FM'
        if mode == "digl" or mode == "digu" or mode == "drm":
            mode_string = 'DIGI'
        indexMode = self.comboMode.findText(mode_string)
        self.comboMode.setCurrentIndex(indexMode)

    def set_tci_stat(self, values , color="#57BD79"):
        self.labelStatusCat.setStyleSheet("color: "+color+"; font-weight: bold;")
        self.labelStatusCat.setText(values)

    def set_tci_label_found(self, values=''):
        self.labelStatusCat.setStyleSheet("color: #FF6C49; font-weight: bold;")
        self.labelStatusCat.setText("TCI Found "+values)
        time.sleep(0.55)
        self.labelStatusCat.setText("")

    def set_telnet_stat(self):
        self.labelStatusTelnet.setStyleSheet("color: #57BD79; font-weight: bold;")
        self.labelStatusTelnet.setText("✔ Telnet")
        time.sleep(0.15)
        self.labelStatusTelnet.setText("")

    def get_band(self):
        return self.comboBand.currentText()

    def get_freq(self):
        freq_string = self.labelFreq.text()
        freq_string = freq_string.replace('Freq: ', '')
        freq_string = freq_string.replace('.', '')
        #print(freq_string.isdigit())

        if freq_string == '' or not freq_string.isdigit():
            band = self.get_band()
            if band == "160":
                freq_string = '1800000'
            elif band == "80":
                freq_string = '3500000'
            elif band == "40":
                freq_string = '7000000'
            elif band == "30":
                freq_string = '10000000'
            elif band == "20":
                freq_string = '14000000'
            elif band == "17":
                freq_string = '18000000'
            elif band == "15":
                freq_string = '21000000'
            elif band == "12":
                freq_string = '24000000'
            elif band == "10":
                freq_string = '28000000'
            elif band == "6":
                freq_string = '54000000'
            elif band == "144":
                freq_string = '144500000'
            else:
                freq_string = 'non'



        return freq_string

    def refresh_interface(self):
        self.labelMyCall.setText(settingsDict['my-call'])
        if settingsDict['mode-swl'] == 'enable':
            self.inputRstR.setText("SWL")
            self.inputRstR.setEnabled(False)
        else:
            self.inputRstR.setText("59")
            self.inputRstR.setEnabled(True)
        self.update_color_schemes()
        try:
            if self.freq_input_window.isEnabled():
                self.freq_input_window.refresh_interface()
        except Exception:
            pass

    def update_color_schemes(self):
        style = "background-color:" + settingsDict['background-color'] + "; color:" + \
                settingsDict['color'] + ";"
        self.labelCall.setStyleSheet(style)
        self.labelRstR.setStyleSheet(style)
        self.labelRstS.setStyleSheet(style)
        self.labelName.setStyleSheet(style)
        self.labelQth.setStyleSheet(style)
        self.labelTime.setStyleSheet(style)
        self.labelFreq.setStyleSheet(style)
        self.labelMyCall.setStyleSheet(style)
        self.comboMode.setStyleSheet(style)
        self.comboBand.setStyleSheet(style)
        self.labelStatusCat.setStyleSheet(style)
        style_form = "background-color:" + settingsDict['form-background'] + "; color:" + settingsDict[
            'color-table'] + "; font: 12px"
        self.inputCall.setStyleSheet(style_form)
        self.inputRstR.setStyleSheet(style_form)
        self.inputRstS.setStyleSheet(style_form)
        self.inputName.setStyleSheet(style_form)
        self.inputQth.setStyleSheet(style_form)
        self.comments.setStyleSheet(style_form)


        self.setStyleSheet(style)

    def update_settings(self, new_settingsDict):
        settingsDict.update(new_settingsDict)
        #print(settingsDict['my-call'])

    def test(data):
        pass

    def diploms_init(self):
        self.diploms = self.get_diploms()

    def get_diploms(self):
        names_diploms=[]
        if settingsDict['diploms-json'] != '':
            list_string = json.loads(settingsDict['diploms-json'])
            for i in range(len(list_string)):
                list_string[i]['name_programm'] = ext.diplom(list_string[i]['name_programm']+".adi", list_string[i]['name_programm']+".rules")
                names_diploms.append(list_string[i]['name_programm'])
        #print("names_diploms:_>", names_diploms)
        return names_diploms

class clusterThread(QThread):
    def __init__(self, cluster_window, form_window, parent=None):
        super().__init__()
        self.telnetCluster = cluster_window
        self.form_window = form_window
        # self.run()

    def run(self):
        HOST = settingsDict['telnet-host']
        PORT = settingsDict['telnet-port']
        call = settingsDict['my-call']
        while 1:
            try:
                telnetObj = telnetlib.Telnet(HOST, PORT)
                break
            except:
                time.sleep(3)
                continue

        lastRow = 0
        message = (call + "\n").encode('ascii')
        telnetObj.write(message)
        message2 = (call + "\n").encode('ascii')
        telnetObj.write(message2)
        splitString = []
        cleanList = []
        i = 0
        print('Starting Telnet cluster:', HOST, ':', PORT, '\nCall:', call, '\n\n')
        while 1:
          try:
            output_data = telnetObj.read_some()


            if output_data != '':
                    lastRow = self.telnetCluster.tableWidget.rowCount()
                    self.form_window.set_telnet_stat()
                    #print (output_data)
                    if output_data[0:2].decode(settingsDict['encodeStandart']) == "DX":
                        splitString = output_data.decode(settingsDict['encodeStandart']).split(' ')
                        count_chars = len(splitString)
                        for i in range(count_chars):
                            if splitString[i] != '':
                                cleanList.append(splitString[i])
                        #color = QColor(100, 50, 50)
                        search_in_diplom_rules_flag = 0
                        call_dict = {'call': cleanList[int(settingsDict['telnet-call-position'])].strip(),
                                     'mode': 'cluster',
                                     'band': 'cluster'}
                        diplom_list = logForm.get_diploms()

                        for i in range(len(diplom_list)):

                            #print("get_color:_>", color)
                            #print ("cicle Diploms:", diplom_list[i])
                            if diplom_list[i].filter(call_dict):
                                color = diplom_list[i].get_color_bg()
                                search_in_diplom_rules_flag = 1
                      #  print("clean list", cleanList[int(settingsDict['telnet-call-position'])].strip())

                        if telnetCluster.cluster_filter(cleanList=cleanList):
    #####
                            #print(cleanList) # Check point - output List with data from cluster telnet-server


                            self.telnetCluster.tableWidget.insertRow(lastRow)

                            #self.telnetCluster.tableWidget
                            self.telnetCluster.tableWidget.setItem(lastRow, 0,
                                                                   QTableWidgetItem(
                                                                       strftime("%H:%M:%S", localtime())))

                            self.telnetCluster.tableWidget.item(lastRow, 0).setForeground(QColor(self.telnetCluster.settings_dict["color-table"]))

                            #self.telnetCluster.tableWidget.item(lastRow, 0).setBackground(color)
                            if search_in_diplom_rules_flag == 1:
                                self.telnetCluster.tableWidget.item(lastRow, 0).setBackground(color)
                            self.telnetCluster.tableWidget.setItem(lastRow, 1,
                                                                   QTableWidgetItem(
                                                                       strftime("%H:%M:%S", gmtime())))
                            self.telnetCluster.tableWidget.item(lastRow, 1).setForeground(QColor(self.telnetCluster.settings_dict["color-table"]))
                            if search_in_diplom_rules_flag == 1:
                                self.telnetCluster.tableWidget.item(lastRow, 1).setBackground(color)

                            if (len(cleanList) > 4):
                                self.telnetCluster.tableWidget.setItem(lastRow, 2,
                                                                       QTableWidgetItem(cleanList[int(settingsDict['telnet-call-position'])]))
                                self.telnetCluster.tableWidget.item(lastRow, 2).setForeground(QColor(self.telnetCluster.settings_dict["color-table"]))

                                if search_in_diplom_rules_flag == 1:
                                    self.telnetCluster.tableWidget.item(lastRow, 2).setBackground(color)

                                self.telnetCluster.tableWidget.setItem(lastRow, 3,
                                                                       QTableWidgetItem(cleanList[int(settingsDict['telnet-freq-position'])]))
                                self.telnetCluster.tableWidget.item(lastRow, 3).setForeground(QColor(self.telnetCluster.settings_dict["color-table"]))

                                if search_in_diplom_rules_flag == 1:
                                    self.telnetCluster.tableWidget.item(lastRow, 3).setBackground(color)


                            self.telnetCluster.tableWidget.setItem(lastRow, 4,
                                                                   QTableWidgetItem(
                                                                      output_data.decode(settingsDict['encodeStandart'])))

                            self.telnetCluster.tableWidget.item(lastRow, 4).setForeground(
                                QColor(self.telnetCluster.settings_dict["color-table"]))

                            if search_in_diplom_rules_flag == 1:
                                 self.telnetCluster.tableWidget.item(lastRow, 4).setBackground(color)


                            self.telnetCluster.tableWidget.scrollToBottom()

                            if settingsDict['spot-to-pan'] == 'enable':
                                freq = std.std().std_freq(freq=cleanList[3])
                                try:
                                    tci.Tci_sender(settingsDict['tci-server']+":"+settingsDict['tci-port']).set_spot(cleanList[4], freq, color="19711680")
                                except:
                                    print("clusterThread: Except in Tci_sender.set_spot")
                            self.telnetCluster.tableWidget.resizeColumnsToContents()
                            self.telnetCluster.tableWidget.resizeRowsToContents()
                        ####
                    # #print(output_data) # Check point - output input-string with data from cluster telnet-server
                    elif output_data[0:3].decode(settingsDict['encodeStandart']) == "WWV":
                        self.telnetCluster.labelIonosphereStat.setText(
                            "Ionosphere status: " + output_data.decode(settingsDict['encodeStandart']))
                        #print("Ionosphere status: ", output_data.decode(settingsDict['encodeStandart']))
                    del cleanList[0:len(cleanList)]
                    time.sleep(0.3)

          except:
              continue

class telnetCluster(QWidget):

    def __init__(self):
        super().__init__()
        # self.mainwindow = mainwindow

        self.host = settingsDict['telnet-host']
        self.port = settingsDict['telnet-port']
        self.call = settingsDict['my-call']
        self.tableWidget = QTableWidget()
        self.allRows = 0
        self.settings_dict = settingsDict

        self.initUI()

    def initUI(self):
        '''
         Design of cluster window

        '''

        self.setGeometry(int(settingsDict['telnet-cluster-window-left']), int(settingsDict['telnet-cluster-window-top']),
                         int(settingsDict['telnet-cluster-window-width']), int(settingsDict['telnet-cluster-window-height']))
        self.setWindowTitle('Telnet cluster')
        self.setWindowIcon(QIcon('logo.png'))
        self.setWindowOpacity(float(settingsDict['clusterWindow-opacity']))
        style = "background-color:" + settingsDict['background-color'] + "; color:" + settingsDict[
            'color'] + ";"
        self.setStyleSheet(style)
        self.labelIonosphereStat = QLabel()
        self.labelIonosphereStat.setStyleSheet("font: 12px;")
        style_table = "background-color:" + settingsDict['form-background'] + "; color:" + settingsDict[
            'color-table'] + "; font: 12px;  gridline-color: " + settingsDict['solid-color'] + ";"
        self.tableWidget.setStyleSheet(style_table)
        fnt = self.tableWidget.font()
        fnt.setPointSize(9)
        self.tableWidget.setFont(fnt)
        self.tableWidget.setRowCount(0)
        #self.tableWidget.horizontalHeader().setStyleSheet("font: 12px;")
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["Time Loc", "Time GMT", "Call", "Freq", " Spot"])
        self.tableWidget.verticalHeader().hide()
        #self.tableWidget.resizeColumnsToContents()
        self.tableWidget.cellClicked.connect(self.click_to_spot)
        #self.tableWidget.resizeColumnsToContents()
        #self.tableWidget.move(0, 0)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.labelIonosphereStat)
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)

        # logForm.test('test')

        self.start_cluster()

    def stop_cluster(self):

        print("stop_cluster:", self.run_cluster.terminate())

    def start_cluster(self):
        self.run_cluster = clusterThread(cluster_window=self, form_window=logForm)
        self.run_cluster.start()

    def click_to_spot(self):
        row = self.tableWidget.currentItem().row()
        freq = self.tableWidget.item(row, 3).text()
        call = self.tableWidget.item(row, 2).text()
        self.isearch = internetworker.internetWorker(window=internetSearch, callsign=call, settings=settingsDict)
        self.isearch.start()
        freq = std.std().std_freq(freq)
        band = std.std().get_std_band(freq)
        mode = std.std().mode_band_plan(band, freq)
        #print("band:_>", band)
        #print("mode:_>", mode)
        #print("freq:_>", freq)

        logForm.set_freq(freq)
        logForm.set_call(call=call)
        logForm.activateWindow()

        if settingsDict['tci'] == 'enable':
            try:
                tci.Tci_sender(settingsDict['tci-server'] + ":" + settingsDict['tci-port']).set_freq(freq)
                if mode != 'ERROR':
                    tci.Tci_sender(settingsDict['tci-server'] + ":" + settingsDict['tci-port']).set_mode('0',mode)

            except:
                print("Set_freq_cluster: Can't connection to server:", settingsDict['tci-server'], ":",
                      settingsDict['tci-port'], "freq:_>", freq)

        if settingsDict['cat'] == 'enable':
            logForm.cat_system.sender_cat(freq=freq, mode=freq)

    def cluster_filter(self, cleanList):
        flag = False
        if len(cleanList) >= 4:
            #print("cluster_filter: len(cleanList)", len(cleanList))
            #print("cluster_filter: inputlist", cleanList)
            #print("cluster_filter: call", cleanList[4])
            #print("cluster_filter: prefix", cleanList[4][0:2])
            if settingsDict['cluster-filter'] == 'enable':
                ### filtering by spot prefix
                filter_by_band = False
                filter_by_spotter_flag = False
                filter_by_prefix_flag = False

                if settingsDict['filter-by-prefix'] == 'enable':
                    list_prefix_spot=settingsDict['filter-prefix'].split(',')
                    if cleanList[4][0:2] in list_prefix_spot:
                        filter_by_prefix_flag = True
                else:
                    filter_by_prefix_flag = True
                ### filtering by prefix spotter
                if settingsDict['filter-by-prefix-spotter'] == "enable":
                    list_prefix_spotter=settingsDict['filter-prefix-spotter'].split(',')
                    if cleanList[2][0:2] in list_prefix_spotter:
                        filter_by_spotter_flag = True
                else:
                    filter_by_spotter_flag = True
                ### filtering by band
                if settingsDict['filter_by_band'] == "enable":
                    list_prefix_spotter = settingsDict['list-by-band'].split(',')
                    freq = std.std().std_freq(cleanList[3])
                    band = std.std().get_std_band(freq)
                    if band in list_prefix_spotter:
                        filter_by_band = True
                else:
                    filter_by_band = True
                #print("cluster_filter: filter_by_prefix_flag:",filter_by_prefix_flag,
                      #"\nfilter_by_spotter_flag:",filter_by_spotter_flag,"\nfilter_by_band", filter_by_band)
                if filter_by_prefix_flag and filter_by_spotter_flag and filter_by_band:
                    flag = True
                else:
                    flag = False


            else:
                flag = True
        return flag

    def changeEvent(self, event):

        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.isMinimized():
                settingsDict['telnet-cluster-window'] = 'false'
                print("telnet-cluster-window: changeEvent:_>", settingsDict['telnet-cluster-window'])
                    #telnetCluster.showMinimized()
            elif self.isVisible():
                settingsDict['telnet-cluster-window'] = 'true'
                print("telnet-cluster-window: changeEvent:_>", settingsDict['telnet-cluster-window'])

            QWidget.changeEvent(self, event)

    def refresh_interface(self):

        self.update_color_schemes()

    def update_color_schemes(self):
        style = "background-color:" + settingsDict['background-color'] + "; color:" + \
                settingsDict['color'] + ";"
        self.labelIonosphereStat.setStyleSheet(style)
        style_form = "background-color:" + settingsDict['form-background'] + "; color:" + settingsDict[
            'color-table'] + "; font: 12px;  gridline-color: " + settingsDict['solid-color'] + ";"
        self.tableWidget.setStyleSheet(style_form)
        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()
        for row in range(rows):
            for col in range(cols):
                self.tableWidget.item(row, col).setForeground(QColor(settingsDict['color-table']))

        self.setStyleSheet(style)

class internetSearch(QWidget):

    def __init__(self):
        super().__init__()
        self.labelImage = QLabel(self)
        #self.pixmap=""
        self.initUI()

    def initUI(self):
        hbox = QHBoxLayout(self)
        self.pixmap = QPixmap("logo.png")
        self.labelImage = QLabel(self)
        self.labelImage.setAlignment(Qt.AlignCenter)
        self.labelImage.setPixmap(self.pixmap)
        hbox.addWidget(self.labelImage)
        self.setLayout(hbox)

        #self.move(100, 200)
        self.setGeometry(int(settingsDict['search-internet-left']),
                         int(settingsDict['search-internet-top']),
                         int(settingsDict['search-internet-width']),
                         int(settingsDict['search-internet-height']))
        self.setWindowTitle('Telnet cluster')
        self.setWindowIcon(QIcon('logo.png'))
        self.setWindowTitle('Image from internet')
        self.setWindowOpacity(float(settingsDict['searchInetWindow-opacity']))
        style = "QWidget{background-color:" + settingsDict['background-color'] + "; color:" + settingsDict[
            'color'] + ";}"
        self.setStyleSheet(style)
        #self.show()

    def changeEvent(self, event):

        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.isMinimized():
                settingsDict['search-internet-window'] = 'false'
                print("search-internet-window: changeEvent:_>", settingsDict['search-internet-window'])
                    #telnetCluster.showMinimized()
            elif self.isVisible():
                settingsDict['search-internet-window'] = 'true'
                print("search-internet-window: changeEvent:_>", settingsDict['search-internet-window'])

            QWidget.changeEvent(self, event)

    def update_photo(self):
        pixmap = QPixmap("logo.png")

        #self.labelImage.setFixedWidth(self.settings['image-width'])
        self.labelImage.setPixmap(pixmap)

    def refresh_interface(self):
        self.update_color_schemes()

    def update_color_schemes(self):
        style = "background-color:" + settingsDict['background-color'] + "; color:" + \
                settingsDict['color'] + ";"
        self.labelImage.setStyleSheet(style)
        self.setStyleSheet(style)

class hello_window(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        width_coordinate = (desktop.width()/2) - 200
        height_coordinate = (desktop.height()/2) - 125
        print("hello_window: ", desktop.width(), width_coordinate)

        self.setGeometry(round(width_coordinate), round(height_coordinate), 400, 250)
        self.setWindowIcon(QIcon('logo.png'))
        self.setWindowTitle('Welcome to LinLog')
        style = "background-color:" + settingsDict['background-color'] + "; color:" + settingsDict[
            'color'] + ";"
        self.setStyleSheet(style)
        style_caption = "background-color:" + settingsDict['background-color'] + "; color:" + settingsDict[
            'color'] + "; font-size: 36px;"
        self.caption_label = QLabel("Hi friend")
        self.caption_label.setStyleSheet(style_caption)
        style_text = "background-color:" + settingsDict['background-color'] + "; color:" + settingsDict[
            'color'] + "; font-size: 12px;"
        self.welcome_text_label = QLabel("It's first runing.\nPlease enter you callsign")
        self.welcome_text_label.setStyleSheet(style_text)
        self.call_input = QLineEdit()
        self.call_input.setStyleSheet("QWidget{background-color:" + settingsDict['form-background'] + "; color:" + settingsDict[
            'color-table'] + ";}")
        self.call_input.setFixedWidth(150)
        self.ok_button = QPushButton("GO")
        self.ok_button.clicked.connect(self.ok_button_push)
        #self.caption_label.setAlignment(Qt.AlignCenter)
        vbox = QVBoxLayout()
        vbox.addWidget(self.caption_label)
        vbox.addWidget(self.welcome_text_label)
        vbox.addWidget(self.call_input)
        vbox.addWidget(self.ok_button)
        vbox.setAlignment(Qt.AlignCenter)

        self.setLayout(vbox)
        self.show()

    def ok_button_push(self):
        if self.call_input.text().strip() != "":
            settingsDict['my-call'] = self.call_input.text().strip().upper()
            settings_file.save_all_settings(self, settingsDict)
            hello_window.close()
            subprocess.call(["python3", "main.py"])
            #subprocess.call("./main")
            #app.exit()




        else:
            self.welcome_text_label.setText("Please enter you callsign")
        print ("Ok_button")

class settings_file:


    def save_all_settings(self, settingsDict):
        print ("save_all_settings", settingsDict)
        filename = 'settings.cfg'
        with open(filename, 'r') as f:
            old_data = f.readlines()
        for index, line in enumerate(old_data):
            key_from_line = line.split('=')[0]
            # print ("key_from_line:",key_from_line)
            for key in settingsDict:

                if key_from_line == key:
                    # print("key",key , "line", line)
                    old_data[index] = key + "=" + settingsDict[key] + "\n"

        with open(filename, 'w') as f:
            f.writelines(old_data)
        print("Save_and_Exit_button: ", old_data)

class Test(QObject):

    def __init__(self):
        super().__init__()

    def test(self):
        pass


if __name__ == '__main__':
    #test = Test()
    #test.test()

    APP_VERSION = '1.262'
    settingsDict = {}
    file = open('settings.cfg', "r")
    for configstring in file:
        if configstring != '' and configstring != ' ' and configstring[0] != '#':
            configstring = configstring.strip()
            configstring = configstring.replace("\r", "")
            configstring = configstring.replace("\n", "")
            splitString = configstring.split('=')
            settingsDict.update({splitString[0]: splitString[1]})

    file.close()
    global All_records
    All_records = []

    #print(settingsDict)
    flag = 1

    app = QApplication(sys.argv)
    signal_complited = Communicate()

    if settingsDict['my-call'] == "":
        hello_window = hello_window()

    else:

        logWindow = log_Window()
        logSearch = logSearch()
        internetSearch = internetSearch()
        logForm = logForm()
        telnetCluster = telnetCluster()
        tci_recv = tci.tci_connect(settingsDict, log_form=logForm)
        
        adi_file = Adi_file()
        about_window = About_window("LinuxLog", "Version: "+APP_VERSION+"<br><a href='http://linixlog.su'>http://linixlog.su</a><br>Baston Sergey<br>UR4LGA<br>bastonsv@gmail.com")
        new_diploma = ext.Diplom_form(settingsDict=settingsDict, log_form=logForm, adi_file=adi_file)

        if settingsDict['log-window'] == 'true':
           logWindow.show()

        if settingsDict['log-search-window'] == 'true':
            logSearch.show()

        if settingsDict['search-internet-window'] == 'true':
            internetSearch.show()

        if settingsDict['log-form-window'] == 'true':
            logForm.show()

        if settingsDict['telnet-cluster-window'] == 'true':
            telnetCluster.show()

        if settingsDict['cat'] == 'enable':
            #logForm.start_cat()
            pass

        if settingsDict['tci'] == 'enable':

            tci_recv.start_tci(settingsDict["tci-server"], settingsDict["tci-port"])



    sys.exit(app.exec_())
