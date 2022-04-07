import json, requests

from module.DbUtils import updateStatusSQL, getStatusSQL
from module.config import getConfig

config = getConfig()

def getJson(path: str) -> json:
    '''
    获取json文件
    
    path: json文件路径
    '''
    with open(path, 'rb') as f:
        data = json.load(f)
    f.close()
    return data
def writeJson(path: str, data: json):
    '''
    写入json文件
    
    path: json文件路径
    data: json数据
    '''
    with open(path, 'w') as r:
        json.dump(data, r)
    r.close()

def getStatus() -> json:
    '''
    从数据库获取status
    '''
    UptimeRobotApiKey = config.UptimeRobotApiKey
    UptimeRobotID = config.UptimeRobotID
    outJson = {}
    statusColor = {
        '0': '⬜️',
        '1': '⬜️',
        '2': '🟩',
        '8': '🟧',
        '9': '🟥'
    }
    
    for i in UptimeRobotID:
        parameter = {
            'api_key': UptimeRobotApiKey,
            'monitors': UptimeRobotID[i]
        }
        reqData = requests.post('https://api.uptimerobot.com/v2/getMonitors', parameter)
        status = 0
        if reqData.status_code == 200:
            status = int(reqData.json()['monitors'][0]['status'])
            updateStatusSQL(i, status)
        else:
            status = getStatusSQL(i)
        outJson[i] = [status, statusColor[str(status)]]
    
    return outJson
