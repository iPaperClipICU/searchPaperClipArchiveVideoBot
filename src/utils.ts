/**
 * 优雅的获取多行文本
 * @param data ['', '', ...]
 * @returns 多行文本
 */
export const getLMsg = (data: any[]) => data.map((v) => String(v)).join("\n");

/**
 * 不优雅的转义文本
 * @param text 文本
 * @param type ''|(|)|code|pre 默认''
 * @returns 文本
 */
export const ECMarkdown = (text: string, type = "") => {
  if (type == "") {
    return text
      .replace(/\_/g, "\\_")
      .replace(/\*/g, "\\*")
      .replace(/\[/g, "\\[")
      .replace(/\]/g, "\\]")
      .replace(/\(/g, "\\(")
      .replace(/\)/g, "\\)")
      .replace(/\~/g, "\\~")
      .replace(/\`/g, "\\`")
      .replace(/\>/g, "\\>")
      .replace(/\#/g, "\\#")
      .replace(/\+/g, "\\+")
      .replace(/\-/g, "\\-")
      .replace(/\=/g, "\\=")
      .replace(/\|/g, "\\|")
      .replace(/\{/g, "\\{")
      .replace(/\}/g, "\\}")
      .replace(/\./g, "\\.")
      .replace(/\!/g, "\\!");
  } else if (type == "(" || type == ")") {
    return text.replace(/\)/g, "\\)").replace(/\\/g, "\\\\");
  } else if (type == "code" || type == "pre") {
    return text.replace(/\`/g, "\\`").replace(/\\/g, "\\\\");
  }
};
