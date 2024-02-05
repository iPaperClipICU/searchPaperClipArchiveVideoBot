import fs from "node:fs";
import path from "node:path";

const searchMap = JSON.parse(
  fs.readFileSync(path.join(__dirname, "../data/searchMap.json"), "utf-8")
) as [string, string[]][];
const searchData = JSON.parse(
  fs.readFileSync(path.join(__dirname, "../data/searchData.json"), "utf-8")
) as Record<string, Record<string, Record<string, string>>>;

export const search = (keyword: string, page = 10) => {
  const kw = keyword.toLocaleLowerCase();

  const data: [string, string, Record<string, string>][][] = [];
  let tmp: [string, string, Record<string, string>][] = [];
  let all = 0;
  for (const i of searchMap) {
    const tag = i[0];
    for (const fileName of i[1]) {
      if (fileName.toLocaleLowerCase().includes(kw)) {
        if (tmp.length === 10) {
          data.push(tmp);
          tmp = [];
        }
        tmp.push([`[${tag}] ${fileName}`, `${String(data.length)}_${String(tmp.length)}`, searchData[tag][fileName]]);
        all++;
      }
    }
  }

  if (all === 0) return null;
  else if (tmp.length !== 0) data.push(tmp);
  return {
    all,
    pages: data.length !== 1,
    data,
  };
};
