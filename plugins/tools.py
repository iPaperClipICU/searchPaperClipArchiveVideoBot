import json
from configobj import ConfigObj

def getConfig():
    # 获取Config
    tmp = ConfigObj('./config.ini', encoding='UTF-8')['Config']
    if tmp['Debug'] in ['True', 'true']: DEBUG = True
    else: DEBUG = False
    
    # 获取 uptimeRobotConfig
    ttmp = ConfigObj('./config.ini', encoding='UTF-8')['uptimeRobotConfig']
    uptimeRobotConfig = {}
    for i in ttmp:
        uptimeRobotConfig[i] = str(i)
    
    CONFIG = {
        'Token': tmp['Token'],
        'SecretID': tmp['SecretID'],
        'SecretKEY': tmp['SecretKEY'],
        'ChatGroup': int(tmp['ChatGroup']),
        'LogsGroup': int(tmp['LogsGroup']),
        'uptimeRobotConfig': uptimeRobotConfig,
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
