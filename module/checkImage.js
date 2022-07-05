const tencentcloud = require("tencentcloud-sdk-nodejs");
const ImsClient = tencentcloud.ims.v20201229.Client;
const { secretID, secretKEY } = require("../config.json").tencent;

/**
 * 腾讯云图片检测
 * @param {String} FileUrl 文件地址
 * @returns {Promise<ImageModerationResponse>} 检测结果
 */
const TencentCheckImageSDK = async (FileUrl) => {
    const client = new ImsClient({
        credential: {
            secretId: secretID,
            secretKey: secretKEY
        },
        region: "ap-singapore",
        profile: {
            httpProfile: {
                endpoint: "ims.tencentcloudapi.com"
            }
        }
    });

    const params = {
        "BizType": "TGroupChat",
        "FileUrl": FileUrl
    };
    try {
        const data = await client.ImageModeration(params);
        return Promise.resolve(data);
    } catch (e) {
        return Promise.reject(e);
    };
};

module.exports = TencentCheckImageSDK;
