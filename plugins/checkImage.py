import json, time
from telegram import Update, ChatPermissions
from telegram.ext import CallbackContext
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ims.v20201229 import ims_client, models
from .tools import getConfig, getJson, writeJson

# Config
CONFIG = getConfig()
CHATGROUP = CONFIG['ChatGroup']
DEBUG = CONFIG['Debug']

def checkImageSDK(URL):
    SECRETID = CONFIG['SecretID']
    SECRETKEY = CONFIG['SecretKEY']
    try:
        cred = credential.Credential(SECRETID, SECRETKEY)
        httpProfile = HttpProfile()
        httpProfile.endpoint = 'ims.tencentcloudapi.com'
    
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = ims_client.ImsClient(cred, 'ap-singapore', clientProfile)
    
        req = models.ImageModerationRequest()
        params = {
            'BizType': 'TGroupChat',
            'FileUrl': URL
        }
        req.from_json_string(json.dumps(params))
    
        resp = client.ImageModeration(req)
        return [0, resp.to_json_string()]
    except TencentCloudSDKException as err:
        return [1, err]

def checkImageModule(image, typeName, fromUser, update, context, permissions):
    TOKEN = CONFIG['Token']
    CHATGROUP = int(CONFIG['ChatGroup'])
    LOGSGROUP = int(CONFIG['LogsGroup'])
    DATAPATH = CONFIG['DataPath']
    
    photo = image
    file = image.get_file()
    filePath = file.file_path
    # check #
    data = checkImageSDK(filePath)
    if data[0] == 0:
        data = json.loads(data[1])
        if data['Suggestion'] != 'Pass':
            fileDownloadPath = file.download(custom_path='./data/image/'+str(int(time.time()))+filePath.replace('https://api.telegram.org/file/bot'+TOKEN+'/'+typeName+'/', '-'))
    
            suggestion = data['Suggestion']
            label = data['Label']
            subLabel = data['SubLabel']
            score = str(data['Score'])
            fileMD5 = data['FileMD5']
            requestID = data['RequestId']
    
            userFullName = fromUser['full_name']
            userName = fromUser['name']
            userID = str(fromUser['id'])
            if data['Suggestion'] == 'Block':
                update.message.bot.delete_message(chat_id=CHATGROUP, message_id=update.message.message_id)
                update.message.bot.restrict_chat_member(chat_id=CHATGROUP, user_id=fromUser['id'], until_date=(time.time()+(30*60)), permissions=permissions(can_send_messages=False))
                chatOut = '检测到色情内容，发送者已被封禁30min' +\
                          '\n发送者: {userName} | {userID} | {userFullName}' +\
                          '\n违规类型: image' +\
                          '\n违规标签: {label}-{subLabel}' +\
                          '\n管理员请前往日志群审查内容，如为儿童类违规请手动封禁'
                logOut = '检测到群聊存在色情内容' +\
                         '\n如存在儿童类违规请第一时间删除文件并封禁发送者'
            else:
                chatOut = '检测到疑似色情内容，请管理员人工复审'
                logOut = '检测到疑似色情内容，请管理员人工复审'
            logOut = logOut +\
                    '\n发送者: {userName} | {userID} | {userFullName}' +\
                    '\n文件类型: image' +\
                    '\n处理建议: {suggestion}' +\
                    '\n标签: {label}-{subLabel}' +\
                    '\n可信度: {score}' +\
                    '\nMD5: {fileMD5}' +\
                    '\nID: {requestID}'
            context.bot.send_message(chat_id=CHATGROUP, text=chatOut) #聊天群组
            if typeName == 'photos':
                logsGroupMessageID = context.bot.send_photo(chat_id=LOGSGROUP, photo=photo, filename='违规图片', protect_content=True).message_id #日志群组
            else:
                logsGroupMessageID = context.bot.send_document(chat_id=LOGSGROUP, document=image, filename='违规图片', protect_content=True).message_id #日志群组
            context.bot.send_message(chat_id=LOGSGROUP, text=logOut, reply_to_message_id = logsGroupMessageID) #日志群组
            # Data #
            outJsonData = {
                'map': { #索引
                    'requestID': requestID,
                    'MD5': fileMD5,
                    'fileDownloadPath': fileDownloadPath
                },
                'data': [
                    { #简化数据
                        'user': [userName, userID, userFullName], #用户名 ID 昵称
                        'fileType': 'image',
                        'suggestion': suggestion,
                        'label': label+'-'+subLabel,
                        'score': score
                    },
                    data #原始数据
                ]
            }
            jsonData = getJson(DATAPATH)
            jsonData[requestID] = outJsonData
            writeJson(DATAPATH, jsonData)
    else:
        err = data[1]
        errOut = '@qshouzi Error in def:checkImageSDK' +\
                 '\ncode: '+err.code +\
                 '\nmessage: '+err.message +\
                 '\nrequestId: '+err.requestId
        context.bot.send_message(chat_id=LOGSGROUP, text=errOut) #日志群组

def checkPhoto(update: Update, context: CallbackContext, permissions=ChatPermissions):
    fromUser = update.message.from_user
    status = context.bot.getChatMember(chat_id=CHATGROUP, user_id=fromUser['id']).status
    if (status not in ['administrator', 'creator']) and (fromUser.is_bot == False):
        if DEBUG: context.bot.send_message(chat_id=CHATGROUP, text='读取到Photo')
        photo = update.message.photo[len(update.message.photo)-1]
        checkImageModule(photo, 'photos', fromUser, update, context, permissions)

def checkImage(update: Update, context: CallbackContext, permissions=ChatPermissions):
    fromUser = update.message.from_user
    status = context.bot.getChatMember(chat_id=CHATGROUP, user_id=fromUser['id']).status
    if (status not in ['administrator', 'creator']) and (fromUser.is_bot == False):
        if DEBUG: context.bot.send_message(chat_id=CHATGROUP, text='读取到Image')
        image = update.message.document
        checkImageModule(image, 'documents', fromUser, update, context, permissions)
