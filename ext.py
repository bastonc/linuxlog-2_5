#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QWidget, QTableWidget, QPushButton,QCalendarWidget, QLayout, QHBoxLayout, QLineEdit, QVBoxLayout, QLabel, QCheckBox, QTableWidgetItem, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import settings
import parse
import json
import main
class test:
    def __init__(self):
        list = [ { "call":
                     "EH8URT",
                 "score": "10"},
                 {"call": "Z81D",
                 "score": "10"},
                 {"call": "Z81D",
                  "score": "10"},
                 {"call": "VP8PJ",
                  "score": "10"},
                 {"call": "VP8LP",
                  "score": "10"}


                ]
        with open("rules.json", 'w') as f:
            f.write(json.dumps(list))
        print("json.dumps", json.dumps(list))

class Diplom_form(QWidget):

    def __init__(self, settingsDict, diplomname=''):
        super().__init__()
        print ("Diplom_form(QWidget) init_")
        self.diplomname = diplomname
        self.settingsDict = settingsDict
        self.initUI()


    def initUI(self):
        if self.diplomname == '':
            self.setWindowTitle("Create diplom")
        else:
            self.setWindowTitle("Edit diplom")
            rules = diplom.get_rules(self.diplomname)
        self.setGeometry(300, 500, 500, 300)
        #self.setFixedWidth(450)
        #self.setFixedHeight(450)
        self.setWindowIcon(QIcon('logo.png'))
        style = "QWidget{background-color:" + self.settingsDict['background-color'] + "; color:" + self.settingsDict[
            'color'] + ";}"
        styleform = "background :" + self.settingsDict['form-background'] + "; font-weight: 200;"
        self.setGeometry(int(self.settingsDict['log-form-window-left']), int(self.settingsDict['log-form-window-top']),
                         int(self.settingsDict['log-form-window-width']), int(self.settingsDict['log-form-window-height']))

        self.setStyleSheet(style)
        self.name_layout = QHBoxLayout()
        self.name_label = QLabel("Name diploma:")
        self.name_label.setFixedWidth(150)
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(styleform)
        self.name_input.setFixedWidth(200)
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_input)
        self.name_layout.addStretch(300)
        #
        self.date_layout = QHBoxLayout()
        self.start_end_date = QVBoxLayout()
        self.start_date_input = QLineEdit()
        self.start_date_input.setFixedWidth(80)
        self.end_date_input = QLineEdit()
        self.end_date_input.setFixedWidth(80)
        self.start_end_date.addWidget(self.start_date_input)
        self.start_end_date.addWidget(self.end_date_input)
        self.date_checkbox = QCheckBox()
        self. date_checkbox.setText("Enable Date in diplom")
        self.date_layout.addLayout(self.start_end_date)
        self.date_layout.addWidget(self.date_checkbox)
        #
        self.score_layout = QHBoxLayout()
        score_text = QLabel("How many points do you need")
        score_text.setStyleSheet(style)
        self.score_input = QLineEdit()
        self.score_input.setText("0")
        self.score_layout.addWidget(score_text)
        self.score_layout.addWidget(self.score_input)
        #
        self.repeat_layout = QHBoxLayout()
        self.text_repeat = QLabel("Repeats:")
        self.repeat_combo = QComboBox()
        self.repeat_combo.setFixedWidth(200)
        self.repeat_combo.addItems(["resolved other bands", "resolved others mod", "resolving other mods and bands", "not resolving"])
        self.repeat_layout.addWidget(self.text_repeat)
        self.repeat_layout.addWidget(self.repeat_combo)
        self.repeat_layout.addStretch(100)
        #
        self.sps_layout = QHBoxLayout()
        self.prefix_check_box = QCheckBox()
        self.prefix_check_box.setText("Use only \n prefix")
        self.sps_text = QLabel("Special calls \n or prefix:")
        self.sps_table_widget = QTableWidget()
        self.sps_table_widget.setStyleSheet(styleform)
        self.sps_table_widget.setFixedWidth(240)
        self. sps_table_widget.setFixedHeight(200)
        self.sps_table_widget.setColumnCount(2)
        #self.sps_table_widget.setColumnWidth(1, 1)
        self.sps_table_widget.setRowCount(10)
        self.sps_table_widget.setHorizontalHeaderLabels(['call', 'scores'])
        self.sps_table_widget.horizontalHeaderItem(0).setToolTip("Enter special call")
        self.sps_table_widget.horizontalHeaderItem(1).setToolTip("Enter scores for QSO")
        add_row = QPushButton("Add rows")
        add_row.clicked.connect(self.add_row)
        self.prefix_lay = QVBoxLayout()
        self.prefix_lay.addWidget(self.prefix_check_box)
        self.prefix_lay.addWidget(self.sps_text)
        self.sps_layout.addLayout(self.prefix_lay)
        self.sps_layout.addWidget(self.sps_table_widget)
        self.sps_layout.addWidget(add_row)
        #
        self.button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.ok_button = QPushButton("Create diploma")
        self.ok_button.clicked.connect(self.save_diplom)
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.ok_button)

        self.global_layout = QVBoxLayout()
        self.global_layout.addLayout(self.name_layout)
        self.global_layout.addLayout(self.date_layout)
        self.global_layout.addLayout(self.score_layout)
        self.global_layout.addLayout(self.repeat_layout)
        self.global_layout.addLayout(self.sps_layout)
        self.global_layout.addLayout(self.button_layout)
        self.setLayout(self.global_layout)

    def add_row(self):

        self.sps_table_widget.insertRow(self.sps_table_widget.rowCount())
        #pass

    def save_diplom(self):
        list_to_json = []
        if self.name_input.text().strip() != '':
            name_programm = self.name_input.text().strip()
            score_complite = self.score_input.text().strip()
            if self.date_checkbox.isChecked():
                date_enable = "y"
                date_start = self.start_date_input.text().strip()
                date_finish = self.end_date_input.text().strip()

            else:
                date_enable = "n"
                date_start = ""
                date_finish = ""
            repeats = self.repeat_combo.currentIndex()
            count_sps = self.sps_table_widget.rowCount()
            for row in range(count_sps):

                if self.sps_table_widget.item(row,0) != None:
                    print('Item content call', self.sps_table_widget.item(row, 0).text())
                    list_to_json.append({'call': self.sps_table_widget.item(row, 0).text(),
                                      'score': self.sps_table_widget.item(row, 1).text(),
                                      'name': name_programm, 'date_e': date_enable,
                                      'date_start':date_start, 'date_finish': date_finish,
                                      'repeats':repeats, 'score_complite': score_complite})
            self.write_rules_to_file(list_to_json, name_output_file=name_programm)
            settings_list = json.loads(self.settingsDict['diploms-json'])
           # print("settings list", settings_list)
            for i in range(len(settings_list)):

                #name = str(settings_list[i]['name_programm'])
                if name_programm == str(settings_list[i]['name_programm']):
                    pass
                else:
                    settings_list.append({'name_programm':name_programm})
                    self.settingsDict['diploms-json'] = json.dumps(settings_list)
                    main.Settings_file.update_file_to_disk(self)
            #print("self.settingsDict['diploms-json']",self.settingsDict['diploms-json'])
            print("Summary list to JSON", list_to_json)
        else:
            self.name_input.setStyleSheet("border: 2px solid #DD5555;")
    def write_rules_to_file(self, data_to_json, name_output_file):
        filename = str(name_output_file).strip()+'.rules'
        with open(filename, 'w') as f:
            f.write(json.dumps(data_to_json))


class diplom:
    '''
    This class work with extended functions for diplom module
    '''
    def __init__(self, file, file_rules):
        self.file = file
        self.file_rules = file_rules
        self.allCollumn = ['records_number', 'QSO_DATE', 'TIME_ON', 'BAND', 'CALL', 'MODE', 'RST_RCVD', 'RST_SENT',
                           'NAME', 'QTH', 'COMMENTS', 'TIME_OFF', 'eQSL_QSL_RCVD']
        self.allRecord = parse.getAllRecord(self.allCollumn, self.file)
        #print("diplom:", self.allRecord)
        self.decode_data = self.get_rules(self.file_rules)

    def get_rules(self, name):
        with open(name, "r") as f:
             return json.load(f)

    def filter (self, call):
        self.call = call
        for i in range(len(self.decode_data)):
            #print("decode in filter", i, " - ", self.decode_data[i])
            if self.call == self.decode_data[i]['call']:
                return True

        return False

    def add_qso(self, list_data):
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
        print("List_data", list_data)
        index = len(list_data)
        with open(self.file, 'a') as file:


                stringToAdiFile = "<BAND:" + str(len(list_data['BAND'])) + ">" + list_data['BAND'] + "<CALL:" + \
                                  str(len(list_data['CALL'])) + ">"

                stringToAdiFile = stringToAdiFile + list_data['CALL'] + "<FREQ:" + str(
                    len(list_data['FREQ'])) + ">" + \
                                  list_data['FREQ']
                stringToAdiFile = stringToAdiFile + "<MODE:" + str(len(list_data['MODE'])) + ">" + list_data[
                    'MODE'] + "<OPERATOR:" + str(len(list_data['OPERATOR']))
                stringToAdiFile = stringToAdiFile + ">" + list_data['OPERATOR'] + "<QSO_DATE:" + str(
                    len(list_data['QSO_DATE'])) + ">"
                stringToAdiFile = stringToAdiFile + list_data['QSO_DATE'] + "<TIME_ON:" + str(
                    len(list_data['TIME_ON'])) + ">"
                stringToAdiFile = stringToAdiFile + list_data['TIME_ON'] + "<RST_RCVD:" + \
                                  str(len(list_data['RST_RCVD'])) + ">" + list_data['RST_RCVD']
                stringToAdiFile = stringToAdiFile + "<RST_SENT:" + str(len(list_data['RST_SENT'])) + ">" + \
                                  list_data['RST_SENT'] + "<NAME:" + str(len(list_data['NAME'])) + ">" + \
                                  list_data['NAME'] + \
                                  "<QTH:" + str(len(list_data['QTH'])) + ">" + list_data['QTH'] + "<COMMENTS:" + \
                                  str(len(list_data['COMMENTS'])) + ">" + list_data['COMMENTS'] + "<TIME_OFF:" + \
                                  str(len(list_data['TIME_OFF'])) + ">" + list_data[
                                      'TIME_OFF'] + "<eQSL_QSL_RCVD:1>Y<EOR>\n"
                file.write(stringToAdiFile)

    def get_count_qso(self):
        return len(self.allRecord)

    def get_all_qso(self):
        return self.allRecord







