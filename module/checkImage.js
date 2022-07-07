const vision = require('@google-cloud/vision');
const client = new vision.ImageAnnotatorClient();

// UNKNOWN        未知的可能性
// VERY_UNLIKELY  这是非常不可能的
// UNLIKELY       不太可能
// POSSIBLE       有可能的
// LIKELY         这有可能
// VERY_LIKELY    很有可能

const getName = (name) => {
    let l;
    if (name === 'UNKNOWN') {
        l = 0;
    } else if (name === 'VERY_UNLIKELY') {
        l = 1;
    } else if (name === 'UNLIKELY') {
        l = 2;
    } else if (name === 'POSSIBLE') {
        l = 3;
    } else if (name === 'LIKELY') {
        l = 4;
    } else if (name === 'VERY_LIKELY') {
        l = 5;
    };

    return [l, name];
};

/**
 * 谷歌图像识别
 * @param {String} imagePath 图片路径
 * @returns {Promise<JSON|Error>} 返回图片的名称
 */
const GoogleCheckImageSDK = async (imagePath) => {
    try {
        const [result] = await client.safeSearchDetection(imagePath);
        const detections = result.safeSearchAnnotation;

        return Promise.resolve({
            'adult': getName(detections.adult), //成人
            'spoof': getName(detections.spoof), //恶搞
            'medical': getName(detections.medical), //医学
            'violence': getName(detections.violence), //暴力
            'racy': getName(detections.racy) //色情
        });
    } catch (e) {
        return Promise.reject(e);
    };
};

module.exports = GoogleCheckImageSDK;
