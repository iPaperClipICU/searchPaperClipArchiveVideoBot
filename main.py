import logging, time

from telegram import Update, ChatPermissions
from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler
)

from module.config import getConfig
from module.search import search, button
# from module.checkImage import checkPhoto, checkImage

config = getConfig()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update: Update, context: CallbackContext) -> None:
    '''
    start
    '''
    context.bot.send_message(chat_id=update.effective_chat.id, text='Github: https://github.com/iPaperClipICU/paperClipReviewBot', disable_web_page_preview=True)

def ping(update: Update, context: CallbackContext) -> None:
    '''
    ping
    '''
    context.bot.send_message(chat_id=update.effective_chat.id, text='pong')

def fuck(update: Update, context: CallbackContext, permissions=ChatPermissions) -> None:
    '''
    删除/禁言
    '''
    command = update.message.text.split()
    if command[0] == '/fuck':
        command.remove('/fuck')
        fromUser = update.message.from_user
        status = context.bot.getChatMember(chat_id=update.effective_chat.id, user_id=fromUser['id']).status
        if (status in ['administrator', 'creator']) or (fromUser['id'] == config.father):
            if command[0] == 'del' and len(command) == 2:
                #转发消息到Log
                context.bot.copy_message(chat_id=config.logsGroup, from_chat_id=update.effective_chat.id, message_id=update.message.reply_to_message.message_id)
                #删除消息
                update.message.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.reply_to_message.message_id)
                #发送Log
                logOut = update.message.from_user.name+' 删除了一条 '+update.message.reply_to_message.from_user.name+' 发送的消息\n原因: '+command[1]
                context.bot.send_message(chat_id=config.logsGroup, text=logOut)
                # context.bot.send_message(chat_id=update.effective_chat.id, text=logOut)
            elif command[0] == 'ban' and len(command) == 3:
                banTime = int(command[1])
                if banTime < 30 or banTime > 31622400: banTime = 1
                update.message.bot.restrict_chat_member(chat_id=update.effective_chat.id, user_id=update.message.reply_to_message.from_user.id,
                                                        until_date=(time.time()+banTime), permissions=permissions(can_send_messages=False))
                if banTime == 1: logOut = '时长: 永久'
                else: logOut = '时长: '+str(banTime)+' 秒'
                logOut = update.message.from_user.name+' 禁言了 '+update.message.reply_to_message.from_user.name+'\n'+logOut+'\n原因: '+command[2]
                context.bot.send_message(chat_id=config.logsGroup, text=logOut)
                # context.bot.send_message(chat_id=update.effective_chat.id, text=logOut)
            elif command[0] == 'fuck' and len(command) == 3:
                #转发消息到Log
                context.bot.copy_message(chat_id=config.logsGroup, from_chat_id=update.effective_chat.id, message_id=update.message.reply_to_message.message_id)
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
                context.bot.send_message(chat_id=config.logsGroup, text=logOut)
                # context.bot.send_message(chat_id=update.effective_chat.id, text=logOut)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text='格式错误\n/fuck del <原因>\n/fuck ban <时长> <原因>\n/fuck fuck <原因>', reply_to_message_id=update.message.message_id)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='你没有权限使用/fuck，禁言30s', reply_to_message_id=update.message.message_id)
            update.message.bot.restrict_chat_member(chat_id=config.chatGroup, user_id=fromUser['id'], until_date=(time.time()+31), permissions=permissions(can_send_messages=False))

def main():
    updater = Updater(token=config.token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('ping', ping))
    dispatcher.add_handler(MessageHandler(Filters.reply & Filters.command & Filters.chat(config.chatGroup), fuck)) #禁言
    dispatcher.add_handler(CommandHandler('search', search)) #搜索
    dispatcher.add_handler(CallbackQueryHandler(button)) #按钮
    # dispatcher.add_handler(MessageHandler((Filters.document.file_extension('png') | Filters.document.file_extension('jpg') | Filters.document.file_extension('jpeg') | Filters.document.file_extension('bmp') | Filters.document.file_extension('gif') | Filters.document.file_extension('webp')) & (~Filters.command) & Filters.chat(config.chatGroup), checkImage))
    # dispatcher.add_handler(MessageHandler(Filters.photo & (~Filters.command) & Filters.chat(config.chatGroup), checkPhoto))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
