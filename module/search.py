import re, json, time, requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from urllib.request import quote

from module.config import getConfig
from module.tools import getJson, writeJson

config = getConfig()

searchData = getJson('./data/searchData.json')
searchMap = getJson('./data/searchMap.json')
statusData = getJson('./data/statusData.json')
statusColor = {
    '0': '⬜️',
    '1': '⬜️',
    '2': '🟩',
    '8': '🟧',
    '9': '🟥'
}

class results:
    def __init__(self):
        self.results = []
    
    def addResult(self, tag: str, name: str, urls: json):
        '''
        添加搜索结果
        
        tag: 标签
        name: 名称
        urls: urls
        '''
        self.results.append({
            'tag': tag,
            'name': name,
            'urls': urls
        })
    
    def addHTML(self, name, html):
        '''
        添加html
        '''
        for result in self.results:
            if result['name'] == name:
                result['html'] = html
                break
    
    def delUrls(self):
        '''
        删除 urls
        '''
        for result in self.results:
            del result['urls']
    
    def ok(self):
        '''
        搜索完成
        '''
        self.isEmpty = len(self.results) == 0 #是否为空
        self.resultsNum = len(self.results) #结果数量
        self.pagesNum = int(self.resultsNum/(config.pageMax+1))+1 #页数
        
        self.nameList = []
        for result in self.results:
            self.nameList.append(result['name'])
    
    def getResults(self, name):
        '''
        获取搜索结果
        '''
        tag = ''
        urls = {}
        for result in self.results:
            if result['name'] == name:
                tag = result['tag']
                urls = result['urls']
                break
        return [tag, urls]

def updateStatusData():
    '''
    更新status数据
    '''
    UptimeRobotApiKey = config.UptimeRobotApiKey
    UptimeRobotID = config.UptimeRobotID
    
    for i in UptimeRobotID:
        parameter = {
            'api_key': UptimeRobotApiKey,
            'monitors': UptimeRobotID[i]
        }
        reqData = requests.post('https://api.uptimerobot.com/v2/getMonitors', parameter)
        status = 0
        if reqData.status_code == 200:
            status = int(reqData.json()['monitors'][0]['status'])
        else:
            status = statusData(i)
        statusData[i] = status
    writeJson('./data/statusData.json', statusData)

def searchModule(keyword: str) -> None or results:
    '''
    获取搜索结果
    
    keywords: 搜索关键词
    '''
    rss = results()
    
    for tag in searchMap:
        for name in searchMap[tag]:
            if re.findall(keyword, name, re.I|re.X) != []:
                rss.addResult(tag, name, searchMap[tag][name])
    rss.ok()
    if rss.isEmpty:
        return None
    else:
        # 生成html
        updateStatusData() #更新status数据
        for name in rss.nameList:
            [tag, urls] = rss.getResults(name)
            
            outHTML = '<b>['+tag+'] '+name+'</b>\n\n'
            for urlName in urls:
                url = urls[urlName]
                status = ''
                if urlName in statusData:
                    status = statusColor[str(statusData[urlName])]
                outHTML += '<a href="'+quote(url, safe='#;/?:@&=+$,', encoding='utf-8')+'">'+urlName+'</a> '+status+'\n'
            rss.addHTML(name, outHTML)
        rss.delUrls()
        
        '''
        pages结构
        [
            [ 第一页
                [ 第一项
                    'tag': tag,
                    'name': name,
                    'html': html
                ], [...], ...
            ], [...], ...
        ]
        '''
        # 结果分页
        pages = []
        tmpNum = 1
        tmpPagesNum = 1
        while tmpPagesNum <= rss.pagesNum:
            page = []
            while (tmpNum <= rss.resultsNum) and (tmpNum <= tmpPagesNum*config.pageMax):
                page.append(rss.results[tmpNum-1])
                tmpNum += 1
            
            pages.append(page)
            tmpNum = (tmpPagesNum*config.pageMax)+1
            tmpPagesNum += 1
        rss.results = pages
        
        return rss

def search(update: Update, context: CallbackContext):
    '''
    搜索
    '''
    chatID = update.message.chat_id
    messageID = update.message.message_id
    if len(context.args) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.from_user['name']+'\n格式: /search <关键词>',
                                 disable_notification=True, reply_to_message_id=messageID, allow_sending_without_reply=True)
    else:
        keyword = '' #搜索关键词
        tmpNum = 0
        while tmpNum < len(context.args):
            keyword += context.args[tmpNum]
            if tmpNum+1 != len(context.args):
                keyword += ' '
            tmpNum += 1
        
        rss = searchModule(keyword) #搜索结果
        if rss == None:
            context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.from_user['name']+'\n未搜索到相关视频',
                                     disable_notification=True, reply_to_message_id=messageID, allow_sending_without_reply=True)
        else:
            keyboard = []
            for i in rss.results[0]:
                keyboard.append([InlineKeyboardButton('['+i['tag']+'] '+i['name'], callback_data='0_'+str(rss.results[0].index(i)))])
            if rss.pagesNum != 1:
                keyboard.append([InlineKeyboardButton('下一页(2)', callback_data='1_menu')])
            messageID = update.message.reply_text(text='🔍查询归档站视频\n共 '+str(rss.resultsNum)+' 个结果 | 1/'+str(rss.pagesNum)+' 页\n'+update.message.from_user['name']+' 请点击选择',
                                                  reply_markup=InlineKeyboardMarkup(keyboard), disable_notification=True,
                                                  reply_to_message_id=messageID, allow_sending_without_reply=True)['message_id']
            '''
            "charID_messageID": {
                "time": 1649279212.5807855, 时间戳
                "resultsNum": 2, 总数
                "pagesNum": 1, 页数
                "results": [
                    [{ 第一页
                        "name": 名称,
                        "tag": 标签,
                        "html": HTML
                    }, ...],
                    [第二页]
                ]
            }
            '''
            searchData[str(chatID)+'_'+str(messageID)] = {
                'time': time.time(), #Time
                'resultsNum': rss.resultsNum, #总数
                'pagesNum': rss.pagesNum, #页数
                'results': rss.results #数据
            }
            # searchData[str(chatID)+'_'+str(messageID)] = {
            #     'time': time.time(), #Time
            #     'all': all, #总数
            #     'page': str(len(out)), #页数
            #     'data': out #数据
            # }
            writeJson('./data/searchData.json', searchData)

'''
callback_data命名规则:
- 归档站信息: "0_0" 第一页第一个
- 前往指定页数: "0_page" 前往第一页
'''
def button(update: Update, context: CallbackContext):
    '''
    按钮
    '''
    query = update.callback_query
    chatID = query.message.chat_id #聊天ID
    messageID = query.message.message_id #消息ID
    fromUserName = query.from_user['name'] #发送者
    resultsData = searchData[str(chatID)+'_'+str(messageID)] #搜索数据
    data = (query.data).split('_') #callback_data
    
    query.answer()
    if data[1] == 'menu': #前往指定页数
        resultsNum = resultsData['resultsNum'] #结果总数
        pagesNum = resultsData['pagesNum'] #结果页数
        results = resultsData['results'][int(data[0])] #当前菜单数据
        
        keyboard = []
        #添加info按钮
        for i in results:
            keyboard.append([InlineKeyboardButton('['+i['tag']+'] '+i['name'], callback_data=str(int(data[0]))+'_'+str(results.index(i)))])
        #添加上一页下一页按钮
        if resultsNum > config.pageMax:
            if int(data[0]) == 0: #第一页
                keyboard.append([InlineKeyboardButton('下一页('+str(int(data[0])+2)+')', callback_data=str(int(data[0])+1)+'_menu')])
            elif int(data[0]) == pagesNum-1: #最后一页
                keyboard.append([InlineKeyboardButton('上一页('+str(int(data[0]))+')', callback_data=str(int(data[0])-1)+'_menu')])
            else:
                keyboard.append([InlineKeyboardButton('上一页('+str(int(data[0]))+')', callback_data=str(int(data[0])-1)+'_menu'),
                                InlineKeyboardButton('下一页('+str(int(data[0])+2)+')', callback_data=str(int(data[0])+1)+'_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text='🔍查询归档站视频\n共 '+str(resultsNum)+' 个结果 | '+str(int(data[0])+1)+'/'+str(pagesNum)+' 页\n'+fromUserName+' 请点击选择',
                                parse_mode='HTML', disable_web_page_preview=True, reply_markup=reply_markup)
    else: #归档站信息
        infoDataHTML = resultsData['results'][int(data[0])][int(data[1])]['html'] #归档站信息HTML
        
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("返回", callback_data=data[0]+'_menu')]])
        query.edit_message_text(text=fromUserName+'\n'+infoDataHTML, parse_mode='HTML',
                                disable_web_page_preview=True, reply_markup=reply_markup)
