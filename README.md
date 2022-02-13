# paperClipReviewBot

官方机器人: [Telegram@paperClipReviewBot](https://t.me/paperClipReviewBot)

你私聊官方机器人体验搜索功能

## 功能

`识别色情图片`: 识别群组发出的色情图片，对接腾讯云AI，对发送内容进行删除，对发送者进行禁言

`禁言 /nsfw <userID> <time(s)>`: 通过指令对指定用户禁言禁言时长小于30s是永久禁言

`搜索归档视频 /search <keywords>`: 通过指令搜索归档站视频

`/ping`: Pong

## 配置

```ini
[Config]
#Telegram Bot Token
Token = <string>
#tencentID
SecretID = <string>
#tencentKey
SecretKEY = <string>
#聊天群组ID
ChatGroup = <int>
#日志群组ID
LogsGroup = <int>
DataPath = .\data\data.json
SearchMapPath = .\plugins\searchMap.json
#BOT创建者ID
Father = <int>
Debug = False
```
