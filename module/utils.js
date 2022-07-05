const https = require('node:https');
const fs = require('node:fs');

/**
 * 优雅的获取多行文本
 * @param {Array} data ['', '', ...]
 * @returns {String} 多行文本
 */
const getLMsg = (data) => {
    let returnMessage = '';
    for (const i in data) returnMessage += '\n' + String(data[i]);
    return returnMessage;
};

/**
 * 不优雅的转义文本
 * @param {String} text 文本
 * @param {String} type ''|(|)|code|pre 默认''
 * @returns {String} 文本
 */
const ECMarkdown = (text, type = '') => {
    if (type == '') {
        return text.replace(/\_/g, '\\_')
            .replace(/\*/g, '\\*')
            .replace(/\[/g, '\\[')
            .replace(/\]/g, '\\]')
            .replace(/\(/g, '\\(')
            .replace(/\)/g, '\\)')
            .replace(/\~/g, '\\~')
            .replace(/\`/g, '\\`')
            .replace(/\>/g, '\\>')
            .replace(/\#/g, '\\#')
            .replace(/\+/g, '\\+')
            .replace(/\-/g, '\\-')
            .replace(/\=/g, '\\=')
            .replace(/\|/g, '\\|')
            .replace(/\{/g, '\\{')
            .replace(/\}/g, '\\}')
            .replace(/\./g, '\\.')
            .replace(/\!/g, '\\!');
    } else if (type == '(' || type == ')') {
        return text.replace(/\)/g, '\\)').replace(/\\/g, '\\\\');
    } else if (type == 'code' || type == 'pre') {
        return text.replace(/\`/g, '\\`').replace(/\\/g, '\\\\');
    };
};

/**
 * 下载文件
 * @param {String} uri URI
 * @param {String} dest 本地保存路径
 */
const downloadFile = (uri, dest) => {
    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(dest);

        https.get(uri, (res) => {
            if (res.statusCode !== 200) {
                reject(res.statusCode);
                return;
            };

            // res.on('end', () => {
            //     // console.log('download end');
            // });

            file.on('finish', () => {
                // console.log('finish write file')
                file.close(resolve);
            }).on('error', (err) => {
                fs.unlink(dest);
                reject(err.message);
            });

            res.pipe(file);
        });
    });
};

module.exports = {
    getLMsg,
    ECMarkdown,
    downloadFile
};
