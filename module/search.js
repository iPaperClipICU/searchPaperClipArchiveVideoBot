const searchMap = require('../data/searchMap.json');
const searchData = require('../data/searchData.json');

const PAGE = require('../config.json').search.pageMax;

/**
 * 搜索归档视频
 * @param {String} keyword 关键词
 * @returns {JSON} 搜索结果
 */
const search = (keyword) => {
    const kw = keyword.toLocaleLowerCase();

    const data = [];
    let tmp = [];
    let all = 0;
    for (const i in searchMap) {
        const tag = searchMap[i][0];
        for (const ii in searchMap[i][1]) {
            const fileName = searchMap[i][1][ii];
            if (fileName.toLocaleLowerCase().indexOf(kw) != -1) {
                if (tmp.length == PAGE) {
                    data.push(tmp);
                    tmp = [];
                }
                tmp.push([`[${tag}] ${fileName}`, `${String(data.length)}_${String(tmp.length)}`, searchData[tag][fileName]]);
                all++;
            }
        }
    }

    if (all === 0) return null;
    else if (tmp.length != 0) data.push(tmp);
    return {
        all: all,
        pages: data.length != 1,
        data: data,
    };
    // {
    //     all: 1,
    //     pages: false,
    //     data: [
    //         [
    //             ['[PaperClip/Vol] Vol.001', '0_1', {
    //                 'xx': 'https://xx.com/xx'
    //             }]
    //         ]
    //     ]
    // }
}

module.exports = search;
