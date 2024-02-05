module.exports = {
  apps : [{
    name   : "PaperClipBot",
    script : "./src/index.ts",
    error_file: "./logs/error.log",
    out_file: "./logs/info.log",
    env: {
    	TelegramToken: "xxx",
    }
  }]
}
