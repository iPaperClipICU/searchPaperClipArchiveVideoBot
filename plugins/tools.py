import json
from configobj import ConfigObj

def getConfig():
    tmp = ConfigObj('./config.ini', encoding='UTF-8')['Config']
    if tmp['Debug'] in ['True', 'true']: DEBUG = True
    else: DEBUG = False
    CONFIG = {
        'Token': tmp['Token'],
        'SecretID': tmp['SecretID'],
        'SecretKEY': tmp['SecretKEY'],
        'ChatGroup': int(tmp['ChatGroup']),
        'LogsGroup': int(tmp['LogsGroup']),
        'DataPath': tmp['DataPath'],
        'searchDataPath': tmp['searchDataPath'],
        'SearchMapPath': tmp['SearchMapPath'],
        'Father': int(tmp['Father']),
        'Debug': DEBUG
    }
    return CONFIG

def getJson(path):
    with open(path, 'rb') as f:
        data = json.load(f)
    f.close()
    return data

def writeJson(path, data):
    with open(path, 'w') as r:
        json.dump(data, r)
    r.close()
