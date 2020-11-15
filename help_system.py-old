import sys
import pymysql
import time
import subprocess
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QLineEdit, QWidget, QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt


class Help(QMainWindow):
    def __init__(self):
        super().__init__()
        #self.key = key
        #self.input_data = input_data
        #if self.key == 'db-error':
        self.help_text_style = "font-size: 12 px;"
        self.initUI()

    def initUI(self):
        #print("I a here")
        self.style_form = "background-color: " + settingsDict['form-background'] + "; color: " + settingsDict[
            'color-table'] + ";"
        desktop = QApplication.desktop()
        width_coordinate = (desktop.width() / 2) - 200
        height_coordinate = (desktop.height() / 2) - 125
        # print("hello_window: ", desktop.width(), width_coordinate)

        self.setGeometry(100, 100, 500, 350)
        self.setWindowIcon(QIcon('logo.png'))
        self.setWindowTitle('Help system |Linux Log')
        style = "background-color:" + settingsDict['background-color'] + "; color:" + settingsDict[
            'color'] + ";"
        self.setStyleSheet(style)
        self.v_Box_Help = QVBoxLayout()
        self.v_Box_Help.setAlignment(Qt.AlignCenter)
        # Caption label
        self.hello_label = QLabel()
        self.hello_label.setText("LinuxLog help")
        self. hello_label.setStyleSheet("font-weight: bold; font-size: 18px;")
        # Help text label
        self.help_text_lay = QHBoxLayout()
        self.help_text = QLabel()
        self.help_text.setStyleSheet(self.help_text_style)
        self.help_text.setText(self.fill_help_text())
        # Help image
        self.help_image  = QPixmap("logo.png")
        scaled_image  = self.help_image.scaled(80, 80, Qt.KeepAspectRatio)
        self.help_image_label = QLabel()
        self.help_image_label.setPixmap(scaled_image)
        self.help_text_lay.addWidget(self.help_image_label)
        self.help_text_lay.addSpacing(10)
        self. help_text_lay.addWidget(self.help_text)
        # help form lay
        self.form_layout = QVBoxLayout()
        self.form_layout.setAlignment(Qt.AlignCenter)
        self.login_db_lay = QHBoxLayout()
        # label Username
        self.login_db_label = QLabel()
        self.login_db_label.setStyleSheet(style)
        self.login_db_label.setText("Username")
        self.login_db_label.setMaximumWidth(60)
        # linedit Username
        self.login_db = QLineEdit()
        self.login_db.setFixedWidth(100)
        self.login_db.setStyleSheet(self.style_form)
        self.login_db.setText(settingsDict['db-user'])
        # password fields
        self.pass_db_lay = QHBoxLayout()
        self.pass_db_label = QLabel()
        self.pass_db_label.setStyleSheet(style)
        self.pass_db_label.setText("Password")
        self.pass_db_label.setMaximumWidth(60)
        self.pass_db = QLineEdit()
        self.pass_db.setFixedWidth(100)
        self.pass_db.setStyleSheet(self.style_form)
        self.pass_db.setText(settingsDict['db-pass'])
        # DataBase fields
        self.base_db_lay = QHBoxLayout()
        self.base_db_label = QLabel()
        self.base_db_label.setStyleSheet(style)
        self.base_db_label.setText("DB Name:")
        self.base_db_label.setMaximumWidth(60)
        self.base_db = QLineEdit()
        self.base_db.setFixedWidth(100)
        self.base_db.setStyleSheet(self.style_form)
        self.base_db.setText(settingsDict['db-name'])
        # Host db fields
        self.host_db_lay = QHBoxLayout()
        self.host_db_label = QLabel()
        self.host_db_label.setStyleSheet(style)
        self.host_db_label.setText("Host DB:")
        self.host_db_label.setMaximumWidth(60)
        self.host_db = QLineEdit()
        self.host_db.setFixedWidth(100)
        self.host_db.setStyleSheet(self.style_form)
        self.host_db.setText(settingsDict['db-host'])

        self.form_button_lay = QHBoxLayout()
        self.form_button_lay.setAlignment(Qt.AlignCenter)
        self.apply_button = QPushButton("Check and Apply")
        self.apply_button.setFixedWidth(150)
        self.apply_button.setFixedHeight(30)
        self.apply_button.clicked.connect(self.check_base)



        self.login_db_lay.addWidget(self.login_db_label)
        self.login_db_lay.addWidget(self.login_db)
        self.pass_db_lay.addWidget(self.pass_db_label)
        self.pass_db_lay.addWidget(self.pass_db)
        self.base_db_lay. addWidget(self.base_db_label)
        self.base_db_lay.addWidget(self.base_db)
        self.host_db_lay.addWidget(self.host_db_label)
        self.host_db_lay.addWidget(self.host_db)
        self.form_button_lay.addWidget(self.apply_button)


        self.form_layout.addLayout(self.login_db_lay)
        self.form_layout.addLayout(self.pass_db_lay)
        self.form_layout.addLayout(self.base_db_lay)
        self.form_layout.addLayout(self.host_db_lay)
        self.form_layout.addLayout(self.form_button_lay)

        self.v_Box_Help.addWidget(self.hello_label)
        self.v_Box_Help.addLayout(self.help_text_lay)
        self.v_Box_Help.addLayout(self.form_layout)
        central_widget = QWidget()
        central_widget.setLayout(self.v_Box_Help)
        self.setCentralWidget(central_widget)
        self.show()

    def check_base(self):

        try:
            connection = pymysql.connect(
                host=self.host_db.text().strip(),
                user=self.login_db.text().strip(),
                password=self.pass_db.text().strip(),
                db=self.base_db.text().strip(),
                charset=settingsDict['db-charset'],
                cursorclass=pymysql.cursors.DictCursor
            )
            connection.close()
            self.update_file_to_disk()
            #time.sleep(1)
            self.close()
            subprocess.call(["python3", "main.py"])
            #
            #exit(0)


        except Exception:
            self.message("<p style='color: red;'>Not Working</p>", "Can't connect to MySQL server \nPlease check data in fileds ")


    def update_file_to_disk(self):
        # self.settingsDict = self
        filename = 'settings.cfg'
        with open(filename, 'r') as f:
            old_data = f.readlines()
        for index, line in enumerate(old_data):
            key_from_line = line.split('=')[0]

            if key_from_line == "db-host":
                    print("key_from_line:", key_from_line)
                    old_data[index] = "db-host="+self.host_db.text().strip() + "\n"
            if key_from_line ==  "db-user":
                old_data[index] = "db-user=" + self.login_db.text().strip() + "\n"
            if key_from_line == "db-pass":
                old_data[index] = "db-pass=" + self.pass_db.text().strip() + "\n"
            if key_from_line == "db-name":
                old_data[index] = "db-name=" + self.base_db.text().strip() + "\n"

        with open(filename, 'w') as f:
            f.writelines(old_data)
        # print("Update_to_disk: ", old_data)
        return True

    def fill_help_text(self, lang='eng'):

        if lang =='eng':
            text = "Hello. I'am help system by LinuxLog.\n" \
                    "You have problem with connected to MySQL database.\n" \
                    "It happens when value in fields incorrect. \n" \
                    "Please check fields bottom.\n\nDATABASE CONNECTION FIELDS"

        return text



    def message(self, caption, text_message):
        message = QMessageBox(self)
        #message.setFixedWidth(350)
        #message.setFixedHeight(200)
        #Geometry(500, 300, 1000, 700)
        message.setWindowTitle("Information")
        message.setText(caption)
        message.setInformativeText(text_message)
        message.setStandardButtons(QMessageBox.Ok)
        message.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
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



    if len(sys.argv) > 1:
        help_w = Help()
        help_w.show()
    sys.exit(app.exec_())