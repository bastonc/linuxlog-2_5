import sys
import json



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