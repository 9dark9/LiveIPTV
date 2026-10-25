# 作者: 海风（kele551）
# 用途: 把 repo\_page.html 嵌进 LIVE直播源.py 的 PAGE 变量。
#   为什么必须内嵌: exe 是 PyInstaller 单文件，运行时没有随包的第二份 html，
#   页面只能以字符串形式待在 .py 里。可 1400 多行的页面塞在 Python 文件中间难改难审，
#   所以页面源码单独留成 _page.html，改页面 = 改这个文件再跑一次本脚本。
#   以前两份是手工同步的（2026-10-24 就靠人肉 commit 对齐），改一处漏两处没人报警 ——
#   现在由 tools/check_page.py 做逐字节断言，打包前必须先过。
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PAGE_HTML = os.path.join(REPO, "_page.html")
MAIN = os.path.join(REPO, "LIVE直播源.py")
BEGIN = 'PAGE = r"""'
END = '\n"""'


def check_safe(html):
    """raw 三引号字符串的两个硬约束，违反任何一条嵌进去都是语法灾难。"""
    if '"""' in html:
        return "页面里有连续三个双引号，r\"\"\" 会被提前截断"
    if html.rstrip("\n").endswith("\\"):
        return "页面末尾是反斜杠，raw 字符串不能以反斜杠结尾"
    return ""


def main():
    html = io.open(PAGE_HTML, encoding="utf-8").read()
    bad = check_safe(html)
    if bad:
        print("_page.html: " + bad)
        return 2
    body = html.rstrip("\n")          # 块尾的换行由 END 提供，多留一份就永远对不齐

    src = io.open(MAIN, encoding="utf-8").read()
    if src.count(BEGIN) != 1:
        print("LIVE直播源.py 里 '%s' 出现 %d 次（应为 1 次），先确认结构再跑"
              % (BEGIN, src.count(BEGIN)))
        return 2
    head, rest = src.split(BEGIN, 1)
    if END not in rest:
        print("LIVE直播源.py 里找不到 PAGE 块的收尾 '''\\n\"\"\"'''")
        return 2
    _, tail = rest.split(END, 1)
    out = head + BEGIN + body + END + tail

    # 写回前自检一遍：新文件里抠出来的 PAGE 必须与 _page.html 逐字符相同
    m = re.search(re.escape(BEGIN) + "(.*?)" + re.escape(END), out, re.S)
    if not m or m.group(1) != body:
        print("嵌入后回读不一致，已放弃写入（不破坏原文件）")
        return 3

    with io.open(MAIN, "w", encoding="utf-8", newline="") as f:
        f.write(out)
    print("已嵌入 _page.html: %d 字符 / LIVE直播源.py 现在 %d 字节"
          % (len(body), len(out.encode("utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
