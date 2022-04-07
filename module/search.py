import re, json, time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from urllib.request import quote

from module.config import getConfig
from module.tools import getJson, writeJson, getStatus
from module.DbUtils import searchSQL

config = getConfig()
tmpData = getJson('./data/searchData.json')

def searchModule(keywords: str) -> None or list:
    '''
    获取搜索结果
    
    keywords: 搜索关键词
    '''
    # with open('./module/searchMap.json', 'r', encoding='utf-8') as r:
    #     data = json.load(r)
    # r.close()
    # keywords = keywords.replace('.', '\\.')
    # out = {}
    
    # for i in data:
    #     for ii in data[i]:
    #         results = re.match(keywords, ii, re.I|re.X)
    #         if (results != None) or (keywords in ii.replace('.', '\\.')):
    #             out[ii]={
    #                 'tag': i,
    #                 'url': data[i][ii]
    #             }
    out = searchSQL(keywords)
    if out == {}:
        return None
    else:
        statusData = getStatus() #获取status
        tmp = {}
        for i in out:
            outHTML = '<b>['+out[i]['tag']+'] '+i+'</b>\n\n'
            for ii in out[i]['url']:
                status = ''
                if ii in statusData:
                    status = statusData[ii][1]
                outHTML = outHTML+'<a href="'+quote(out[i]['url'][ii], safe='#;/?:@&=+$,', encoding='utf-8')+'">'+ii+'</a> '+status+'\n'
            tmp[i] = {
                'tag': '['+out[i]['tag']+'] ',
                'html': outHTML
            }
        tmpName = []
        for i in tmp:
            tmpName.append(i)
        
        length = [int(len(tmp)/10), len(tmp)-(10*(int(len(tmp)/10)))]
        counterNum = 1
        data = []
        if (length[0] > 1) or (length[0] == 1 and length[1] > 0):
            while counterNum <= length[0]:
                data.append([])
                for i in tmpName[((counterNum-1)*10):(counterNum*10)]:
                    data[counterNum-1].append({
                        'name': i,
                        'tag': tmp[i]['tag'],
                        'html': tmp[i]['html']
                    })
                counterNum=counterNum+1
            if length[1] != 0:
                data.append([])
                for i in tmpName[length[0]*10:length[0]*10+length[1]]:
                    data[length[0]].append({
                        'name': i,
                        'tag': tmp[i]['tag'],
                        'html': tmp[i]['html']
                    })
        else:
            data.append([])
            for i in tmp:
                data[0].append({
                    'name': i,
                    'tag': tmp[i]['tag'],
                    'html': tmp[i]['html']
                })
        return [data, str(len(tmpName))]

def search(update: Update, context: CallbackContext):
    '''
    搜索
    '''
    chatID = update.message.chat_id
    messageID = update.message.message_id
    if len(context.args) != 0:
        keywords = '' #搜索关键词
        tmpNum = 0
        while tmpNum < len(context.args):
            keywords += context.args[tmpNum]
            if tmpNum+1 != len(context.args):
                keywords += ' '
            tmpNum += 1
        
        searchResults = searchModule(keywords) #搜索结果
        if searchResults == None:
            context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.from_user['name']+'\n未搜索到相关视频',
                                     disable_notification=True, reply_to_message_id=messageID, allow_sending_without_reply=True)
        else:
            [out, all] = searchResults
            keyboard = []
            for i in out[0]:
                keyboard.append([InlineKeyboardButton(i['tag']+' '+i['name'], callback_data='0_'+str(out[0].index(i)))])
            if len(out) != 1:
                keyboard.append([InlineKeyboardButton('下一页(2)', callback_data='1_menu')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            messageID = update.message.reply_text(text='🔍查询归档站视频\n共 '+all+' 个结果 | 1/'+str(len(out))+' 页\n'+update.message.from_user['name']+' 请点击选择',
                                                  reply_markup=reply_markup, disable_notification=True,
                                                  reply_to_message_id=messageID, allow_sending_without_reply=True)['message_id']
            '''
            "charID_messageID": {
                "time": 1649279212.5807855, 时间戳
                "all": 2, 总数
                "page": 1, 页数
                "data": [
                    [{ 第一页
                        "name": 名称,
                        "tag": 标签,
                        "html": HTML
                    }, ...],
                    [第二页]
                ]
            }
            '''
            tmpData[str(chatID)+'_'+str(messageID)] = {
                'time': time.time(), #Time
                'all': all, #总数
                'page': str(len(out)), #页数
                'data': out #数据
            }
            writeJson('./data/searchData.json', tmpData)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.from_user['name']+'\n格式: /search <关键词>',
                                 disable_notification=True, reply_to_message_id=messageID, allow_sending_without_reply=True)

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
    searchData = tmpData[str(chatID)+'_'+str(messageID)] #搜索数据
    data = (query.data).split('_') #callback_data
    
    query.answer()
    if data[1] == 'menu': #前往指定页数
        all = searchData['all'] #结果总数
        page = searchData['page'] #结果页数
        menuData = searchData['data'][int(data[0])] #当前菜单数据
        
        keyboard = []
        #添加视频按钮
        for i in menuData:
            keyboard.append([InlineKeyboardButton(i['tag']+' '+i['name'], callback_data=str(int(data[0]))+'_'+str(menuData.index(i)))])
        #添加上一页下一页按钮
        if int(all) > 10:
            if int(data[0]) == 0: #第一页
                keyboard.append([InlineKeyboardButton('下一页('+str(int(data[0])+2)+')', callback_data=str(int(data[0])+1)+'_menu')])
            elif int(data[0]) == int(page)-1: #最后一页
                keyboard.append([InlineKeyboardButton('上一页('+str(int(data[0]))+')', callback_data=str(int(data[0])-1)+'_menu')])
            else:
                keyboard.append([InlineKeyboardButton('上一页('+str(int(data[0]))+')', callback_data=str(int(data[0])-1)+'_menu'),
                                InlineKeyboardButton('下一页('+str(int(data[0])+2)+')', callback_data=str(int(data[0])+1)+'_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text='🔍查询归档站视频\n共 '+all+' 个结果 | '+str(int(data[0])+1)+'/'+page+' 页\n'+fromUserName+' 请点击选择',
                                parse_mode='HTML', disable_web_page_preview=True, reply_markup=reply_markup)
    else: #归档站信息
        infoDataHTML = searchData['data'][int(data[0])][int(data[1])]['html'] #归档站信息HTML
        
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("返回", callback_data=data[0]+'_menu')]])
        query.edit_message_text(text=fromUserName+'\n'+infoDataHTML, parse_mode='HTML',
                                disable_web_page_preview=True, reply_markup=reply_markup)
