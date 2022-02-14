import re, json, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from urllib.request import quote
from .tools import getConfig, getJson, writeJson

CONFIG = getConfig()
SEARCHDATAPATH = CONFIG['searchDataPath']
tmpData = getJson(SEARCHDATAPATH)

def searchModule(keywords):
    with open(CONFIG['SearchMapPath'], 'r', encoding='utf-8') as r:
        data = json.load(r)
    r.close()
    keywords = keywords.replace('.', '\\.')
    out = {}
    
    for i in data:
        for ii in data[i]:
            results = re.match(keywords, ii, re.I|re.X)
            if (results != None) or (keywords in ii.replace('.', '\\.')):
                out[ii]={
                    'tag': i,
                    'url': data[i][ii]
                }
    if len(out) == 0:
        return None
    else:
        tmp = {}
        for i in out:
            outHTML = '<b>['+out[i]['tag']+'] '+i+'</b>\n\n'
            for ii in out[i]['url']:
                outHTML = outHTML+'<a href="'+quote(out[i]['url'][ii], safe='#;/?:@&=+$,', encoding='utf-8')+'">'+ii+'</a>\n'
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
    chatID = update.message.chat_id
    messageID = update.message.message_id
    if len(context.args) != 0:
        keywords = ''
        for i in context.args: keywords=keywords+i
        out = searchModule(keywords)
        all = out[1]
        out = out[0]
        if out == None:
            context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.from_user['name']+'\n未搜索到相关视频',
                                     disable_notification=True, reply_to_message_id=messageID, allow_sending_without_reply=True)
        else:
            keyboard = []
            for i in out[0]:
                keyboard.append([InlineKeyboardButton(i['tag']+' '+i['name'], callback_data='0_'+str(out[0].index(i)))])
            if len(out) != 1:
                keyboard.append([InlineKeyboardButton('下一页(2)', callback_data='0_next')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            messageID = update.message.reply_text(text='🔍查询归档站视频\n共 '+all+' 个结果 | 1/'+str(len(out))+' 页\n'+update.message.from_user['name']+' 请点击选择',
                                      reply_markup=reply_markup, disable_notification=True,
                                      reply_to_message_id=messageID, allow_sending_without_reply=True)['message_id']
            tmpData[str(chatID)+'_'+str(messageID)] = {
                'time': time.time(),
                'all': all,
                'page': str(len(out)),
                'data': out
            }
            writeJson(SEARCHDATAPATH, tmpData)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='格式: /search <关键词>', disable_notification=True,
                                 reply_to_message_id=messageID, allow_sending_without_reply=True)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    chatID = query.message.chat_id
    messageID = query.message.message_id
    data = query.data
    data = [(re.search('.+_', data))[0].replace('_', ''), (re.search('_.+', data))[0].replace('_', '')]
    
    if data[1] == 'previous':
        tmp = tmpData[str(chatID)+'_'+str(messageID)]
        all = tmp['all']
        page = tmp['page']
        tmp = tmp['data'][int(data[0])-1]
        
        keyboard = []
        for i in tmp:
            keyboard.append([InlineKeyboardButton(i['tag']+' '+i['name'], callback_data=str(int(data[0])-1)+'_'+str(tmp.index(i)))])
        if int(data[0])-1 == 0:
            keyboard.append([InlineKeyboardButton('下一页('+str(int(data[0])+1)+')', callback_data=str(int(data[0])-1)+'_next')])
        else:
            keyboard.append([InlineKeyboardButton('上一页('+str(int(data[0])-1)+')', callback_data=str(int(data[0])-1)+'_previous'),
                        InlineKeyboardButton('下一页('+str(int(data[0])+1)+')', callback_data=str(int(data[0])-1)+'_next')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.answer()
        query.edit_message_text(text='🔍查询归档站视频\n共 '+all+' 个结果 | '+str(int(data[0]))+'/'+page+' 页\n'+query.from_user['name']+' 请点击选择',
                                parse_mode='HTML', disable_web_page_preview=True, reply_markup=reply_markup)
    elif data[1] == 'next':
        tmp = tmpData[str(chatID)+'_'+str(messageID)]
        all = tmp['all']
        page = tmp['page']
        tmp = tmp['data'][int(data[0])+1]
        
        keyboard = []
        for i in tmp:
            keyboard.append([InlineKeyboardButton(i['tag']+' '+i['name'], callback_data=str(int(data[0])+1)+'_'+str(tmp.index(i)))])
        if int(data[0])+2 == int(page):
            keyboard.append([InlineKeyboardButton('上一页('+str(int(data[0])+1)+')', callback_data=str(int(data[0])+1)+'_previous')])
        else:
            keyboard.append([InlineKeyboardButton('上一页('+str(int(data[0])+1)+')', callback_data=str(int(data[0])+1)+'_previous'),
                            InlineKeyboardButton('下一页('+str(int(data[0])+3)+')', callback_data=str(int(data[0])+1)+'_next')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.answer()
        query.edit_message_text(text='🔍查询归档站视频\n共 '+all+' 个结果 | '+str(int(data[0])+2)+'/'+page+' 页\n'+query.from_user['name']+' 请点击选择',
                                parse_mode='HTML', disable_web_page_preview=True, reply_markup=reply_markup)
    elif data[1] == 'back':
        tmp = tmpData[str(chatID)+'_'+str(messageID)]
        all = tmp['all']
        page = tmp['page']
        tmp = tmp['data'][int(data[0])]
        
        keyboard = []
        for i in tmp:
            keyboard.append([InlineKeyboardButton(i['tag']+' '+i['name'], callback_data=str(int(data[0]))+'_'+str(tmp.index(i)))])
        if int(all) > 10:
            if int(data[0]) == 0:
                keyboard.append([InlineKeyboardButton('下一页('+str(int(data[0])+2)+')', callback_data=str(int(data[0]))+'_next')])
            elif int(data[0]) == int(page)-1:
                keyboard.append([InlineKeyboardButton('上一页('+str(int(data[0]))+')', callback_data=str(int(data[0]))+'_previous')])
            else:
                keyboard.append([InlineKeyboardButton('上一页('+str(int(data[0]))+')', callback_data=str(int(data[0]))+'_previous'),
                                InlineKeyboardButton('下一页('+str(int(data[0])+2)+')', callback_data=str(int(data[0]))+'_next')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.answer()
        query.edit_message_text(text='🔍查询归档站视频\n共 '+all+' 个结果 | '+str(int(data[0])+1)+'/'+page+' 页\n'+query.from_user['name']+' 请点击选择',
                                parse_mode='HTML', disable_web_page_preview=True, reply_markup=reply_markup)
    else:
        tmp = tmpData[str(chatID)+'_'+str(messageID)]['data'][int(data[0])][int(data[1])]
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("返回", callback_data=data[0]+'_back')]])
        query.answer()
        query.edit_message_text(text=query.from_user['name']+'\n'+tmp['html'], parse_mode='HTML', disable_web_page_preview=True, reply_markup=reply_markup)
