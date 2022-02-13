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
        'SearchMapPath': tmp['SearchMapPath'],
        'Father': int(tmp['Father']),
        'Debug': DEBUG
    }
    return CONFIG
