const TelegramBot = require('node-telegram-bot-api');
const fs = require('node:fs');
const MD5 = require('crypto-js/md5');

const search = require('./module/search');
const GoogleCheckImageSDK = require('./module/checkImage');
const { getLMsg, ECMarkdown, downloadFile } = require('./module/utils');

const TelegramConfig = require('./config.json').telegram;

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

/**
 * 获取用户名
 * @param {TelegramBot.Message} msg TelegramBot.Message
 * @returns {String} 用户名
 */
const getUserName = (msg) => {
    if (msg.from.username == void 0) {
        return `${msg.from.first_name} ${msg.from.last_name}`;
    } else {
        return `@${msg.from.username}`;
    };
};

bot.onText(/^\/search$/, (msg, match) => {
    const chatID = msg.chat.id;
    const messageID = msg.message_id;
    const userName = ECMarkdown(getUserName(msg));
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
    const fileLink = await bot.getFileLink(fileID);
    const ImagePath = `./data/image/${messageID}_${userID}_${fileID}.${fileLink.split('.').pop()}`;

    // 下载图片
    try {
        await downloadFile(fileLink, ImagePath);
    } catch (e) {
        bot.sendMessage(TelegramConfig.logsGroup, getLMsg([
            '@qshouzi Error in def:downloadFile',
            ECMarkdown(String(e))
        ]), {
            parse_mode: "MarkdownV2",
            disable_web_page_preview: true
        });
        return;
    };

    let GoogleCheckImageSDK_data;
    try {
        GoogleCheckImageSDK_data = await GoogleCheckImageSDK(ImagePath);
    } catch (e) {
        bot.sendMessage(TelegramConfig.logsGroup, getLMsg([
            '@qshouzi Error in def:checkImageSDK',
            ECMarkdown(String(e))
        ]), {
            parse_mode: "MarkdownV2",
            disable_web_page_preview: true
        });
        return;
    };

    const { adult, spoof, medical, violence, racy } = GoogleCheckImageSDK_data;
    if (
        adult[0] == null ||
        spoof[0] == null ||
        medical[0] == null ||
        violence[0] == null ||
        racy[0] == null
    ) {
        bot.sendMessage(TelegramConfig.logsGroup, getLMsg([
            '@qshouzi GoogleCheckImageSDK_data value Error',
            '`' + ECMarkdown(String(GoogleCheckImageSDK_data)) + '`'
        ]), {
            parse_mode: "MarkdownV2",
            disable_web_page_preview: true
        });
        return;
    };

    // 疑似
    if ((adult[0] == 4 || violence[0] >= 4 || racy[0] >= 4) && adult[0] != 5) {
        bot.sendMessage(TelegramConfig.chatGroup, getLMsg([
            `\\#${userID}\\_${messageID}A`,
            '疑似包含违规内容',
            '',
            `adult 成人: ${String(adult[0])}/5`,
            `violence 暴力: ${String(violence[0])}/5`,
            `racy 色情: ${String(racy[0])}/5`
        ]), {
            parse_mode: "MarkdownV2",
            reply_to_message_id: messageID,
            allow_sending_without_reply: true,
            disable_web_page_preview: true,
        });
        return;
    } else if (adult[0] != 5) {
        // 合法
        fs.unlink(ImagePath, (err) => {
            if (err) {
                bot.sendMessage(TelegramConfig.logsGroup, getLMsg([
                    '@qshouzi Error in def:fs.unlink',
                    ECMarkdown(String(err))
                ]), {
                    parse_mode: "MarkdownV2",
                    disable_web_page_preview: true
                });
            };
        });
        return;
    };

    // 非法
    // 发送违规图片到LOG
    if (type == 'document') {
        await bot.sendDocument(TelegramConfig.logsGroup, fileID);
    } else if (type == 'photo') {
        await bot.sendPhoto(TelegramConfig.logsGroup, fileID);
    };

    // 禁言
    await bot.restrictChatMember(chatID, userID, {
        until_date: Math.floor(Date.now() / 1000) + (30 * 60), //30分钟
        permissions: { can_send_messages: false }
    });
    // 删除消息
    bot.deleteMessage(chatID, messageID);
    const chatMsg = getLMsg([
        '检测到色情内容，发送者已被封禁30min',
        `发送者: [${userName}](tg://user?id=${String(userID)}) \\| ${String(userID)}`,
        '违规类型: image'
    ]);
    bot.sendMessage(TelegramConfig.chatGroup, chatMsg, {
        parse_mode: "MarkdownV2",
        disable_web_page_preview: true
    });
    bot.sendMessage(TelegramConfig.logsGroup, chatMsg, {
        parse_mode: "MarkdownV2",
        disable_web_page_preview: true
    });
};
bot.on('document', async (msg, match) => {
    const chatID = msg.chat.id;
    const messageID = msg.message_id;
    const userName = ECMarkdown(getUserName(msg));
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
    const userName = ECMarkdown(getUserName(msg));
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
    const userName = ECMarkdown(getUserName(msg));
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
    const userName = ECMarkdown(getUserName(msg));
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
