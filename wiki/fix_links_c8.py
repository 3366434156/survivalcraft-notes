# -*- coding: utf-8 -*-
"""C8 迁库收尾：跨库链接修整。运行一次即可，可重复（幂等）。"""
import re
from pathlib import Path

SC = Path(r"E:\数据\生存战争系列\SC完全学习笔记")
PW = Path(r"E:\数据\生存战争系列\SC与完美世界完全学习笔记")
SC_ABS = "E:\\数据\\生存战争系列\\SC完全学习笔记\\10-SC引擎\\"

# 1) SC 库页面：指向完美世界姊妹库的链接 → 置灰文字
n1 = 0
for f in (SC / "10-SC引擎").glob("*.md"):
    t = f.read_text(encoding="utf-8")
    t2, k = re.subn(
        r"\[([^\]]+)\]\((?:\.\.[\\/])?(?:20-完美世界2\.4|30-经验坑洞|40-外部资源)[\\/][^)]+\)",
        r"\1（→完美世界姊妹库）", t)
    if k:
        f.write_text(t2, encoding="utf-8"); n1 += k
        print("SC页", f.name, "×", k)

# 2) 主库：指向 ../10-SC引擎/ 的链接 → SC 库绝对路径文字
n2 = 0
for f in PW.rglob("*.md"):
    if "90-原始报告" in str(f):
        continue
    t = f.read_text(encoding="utf-8")
    t2, k = re.subn(
        r"\[([^\]]+)\]\(\.\./10-SC引擎/([^)#]+)(#[^)]*)?\)",
        lambda m: "%s（SC库：%s%s）" % (m.group(1), SC_ABS, m.group(2)), t)
    if k:
        f.write_text(t2, encoding="utf-8"); n2 += k
        print("PW页", f.name, "×", k)

# 3) 主库 45 菜谱：第一节收拢为指针（避免双头漂移）
p45 = PW / "45-原版范例菜谱.md"
t = p45.read_text(encoding="utf-8")
i = t.find("## 一、SC 原版引擎范例")
j = t.find("## 二、")
if 0 <= i < j:
    new = ("## 一、SC 原版引擎范例 → 已独立成库\n\n"
           "SC 原版范例总表迁至 **E:\\数据\\生存战争系列\\SC完全学习笔记\\45-SC原版范例菜谱.md**"
           "（独立库随仓库上传；含 AI/方块/地形/子系统/存档/渲染/UI/弹道分类，随波次回填）。\n\n"
           "本节不再在此维护，避免双头漂移。\n\n")
    p45.write_text(t[:i] + new + t[j:], encoding="utf-8")
    print("45菜谱 第一节已收拢")

# 4) 主库 README：SC 引擎侧路由表改为指向独立库
pRD = PW / "README.md"
t = pRD.read_text(encoding="utf-8")
i = t.find("### SC 引擎侧")
j = t.find("### 本项目侧")
if 0 <= i < j:
    new = ("### SC 引擎侧 → 已独立成库\n\n"
           "| 我想问… | 看这页 |\n|---|---|\n"
           "| SC 引擎 15 域页面 + 02a/03a/04a/05a 逐文件明细 + SC 范例菜谱 | "
           "独立库 `E:\\数据\\生存战争系列\\SC完全学习笔记\\`（README 页面地图 · 10-SC引擎\\ · 45-SC原版范例菜谱.md；wiki 站 wiki\\site\\README.html） |\n\n")
    pRD.write_text(t[:i] + new + t[j:], encoding="utf-8")
    print("README SC 侧已改指独立库")

print("DONE sc_links=%d pw_links=%d" % (n1, n2))
