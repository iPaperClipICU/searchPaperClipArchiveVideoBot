import logging
from telegram import Update, ChatPermissions
from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler
)
from plugins.checkImage import checkPhoto, checkImage
from plugins.search import search, button
from plugins.getConfig import getConfig

# Config
CONFIG = getConfig()
TOKEN = CONFIG['Token']
CHATGROUP = CONFIG['ChatGroup']
FATHER = CONFIG['Father']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# def:Start #
def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Github: https://github.com/iPaperClipICU/paperClipReviewBot', disable_web_page_preview=True)

# def:ping #
def ping(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='pong')

# def:nsfw #
def nsfw(update: Update, context: CallbackContext, permissions=ChatPermissions):
    # /nsfw <userID> <time(s)>
    fromUser = update.message.from_user
    status=context.bot.getChatMember(chat_id=CHATGROUP, user_id=fromUser['id']).status
    if (status in ['administrator', 'creator']) or (fromUser['id'] == FATHER):
        if len(context.args) == 2:
            user = context.args[0]
            time = context.args[1]
            update.message.bot.restrict_chat_member(chat_id=CHATGROUP, user_id=user, until_date=(time.time()+time), permissions=permissions(can_send_messages=False))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='格式: /nsfw <userID> <time(s)>\nuserID 是一串数字\ntime 小于30s永久禁言')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='你没有权限使用/nsfw，禁言10s')
        update.message.bot.restrict_chat_member(chat_id=CHATGROUP, user_id=fromUser['id'], until_date=(time.time()+10), permissions=permissions(can_send_messages=False))

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('ping', ping))
    dispatcher.add_handler(CommandHandler('nsfw', nsfw))
    dispatcher.add_handler(CommandHandler('search', search))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler((Filters.document.file_extension('png') | Filters.document.file_extension('jpg') | Filters.document.file_extension('jpeg') | Filters.document.file_extension('bmp') | Filters.document.file_extension('gif') | Filters.document.file_extension('webp')) & (~Filters.command) & Filters.chat(CHATGROUP), checkImage))
    dispatcher.add_handler(MessageHandler(Filters.photo & (~Filters.command) & Filters.chat(CHATGROUP), checkPhoto))
    
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
