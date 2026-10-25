# 作者: 海风（kele551）
# 用途: 把仓库里的代码文件拷到 ../src 开发目录（本机跑源码用），只拷代码，
#   不碰 src 里的 config.json / 日志 / logos_lib / hls.min.js 这些运行期与资源文件。
# 为什么还要 src: 它是历史遗留的"跑起来的那份"，logos_lib(台标离线库 381 张)和
#   LIVE直播源.ico 也放在那儿。代码的**唯一来源**是仓库，src 只是镜像。
# 跑法: python tools/sync_src.py
import hashlib
import io
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC = os.path.join(os.path.dirname(REPO), "src")
CODE_FILES = ["LIVE直播源.py", "_page.html", "_ed25519.py", "_tray.py", "_toast.py",
              "tray.ico", "tray_busy.ico"]


def main():
    n = 0
    for name in CODE_FILES:
        a, b = os.path.join(REPO, name), os.path.join(SRC, name)
        if not os.path.exists(a):
            print("仓库里没有 %s，跳过" % name)
            continue
        data = io.open(a, "rb").read()
        if os.path.exists(b) and io.open(b, "rb").read() == data:
            print("  一致  %-16s" % name)
            continue
        io.open(b, "wb").write(data)
        n += 1
        print("  已同步 %-16s %s 字节  %s" % (name, format(len(data), ","),
                                              hashlib.sha256(data).hexdigest()[:12]))
    print("共同步 %d 个文件" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
