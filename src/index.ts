import crypto from "node:crypto";
import { Telegraf, type Context } from "telegraf";
import type { InlineKeyboardButton } from "telegraf/typings/core/types/typegram";
import { search } from "./search";
import { ECMarkdown, getLMsg } from "./utils";

const TelegramToken = process.env.TelegramToken as string;
const bot = new Telegraf(TelegramToken);

const getUserName = (ctx: Context) => {
  if (ctx.from?.username) return `@${ctx.from.username}`;
  else return `${ctx.from?.first_name ?? ""} ${ctx.from?.last_name ?? ""}`;
};

bot.command("start", async (ctx) => {
  await ctx.sendMessage(
    getLMsg([
      "Github: [iPaperClipICU/paperClipReviewBot](https://github.com/iPaperClipICU/paperClipReviewBot)",
      "",
      "`/search <关键词>`: 搜索归档视频\\(关键词限制20个字符\\)",
    ]),
    {
      parse_mode: "MarkdownV2",
      disable_web_page_preview: true,
    }
  );
});
bot.command("ping", async (ctx) => {
  ctx.sendMessage("pong!");
});

let searchResultTmp: Record<
  string,
  {
    all: number;
    pages: boolean;
    data: [string, string, Record<string, string>][][];
  }
> = {};
bot.command("search", async (ctx) => {
  const messageID = ctx.message.message_id;
  const userName = ECMarkdown(getUserName(ctx));
  const userID = ctx.from.id;

  if (ctx.args.length <= 0) {
    // 没有 keyword
    await ctx.sendMessage(
      getLMsg([
        `[${userName}](tg://user?id=${String(userID)})`,
        "`/search <关键词>` 关键词限制20个字符",
      ]),
      {
        parse_mode: "MarkdownV2",
        reply_to_message_id: messageID,
        allow_sending_without_reply: true,
        disable_web_page_preview: true,
      }
    );
  } else {
    // 有 keyword
    const keyword = ctx.args.join(" ").toLocaleLowerCase();
    const searchResult = search(keyword);
    if (!searchResult) {
      await ctx.sendMessage(
        getLMsg([
          `[${userName}](tg://user?id=${String(userID)})`,
          "未搜索到相关视频",
        ]),
        {
          parse_mode: "MarkdownV2",
          disable_web_page_preview: true,
          disable_notification: true,
          reply_to_message_id: messageID,
          allow_sending_without_reply: true,
        }
      );
      return;
    }

    const keyword_md5 = crypto
      .createHash("md5")
      .update("keyword")
      .digest("hex");
    searchResultTmp[keyword_md5] = searchResult;

    const inlineKeyboard: InlineKeyboardButton[][] = [];
    for (const i in searchResult.data[0]) {
      const tmp = searchResult.data[0][i];
      inlineKeyboard.push([
        {
          text: tmp[0],
          callback_data: `F_${keyword_md5}_${tmp[1]}`,
        },
      ]);
    }
    if (searchResult.pages) {
      inlineKeyboard.push([
        {
          text: "下一页(2)",
          callback_data: `P_${keyword_md5}_1`,
        },
      ]);
    }

    await ctx.sendMessage(
      getLMsg([
        "🔍查询归档站视频",
        `共 ${String(searchResult.all)} 个结果 \\| 1/${String(
          searchResult.data.length
        )} 页`,
        `[${userName}](tg://user?id=${String(userID)}) 请点击选择`,
      ]),
      {
        parse_mode: "MarkdownV2",
        disable_web_page_preview: true,
        disable_notification: true,
        reply_to_message_id: messageID,
        allow_sending_without_reply: true,
        reply_markup: {
          inline_keyboard: inlineKeyboard,
        },
      }
    );
  }
});

/**
 * callbackData
 * F_xxx_0_1: 文件页 F_MD5(keyword)_PageNum_File
 * P_xxx_0: 搜索页 P_MD5(keyword)_PageNum
 * PageNum 为在 searchData_tmp 中的下标
 */
bot.on("callback_query", async (ctx) => {
  const callbackData = String((ctx.callbackQuery as any)?.data);
  const userName = ECMarkdown(getUserName(ctx));
  const userID = ctx.from?.id;

  const cbData = callbackData.split("_");
  const keyword_md5 = cbData[1];
  const pageNum = Number(cbData[2]);
  const searchResult = searchResultTmp[keyword_md5];
  if (!searchResult) {
    // 过期
    await ctx.editMessageText(
      getLMsg([
        `[${userName}](tg://user?id=${String(userID)})`,
        "已过期, 请重新搜索",
      ]),
      {
        parse_mode: "MarkdownV2",
        disable_web_page_preview: true,
      }
    );
  } else if (callbackData.startsWith("F_")) {
    // 文件页面 F_xxx_0_1
    const fileNum = Number(cbData[3]);

    const fileData = searchResult.data[pageNum][fileNum];
    let fileMessage = getLMsg([
      `[${userName}](tg://user?id=${String(userID)})`,
      `*${ECMarkdown(fileData[0])}*`,
      "",
    ]);
    for (const i in fileData[2])
      fileMessage += `\n[${ECMarkdown(i)}](${ECMarkdown(
        encodeURI(fileData[2][i]),
        "("
      )})`;

    await ctx.editMessageText(fileMessage, {
      parse_mode: "MarkdownV2",
      disable_web_page_preview: true,
      reply_markup: {
        inline_keyboard: [
          [
            {
              text: "返回",
              callback_data: `P_${keyword_md5}_${String(pageNum)}`,
            },
          ],
        ],
      },
    });
  } else if (callbackData.startsWith("P_")) {
    // 搜索页 P_xxx_0
    const pageData = searchResult.data[pageNum];
    const inlineKeyboard: InlineKeyboardButton[][] = [];
    for (const tmp of pageData) {
      inlineKeyboard.push([
        {
          text: tmp[0],
          callback_data: `F_${keyword_md5}_${tmp[1]}`,
        },
      ]);
    }
    if (searchResult.data.length !== 1) {
      // 分页
      if (searchResult.data.length - 1 == pageNum) {
        // 最后一页
        inlineKeyboard.push([
          {
            text: `上一页(${String(pageNum)})`,
            callback_data: `P_${keyword_md5}_${String(pageNum - 1)}`,
          },
        ]);
      } else if (pageNum == 0) {
        // 第一页
        inlineKeyboard.push([
          {
            text: `下一页(${String(pageNum + 2)})`,
            callback_data: `P_${keyword_md5}_${String(pageNum + 1)}`,
          },
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
          },
        ]);
      }
    }

    await ctx.editMessageText(
      getLMsg([
        "🔍查询归档站视频",
        `共 ${String(searchResult.all)} 个结果 \\| ${String(
          pageNum + 1
        )}/${String(searchResult.data.length)} 页`,
        `[${userName}](tg://user?id=${String(userID)}) 请点击选择`,
      ]),
      {
        parse_mode: "MarkdownV2",
        disable_web_page_preview: true,
        reply_markup: {
          inline_keyboard: inlineKeyboard,
        },
      }
    );
  }
  await ctx.answerCbQuery();
});

bot.launch();
process.once("SIGINT", () => bot.stop("SIGINT"));
process.once("SIGTERM", () => bot.stop("SIGTERM"));
