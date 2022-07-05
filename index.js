const TelegramBot = require('node-telegram-bot-api');
const search = require('./module/search');
const TencentCheckImageSDK = require('./module/checkImage');
const { getLMsg, ECMarkdown, downloadFile } = require('./module/utils');
const MD5 = require('crypto-js/md5');

const TelegramConfig = require('./config.json');

const token = TelegramConfig.token;
const bot = new TelegramBot(token, { polling: true });

let searchData_tmp = {};

bot.onText(/\/start/, (msg, match) => {
    bot.sendMessage(msg.chat.id, getLMsg([
        'Github: [iPaperClipICU/paperClipReviewBot](https://github.com/iPaperClipICU/paperClipReviewBot)',
        '',
        '`/search <关键词>`: 搜索归档视频\\(关键词限制20个字符\\)'
    ]), {
        parse_mode: "MarkdownV2",
        disable_web_page_preview: true,
    });
});
bot.onText(/\/ping/, (msg, match) => {
    bot.sendMessage(msg.chat.id, 'pong');
});

bot.onText(/^\/search$/, (msg, match) => {
    const chatID = msg.chat.id;
    const messageID = msg.message_id;
    const userName = ECMarkdown('@' + msg.from.username || `${msg.from.first_name} ${msg.from.last_name}`);
    const userID = msg.from.id;

    bot.sendMessage(chatID, getLMsg([
        `[${userName}](tg://user?id=${String(userID)})`,
        '`/search <关键词>` 关键词限制20个字符'
    ]), {
        parse_mode: "MarkdownV2",
        reply_to_message_id: messageID,
        allow_sending_without_reply: true,
        disable_web_page_preview: true,
    });
});

const checkImage = async (chatID, messageID, userName, userID, fileID, type) => {
    let fileLink = await bot.getFileLink(fileID);

    let TencentCheckImageSDK_data;
    try {
        TencentCheckImageSDK_data = await TencentCheckImageSDK(fileLink);
    } catch (e) {
        bot.sendMessage(TelegramConfig.logsGroup, getLMsg([
            '@qshouzi Error in def:checkImageSDK',
            `code: ${ECMarkdown(e.code)}`,
            `message: ${ECMarkdown(e.message)}`,
            `requestId: ${ECMarkdown(e.requestId)}`
        ]), {
            parse_mode: "MarkdownV2",
            disable_web_page_preview: true
        });
        return;
    };

    // 合法
    if (TencentCheckImageSDK_data.Suggestion == 'Pass') return;

    // 非法
    const suggestion = TencentCheckImageSDK_data['Suggestion'];
    const label = TencentCheckImageSDK_data['Label'];
    const subLabel = TencentCheckImageSDK_data['SubLabel'];
    const score = String(TencentCheckImageSDK_data['Score']);
    const fileMD5 = TencentCheckImageSDK_data['FileMD5'];
    const requestID = TencentCheckImageSDK_data['RequestId'];

    // 下载图片
    fileLink = await bot.getFileLink(fileID);
    await downloadFile(fileLink, `./data/image/${messageID}_${userID}_${fileID}.${fileLink.split('.').pop()}`);

    // 发送违规图片
    if (type == 'document') {
        await bot.sendDocument(TelegramConfig.logsGroup, fileID);
    } else if (type == 'photo') {
        await bot.sendPhoto(TelegramConfig.logsGroup, fileID);
    };

    let chatMsg, logMsg;
    if (suggestion == 'Block') {
        // 禁言
        bot.restrictChatMember(chatID, userID, {
            until_date: Math.floor(Date.now() / 1000) + (30*60), //30分钟
            permissions: {can_send_messages: false}
        });
        // 删除消息
        bot.deleteMessage(chatID, messageID);
        chatMsg = getLMsg([
            '检测到色情内容，发送者已被封禁30min',
            `发送者: [${userName}](tg://user?id=${String(userID)}) \\| ${String(userID)}`,
            '违规类型: image',
            `违规标签: ${ECMarkdown(`${label}-${subLabel}`)}`
        ]);
        logMsg = getLMsg([
            '检测到群聊存在色情内容',
            '如存在儿童类违规请第一时间删除文件并封禁发送者'
        ]);
    } else {
        chatMsg = '检测到疑似色情内容，请管理员人工复审';
        logMsg = '检测到疑似色情内容，请管理员人工复审';
    };
    logMsg += getLMsg([
        `发送者: [${userName}](tg://user?id=${String(userID)}) \\| ${String(userID)}`,
        '文件类型: image',
        `处理建议: ${ECMarkdown(suggestion)}`,
        `标签: ${ECMarkdown(`${label}-${subLabel}`)}`,
        `可信度: ${ECMarkdown(score)}`,
        `MD5: ${ECMarkdown(fileMD5)}`,
        `ID: ${ECMarkdown(requestID)}`
    ]);
    bot.sendMessage(TelegramConfig.chatGroup, chatMsg, {
        parse_mode: "MarkdownV2",
        disable_web_page_preview: true
    });
    bot.sendMessage(TelegramConfig.logsGroup, logMsg, {
        parse_mode: "MarkdownV2",
        disable_web_page_preview: true
    });
};
bot.on('document', async (msg, match) => {
    const chatID = msg.chat.id;
    const messageID = msg.message_id;
    const userName = ECMarkdown('@' + msg.from.username || `${msg.from.first_name} ${msg.from.last_name}`);
    const userID = msg.from.id;

    if (chatID != TelegramConfig.chatGroup) return;
    const status = (await bot.getChatMember(chatID, userID)).status;
    if (status == 'administrator' || status == 'creator' || msg.from.is_bot) return;

    const fileMimeType = msg.document.mime_type;
    const fileID = msg.document.file_id;
    if (fileMimeType.substring(0, 5) != 'image') return;

    checkImage(chatID, messageID, userName, userID, fileID, 'document');
});
bot.on('photo', async (msg, match) => {
    const chatID = msg.chat.id;
    const messageID = msg.message_id;
    const userName = ECMarkdown('@' + msg.from.username || `${msg.from.first_name} ${msg.from.last_name}`);
    const userID = msg.from.id;

    if (chatID != TelegramConfig.chatGroup) return;
    const status = (await bot.getChatMember(chatID, userID)).status;
    if (status == 'administrator' || status == 'creator' || msg.from.is_bot) return;

    const fileID = msg.photo[msg.photo.length - 1].file_id;

    checkImage(chatID, messageID, userName, userID, fileID, 'photo');
});

bot.onText(/\/search (.+)/, (msg, match) => {
    const chatID = msg.chat.id;
    const messageID = msg.message_id;
    const userName = ECMarkdown('@' + msg.from.username || `${msg.from.first_name} ${msg.from.last_name}`);
    const userID = msg.from.id;

    const keyword = String(match[1]).toLocaleLowerCase();

    const search_data = search(keyword);
    if (search_data == null) {
        bot.sendMessage(chatID, getLMsg([
            `[${userName}](tg://user?id=${String(userID)})`,
            '未搜索到相关视频'
        ]), {
            parse_mode: "MarkdownV2",
            disable_web_page_preview: true,
            disable_notification: true,
            reply_to_message_id: messageID,
            allow_sending_without_reply: true,
        });
        return;
    };

    const keyword_md5 = MD5(keyword).toString();
    searchData_tmp[keyword_md5] = search_data;

    const inlineKeyboard = [];
    for (const i in search_data.data[0]) {
        const tmp = search_data.data[0][i];
        inlineKeyboard.push([{
            text: tmp[0],
            callback_data: `F_${keyword_md5}_${tmp[1]}`,
        }]);
    }
    if (search_data.pages) {
        inlineKeyboard.push([{
            text: '下一页(2)',
            callback_data: `P_${keyword_md5}_1`,
        }]);
    }

    bot.sendMessage(chatID, getLMsg([
        '🔍查询归档站视频',
        `共 ${String(search_data.all)} 个结果 \\| 1/${String(search_data.data.length)} 页`,
        `[${userName}](tg://user?id=${String(userID)}) 请点击选择`
    ]), {
        parse_mode: "MarkdownV2",
        disable_web_page_preview: true,
        disable_notification: true,
        reply_to_message_id: messageID,
        allow_sending_without_reply: true,
        reply_markup: {
            inline_keyboard: inlineKeyboard
        }
    });
});

/**
 * callbackData
 * F_xxx_0_1: 文件页 F_MD5(keyword)_PageNum_File
 * P_xxx_0: 搜索页 P_MD5(keyword)_PageNum
 * PageNum 为在 searchData_tmp 中的下标
 */
bot.on('callback_query', (msg) => {
    const chatID = msg.message.chat.id;
    const messageID = msg.message.message_id;
    const callbackData = msg.data;
    const userName = ECMarkdown('@' + msg.from.username || `${msg.from.first_name} ${msg.from.last_name}`);
    const userID = msg.from.id;

    if (callbackData.substring(0, 2) == 'F_') {
        // 文件页 F_xxx_0_1
        const keyword_md5 = callbackData.split('_')[1];
        const pageNum = Number(callbackData.split('_')[2]);
        const fileNum = Number(callbackData.split('_')[3]);

        const search_data = searchData_tmp[keyword_md5];
        if (search_data == void 0) {
            // 过期
            bot.editMessageText(getLMsg([
                `[${userName}](tg://user?id=${String(userID)})`,
                '已过期, 请重新搜索'
            ]), {
                parse_mode: 'MarkdownV2',
                chat_id: chatID,
                message_id: messageID,
                disable_web_page_preview: true,
            });
            bot.answerCallbackQuery(msg.id);
            return;
        };
        const file_data = search_data.data[pageNum][fileNum];

        let fileMessage = getLMsg([
            `[${userName}](tg://user?id=${String(userID)})`,
            `*${ECMarkdown(file_data[0])}*`,
            ''
        ]);
        for (const i in file_data[2]) fileMessage += `\n[${ECMarkdown(i)}](${ECMarkdown(encodeURI(file_data[2][i]), '(')})`;

        const inlineKeyboard = [[{
            text: '返回', callback_data: `P_${keyword_md5}_${String(pageNum)}`
        }]];
        bot.editMessageText(fileMessage, {
            parse_mode: 'MarkdownV2',
            chat_id: chatID,
            message_id: messageID,
            disable_web_page_preview: true,
            reply_markup: {
                inline_keyboard: inlineKeyboard
            }
        });
    } else if (callbackData.substring(0, 2) == 'P_') {
        // 搜索页 P_xxx_0
        const keyword_md5 = callbackData.split('_')[1];
        const pageNum = Number(callbackData.split('_')[2]);

        const search_data = searchData_tmp[keyword_md5];
        if (search_data == void 0) {
            // 过期
            bot.editMessageText(getLMsg([
                `[${userName}](tg://user?id=${String(userID)})`,
                '已过期, 请重新搜索'
            ]), {
                parse_mode: 'MarkdownV2',
                chat_id: chatID,
                message_id: messageID,
                disable_web_page_preview: true,
            });
            bot.answerCallbackQuery(msg.id);
            return;
        }

        const page_data = search_data.data[pageNum];
        const inlineKeyboard = [];
        for (const i in page_data) {
            const tmp = page_data[i];
            inlineKeyboard.push([{
                text: tmp[0],
                callback_data: `F_${keyword_md5}_${tmp[1]}`,
            }]);
        }
        if (search_data.data.length != 1) {
            // 分页
            if (search_data.data.length - 1 == pageNum) {
                // 最后一页
                inlineKeyboard.push([
                    {
                        text: `上一页(${String(pageNum)})`,
                        callback_data: `P_${keyword_md5}_${String(pageNum - 1)}`,
                    }
                ]);
            } else if (pageNum == 0) {
                // 第一页
                inlineKeyboard.push([
                    {
                        text: `下一页(${String(pageNum + 2)})`,
                        callback_data: `P_${keyword_md5}_${String(pageNum + 1)}`,
                    }
                ]);
            } else {
                inlineKeyboard.push([
                    {
                        text: `上一页(${String(pageNum)})`,
                        callback_data: `P_${keyword_md5}_${String(pageNum - 1)}`,
                    },
                    {
                        text: `下一页(${String(pageNum + 2)})`,
                        callback_data: `P_${keyword_md5}_${String(pageNum + 1)}`,
                    }
                ]);
            };
        };

        bot.editMessageText(getLMsg([
            '🔍查询归档站视频',
            `共 ${String(search_data.all)} 个结果 \\| ${String(pageNum + 1)}/${String(search_data.data.length)} 页`,
            `[${userName}](tg://user?id=${String(userID)}) 请点击选择`
        ]), {
            parse_mode: 'MarkdownV2',
            chat_id: chatID,
            message_id: messageID,
            disable_web_page_preview: true,
            reply_markup: {
                inline_keyboard: inlineKeyboard
            }
        });
    };

    bot.answerCallbackQuery(msg.id);
});

bot.on('error', (e) => {
    console.log('[TelegramBotError]', e);
});
