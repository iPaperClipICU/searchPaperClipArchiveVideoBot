import json, pymysql

from module.config import getConfig

config = getConfig()

def openConn() -> None:
    '''
    新建数据库连接
    '''
    global conn
    global cursor

    conn = pymysql.connect(
        host = config.SQL['host'],
        user = config.SQL['user'],
        password = config.SQL['password'],
        db = config.SQL['db'],
        charset=config.SQL['charset']
    )
    cursor = conn.cursor()
def closeConn() -> None:
    '''
    关闭数据库连接
    '''
    cursor.close()
    conn.commit()
    conn.close()

def searchSQL(keyword: str) -> None or json:
    '''
    通过关键字查询数据库
    
    keyword: 关键字
    '''
    openConn()
    sql = '''
    SELECT
        t.tag,
        i.`name`,
        i.WanderingPaperClip,
        i.PaperClipTK,
        i.iPaperClipICU,
        i.Telegram 
    FROM
        info i
        JOIN tag t ON i.tagNum = t.tagNum 
    WHERE
        NAME LIKE "%'''+keyword+'''%";
    '''
    rows = cursor.execute(sql) #执行sql语句
    data = cursor.fetchall() #获取查询结果
    closeConn()
    
    outJson = {}
    for i in data:
        [tag, name, WanderingPaperClip, PaperClipTK, iPaperClipICU, Telegram] = i
        outJson[name] = {
            'tag': tag,
            'url': {}
        }
        if WanderingPaperClip != None:
            outJson[name]['url']['Wandering PaperClip 流浪回形针'] = WanderingPaperClip
        if PaperClipTK != None:
            outJson[name]['url']['回形针归档站|paperclip.tk'] = PaperClipTK
        if iPaperClipICU != None:
            outJson[name]['url']['回形针重症监护室'] = iPaperClipICU
        if Telegram != None:
            outJson[name]['url']['Telegram@PaperClipCN'] = Telegram
    return outJson

def updateStatusSQL(name: str, status: int) -> None:
    '''
    更新数据库 status
    
    name: name
    status: status
    '''
    openConn()
    sql = '''
    UPDATE STATUS 
    	SET STATUS = '''+str(status)+''' 
    WHERE
    	NAME = "'''+name+'''"
    '''
    rows = cursor.execute(sql)
    closeConn()
def getStatusSQL(name: str) -> int:
    '''
    获取数据库 status
    
    name: name
    '''
    openConn()
    sql = 'SELECT status FROM status WHERE name = "'+name+'";'
    rows = cursor.execute(sql) #执行sql语句
    data = cursor.fetchall() #获取查询结果
    return data[0][0]
