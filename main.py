import logging, time, base64
from telegram import Update, ChatPermissions, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    InlineQueryHandler
)
from plugins.checkImage import checkPhoto, checkImage
from plugins.search import search, button
from plugins.tools import getConfig

# Config
CONFIG = getConfig()
TOKEN = CONFIG['Token']
CHATGROUP = CONFIG['ChatGroup']
LOGSGROUP = CONFIG['LogsGroup']
FATHER = CONFIG['Father']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Github: https://github.com/iPaperClipICU/paperClipReviewBot', disable_web_page_preview=True)

def ping(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='pong')

def fuck(update: Update, context: CallbackContext, permissions=ChatPermissions):
    command = update.message.text.split()
    if command[0] == '/fuck':
        command.remove('/fuck')
        context.bot.send_message(chat_id=update.effective_chat.id, text='读取到fuck')
        fromUser = update.message.from_user
        status = context.bot.getChatMember(chat_id=update.effective_chat.id, user_id=fromUser['id']).status
        if (status in ['administrator', 'creator']) or (fromUser['id'] == FATHER):
            if command[0] == 'del' and len(command) == 2:
                #转发消息到Log
                context.bot.forward_message(chat_id=LOGSGROUP, from_chat_id=update.effective_chat.id, message_id=update.message.reply_to_message.message_id)
                #删除消息
                update.message.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.reply_to_message.message_id)
                #发送Log
                logOut = update.message.from_user.name+' 删除了一条 '+update.message.reply_to_message.from_user.name+' 发送的消息\n原因: '+command[1]
                context.bot.send_message(chat_id=LOGSGROUP, text=logOut)
                context.bot.send_message(chat_id=update.effective_chat.id, text=logOut)
            elif command[0] == 'ban' and len(command) == 3:
                banTime = int(command[1])
                if banTime < 30 or banTime > 31622400: banTime = 1
                update.message.bot.restrict_chat_member(chat_id=update.effective_chat.id, user_id=update.message.reply_to_message.from_user.id,
                                                        until_date=(time.time()+banTime), permissions=permissions(can_send_messages=False))
                if banTime == 1: logOut = '时长: 永久'
                else: logOut = '时长: '+str(banTime)+' 秒'
                logOut = update.message.from_user.name+' 禁言了 '+update.message.reply_to_message.from_user.name+'\n'+logOut+'\n原因: '+command[2]
                context.bot.send_message(chat_id=LOGSGROUP, text=logOut)
                context.bot.send_message(chat_id=update.effective_chat.id, text=logOut)
            elif command[0] == 'fuck' and len(command) == 3:
                context.bot.send_message(chat_id=update.effective_chat.id, text='读取到fuckfuck')
                #转发消息到Log
                context.bot.forward_message(chat_id=LOGSGROUP, from_chat_id=update.effective_chat.id, message_id=update.message.reply_to_message.message_id)
                #删除消息
                update.message.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.reply_to_message.message_id)
                #禁言
                banTime = int(command[1])
                if banTime < 30 or banTime > 31622400: banTime = 1
                update.message.bot.restrict_chat_member(chat_id=update.effective_chat.id, user_id=update.message.reply_to_message.from_user.id,
                                                        until_date=(time.time()+banTime), permissions=permissions(can_send_messages=False))
                #发送Log
                if banTime == 1: logOut = '\n时长: 永久'
                else: logOut = '\n时长: '+str(banTime)+' 秒'
                logOut = '\n'+update.message.from_user.name+' 删除了一条 '+update.message.reply_to_message.from_user.name+' 发送的消息' +\
                         '\n'+update.message.from_user.name+' 禁言了 '+update.message.reply_to_message.from_user.name +\
                         logOut +\
                         '\n原因: '+command[2]
                context.bot.send_message(chat_id=LOGSGROUP, text=logOut)
                context.bot.send_message(chat_id=update.effective_chat.id, text=logOut)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text='格式错误\n/fuck del <原因>\n/fuck ban <时长> <原因>\n/fuck fuck <原因>', reply_to_message_id=update.message.message_id)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='你没有权限使用/fuck，禁言30s', reply_to_message_id=update.message.message_id)
            update.message.bot.restrict_chat_member(chat_id=CHATGROUP, user_id=fromUser['id'], until_date=(time.time()+31), permissions=permissions(can_send_messages=False))
    
def how(update: Update, context: CallbackContext):
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(
        InlineQueryResultArticle(
            id=str(time.time())+'-Baidu-'+query,
            title='Baidu',
            hide_url=True,
            input_message_content=InputTextMessageContent('https://ipaperclip.icu/baidu/?q='+base64.b64encode(query.encode()).decode())
        ),
    )
    results.append(
        InlineQueryResultArticle(
            id=str(time.time())+'-Bing-'+query,
            title='Bing',
            hide_url=True,
            input_message_content=InputTextMessageContent('https://ipaperclip.icu/bing/?q='+base64.b64encode(query.encode()).decode())
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('ping', ping))
    dispatcher.add_handler(MessageHandler(Filters.reply & Filters.command & Filters.chat(CHATGROUP), fuck))
    dispatcher.add_handler(InlineQueryHandler(how))
    dispatcher.add_handler(CommandHandler('search', search))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler((Filters.document.file_extension('png') | Filters.document.file_extension('jpg') | Filters.document.file_extension('jpeg') | Filters.document.file_extension('bmp') | Filters.document.file_extension('gif') | Filters.document.file_extension('webp')) & (~Filters.command) & Filters.chat(CHATGROUP), checkImage))
    dispatcher.add_handler(MessageHandler(Filters.photo & (~Filters.command) & Filters.chat(CHATGROUP), checkPhoto))
    
    updater.start_polling()

    updater.idle()

if __name__ == '__main__': main()
