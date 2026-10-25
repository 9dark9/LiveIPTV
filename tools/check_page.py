# 作者: 海风（kele551）
# 用途: 打包/改完页面后的一致性闸门。三件事，任何一件不过就非零退出：
#   1) LIVE直播源.py 里的 PAGE 必须与 _page.html 逐字符相同（否则 exe 带的不是你看的那份页面）
#   2) 仓库外的 ../src 开发副本必须与仓库一致（以前 build_exe.py 直接打包 ../src，
#      改了仓库忘拷 src，发出去的包就是旧代码 —— 2026-10-25 起打包只读仓库，src 漂移默认只提醒，
#      加 --strict-src 才判失败）
#   3) 主程序能编译（语法错、raw 字符串被截断都在这里挡住）
# 跑法: python tools/check_page.py [--strict-src]
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC = os.path.join(os.path.dirname(REPO), "src")   # 运行/资源目录，不是代码来源
MAIN = os.path.join(REPO, "LIVE直播源.py")
PAGE_HTML = os.path.join(REPO, "_page.html")
BEGIN = 'PAGE = r"""'
END = '\n"""'
CODE_FILES = ["LIVE直播源.py", "_page.html", "_ed25519.py", "_tray.py", "_toast.py",
              "tray.ico", "tray_busy.ico"]

fails = []


def fail(msg):
    fails.append(msg)
    print("  [失败] " + msg)


def ok(msg):
    print("  [通过] " + msg)


def warn(msg):
    print("  [提醒] " + msg)


def main(argv=None):
    # 默认只把 src 漂移当提醒（打包已经不读 src，漂了也不影响产物）；
    # --strict-src 时按失败处理，供日常体检/发版闸门用。
    strict_src = "--strict-src" in (argv or sys.argv[1:])
    print("-" * 70)
    print("1. 页面单一来源：PAGE 必须等于 _page.html")
    html = io.open(PAGE_HTML, encoding="utf-8").read().rstrip("\n")
    src = io.open(MAIN, encoding="utf-8").read()
    m = re.search(re.escape(BEGIN) + "(.*?)" + re.escape(END), src, re.S)
    if not m:
        fail("LIVE直播源.py 里找不到 PAGE 块")
    elif m.group(1) == html:
        ok("PAGE 与 _page.html 逐字符一致（%d 字符）" % len(html))
    else:
        fail("PAGE 与 _page.html 不一致（PAGE %d 字符 / 文件 %d 字符）→ 跑 python tools/embed_page.py"
             % (len(m.group(1)), len(html)))

    print("-" * 70)
    print("2. 开发副本 ../src 与仓库是否同步（打包不读它，只影响你本机跑源码）")
    drift = []
    for name in CODE_FILES:
        a, b = os.path.join(REPO, name), os.path.join(SRC, name)
        if not os.path.exists(b):
            drift.append("%s（src 里没有）" % name)
            continue
        same = io.open(a, "rb").read() == io.open(b, "rb").read()
        if not same:
            drift.append(name)
    if drift:
        (fail if strict_src else warn)(
            "src 副本已漂移: %s → 跑 python tools/sync_src.py" % ", ".join(drift))
    else:
        ok("src 的 %d 个代码文件与仓库一致" % len(CODE_FILES))

    print("-" * 70)
    print("3. 主程序可编译")
    try:
        compile(io.open(MAIN, encoding="utf-8").read(), MAIN, "exec")
        ok("LIVE直播源.py 语法通过")
    except SyntaxError as e:
        fail("语法错误: %s (第 %s 行)" % (e.msg, e.lineno))

    print("-" * 70)
    if fails:
        print("一致性检查未通过（%d 项）—— 别打包" % len(fails))
        return 1
    print("一致性检查全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
