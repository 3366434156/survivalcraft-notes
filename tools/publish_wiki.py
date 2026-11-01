# -*- coding: utf-8 -*-
"""把本库内容镜像到 GitHub Wiki：tools/publish_wiki.py

- 镜像范围：AGENTS/学习路线 + Mod开发 16 页 + 引擎主线 24 页 + 明细 20 页（与站点同源，README 不镜像——Home 替代）
- 链接改写：仓库内 .md 相对链接 → Wiki 平面页名（去目录、去锚点；README.md → Home）；图片 → raw.githubusercontent 绝对地址
- Wiki 由本脚本全权托管：不在镜像集合里的旧 .md 会被删除（用户手写页会被清掉，谨慎）
- 初始化：Wiki 无页面时先经 REST API 播种 Home（之后 git 仓库才存在）
- 同步：临时目录 clone → 覆盖/删除 → 变化才 commit/push；git 直连失败自动改走 127.0.0.1:7897 代理
"""
import os, re, stat, subprocess, sys, tempfile, shutil, json, pathlib

def rmtree_ro(p):
    """Windows 下 .git 只读对象挡 rmtree：逐个 chmod 后重试"""
    shutil.rmtree(p, onerror=lambda f, path, exc: (os.chmod(path, stat.S_IWRITE), f(path)))

REPO = pathlib.Path(__file__).resolve().parent.parent
OWNER, NAME = "3366434156", "survivalcraft-notes"
WIKI_GIT = "https://github.com/%s/%s.wiki.git" % (OWNER, NAME)
RAW_BASE = "https://raw.githubusercontent.com/%s/%s/main/" % (OWNER, NAME)
PROXY = "http://127.0.0.1:7897"

MIRRor = []  # (wiki 页名, 源文件相对路径)
for name in ["AGENTS.md", "学习路线.md"]:
    MIRRor.append((name[:-3], name))
for name in ["Mod开发配方.md", "Mod开发配方2.md", "Mod钩子总表.md", "Mod钩子明细.md",
             "数据格式参考.md", "数据格式参考2.md", "数据格式参考3.md",
             "Mod排错手册.md", "Mod排错手册2.md", "Mod示例-数据驱动.md", "Mod示例-代码方块.md",
             "Mod示例-电力元件.md", "Mod示例-自定义生物.md", "Mod示例-自定义界面.md",
             "Mod示例-自定义特效.md", "Mod示例-自定义食物.md"]:
    MIRRor.append((name[:-3], name))
ENGINE = REPO / "01-引擎"
for f in sorted(ENGINE.glob("*.md")):
    MIRRor.append((f.stem, "01-引擎/" + f.name))
for f in sorted((ENGINE / "明细").glob("*.md")):
    MIRRor.append((f.stem, "01-引擎/明细/" + f.name))

def run(cmd, cwd=None, proxy=False):
    args = list(cmd)
    if proxy:
        args = ["-c", "http.proxy=" + PROXY, "-c", "https.proxy=" + PROXY] + args
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")

LINK_RE = re.compile(r"(\[)([^\]]*)(\]\()([^)\s]+)([^)]*\))")

def rewrite_links(text, src_rel):
    def sub(m):
        label, target, tail = m.group(2), m.group(4), m.group(5)
        if target.startswith(("http://", "https://", "#")):
            return m.group(0)
        if target.endswith((".png", ".jpg", ".webp", ".gif")):
            # 图片 → 主仓库 raw 绝对地址（Wiki 不托管图片）
            return "%s%s(%smedia/%s%s" % (m.group(1), label, m.group(3), os.path.basename(target), tail)
        if target.endswith(".md"):
            base = os.path.basename(target)[:-3]
            page = "Home" if base == "README" else base
            return "[%s](%s)" % (label, page)
        return m.group(0)
    return LINK_RE.sub(sub, text)

def build_pages(stage):
    stage.mkdir(parents=True, exist_ok=True)
    for page, rel in MIRRor:
        src = REPO / rel
        text = src.read_text(encoding="utf-8")
        (stage / (page + ".md")).write_text(rewrite_links(text, rel), encoding="utf-8")
    # Home（Wiki 专用入口，比 README 更贴 Wiki 场景）
    home = ["# SC 源码笔记 · Wiki",
            "",
            "> Survivalcraft 引擎（1644 个 .cs）的行号级学习笔记，**优先为 AI agent 开发 mod 服务**。",
            "> 本 Wiki 与 [在线交互版](https://%s.github.io/%s/) 同源（搜索/双主题/文件速跳在那边更完整）。" % (OWNER, NAME),
            "",
            "## 三条上手路径",
            "",
            "| 我是谁 | 入口 |",
            "|---|---|",
            "| **AI agent**（首选） | [AGENTS](AGENTS)——30 秒心智模型 + 查库协议 8 步，挂全套参考 |",
            "| **mod 开发者** | [学习路线](学习路线) → [Mod开发配方](Mod开发配方)（任务→照抄哪里） |",
            "| **查问题** | [Mod排错手册](Mod排错手册)（250 条按症状）/ [24-机制全链](24-机制全链)（跨域挂点） |",
            "",
            "## agent 十件套",
            "",
            "Mod开发配方（精选）/ [Mod开发配方2](Mod开发配方2)（全量 235 条）· [Mod钩子总表](Mod钩子总表)/[明细](Mod钩子明细)（236 钩子）· [数据格式参考](数据格式参考)/[2](数据格式参考2)/[3](数据格式参考3) · [Mod排错手册](Mod排错手册)/[2](Mod排错手册2) · 端到端示例×7（[数据驱动](Mod示例-数据驱动)/[代码方块](Mod示例-代码方块)/[电力元件](Mod示例-电力元件)/[自定义生物](Mod示例-自定义生物)/[自定义界面](Mod示例-自定义界面)/[自定义特效](Mod示例-自定义特效)/[自定义食物](Mod示例-自定义食物)）",
            "",
            "## 引擎主线（24 页）",
            "",
            "| 页 | 页 | 页 |",
            "|---|---|---|"]
    mains = [p for p, rel in MIRRor if rel.startswith("01-引擎/") and rel.count("/") == 1]
    for i in range(0, len(mains), 3):
        home.append("| " + " | ".join("[%s](%s)" % (p, p) for p in mains[i:i + 3]) + " |")
    home += ["", "## 逐文件明细（20 页）", "", "02a · 03a · 04a · 05a · 06a · 07a · 08a · 09a · 10a · 11a · 12a · 15a · 16a/16b · 17a · 18a · 19a · 20a · 21a · 22a —— 各自主线页右侧/文内可直达；明细页直接按页名搜索打开。",
             "",
             "## 源码",
             "",
             "- 引擎源码仓库：https://gitee.com/SC-SPM/SurvivalcraftApi （公开，大陆可直连克隆）",
             "- 页内源码引用 = 仓库相对路径+实读行号（如 `Survivalcraft\\Game\\Program.cs:78`），克隆后按同名文件定位。"]
    (stage / "Home.md").write_text("\n".join(home), encoding="utf-8")
    # Sidebar
    sb = ["**总览**", "", "- [Home](Home)", "- [AGENTS](AGENTS)（agent 入口）", "- [学习路线](学习路线)", "",
          "**Mod 开发**", ""]
    for p, rel in MIRRor:
        if rel.startswith("Mod") or rel.startswith("数据格式"):
            sb.append("- [%s](%s)" % (p, p))
    sb += ["", "**引擎主线**", ""]
    for p, rel in MIRRor:
        if rel.startswith("01-引擎/") and rel.count("/") == 1:
            sb.append("- [%s](%s)" % (p, p))
    sb += ["", "**逐文件明细**", ""]
    for p, rel in MIRRor:
        if rel.startswith("01-引擎/明细/"):
            sb.append("- [%s](%s)" % (p, p))
    (stage / "_Sidebar.md").write_text("\n".join(sb), encoding="utf-8")
    (stage / "_Footer.md").write_text(
        "本 Wiki 由 `tools/publish_wiki.py` 自动镜像（内容以 [在线交互版](https://%s.github.io/%s/) 为准）· 引擎源码：<https://gitee.com/SC-SPM/SurvivalcraftApi>" % (OWNER, NAME),
        encoding="utf-8")

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    stage = pathlib.Path(tempfile.gettempdir()) / "sc-wiki-stage"
    if stage.exists():
        rmtree_ro(stage)
    build_pages(stage)
    # clone；wiki 未初始化时 clone 404 → 本地 init + 首推（GitHub 会在首推时创建 wiki 仓库）
    wdir = pathlib.Path(tempfile.gettempdir()) / "sc-wiki-sync"
    if wdir.exists():
        rmtree_ro(wdir)
    code, out = run(["clone", WIKI_GIT, str(wdir)])
    initialized = code == 0
    if not initialized:
        code, out = run(["clone", WIKI_GIT, str(wdir)], proxy=True)
        initialized = code == 0
    if not initialized:
        wdir.mkdir(parents=True, exist_ok=True)
        run(["init", "-b", "master"], cwd=str(wdir))
        run(["remote", "add", "origin", WIKI_GIT], cwd=str(wdir))
        print("wiki 仓库不可克隆，走首推初始化")
    # 同步：写镜像页，删除不属于镜像的 .md
    keep = {p + ".md" for p, _ in MIRRor} | {"Home.md", "_Sidebar.md", "_Footer.md"}
    for old in wdir.glob("*.md"):
        if old.name not in keep:
            old.unlink()
    for f in stage.glob("*.md"):
        shutil.copy(f, wdir / f.name)
    run(["add", "-A"], cwd=str(wdir))
    code, out = run(["status", "--porcelain"], cwd=str(wdir))
    if not out.strip() and initialized:
        print("Wiki 已是最新，无变更。")
        return 0
    run(["-c", "user.name=3366434156", "-c", "user.email=3366434156@users.noreply.github.com",
         "commit", "-m", "镜像同步：站点 %d 页（Home/侧边栏/十件套/24 主线/20 明细）" % len(keep)], cwd=str(wdir))
    branch = "master"
    code, out = run(["push", "-u", "origin", branch], cwd=str(wdir))
    if code != 0 and "fetch first" in out:
        # 远端有播种提交（用户手建首页）：收编后以镜像为准重放
        run(["fetch", "origin", branch], cwd=str(wdir), proxy=True)
        run(["rebase", "-X", "theirs", "origin/" + branch], cwd=str(wdir))
        code, out = run(["push", "-u", "origin", branch], cwd=str(wdir))
    if code != 0:
        code, out = run(["push", "-u", "origin", branch], cwd=str(wdir), proxy=True)
    print("push:", "OK" if code == 0 else out[:400])
    return 0 if code == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
