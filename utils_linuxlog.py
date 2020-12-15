import sys
import json
import pymysql
import random
import datetime
from pymysql.cursors import DictCursor
from time import gmtime, strftime



def reset_country_file(country_dict={}):
    if country_dict == {}:
        country_dict = {
            'Ukraine': {'prefix': ['UR', 'UT', 'UX', 'EM', 'EN'],
                        'itu': '29',
                        'cq-zone': '16'},
            'Botswana': {'prefix': ['A2'],
                         'itu': '57',
                         'cq-zone': '38'},
            'Tonga Isl.': {'prefix': ['A3'],
                           'itu': '62',
                           'cq-zone': '32'},
            'Oman & Muscat': {'prefix': ['A4'],
                              'itu': '39',
                              'cq-zone': '21'},
            'Bhutan': {'prefix': ['A5'],
                       'itu': '41',
                       'cq-zone': '22'},
            'UAE': {'prefix': ['A6'],
                    'itu': '39',
                    'cq-zone': '21'},
            'Qatar': {'prefix': ['A7'],
                      'itu': '39',
                      'cq-zone': '21'},
            'Bahrain': {'prefix': ['A9'],
                        'itu': '39',
                        'cq-zone': '21'},
            'Pakistan': {'prefix': ['AP', 'AS'],
                         'itu': '41',
                         'cq-zone': '21'},
            'Scarb. Reef': {'prefix': ['BS7'],
                            'itu': '50',
                            'cq-zone': '27'},
            'Taiwan': {'prefix': ['BV'],
                       'itu': '44',
                       'cq-zone': '24'},
            'Pratas': {'prefix': ['BV9P'],
                       'itu': '44',
                       'cq-zone': '24'},
            'China': {'prefix': ['BX', 'BZ'],
                      'itu': '42, 43, 44',
                      'cq-zone': '23, 24'},
            'Rep.of Nauru': {'prefix': ['C2'],
                             'itu': '65',
                             'cq-zone': '31'},
            'Andorra': {'prefix': ['C3'],
                        'itu': '27',
                        'cq-zone': '14'},
            'Gambia': {'prefix': ['C5'],
                       'itu': '46',
                       'cq-zone': '35'},
            'Bahamas': {'prefix': ['C6'],
                        'itu': '11',
                        'cq-zone': '08'},
            'Mozambique': {'prefix': ['C9'],
                           'itu': '53',
                           'cq-zone': '37'},
            'Chili': {'prefix': ['CE'],
                      'itu': '14,15,16',
                      'cq-zone': '12'},
            'Antarctica': {'prefix': ['CE9', 'KC4'],
                           'itu': '73',
                           'cq-zone': '13'},
            'Cuba': {'prefix': ['CM', 'CO'],
                     'itu': '11',
                     'cq-zone': '08'},
            'Morocco': {'prefix': ['CN'],
                        'itu': '37',
                        'cq-zone': '33'},
            'Gambia': {'prefix': ['C5'],
                       'itu': '46',
                       'cq-zone': '35'},
            'Bolivia': {'prefix': ['CP'],
                        'itu': '12,13,14',
                        'cq-zone': '12'},
        }

    with open(settingsDict['country-file'], 'w') as f:
        json.dump(country_dict, f)

def csv_to_json_country(csv_file):
    """
    need CSV file with format:
                    "pfx,pfx;country;cq-zone;itu"
    :return: convert CSV to JSON and create file and settingsDict['country-file']
    """
    with open(csv_file, 'r') as f:
        lines = f.readlines()

    object_to_json = {}
    for line in lines:
        prefix_list_clean = []
        data_list = line.split(';')
        #print("Data_list", data_list)
        prefix_list_dark = data_list[0].split(',')
        for elem in prefix_list_dark:
            elem_clean = elem.strip()
            prefix_list_clean.append(elem_clean)
        country = data_list[1]
        cq_zone = data_list[2]
        itu = data_list[3]
        object_to_json.update({
            country: {'prefix':prefix_list_clean,
                      'itu': itu,
                      'cq-zone': cq_zone
                      }
        })

    reset_country_file(object_to_json)
    #print("Full Object", object_to_json)

def delete_all_qso(table_name):

    connection = pymysql.connect(
        host=settingsDict['db-host'],
        user=settingsDict['db-user'],
        password=settingsDict['db-pass'],
        db=settingsDict['db-name'],
        charset=settingsDict['db-charset'],
        cursorclass=DictCursor
    )
    query = "DELETE FROM "+str(table_name[0])
    result = connection.cursor().execute(query)
    connection.commit()
    print("Result clear operation for", table_name, ":", result)

def generate_adif(count, name_file):
    if count.isdigit():
        strings_list = []
        for i in range(int(count)):
            laters_list = ['A', 'B', 'C', 'D', 'E', 'F',
                           'G', 'H', 'I', 'K', 'L', 'M',
                           'N', 'O', 'P', 'Q', 'R', 'S',
                           'T', 'V', 'X', 'Y', 'Z']
            digit_list =['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
            char_1 = random.choice(laters_list)
            char_2 = random.choice(laters_list)
            random_digit = random.choice(digit_list)
            char_3 = random.choice(laters_list)
            char_4 = random.choice(laters_list)
            char_5 = random.choice(laters_list)
            call = char_1+char_2+str(random_digit)+char_3+char_4+char_5
            date_dirty = str(datetime.date.today())
            #print(date_dirty)
            date_qso = date_dirty.replace('-','')
            time_qso = str(strftime("%H%M%S", gmtime()))
            freq = "21170000"

            recordObject = {
                'QSO_DATE': date_qso,
                'TIME_ON': time_qso,
                'FREQ': freq,
                'CALL': call,
                'MODE': "SSB",
                'RST_RCVD': "59",
                'RST_SENT': "59",
                'NAME': "Nam",
                'QTH': "qth",
                'OPERATOR': settingsDict['my-call'],
                'BAND': "15M",
                'COMMENT': "comment",
                'TIME_OFF': time_qso,
                'COUNTRY': "country",
                'ITUZ': "29",
                'EQSL_QSL_SENT': 'N',
                'CLUBLOG_QSO_UPLOAD_STATUS': 'N', }



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
                    len(recordObject['COMMENT'])) + ">" + recordObject[
                                       'COMMENT'] + "<TIME_OFF:" + str(len(recordObject['TIME_OFF'])) + ">" + recordObject[
                                      'TIME_OFF'] + "<EQSL_QSL_SENT:" + str(len(recordObject['EQSL_QSL_SENT'])) + ">" + str(
                    recordObject['EQSL_QSL_SENT']) + \
                                 "<CLUBLOG_QSO_UPLOAD_STATUS:" + str(
                    len(recordObject['CLUBLOG_QSO_UPLOAD_STATUS'])) + ">" + str(
                    recordObject['CLUBLOG_QSO_UPLOAD_STATUS']) + "<EOR>\n"
            #print(stringToAdiFile)
            strings_list.append(stringToAdiFile)

            date = datetime.datetime.now()
            header_string = "ADIF from LinuxLog Generator ADIF v.0.1 \n"
            header_string += "Copyright 2019-" + str(date.year) + "  Baston V. Sergey\n"
            header_string += "Header generated on " + str(datetime.datetime.now()) + " by " + settingsDict['my-call'] + "\n"
            header_string += "File output restricted to QSOs by : All Operators - All Bands - All Modes \n"
            header_string += "<PROGRAMID:8>LinuxLog\n"
            header_string += "<PROGRAMVERSION:" + str(len("0.1")) + ">" + "0.1\n"
            header_string += "<EOH>\n\n"
        with open(name_file, "w") as f:
            f.write(header_string)
            f.writelines(strings_list)

parameter = sys.argv[1]
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

print (parameter)
if parameter == 'reset-country':
    reset_country_file()
if parameter == 'csv-country':
    if sys.argv[2] != '':
        csv_to_json_country(sys.argv[2])
if parameter == 'clear-log':
    if sys.argv[2] != '':
        delete_all_qso(str(sys.argv[2]).split())
    else:
        print("Incorrect name table \nUse utils_linuxlog.py --clear-log <name table>")
if parameter == 'generate-adif':
    if sys.argv[2] != '' and sys.argv[2].isdigit():
        if sys.argv[3] != '':
            generate_adif(sys.argv[2],sys.argv[3])
        else:
            print("No output filename ")
    else:
        print("No 'count' or 'count' not digit")

if parameter == 'help':
    print("RESET COUNTRY")
    print("Command: python3 utils_linuxlog.py reset-country")
    print("Create file with counrty file in json format.\nUse for testing")

    print("CSV COUNTRY")
    print("Command: python3 utils_linuxlog.py csv-country <csv-file.csv>")
    print("Convert csv file with country to JSON country file.\nUse for testing")

    print("CLEAR LOG")
    print("Command: python3 utils_linuxlog.py clear-log YOU-CALL")
    print("Delete all records (QSO) from mysql base.")

    print("GENERATE ADIF")
    print("Command: python3 utils_linuxlog.py generate-adif count name-output-file")
    print("count - digit how many records generate\n"
          "Generate random QSO in ADIF file (name-output-file)")