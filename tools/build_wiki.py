# -*- coding: utf-8 -*-
"""
SC 源码笔记 wiki 生成器（零依赖，纯标准库）
- 只渲染 SC 原版库（README / AGENTS / Mod开发参考组 / 01-引擎主线+明细），不含任何 mod 项目内容。
- 输出自包含静态站 docs\（无CDN，离线可开，GitHub Pages 从 /docs 目录部署）。
- 重新生成：python tools/build_wiki.py
"""
import html
import json
import os
import re
import sys
from pathlib import Path

SC_ROOT = Path(r"E:\数据\生存战争系列\SC完全学习笔记")
ENGINE = SC_ROOT / "01-引擎"
DETAIL = ENGINE / "明细"
OUT = SC_ROOT / "docs"  # GitHub Pages 从 /docs 目录部署

SITE_NAME = "SC 源码笔记"
SITE_SUB = "SURVIVALCRAFT · 行号级引擎笔记"
SITE_REPO = "https://github.com/3366434156/survivalcraft-notes"
SITE_URL = "https://3366434156.github.io/survivalcraft-notes/"  # 部署根（404 兜底页跳转用）
SEC_LABELS = {"总览": "总览", "Mod开发": "Mod 开发", "SC引擎": "引擎主线", "SC引擎·明细": "逐文件明细"}

HERO_HTML = """
<div class=hero><div class=hero-grid>
<a class=hcard href="学习路线.html"><span class=ico>🧭</span><b>人是这样上手的</b><span>做 mod / 读引擎 / 查问题，三条路线 + 20 词概念词典</span></a>
<a class=hcard href="AGENTS.html"><span class=ico>🤖</span><b>agent 从这进</b><span>30 秒心智模型 + 查库协议 8 步，挂全套参考</span></a>
<a class=hcard href="Mod开发配方.html"><span class=ico>🔎</span><b>直接查任务</b><span>“我想做 X”→ 照抄哪段原版代码（带行号）</span></a>
</div></div>
"""

# ---------- 收集源文件 ----------
def collect_sources():
    pages = []  # (section, src_path, out_rel, order)
    def add(section, src, out_rel, order):
        pages.append({"section": section, "src": src, "out": out_rel, "order": order})

    overview = [
        ("总览", SC_ROOT / "README.md", "index.html", 0),
        ("总览", SC_ROOT / "AGENTS.md", "AGENTS.html", 1),
        ("总览", SC_ROOT / "学习路线.md", "学习路线.html", 2),
    ]
    for sec, p, o, k in overview:
        if p.exists():
            add(sec, p, o, k)

    moddev = [
        ("Mod开发", "Mod开发配方.md", 0),
        ("Mod开发", "Mod开发配方2.md", 1),
        ("Mod开发", "Mod钩子总表.md", 2),
        ("Mod开发", "Mod钩子明细.md", 3),
        ("Mod开发", "数据格式参考.md", 4),
        ("Mod开发", "数据格式参考2.md", 5),
        ("Mod开发", "数据格式参考3.md", 6),
        ("Mod开发", "Mod排错手册.md", 7),
        ("Mod开发", "Mod排错手册2.md", 8),
        ("Mod开发", "Mod示例-数据驱动.md", 9),
        ("Mod开发", "Mod示例-代码方块.md", 10),
        ("Mod开发", "Mod示例-电力元件.md", 11),
        ("Mod开发", "Mod示例-自定义生物.md", 12),
        ("Mod开发", "Mod示例-自定义界面.md", 13),
        ("Mod开发", "Mod示例-自定义特效.md", 14),
        ("Mod开发", "Mod示例-自定义食物.md", 15),
    ]
    for sec, name, k in moddev:
        p = SC_ROOT / name
        if p.exists():
            add(sec, p, name.replace(".md", ".html"), k)

    if ENGINE.exists():
        mains = sorted(p for p in ENGINE.glob("*.md") if p.is_file())
        details = sorted(DETAIL.glob("*.md")) if DETAIL.exists() else []
        for f in mains:
            add("SC引擎", f, "01-引擎/" + f.name.replace(".md", ".html"), f.name)
        for f in details:
            add("SC引擎·明细", f, "01-引擎/明细/" + f.name.replace(".md", ".html"), f.name)
    return pages

# ---------- 最小 GFM 转换器 ----------
CODE_RE = re.compile(r"`([^`]+)`")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
ITAL_RE = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
IMG_COPIES = []  # (绝对路径, 输出相对路径)

def _stage_local_image(src_text, src_file):
    """本地图片引用 → 登记拷贝；返回站点内相对 src（原样），不存在则 None。"""
    if re.match(r"^https?://", src_text):
        return src_text
    abs_p = (src_file.parent / src_text).resolve()
    try:
        rel = abs_p.relative_to(SC_ROOT)
    except ValueError:
        return None
    if not abs_p.is_file():
        return None
    IMG_COPIES.append((abs_p, rel.as_posix()))
    return rel.as_posix()

def build_registry(pages):
    reg = {}
    for p in pages:
        reg[os.path.normcase(str(p["src"].resolve()))] = p["out"]
    return reg

def rewrite_link_target(href, src_file, reg):
    m = re.match(r"^([^#]+)(#.*)?$", href)
    if not m:
        return None
    target, frag = m.group(1), m.group(2) or ""
    if not target.lower().endswith(".md"):
        return ("keep", href)
    abs_target = os.path.normcase(str((src_file.parent / target).resolve()))
    if abs_target in reg:
        # reg 值是站点根相对路径；子页引用须按自身深度补 ../ 前缀（根页 relpath='.' → 无前缀）
        depth = os.path.relpath(SC_ROOT, src_file.parent)
        prefix = "" if depth == "." else depth.replace(os.sep, "/") + "/"
        return ("ok", prefix + reg[abs_target] + frag)
    return ("dead", None)  # 不在站点内 → 置灰不可点

def inline(text, src_file, reg):
    text = html.escape(text, quote=False)
    # 已有实体（&lt; 等）在 escape 后变成 &amp;lt;，还原
    text = text.replace("&amp;lt;", "&lt;").replace("&amp;gt;", "&gt;").replace("&amp;amp;", "&amp;")
    spans = []
    def stash(m):
        # text 入口已整体 escape 过一次（作者实体已在上方还原），此处不能再逃逸——否则 <T> 会显示成 &lt;T&gt;
        spans.append("<code>%s</code>" % m.group(1))
        return "\x00%d\x00" % (len(spans) - 1)
    text = CODE_RE.sub(stash, text)
    def img(m):
        alt, src = m.group(1), m.group(2)
        staged = _stage_local_image(src, src_file)
        if staged is None:
            return '<span class="deadlink">[图片缺失: %s]</span>' % html.escape(src)
        return '<img src="%s" alt="%s" loading=lazy style="max-width:100%%;border:1px solid var(--line);border-radius:10px;box-shadow:var(--shadow-sm)">' % (
            html.escape(staged, quote=True), html.escape(alt, quote=True))
    text = IMG_RE.sub(img, text)
    def link(m):
        label, href = m.group(1), m.group(2)
        label = BOLD_RE.sub(r"<b>\1</b>", label)
        status, val = rewrite_link_target(href, src_file, reg)
        if status == "ok":
            return '<a href="%s">%s</a>' % (val, label)
        if status == "keep":
            return '<a href="%s">%s</a>' % (html.escape(href, quote=True), label)
        return '<span class="deadlink" title="引用的材料未随本站分发">%s ⟶未收录</span>' % label
    text = LINK_RE.sub(link, text)
    text = BOLD_RE.sub(r"<b>\1</b>", text)
    text = ITAL_RE.sub(r"<i>\1</i>", text)
    for i, s in enumerate(spans):
        text = text.replace("\x00%d\x00" % i, s)
    return text

def slug(t):
    return re.sub(r"[^\w\u4e00-\u9fff]+", "-", t).strip("-").lower()[:48]

# ---------- 构建时语法高亮（零运行时依赖：生成期直接产出带 span 的 HTML）----------
CS_KWS = frozenset("""abstract as base bool break byte case catch char checked class const continue decimal
default delegate do double else enum event explicit extern false finally fixed float for foreach get goto if
implicit in init int interface internal is lock long namespace new null object operator out override params
private protected public readonly record ref return sealed set short sizeof stackalloc static string struct
switch this throw true try typeof uint ulong unchecked unsafe ushort using var virtual void volatile when
where while yield""".split())

_RE_CSHARP = re.compile(
    r'(?P<comment>//[^\n]*|/\*.*?\*/)'
    r'|(?P<string>\$?@?"(?:[^"]|"")*"|\$?"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\')'
    r'|(?P<number>\b0[xX][0-9a-fA-F]+\b|\b\d(?:[\d_]*\.?[\d_]*)?[fFdDmMuUlL]*\b)'
    r'|(?P<word>[A-Za-z_][A-Za-z0-9_]*)', re.S)

_RE_XML = re.compile(
    r'(?P<comment><!--.*?-->)'
    r'|(?P<tag><[/?!?]?[\w:.-]*|/?>|\?>)'
    r'|(?P<string>"[^"]*")'
    r'|(?P<attr>[\w:.-]+)(?==)', re.S)

_RE_JSON = re.compile(
    r'(?P<key>"(?:[^"\\]|\\.)*")\s*:'
    r'|(?P<string>"(?:[^"\\]|\\.)*")'
    r'|(?P<number>-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b)'
    r'|(?P<kw>\b(?:true|false|null)\b)')

_HL_MAP = {"csharp": _RE_CSHARP, "cs": _RE_CSHARP, "xml": _RE_XML, "json": _RE_JSON}

def highlight(code, lang):
    pat = _HL_MAP.get((lang or "").lower())
    if pat is None:
        return html.escape(code)
    out, last = [], 0
    for m in pat.finditer(code):
        out.append(html.escape(code[last:m.start()], quote=False))
        g = m.lastgroup
        if g == "word":
            w = m.group("word")
            cls = "k" if w in CS_KWS else ("t" if w[0].isupper() else None)
            out.append(html.escape(w, quote=False) if cls is None else '<span class=%s>%s</span>' % (cls, html.escape(w, quote=False)))
        else:
            cls = {"comment": "c", "string": "s", "number": "n", "word": None,
                   "tag": "t2", "attr": "a", "key": "a", "kw": "k"}[g]
            out.append('<span class=%s>%s</span>' % (cls, html.escape(m.group(0), quote=False)))
        last = m.end()
    out.append(html.escape(code[last:], quote=False))
    return "".join(out)

def md_to_html(md_text, src_file, reg):
    lines = md_text.splitlines()
    out, i, n = [], 0, len(lines)
    para = []
    used_ids = set()
    toc = []  # (level, title, id)
    files = []  # (row-id, 文件名) —— 逐文件表登记
    def flush():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(para), src_file, reg))
            para.clear()
    while i < n:
        line = lines[i]
        s = line.strip()
        if s.startswith("```"):
            flush()
            lang = s[3:].strip()
            buf = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            pre_html = '<pre class="code%s"><code>%s</code></pre>' % (
                (" lang-" + lang) if lang else "", highlight("\n".join(buf), lang))
            out.append('<div class=codewrap><div class=codehead><span class="cdot d1"></span><span class="cdot d2"></span><span class="cdot d3"></span><span class=cinfo>%s</span></div>%s</div>' % (
                html.escape(lang or "text"), pre_html))
            continue
        if not s:
            flush(); i += 1; continue
        if re.match(r"^(-{3,}|\*{3,})$", s):
            flush(); out.append("<hr>"); i += 1; continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            flush(); lvl = len(m.group(1)); t = m.group(2)
            base = slug(t); hid = base; k = 2
            while hid in used_ids:
                hid = "%s-%d" % (base, k); k += 1
            used_ids.add(hid)
            if 2 <= lvl <= 3:
                toc.append((lvl, t, hid))
            out.append("<h%d id=\"%s\">%s</h%d>" % (lvl, hid, inline(t, src_file, reg), lvl))
            i += 1; continue
        if s.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|?$", lines[i+1].strip()):
            flush()
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip()); i += 1
            def cells(r):
                r = r.strip().strip("|")
                return [c.strip() for c in re.split(r"(?<!\\)\|", r)]
            head = cells(rows[0])
            body = [cells(r) for r in rows[2:]]
            is_filetable = bool(head) and ("文件" in head[0] or "符号" in head[0])
            fstart = len(files)
            th = "".join("<th>%s</th>" % inline(c, src_file, reg) for c in head)
            trs = []
            for r in body:
                r = (r + [""] * len(head))[:len(head)]
                rid = ""
                if is_filetable and r[0]:
                    raw = r[0].replace("`", "")
                    rid = "f-%d-%s" % (len(files), slug(raw) or "row")
                    while rid in used_ids:
                        rid += "x"
                    used_ids.add(rid)
                    files.append((rid, raw))
                trs.append("<tr%s>%s</tr>" % ((' id="%s"' % rid) if rid else "", "".join("<td>%s</td>" % inline(c, src_file, reg) for c in r)))
            tbl = '<div class="tablewrap%s"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
                " tall" if len(body) > 40 else "", th, "".join(trs))
            if is_filetable:
                cs = [(raw, rid) for rid, raw in files[fstart:] if ".cs" in raw]
                if len(cs) >= 3:
                    chip_html = "".join('<a href="#%s">%s</a>' % (rid, html.escape(raw)) for raw, rid in cs)
                    tbl = ('<details class=jumpbox><summary>⚡ 文件快速跳转 · %d</summary><div class=chips>%s</div></details>' % (len(cs), chip_html)) + tbl
            out.append(tbl)
            continue
        if s.startswith("> "):
            flush()
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip()); i += 1
            out.append("<blockquote>%s</blockquote>" % inline(" ".join(buf), src_file, reg))
            continue
        m = re.match(r"^-\s+(.*)$", s)
        if m:
            flush(); items = [m.group(1)]
            i += 1
            while i < n:
                s2 = lines[i].strip()
                m2 = re.match(r"^-\s+(.*)$", s2)
                if m2:
                    items.append(m2.group(1)); i += 1
                elif s2 and lines[i].startswith(("  ", "\t")):
                    items[-1] += " " + s2; i += 1
                else:
                    break
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % inline(it, src_file, reg) for it in items))
            continue
        m = re.match(r"^(\d+)[.、]\s+(.*)$", s)
        if m:
            flush(); items = [m.group(2)]; i += 1
            while i < n:
                m2 = re.match(r"^(\d+)[.、]\s+(.*)$", lines[i].strip())
                if m2:
                    items.append(m2.group(2)); i += 1
                else:
                    break
            out.append("<ol>%s</ol>" % "".join("<li>%s</li>" % inline(it, src_file, reg) for it in items))
            continue
        para.append(s); i += 1
    flush()
    return "\n".join(out), toc, files

# ---------- 页面模板 ----------
CSS = """
:root{
--bg:#f8fafc;--sheet:#ffffff;--surface-2:#f1f5f9;--side-bg:#f8fafc;
--ink:#0f172a;--ink-soft:#475569;--ink-faint:#94a3b8;
--line:#e6e9f0;--line-strong:#d5dbe5;
--acc:#4f46e5;--acc-2:#7c3aed;--acc-ink:#4338ca;--acc-soft:#eef2ff;
--top-bg:rgba(248,250,252,.82);--code-bg:#0f172a;--code-ink:#e2e8f0;
--shadow:0 1px 2px rgba(2,6,23,.05),0 12px 32px -8px rgba(2,6,23,.10);
--shadow-sm:0 1px 2px rgba(2,6,23,.06);
--header-h:58px;--side-w:264px}
:root[data-theme=dark]{
--bg:#0a0d14;--sheet:#10141f;--surface-2:#161c2b;--side-bg:#0c101a;
--ink:#e6e9f0;--ink-soft:#a6afc2;--ink-faint:#64708c;
--line:#1e2536;--line-strong:#2b3550;
--acc:#818cf8;--acc-2:#a78bfa;--acc-ink:#a5b4fc;--acc-soft:rgba(99,102,241,.16);
--top-bg:rgba(10,13,20,.78);--code-bg:#0b101c;--code-ink:#d7dee8;
--shadow:0 1px 2px rgba(0,0,0,.45),0 14px 36px -10px rgba(0,0,0,.55);
--shadow-sm:0 1px 2px rgba(0,0,0,.4)}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:calc(var(--header-h) + 20px)}
body{margin:0;font-family:ui-sans-serif,system-ui,"Segoe UI","Microsoft YaHei UI","Microsoft YaHei",-apple-system,sans-serif;
color:var(--ink);font-size:15px;line-height:1.8;
background:radial-gradient(1000px 460px at 78% -12%,rgba(99,102,241,.09),transparent 60%),
radial-gradient(820px 420px at -8% -4%,rgba(124,58,237,.06),transparent 55%),var(--bg);
transition:color .2s,background-color .2s}
::selection{background:var(--acc-soft);color:var(--acc-ink)}
::-webkit-scrollbar{width:10px;height:10px}
::-webkit-scrollbar-thumb{background:var(--line-strong);border-radius:8px;border:2px solid transparent;background-clip:content-box}
::-webkit-scrollbar-track{background:transparent}
/* 顶栏：玻璃 */
#top{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:12px;height:var(--header-h);padding:0 clamp(14px,2.5vw,24px);
background:var(--top-bg);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}
#burger{display:none;border:1px solid var(--line);background:var(--sheet);border-radius:9px;padding:5px 11px;font-size:16px;cursor:pointer;color:var(--ink);line-height:1.4}
#top .brand{display:flex;align-items:center;gap:9px;text-decoration:none;white-space:nowrap;min-width:0}
#top .brand b{font-size:16.5px;font-weight:700;color:var(--ink);letter-spacing:-.2px;display:flex;align-items:center;gap:9px}
#top .brand b::before{content:"";width:22px;height:22px;border-radius:7px;flex:0 0 22px;
background:linear-gradient(135deg,var(--acc),var(--acc-2));box-shadow:0 4px 12px rgba(99,102,241,.4)}
#top .brand small{font-size:10.5px;color:var(--ink-faint);letter-spacing:1.6px}
.searchwrap{position:relative;margin-left:auto;width:min(340px,38vw)}
#themeBtn{border:1px solid var(--line);background:var(--surface);border-radius:9px;padding:6px 10px;cursor:pointer;font-size:14px;line-height:1.2;color:var(--ink)}
#themeBtn:hover{border-color:var(--acc);box-shadow:0 0 0 3px var(--acc-soft)}
#top .gh{color:var(--ink-soft);font-size:12.5px;text-decoration:none;white-space:nowrap;border:1px solid var(--line);border-radius:9px;padding:6px 11px;background:var(--surface)}
#top .gh:hover{color:var(--acc);border-color:var(--acc)}
/* 布局 */
#layout{display:flex;min-height:calc(100vh - var(--header-h))}
#backdrop{display:none}
#side{width:var(--side-w);flex:0 0 var(--side-w);background:var(--side-bg);border-right:1px solid var(--line);position:sticky;top:var(--header-h);height:calc(100vh - var(--header-h));overflow-y:auto;padding:16px 12px 48px}
#side .sec{margin:18px 8px 6px;font-size:10.5px;font-weight:700;color:var(--ink-faint);letter-spacing:2.2px;text-transform:uppercase}
#side .sec:first-child{margin-top:4px}
#nav a{display:block;padding:5.5px 10px;margin:1px 0;border-radius:8px;color:var(--ink-soft);text-decoration:none;font-size:13.5px;line-height:1.5;transition:background .12s,color .12s}
#nav a:hover{background:var(--acc-soft);color:var(--acc-ink)}
#nav a.active{background:var(--acc-soft);color:var(--acc-ink);font-weight:600;box-shadow:inset 2px 0 0 var(--acc)}
/* 正文 + 右侧目录 */
#main{flex:1;min-width:0;padding:32px clamp(16px,3.5vw,44px) 80px}
#contentrow{display:flex;gap:34px;align-items:flex-start;justify-content:center;max-width:1240px;margin:0 auto}
article{flex:1;min-width:0;max-width:880px;background:var(--sheet);border:1px solid var(--line);border-radius:16px;padding:clamp(24px,4vw,46px) clamp(22px,4.5vw,50px);box-shadow:var(--shadow)}
h1{font-size:clamp(23px,3vw,29px);font-weight:800;letter-spacing:-.6px;margin:0 0 14px;
background:linear-gradient(120deg,var(--ink) 30%,var(--acc-ink));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
h2{font-size:clamp(18px,2.1vw,20.5px);font-weight:700;letter-spacing:-.3px;margin:42px 0 14px;padding-bottom:9px;border-bottom:1px solid var(--line)}
h3{font-size:16px;font-weight:700;margin:26px 0 10px}
p{margin:10px 0}
a{color:var(--acc-ink);text-decoration:none}
a:hover{text-decoration:underline;text-underline-offset:3px}
blockquote{margin:18px 0;padding:13px 18px;background:var(--acc-soft);border-left:3px solid var(--acc);border-radius:6px 12px 12px 6px;color:var(--ink-soft);font-size:14.5px}
blockquote p{margin:4px 0}
code{background:var(--surface-2);border:1px solid var(--line);border-radius:6px;padding:1px 6px;font-family:ui-monospace,Consolas,"Cascadia Mono",monospace;font-size:.86em;color:var(--acc-ink);overflow-wrap:break-word}
:root[data-theme=dark] code{color:#c7d2fe}
pre.code{background:var(--code-bg);color:var(--code-ink);border:1px solid var(--line);border-radius:12px;padding:16px 18px;overflow-x:auto;box-shadow:var(--shadow-sm)}
pre.code code{background:none;border:none;color:inherit;padding:0;font-size:13px;line-height:1.65;overflow-wrap:normal}
.tablewrap{overflow-x:auto;margin:16px 0;border:1px solid var(--line);border-radius:12px;background:var(--sheet);box-shadow:var(--shadow-sm)}
table{border-collapse:collapse;width:100%;font-size:13.5px;line-height:1.7}
th{background:var(--surface-2);color:var(--ink);font-weight:600;text-align:left}
th,td{border-bottom:1px solid var(--line);padding:8px 13px;vertical-align:top;overflow-wrap:break-word}
tbody tr:last-child td{border-bottom:none}
tbody tr{transition:background .1s}
tbody tr:hover{background:var(--acc-soft)}
hr{border:none;border-top:1px solid var(--line);margin:30px 0}
ul,ol{padding-left:1.5em;margin:10px 0}
li{margin:4px 0}
#foot{max-width:1240px;margin:40px auto 0;padding:14px 20px 0;border-top:1px solid var(--line);font-size:12px;color:var(--ink-faint);text-align:center;letter-spacing:.4px}
/* 语法高亮（GitHub Dark 色系，代码底两主题同色） */
pre.code .k{color:#ff7b72}
pre.code .t{color:#ffa657}
pre.code .s{color:#a5d6ff}
pre.code .c{color:#8b949e;font-style:italic}
pre.code .n{color:#79c0ff}
pre.code .a{color:#d2a8ff}
pre.code .t2{color:#7ee787}
/* 上一页/下一页 */
.pn{display:flex;gap:14px;margin:36px 0 6px}
.pn a{flex:1;min-width:0;display:flex;flex-direction:column;gap:3px;padding:14px 16px;border:1px solid var(--line);border-radius:12px;background:var(--sheet);text-decoration:none;transition:border-color .15s,transform .15s,box-shadow .15s}
.pn a:hover{border-color:var(--acc);transform:translateY(-2px);box-shadow:0 8px 20px -10px rgba(79,70,229,.35)}
.pn a.next{text-align:right}
.pn a small{color:var(--ink-faint);font-size:11.5px;letter-spacing:.5px}
.pn a b{color:var(--acc-ink);font-size:14px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.pn .pnvoid{flex:1}
/* 首页三入口卡片 */
.hero{margin:24px 0 4px}
.hero-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.hcard{position:relative;display:flex;flex-direction:column;gap:6px;padding:18px 18px 15px;border:1px solid var(--line);border-radius:14px;background:linear-gradient(180deg,var(--sheet),var(--surface-2));text-decoration:none;overflow:hidden;transition:transform .18s,border-color .18s,box-shadow .18s}
.hcard::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:linear-gradient(180deg,var(--acc),var(--acc-2));opacity:0;transition:opacity .18s}
.hcard:hover{transform:translateY(-3px);border-color:var(--acc);box-shadow:0 10px 26px -12px rgba(79,70,229,.4)}
.hcard:hover::before{opacity:1}
.hcard .ico{font-size:21px;line-height:1}
.hcard b{font-size:15.5px;color:var(--ink)}
.hcard span{font-size:12.5px;color:var(--ink-soft)}
/* 长表格：内部滚动 + 粘性表头 */
.tablewrap.tall{max-height:calc(100vh - 150px);overflow:auto}
.tablewrap.tall th{position:sticky;top:0;z-index:2;box-shadow:inset 0 -1px 0 var(--line-strong)}
@media(max-width:760px){.hero-grid{grid-template-columns:1fr}.pn{flex-direction:column}}
.deadlink{color:var(--ink-faint);border-bottom:1px dotted var(--line-strong)}
/* ── 交互层 ── */
#pbar{position:fixed;top:0;left:0;height:3px;width:0;z-index:40;background:linear-gradient(90deg,var(--acc),var(--acc-2));border-radius:0 3px 3px 0}
#btt{position:fixed;right:22px;bottom:26px;z-index:18;width:42px;height:42px;border-radius:12px;border:1px solid var(--line);background:var(--sheet);color:var(--acc);font-size:17px;cursor:pointer;opacity:0;pointer-events:none;transform:translateY(8px);transition:all .25s;box-shadow:var(--shadow-sm)}
#btt.show{opacity:1;pointer-events:auto;transform:none}
#btt:hover{border-color:var(--acc);box-shadow:0 0 0 3px var(--acc-soft);transform:translateY(-2px)}
pre.code{position:relative}
.copybtn{position:absolute;top:8px;right:8px;border:1px solid rgba(255,255,255,.16);background:rgba(255,255,255,.07);color:var(--code-ink);border-radius:7px;padding:3px 9px;font-size:11.5px;cursor:pointer;opacity:0;transition:all .18s}
pre.code:hover .copybtn{opacity:1}
.copybtn:hover{background:rgba(255,255,255,.15);border-color:var(--acc)}
.copybtn.ok{color:#4ade80;border-color:rgba(74,222,128,.6)}
.tablewrap{transition:box-shadow .2s,border-color .2s}
.tablewrap:hover{border-color:var(--line-strong);box-shadow:0 6px 24px -8px rgba(2,6,23,.18)}
tr[id] td:first-child{font-family:ui-monospace,Consolas,"Cascadia Mono",monospace;font-size:12.5px}
tr[id] td{transition:background .12s}
tr[id]:hover td{background:var(--acc-soft)}
#nav a{transition:background .15s,color .15s,padding-left .15s}
#nav a:hover{padding-left:15px}
#tocnav a{transition:color .12s,background .12s,padding-left .15s}
#tocnav a:hover{padding-left:15px}
.jumpbox{margin:12px 0 2px}
.jumpbox summary{cursor:pointer;font-size:12px;font-weight:600;color:var(--acc-ink);background:var(--acc-soft);border:1px solid var(--line);border-radius:9px;padding:5px 12px;display:inline-block;list-style:none;transition:all .15s;user-select:none}
.jumpbox summary::-webkit-details-marker{display:none}
.jumpbox summary:hover{border-color:var(--acc);box-shadow:0 0 0 3px var(--acc-soft)}
.chips{display:flex;flex-wrap:wrap;gap:5px;padding:9px 2px}
.chips a{font-family:ui-monospace,Consolas,monospace;font-size:11.5px;color:var(--ink-soft);background:var(--surface-2);border:1px solid var(--line);border-radius:7px;padding:2px 8px;text-decoration:none;transition:all .12s}
.chips a:hover{color:var(--acc-ink);border-color:var(--acc);background:var(--acc-soft);transform:translateY(-1px)}
.rv{opacity:0;transform:translateY(10px)}
.rv.in{opacity:1;transform:none;transition:opacity .45s ease,transform .45s ease}
@media (prefers-reduced-motion: reduce){.rv{opacity:1;transform:none}}
/* 右侧目录 */
#toc{flex:0 0 224px;position:sticky;top:calc(var(--header-h) + 26px);max-height:calc(100vh - var(--header-h) - 52px);overflow-y:auto;font-size:12.5px;line-height:1.5;padding:4px 0 20px}
.toc-title{font-size:11px;font-weight:700;letter-spacing:2px;color:var(--ink-faint);margin:8px 10px 10px;text-transform:uppercase}
#tocnav a{display:block;padding:4px 10px;border-left:2px solid var(--line);color:var(--ink-soft);text-decoration:none;border-radius:0 7px 7px 0;margin:1px 0}
#tocnav a.lvl3{padding-left:22px;font-size:12px;color:var(--ink-faint)}
#tocnav a:hover{color:var(--acc);text-decoration:none}
#tocnav a.active{color:var(--acc-ink);border-left-color:var(--acc);background:var(--acc-soft);font-weight:600}
@media(max-width:1279px){#toc{display:none}#contentrow{max-width:920px}}
/* 大屏加宽档：含 40+ 行大表的页(wideart)放得更开，散文页适度加宽 */
article.wideart{max-width:1060px}
@media(min-width:1600px){#contentrow{max-width:1580px}#foot{max-width:1580px}article{max-width:960px}article.wideart{max-width:1300px}}
@media(min-width:2000px){#contentrow{max-width:1720px}#foot{max-width:1720px}article{max-width:1020px}article.wideart{max-width:1420px}body{font-size:15.5px}table{font-size:14px}}
/* 窄屏 */
@media(max-width:1024px){
#burger{display:block}
#backdrop{position:fixed;inset:var(--header-h) 0 0 0;background:rgba(2,6,23,.42);z-index:14;opacity:0;pointer-events:none;transition:opacity .2s}
#backdrop.show{opacity:1;pointer-events:auto}
#side{position:fixed;left:calc(-1*var(--side-w) - 24px);top:var(--header-h);transition:left .2s ease;z-index:15;box-shadow:14px 0 36px rgba(2,6,23,.2)}
#side.open{left:0}
#top .gh{display:none}
#top .brand small{display:none}
.searchwrap{width:min(230px,50vw)}
.searchwrap kbd{display:none}
#main{padding:22px clamp(14px,3vw,24px) 70px}
article{padding:22px 18px 30px;border-radius:14px}
}
/* ── 高级交互层 ── */
#layout{position:relative;z-index:1}
.blob{position:fixed;border-radius:50%;filter:blur(70px);pointer-events:none;z-index:0}
.b1{width:560px;height:560px;top:-160px;right:-120px;background:radial-gradient(circle,rgba(99,102,241,.20),transparent 65%);animation:drift1 30s ease-in-out infinite alternate}
.b2{width:480px;height:480px;bottom:-140px;left:-140px;background:radial-gradient(circle,rgba(124,58,237,.15),transparent 65%);animation:drift2 36s ease-in-out infinite alternate}
:root[data-theme=dark] .blob{opacity:.7}
@keyframes drift1{to{transform:translate(-60px,80px) scale(1.08)}}
@keyframes drift2{to{transform:translate(70px,-60px) scale(1.12)}}
@media (prefers-reduced-motion: reduce){.blob{animation:none}}
article.spot{position:relative}
.spot::after{content:"";position:absolute;inset:0;border-radius:inherit;background:radial-gradient(560px circle at var(--mx,50%) var(--my,-30%),rgba(99,102,241,.06),transparent 46%);opacity:0;transition:opacity .4s;pointer-events:none}
.spot:hover::after{opacity:1}
.hcard::after{content:"";position:absolute;inset:0;background:radial-gradient(300px circle at var(--mx,50%) var(--my,50%),rgba(99,102,241,.13),transparent 50%);opacity:0;transition:opacity .3s;pointer-events:none}
.hcard:hover::after{opacity:1}
.searchwrap{display:flex;align-items:center;gap:8px;padding:7.5px 12px;border:1px solid var(--line);border-radius:10px;background:var(--surface-2);color:var(--ink-faint);font-size:13px;cursor:pointer;margin-left:auto;width:min(320px,36vw);transition:border-color .15s,box-shadow .15s}
.searchwrap:hover{border-color:var(--acc);box-shadow:0 0 0 3px var(--acc-soft)}
.searchwrap .ph{flex:1;text-align:left}
.searchwrap kbd{border:1px solid var(--line);border-radius:5px;padding:0 5px;font-size:10.5px;font-family:inherit}
#kmodal{position:fixed;inset:0;z-index:50;background:rgba(2,6,23,.5);backdrop-filter:blur(6px);display:none;align-items:flex-start;justify-content:center;padding-top:13vh}
#kmodal.show{display:flex}
#kpanel{width:min(620px,92vw);background:var(--sheet);border:1px solid var(--line);border-radius:16px;box-shadow:0 30px 80px rgba(2,6,23,.4);overflow:hidden;animation:kIn .18s ease}
@keyframes kIn{from{transform:scale(.96) translateY(-10px);opacity:0}}
.khead{display:flex;align-items:center;gap:10px;padding:14px 16px;border-bottom:1px solid var(--line)}
.kicon{color:var(--acc);font-size:16px}
#kinput{flex:1;border:none;outline:none;background:none;color:var(--ink);font-size:15px}
#kinput::placeholder{color:var(--ink-faint)}
.khead kbd,.kfoot kbd{border:1px solid var(--line);border-radius:5px;padding:1px 6px;font-size:11px;color:var(--ink-faint);font-family:inherit}
#kres{max-height:52vh;overflow:auto;padding:8px}
#kres a{display:flex;flex-direction:column;gap:2px;padding:9px 12px;border-radius:10px;text-decoration:none;color:var(--ink);transition:background .1s}
#kres a b{font-weight:600}
#kres a .snip{font-size:12px;color:var(--ink-faint)}
#kres a:hover,#kres a.sel{background:var(--acc-soft)}
#kres a.sel{outline:1.5px solid var(--acc)}
.kempty{padding:24px;text-align:center;color:var(--ink-faint);font-size:13.5px}
.kfoot{padding:9px 16px;border-top:1px solid var(--line);font-size:11.5px;color:var(--ink-faint);display:flex;gap:16px}
#lbox{position:fixed;inset:0;z-index:55;background:rgba(2,6,23,.78);backdrop-filter:blur(6px);display:none;align-items:center;justify-content:center;cursor:zoom-out}
#lbox.show{display:flex}
#lbox img{max-width:92vw;max-height:92vh;border-radius:12px;box-shadow:0 30px 80px rgba(0,0,0,.5);animation:lbIn .22s ease}
@keyframes lbIn{from{transform:scale(.94);opacity:0}}
article img{cursor:zoom-in;transition:transform .2s}
/* 代码块终端化 */
.codewrap{border:1px solid var(--line);border-radius:12px;overflow:hidden;margin:16px 0;background:var(--code-bg);box-shadow:var(--shadow-sm);transition:border-color .2s,box-shadow .2s}
.codewrap:hover{border-color:var(--acc);box-shadow:0 6px 26px -8px rgba(99,102,241,.35)}
.codehead{display:flex;align-items:center;gap:6px;padding:9px 14px;background:rgba(255,255,255,.045);border-bottom:1px solid rgba(255,255,255,.07)}
.cdot{width:10px;height:10px;border-radius:50%}
.d1{background:#ff5f57}.d2{background:#febc2e}.d3{background:#28c840}
.cinfo{margin-left:auto;font-size:11px;color:rgba(255,255,255,.45);font-family:ui-monospace,Consolas,monospace;letter-spacing:.5px}
pre.code{margin:0;border:none;border-radius:0;box-shadow:none}
/* 目录滑动指示器 */
#tocnav{position:relative}
.tocind{position:absolute;left:0;width:2px;background:linear-gradient(180deg,var(--acc),var(--acc-2));border-radius:2px;transition:top .25s cubic-bezier(.4,0,.2,1),height .25s}
#tocnav a.active{border-left-color:transparent}
/* 表格逐行瀑布 */
.rv tbody tr{opacity:0;transform:translateY(5px)}
.rv.in tbody tr{animation:rowIn .32s both;animation-delay:calc(var(--r,0)*14ms)}
@keyframes rowIn{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}
#top.scrolled{box-shadow:0 10px 28px -14px rgba(2,6,23,.28)}
@media (prefers-reduced-motion: reduce){.rv tbody tr{opacity:1;transform:none;animation:none}.tocind{transition:none}}
/* 手机档（置于 CSS 末尾保证覆盖上方 searchwrap 宽度）：搜索收成纯图标钮，把宽度让给品牌名 */
@media(max-width:600px){
.searchwrap{width:38px;padding:7.5px 0;justify-content:center}
.searchwrap .ph{display:none}
#top{gap:8px}
#top .brand b{font-size:15px;letter-spacing:-.1px;max-width:46vw;overflow:hidden;text-overflow:ellipsis}
}
@media print{
#top,#side,#backdrop,#toc,#foot,#burger,.searchwrap,#themeBtn{display:none!important}
body{background:#fff;color:#000}
#main{padding:0}#contentrow{display:block}
article{box-shadow:none;border:none;max-width:100%}
a{color:inherit}
}
"""
JS = """
const $=s=>document.querySelector(s);
const ROOT=%ROOT%; // 站点根相对前缀（按页面深度注入）
// 主题切换
const tbtn=$('#themeBtn');
function applyTheme(t){document.documentElement.dataset.theme=t;try{localStorage.setItem('theme',t)}catch(e){}tbtn.textContent=t==='dark'?'☀️':'🌙'}
applyTheme(document.documentElement.dataset.theme||'light');
tbtn.addEventListener('click',()=>applyTheme(document.documentElement.dataset.theme==='dark'?'light':'dark'));
// ⌘K 命令面板
let IDX=[];
fetch(ROOT+'search.json').then(r=>r.json()).then(d=>{IDX=d});
const kmodal=$('#kmodal'),kinput=$('#kinput'),kres=$('#kres'),kopen2=$('#search');
let ksel=0,khits=[];
function kRender(){
  const q=kinput.value.trim().toLowerCase();
  khits=q?IDX.filter(p=>p.t.toLowerCase().includes(q)||p.b.toLowerCase().includes(q)).slice(0,12):IDX.slice(0,8);
  ksel=0;
  kres.innerHTML=khits.map((p,i)=>{
    const j=q?p.b.toLowerCase().indexOf(q):-1;
    const snip=j>=0?p.b.slice(Math.max(0,j-18),j+46):'';
    return `<a href="${ROOT}${p.u}" class="${i===0?'sel':''}"><b>${p.t}</b><span class=snip>…${snip}…</span></a>`
  }).join('')||'<div class=kempty>无命中</div>';
}
function kOpen(){kmodal.classList.add('show');kinput.value='';kRender();setTimeout(()=>kinput.focus(),30)}
function kClose(){kmodal.classList.remove('show')}
function kMove(d){const as=[...kres.querySelectorAll('a')];if(!as.length)return;ksel=(ksel+d+as.length)%as.length;as.forEach((a,i)=>a.classList.toggle('sel',i===ksel));as[ksel].scrollIntoView({block:'nearest'})}
kopen2.addEventListener('click',kOpen);
kinput.addEventListener('input',kRender);
kmodal.addEventListener('click',e=>{if(e.target===kmodal)kClose()});
document.addEventListener('keydown',e=>{
  if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();kOpen()}
  else if(e.key==='/'&&document.activeElement!==kinput){e.preventDefault();kOpen()}
  else if(e.key==='Escape'){kClose()}
  else if(kmodal.classList.contains('show')&&kres.querySelector('a')){
    if(e.key==='ArrowDown'){e.preventDefault();kMove(1)}
    else if(e.key==='ArrowUp'){e.preventDefault();kMove(-1)}
    else if(e.key==='Enter'){e.preventDefault();const as=[...kres.querySelectorAll('a')];if(as[ksel])location.href=as[ksel].href}
  }
});
// 移动端侧栏抽屉
const burger=$('#burger'),side=$('#side'),backdrop=$('#backdrop');
function setSide(open){side.classList.toggle('open',open);backdrop.classList.toggle('show',open)}
burger.addEventListener('click',e=>{e.stopPropagation();setSide(!side.classList.contains('open'))});
document.addEventListener('click',e=>{if(window.innerWidth<=1024&&side.classList.contains('open')&&!side.contains(e.target)&&e.target!==burger)setSide(false)});
backdrop.addEventListener('click',()=>setSide(false));
// 高亮当前页
const here=decodeURIComponent(location.pathname.split('/').pop()||'index.html');
document.querySelectorAll('#nav a').forEach(a=>{if(decodeURIComponent(a.getAttribute('href')).endsWith(here))a.classList.add('active')});
// 右侧目录：滑动指示器 + 滚动高亮
const tocnav=$('#tocnav');
const tocLinks=[...document.querySelectorAll('#tocnav a')];
if(tocLinks.length){
  const tind=document.createElement('div');tind.className='tocind';tocnav.prepend(tind);
  const heads=tocLinks.map(a=>document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1))));
  const onScroll=()=>{
    let idx=0;
    for(let i=0;i<heads.length;i++){if(heads[i]&&heads[i].getBoundingClientRect().top<=100)idx=i}
    tocLinks.forEach((a,i)=>a.classList.toggle('active',i===idx));
    const a=tocLinks[idx];
    if(a){tind.style.top=a.offsetTop+'px';tind.style.height=a.offsetHeight+'px'}
  };
  document.addEventListener('scroll',onScroll,{passive:true});onScroll();
}
// 阅读进度条 + 回到顶部 + 顶栏收缩
const pbar=$('#pbar'),btt=$('#btt'),topEl=$('#top');
function onScroll2(){const h=document.documentElement;const max=h.scrollHeight-innerHeight;const pr=max>0?h.scrollTop/max:0;pbar.style.width=(pr*100).toFixed(2)+'%';btt.classList.toggle('show',h.scrollTop>600);topEl.classList.toggle('scrolled',h.scrollTop>10)}
document.addEventListener('scroll',onScroll2,{passive:true});onScroll2();
btt.addEventListener('click',()=>scrollTo({top:0,behavior:'smooth'}));
// 代码块复制按钮
document.querySelectorAll('pre.code').forEach(pre=>{
  const b=document.createElement('button');b.className='copybtn';b.textContent='复制';
  b.addEventListener('click',async()=>{const txt=pre.innerText;let ok=false;
    try{await navigator.clipboard.writeText(txt);ok=true}catch(e){
      try{const ta=document.createElement('textarea');ta.value=txt;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();ok=document.execCommand('copy');ta.remove()}catch(e2){}}
    b.textContent=ok?'✓ 已复制':'失败';
    if(ok){b.classList.add('ok');setTimeout(()=>{b.textContent='复制';b.classList.remove('ok')},1400)}});
  pre.appendChild(b);
});
// 区块滚动淡入 + 表格逐行瀑布 + 卡片跟随光晕 + 图片灯箱
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{threshold:.05});
document.querySelectorAll('article > .tablewrap, article > .codewrap, article > blockquote').forEach(el=>{
  el.classList.add('rv');io.observe(el);
  el.querySelectorAll('tbody tr').forEach((tr,i)=>tr.style.setProperty('--r',Math.min(i,24)));
});
document.querySelectorAll('.spot,.hcard').forEach(el=>{
  el.addEventListener('mousemove',e=>{
    const r=el.getBoundingClientRect();
    el.style.setProperty('--mx',(e.clientX-r.left)+'px');
    el.style.setProperty('--my',(e.clientY-r.top)+'px');
  });
});
const lb=document.createElement('div');lb.id='lbox';lb.innerHTML='<img alt="">';document.body.appendChild(lb);
document.querySelector('article').addEventListener('click',e=>{
  if(e.target.tagName==='IMG'){lb.querySelector('img').src=e.target.src;lb.classList.add('show')}
  else if(lb.classList.contains('show'))lb.classList.remove('show');
});
lb.addEventListener('click',()=>lb.classList.remove('show'));
document.addEventListener('keydown',e=>{if(e.key==='Escape')lb.classList.remove('show')});
"""

def page_shell(title, body_html, nav_html, root_prefix, toc_html, aside_extra, wide=False):
    artcls = ' class="spot wideart"' if wide else " class=spot"
    js = JS.replace("%ROOT%", json.dumps(root_prefix))
    title_suffix = "" if title == SITE_NAME else " · %s" % SITE_NAME
    return ("<!doctype html><html lang=zh><head><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            "<script>(function(){try{var t=localStorage.getItem('theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');document.documentElement.dataset.theme=t}catch(e){}})()</script>"
            "<title>%s%s</title><style>%s</style></head><body>"
            "<div id=pbar></div>"
            "<div class=\"blob b1\"></div><div class=\"blob b2\"></div>"
            "<header id=top>"
            "<button id=burger aria-label=目录>☰</button>"
            "<a class=brand href=\"%sindex.html\"><b>%s</b><small>%s</small></a>"
            "<div class=searchwrap id=search title='搜索（⌘K）'><span class=kicon>⌕</span><span class=ph>搜索…</span><kbd>⌘K</kbd></div>"
            "<button id=themeBtn aria-label=切换主题>🌙</button>"
            "<a class=gh href=\"%s\" target=_blank rel=noopener>GitHub ↗</a>"
            "</header>"
            "<div id=layout><aside id=side><nav id=nav>%s</nav></aside>"
            "<main id=main><div id=contentrow><article%s>%s</article><aside id=toc>%s%s</aside></div>"
            "<div id=foot>%s · 由 tools/build_wiki.py 生成</div>"
            "</main></div>"
            "<div id=backdrop></div>"
            "<div id=kmodal><div id=kpanel><div class=khead><span class=kicon>⌕</span><input id=kinput placeholder='搜索全部页面…' autocomplete=off><kbd>ESC</kbd></div><div id=kres></div><div class=kfoot><span>↑↓ 选择</span><span>Enter 打开</span><span>ESC 关闭</span></div></div></div>"
            "<button id=btt aria-label=回到顶部>↑</button>"
            "<script>%s</script></body></html>"
            ) % (html.escape(title), title_suffix, CSS, root_prefix, SITE_NAME, SITE_SUB, SITE_REPO, nav_html, artcls, body_html, toc_html, aside_extra, SITE_NAME, js)

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    pages = collect_sources()
    if not pages:
        print("no sources"); return
    reg = build_registry(pages)
    OUT.mkdir(parents=True, exist_ok=True)
    nav = []
    cur_sec = None
    counts = {}
    for p in pages:
        counts[p["section"]] = counts.get(p["section"], 0) + 1
    ordered = sorted(pages, key=lambda x: (["总览", "Mod开发", "SC引擎", "SC引擎·明细"].index(x["section"]), x["order"]))
    for p in ordered:
        if p["section"] != cur_sec:
            cur_sec = p["section"]
            nav.append('<div class=sec>%s · %d</div>' % (SEC_LABELS[cur_sec], counts[cur_sec]))
        nav.append('<a href="%s">%s</a>' % (p["out"], html.escape(p["src"].stem)))
    nav_html = "".join(nav)

    index_data = []
    built = []
    for p in pages:
        md = p["src"].read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^#\s+(.+)$", md, re.M)
        title = m.group(1).strip() if m else p["src"].stem
        body, toc, files = md_to_html(md, p["src"], reg)
        built.append((p, title, body, toc, files))
    files_map = {p["src"].name: files for p, title, body, toc, files in built}

    for p, title, body, toc, files in built:
        toc_items = "".join('<a class="lvl%d" href="#%s">%s</a>' % (lvl, hid, html.escape(re.sub(r"[*`]", "", t))) for lvl, t, hid in toc)
        toc_html = ('<div class=toc-title>本页目录</div><nav id=tocnav>%s</nav>' % toc_items) if toc_items else ""
        aside_extra = ""
        if p["section"] == "SC引擎":
            mnum = re.match(r"^(\d{2})-", p["src"].stem)
            if mnum:
                num = mnum.group(1)
                chips = []
                for dname in sorted(files_map):
                    if re.match(num + r"[ab]-", dname):
                        for rid, raw in files_map[dname]:
                            if ".cs" in raw:
                                chips.append('<a href="明细/%s#%s">%s</a>' % (dname.replace(".md", ".html"), rid, html.escape(raw)))
                if chips:
                    aside_extra = ('<details class=jumpbox open><summary>⚡ 文件速跳 · %d</summary><div class=chips>%s</div></details>'
                                   % (len(chips), "".join(chips)))
        out_path = OUT / p["out"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        root_prefix = "../" * p["out"].count("/")
        # 侧栏导航是全站共用一份（相对站点根），子页必须按深度补 ../ 前缀，否则子页侧栏全 404。
        # 注意替换串不带收口引号——引号要在原 href 值之后闭合
        page_nav = nav_html.replace('<a href="', '<a href="%s' % root_prefix) if root_prefix else nav_html
        # 上一页/下一页（全站阅读序 = 侧栏顺序）
        idx = ordered.index(p)
        def _pnlink(pp, label, nxt):
            if pp is None:
                return '<span class=pnvoid></span>'
            return ('<a class="%s" href="%s%s"><small>%s · %s</small><b>%s</b></a>'
                    % ("next" if nxt else "prev", root_prefix, pp["out"], label,
                       html.escape(pp["section"]), html.escape(pp["src"].stem)))
        pn = '<nav class=pn>%s%s</nav>' % (
            _pnlink(ordered[idx - 1] if idx > 0 else None, "上一页", False),
            _pnlink(ordered[idx + 1] if idx < len(ordered) - 1 else None, "下一页", True))
        page_body = (HERO_HTML + body) if p["out"] == "index.html" else body
        # 任一表 >20 行的页面放宽正文列（构建期已知，散文页保持舒适行宽）
        wide = any(ch.count("<tr") > 20 for ch in re.split(r'class="tablewrap', body))
        out_path.write_text(page_shell(title, page_body + pn, page_nav, root_prefix, toc_html, aside_extra, wide), encoding="utf-8")
        text_sample = re.sub(r"[`#>*|\-\[\]()]", "", md)[:26000]
        index_data.append({"t": title, "u": p["out"], "b": text_sample.lower()})
        print("OK", p["out"])

    (OUT / "search.json").write_text(json.dumps(index_data, ensure_ascii=False), encoding="utf-8")
    write_404()
    # 清理改名/删页残留：docs 下不属于本次产物的 html 一律移除（构建器只写不删会留陈旧页）
    keep = {p["out"] for p in pages} | {"404.html"}
    for root, dirs, files in os.walk(OUT):
        for f in files:
            if f.endswith(".html"):
                rel = os.path.relpath(os.path.join(root, f), OUT).replace(os.sep, "/")
                if rel not in keep:
                    os.remove(os.path.join(root, f))
                    print("PRUNED", rel)
    for abs_p, rel in IMG_COPIES:
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(abs_p.read_bytes())
    print("DONE pages=%d images=%d out=%s" % (len(pages), len(IMG_COPIES), OUT))


def write_404():
    """GitHub Pages 对任意 404 路径都会伺服 /404.html：取失效 URL 的最后一段文件名，
    在 search.json 里按输出文件名匹配，命中即跳到该页现址（页面改路径/改目录后老链接自动着陆）；
    未命中或非 .html 请求回首页。GitHub Pages 对 404 路径不带查询串，无需处理参数。"""
    js = """
const BASE=%BASE%;
const seg=decodeURIComponent(location.pathname).split('/').pop()||'';
const box=document.getElementById('m404');
if(seg&&seg.endsWith('.html')){
  fetch(BASE+'search.json').then(r=>r.json()).then(list=>{
    const hit=list.find(e=>e.u&&e.u.split('/').pop()===seg);
    box.textContent=hit?('找到同名页面，正在跳转：'+hit.t):('没有找到「'+seg+'」，返回首页…');
    setTimeout(()=>location.replace(hit?BASE+hit.u:BASE),1200);
  }).catch(()=>location.replace(BASE));
}else{box.textContent='返回首页…';setTimeout(()=>location.replace(BASE),1200);}
""".replace("%BASE%", json.dumps(SITE_URL))
    html404 = (
        '<!doctype html><html lang=zh><head><meta charset=utf-8>'
        '<meta name=viewport content="width=device-width,initial-scale=1">'
        '<title>404 · %s</title><style>'
        'body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;'
        'background:#f8fafc;color:#0f172a;font:15px/1.7 system-ui,"Segoe UI","Microsoft YaHei",sans-serif}'
        '.card{max-width:520px;padding:44px 48px;background:#fff;border:1px solid #e6e9f0;border-radius:16px;'
        'box-shadow:0 8px 28px rgba(15,23,42,.06);text-align:center}'
        'h1{margin:0 0 6px;font-size:44px;background:linear-gradient(90deg,#4f46e5,#7c3aed);'
        '-webkit-background-clip:text;background-clip:text;color:transparent}'
        'p{margin:10px 0 0;color:#475569}a{color:#4f46e5}'
        '</style></head><body><div class=card><h1>404</h1>'
        '<p id=m404>页面可能已搬家，正在为你定位…</p>'
        '<p><a href="%sindex.html">手动返回首页</a></p></div>'
        '<script>%s</script></body></html>'
    ) % (SITE_NAME, SITE_URL, js)
    (OUT / "404.html").write_text(html404, encoding="utf-8")
    print("OK 404.html")

if __name__ == "__main__":
    main()
