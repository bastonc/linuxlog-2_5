from PyQt6.QtWidgets import QMessageBox, QLineEdit, QWidget, QLabel, QPushButton, \
    QVBoxLayout, QApplication
from PyQt6 import QtCore

class std:
    def __init__(self):
        self.band_rules = {}
        file = open("bandplan.cfg", "r")
        for rules_in_band in file:
            if rules_in_band != '' and rules_in_band != ' ' and rules_in_band[0] != '#':
                rulesstring = rules_in_band.strip()
                rulesstring = rules_in_band.replace("\r", "")
                rulesstring = rules_in_band.replace("\n", "")
                splitString = rulesstring.split('=')
                self.band_rules.update({splitString[0]: splitString[1]})
        file.close()

    def mode_band_plan(self, band, freq):
        try:
            if int(self.band_rules["start-cw"+band]) < int(freq) <= int(self.band_rules["end-cw"+band]):
                mode = "CW"
            elif int(self.band_rules["start-ssb"+band]) < int(freq) <= int(self.band_rules["end-ssb"+band]):
                if int(band) < 40:
                    mode = "USB"
                else:
                    mode = "LSB"
            elif int(self.band_rules["start-digi"+band]) < int(freq) <= int(self.band_rules["end-digi"+band]):
                if int(band) < 40:
                    mode = ("DIGU", "PKTUSB")
                else:
                    mode = ("DIGL", "PKTLSB")
            else:
                mode = "ERROR"
        except Exception:
            mode = "ERROR"
        return mode


    def get_index_column(self, tableWidget_qso):

        index_columns = {}
        for i in range(tableWidget_qso.columnCount()):
            column = tableWidget_qso.horizontalHeaderItem(i).text()
            if column == 'id':
                index_columns.update({'id': i})
            if column == 'QSO_DATE':
                index_columns.update({'QSO_DATE': i})
            if column == 'TIME_ON':
                index_columns.update({'TIME_ON': i})
            if column == 'CALL':
                index_columns.update({'CALL': i})
            if column == 'RST_RCVD':
                index_columns.update({'RST_RCVD': i})
            if column == 'RST_SENT':
                index_columns.update({'RST_SENT': i})
            if column == 'NAME':
                index_columns.update({'NAME': i})
            if column == 'QTH':
                index_columns.update({'QTH': i})
            if column == 'BAND':
                index_columns.update({'BAND': i})
            if column == 'COMMENT':
                index_columns.update({'COMMENT': i})
            if column == 'TIME_OFF':
                index_columns.update({'TIME_OFF': i})
            if column == 'EQSL_QSL_SENT':
                index_columns.update({'EQSL_QSL_SENT': i})
            if column == 'MODE':
                index_columns.update({'MODE': i})
            if column == 'CLUBLOG_QSO_UPLOAD_STATUS':
                index_columns.update({'CLUBLOG_QSO_UPLOAD_STATUS': i})

        return index_columns

    def get_std_band(self, freq):  # get Band in m
        band ="GEN"
        if int(freq) >= 1800000 and int(freq) <= 2000000:
            band = '160'
        if int(freq) >= 3500000 and int(freq) <= 3800000:
            band = '80'
        if int(freq) >= 7000000 and int(freq) <= 7200000:
            band = '40'
        if int(freq) >= 10100000 and int(freq) <= 10150000:
            band = '30'
        if int(freq) >= 14000000 and int(freq) <= 14500000:
            band = '20'
        if int(freq) >= 18068000 and int(freq) <= 18168000:
            band = '17'
        if int(freq) >= 21000000 and int(freq) <= 21450000:
            band = '15'
        if int(freq) >= 24890000 and int(freq) <= 24990000:
            band = '12'
        if int(freq) >= 28000000 and int(freq) <= 29700000:
            band = '10'
        if int(freq) >= 28000000 and int(freq) <= 29700000:
            band = '10'
        if int(freq) >= 50000000 and int(freq) <= 54000000:
            band = '6'
        if int(freq) >= 144000000 and int(freq) <= 146500000:
            band = '2'
        return band

    def std_freq(self, freq):   # get format freq in Hz (Ex.14000000)
        freq = freq.replace('.', '')
        len_freq = len(freq)
        if len_freq < 8 and len_freq <= 5:
            while len_freq < 7:
                freq += "0"
                len_freq = len(freq)
            freq = "0" + freq
        if len(freq) < 8 and len(freq) > 5 and len(freq) != 7:
            while len_freq < 8:
                freq += "0"
                len_freq = len(freq)
        if len(freq) == 7 and int(freq) > 1000000:
            freq += "00"

        return freq

    def message(self, detail_text, text_short):
        message = QMessageBox()
        message.setGeometry(500, 300, 1000, 500)
        message.setWindowTitle("Information")
        message.setText(text_short)
        message.setInformativeText(detail_text)
        message.setStandardButtons(QMessageBox.StandardButton.Ok)
        message.exec()

    def std_time(self, string_time):
        time_formated = string_time
        time_split = time_formated.split(":")
        time_string = ""
        for digit in time_split:
            if len(digit) < 2:
                digit_new = "0" + digit
            else:
                digit_new = digit
            time_string += digit_new
        return time_string
    def adi_time_to_std_time(self, adi_time):
        if len(adi_time) == 4:
            time = adi_time[:2] + ":" + adi_time[2:4] + ":00"
        else:
            time = adi_time[:2] + ":" + adi_time[2:4] + ":" + adi_time[4:]
        return time

    def adi_date_to_std_date(self, adi_date):
        date = adi_date[:4] + "-" + adi_date[4:6] + "-" + adi_date[6:]
        return date

    def adi_time_add_seconds(self, adi_time):
        if len(adi_time) == 4:
            return adi_time + "00"
        return adi_time
class wnd_what(QWidget):
    ok = QtCore.pyqtSignal(str)
    def __init__(self, header_text):
        super(wnd_what, self).__init__()
        self.header_text = header_text
        self.initUI()

    def initUI(self):
        desktop = QApplication.primaryScreen().availableGeometry()
        width_coordinate = (desktop.width() / 2 - 75)
        height_coordinate = (desktop.height() / 2) - 40
        self.setGeometry(round(width_coordinate), round(height_coordinate), 300, 80)
        self.setFixedWidth(170)
        self.setFixedHeight(90)
        self.label = QLabel(str(self.header_text))
        self.input_line = QLineEdit()
        self.input_line.setFixedWidth(150)
        self.input_line.setFixedHeight(25)
        self.button_ok = QPushButton("Save")
        self.button_ok.setFixedWidth(50)
        self.button_ok.setFixedHeight(20)
        self.button_ok.clicked.connect(self.out_data)
        self.v_box = QVBoxLayout()
        self.v_box.totalHeightForWidth(100)
        self.v_box.addWidget(self.label)
        self.v_box.addWidget(self.input_line)
        self.v_box.addWidget(self.button_ok)
        self.setLayout(self.v_box)
        self.show()
    def out_data(self):
        if self.input_line.text().strip() != '':
            self.ok.emit(self.input_line.text().strip())
            self.close()
            return self.input_line.text().strip()
