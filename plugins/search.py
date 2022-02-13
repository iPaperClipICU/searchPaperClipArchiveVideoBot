import re, json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from urllib.request import quote
from .getConfig import getConfig

CONFIG = getConfig()

def searchModule(keywords):
    with open(CONFIG['SearchMapPath'], 'r', encoding='utf-8') as r:
        data = json.load(r)
    r.close()
    keywords = keywords.replace('.', '\\.')
    out = {}
    map = []
    
    for i in data['map']:
        results = re.match(keywords, data['map'][i], re.I|re.X)
        if (results != None) or (keywords in data['map'][i].replace('.', '\\.')):
            map.append(i)
    del data['map']
    if len(map) != 0:
        for i in map:
            for ii in data[i]:
                results = re.match(keywords, ii, re.I|re.X)
                if (results != None) or (keywords in ii.replace('.', '\\.')):
                    out[ii]={
                        'tag': i,
                        'url': data[i][ii]
                    }
    else:
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
        return tmp

def search(update: Update, context: CallbackContext):
    keyboard = []
    messageID = update.message.message_id
    if len(context.args) == 1:
        keywords = context.args[0]
        out = searchModule(keywords)
        if out == None:
            context.bot.send_message(chat_id=update.effective_chat.id, text='未搜索到相关视频', disable_notification=True,
                                     reply_to_message_id=messageID, allow_sending_without_reply=True)
        else:
            for i in out:
                keyboard.append([InlineKeyboardButton(out[i]['tag']+i, callback_data=i)])
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(update.message.from_user['name']+'\n查询到 '+str(len(out))+' 个结果，请点击选择',
                                      reply_markup=reply_markup, disable_notification=True,
                                      reply_to_message_id=messageID, allow_sending_without_reply=True)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='格式: /search <keywords>', disable_notification=True,
                                 reply_to_message_id=messageID, allow_sending_without_reply=True)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    out = searchModule(query.data)
    query.edit_message_text(text=query.from_user['name']+'\n'+out[query.data]['html'], parse_mode='HTML', disable_web_page_preview=True)
