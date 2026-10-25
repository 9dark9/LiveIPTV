# -*- coding: utf-8 -*-
"""LIVE直播源 · 判据单测（不导入主程序，避免触发建目录/读配置等顶层副作用）。

做法：用 ast 从 LIVE直播源.py 里把要测的**纯函数**摘出来单独 exec，再断言。
被摘的函数必须不依赖实例状态（guard_verdict / compute_stats 都是 @staticmethod）。

跑法：python tests/test_logic.py
"""
import ast
import io
import os
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "LIVE直播源.py")
WANT = ("guard_verdict", "compute_stats")

fails = []


def check(name, got, exp):
    ok = got == exp
    print("  [%s] %-42s got=%r exp=%r" % ("通过" if ok else "失败", name, got, exp))
    if not ok:
        fails.append(name)


def grab():
    """从源码里摘出 Updater 的指定静态方法，exec 成一个命名空间返回。"""
    tree = ast.parse(io.open(SRC, encoding="utf-8").read(), filename=SRC)
    found = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for sub in node.body:
            if isinstance(sub, ast.FunctionDef) and sub.name in WANT:
                mod = ast.Module(body=[sub], type_ignores=[])
                ast.fix_missing_locations(mod)
                ns = {}
                exec(compile(mod, SRC, "exec"), ns)
                found[sub.name] = ns[sub.name]
    missing = [w for w in WANT if w not in found]
    if missing:
        raise SystemExit("源码里没找到这些函数，测试先失效: %s" % missing)
    return found


def ch(group="央视", nsrc=1):
    return {"group": group, "sources": [{"url": "http://x/%d" % i} for i in range(nsrc)]}


def main():
    f = grab()
    gv, cs = f["guard_verdict"], f["compute_stats"]

    print("-" * 70)
    print("1. 缓存守卫 guard_verdict：本轮结果能不能覆盖上轮（空串=可以）")
    check("首次运行（上轮 0）→ 照旧写入", gv(0, 0), "")
    check("上轮 0、本轮有 → 照旧写入", gv(0, 120), "")
    check("本轮为空 → 不覆盖", gv(120, 0), "本轮没抓到任何频道")
    check("掉一半整（60/120）→ 可以覆盖", gv(120, 60), "")
    check("差一点过半（59/120）→ 不覆盖", gv(120, 59),
          "本轮只剩 59 个频道（上轮 120 个），掉得太狠")
    check("正常小掉（118/120）→ 可以覆盖", gv(120, 118), "")
    check("变多（200/120）→ 可以覆盖", gv(120, 200), "")

    print("-" * 70)
    print("2. compute_stats：统计口径没被守卫改动带歪")
    d = {"a": ch("央视"), "b": ch("卫视", 0), "c": ch("香港")}
    st = cs(d)
    check("频道数", st["channels"], 3)
    check("有源的频道数(可用)", st["live"], 2)
    check("源总数", st["sources"], 2)
    check("港澳台数", st["hkmt"], 1)
    check("空输入不炸", cs({})["channels"], 0)

    print("-" * 70)
    if fails:
        print("有 %d 条失败: %s" % (len(fails), ", ".join(fails)))
        return 1
    print("全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
