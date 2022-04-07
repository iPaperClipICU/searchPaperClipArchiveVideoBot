import json

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
