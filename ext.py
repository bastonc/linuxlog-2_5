#!/usr/bin/python3
# -*- coding: utf-8 -*-
import parse
import json
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
        with open(self.file_rules, "r") as f:
            self.decode_data = json.load(f)

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





