# -*- coding: utf-8 -*-
"""
SC 源码笔记 wiki 生成器（零依赖，纯标准库）
- 只渲染 SC 原版库（README / AGENTS / 00-规则 / 02-范例配方 / 01-引擎主线+明细），不含任何 mod 项目内容。
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
SEC_LABELS = {"总览": "总览", "Mod开发": "Mod开发", "SC引擎": "引擎主线", "SC引擎·明细": "逐文件明细"}

# ---------- 收集源文件 ----------
def collect_sources():
    pages = []  # (section, src_path, out_rel, order)
    def add(section, src, out_rel, order):
        pages.append({"section": section, "src": src, "out": out_rel, "order": order})

    overview = [
        ("总览", SC_ROOT / "README.md", "index.html", 0),
        ("总览", SC_ROOT / "AGENTS.md", "AGENTS.html", 1),
    ]
    for sec, p, o, k in overview:
        if p.exists():
            add(sec, p, o, k)

    moddev = [
        ("Mod开发", "Mod开发配方.md", 0),
        ("Mod开发", "Mod钩子总表.md", 1),
        ("Mod开发", "Mod钩子明细.md", 2),
        ("Mod开发", "数据格式参考.md", 3),
        ("Mod开发", "数据格式参考2.md", 4),
        ("Mod开发", "Mod排错手册.md", 5),
        ("Mod开发", "Mod排错手册2.md", 6),
        ("Mod开发", "Mod示例-数据驱动.md", 7),
        ("Mod开发", "Mod示例-代码方块.md", 8),
        ("Mod开发", "Mod示例-电力元件.md", 9),
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
        return ("ok", reg[abs_target] + frag)
    return ("dead", None)  # 不在站点内 → 置灰不可点

def inline(text, src_file, reg):
    text = html.escape(text, quote=False)
    # 已有实体（&lt; 等）在 escape 后变成 &amp;lt;，还原
    text = text.replace("&amp;lt;", "&lt;").replace("&amp;gt;", "&gt;").replace("&amp;amp;", "&amp;")
    spans = []
    def stash(m):
        spans.append("<code>%s</code>" % html.escape(m.group(1)))
        return "\x00%d\x00" % (len(spans) - 1)
    text = CODE_RE.sub(stash, text)
    def img(m):
        alt, src = m.group(1), m.group(2)
        staged = _stage_local_image(src, src_file)
        if staged is None:
            return '<span class="deadlink">[图片缺失: %s]</span>' % html.escape(src)
        return '<img src="%s" alt="%s" loading=lazy style="max-width:100%%;border:1px solid var(--line);border-radius:8px;box-shadow:0 4px 16px rgba(90,66,20,.10)">' % (
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

def md_to_html(md_text, src_file, reg):
    lines = md_text.splitlines()
    out, i, n = [], 0, len(lines)
    para = []
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
            out.append("<pre class=\"code%s\"><code>%s</code></pre>" % (
                (" lang-" + lang) if lang else "", html.escape("\n".join(buf))))
            continue
        if not s:
            flush(); i += 1; continue
        if re.match(r"^(-{3,}|\*{3,})$", s):
            flush(); out.append("<hr>"); i += 1; continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            flush(); lvl = len(m.group(1)); t = m.group(2)
            out.append("<h%d id=\"%s\">%s</h%d>" % (lvl, slug(t), inline(t, src_file, reg), lvl))
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
            th = "".join("<th>%s</th>" % inline(c, src_file, reg) for c in head)
            trs = []
            for r in body:
                r = (r + [""] * len(head))[:len(head)]
                trs.append("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c, src_file, reg) for c in r))
            out.append("<div class=tablewrap><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>" % (th, "".join(trs)))
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
    return "\n".join(out)

# ---------- 页面模板 ----------
CSS = """
:root{--paper:#f6f1e4;--sheet:#fdfaf2;--side-bg:#efe8d5;--ink:#2f2a20;--ink-soft:#5c5340;--ink-faint:#948a74;
--acc:#a05a1c;--acc-strong:#7c440e;--acc-soft:#f4e8cd;--line:#e2d8bd;--line-strong:#cdbf9c;
--header-h:56px;--side-w:264px;
--serif:Georgia,"Times New Roman","Source Han Serif SC","Noto Serif SC",SimSun,serif;
--sans:"Segoe UI","Microsoft YaHei UI","Microsoft YaHei",system-ui,-apple-system,sans-serif;
--mono:Consolas,"Cascadia Mono","Courier New",monospace}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:calc(var(--header-h) + 18px)}
body{margin:0;font-family:var(--sans);color:var(--ink);font-size:15.5px;line-height:1.85;
background:radial-gradient(1100px 500px at 50% -8%,rgba(160,122,60,.07),transparent 60%),
repeating-linear-gradient(0deg,rgba(140,105,50,.014) 0 1px,transparent 1px 4px),var(--paper)}
/* 顶栏：纸条 */
#top{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:14px;height:var(--header-h);padding:0 clamp(14px,2.5vw,24px);
background:rgba(246,241,228,.94);backdrop-filter:blur(8px);border-bottom:3px double var(--line-strong)}
#burger{display:none;border:1px solid var(--line-strong);background:var(--sheet);border-radius:8px;padding:5px 11px;font-size:16px;cursor:pointer;color:var(--ink);line-height:1.4}
#top .brand{display:flex;align-items:baseline;gap:10px;text-decoration:none;white-space:nowrap;min-width:0}
#top .brand b{font-family:var(--serif);font-size:19px;color:var(--ink);letter-spacing:1px}
#top .brand small{font-size:10.5px;color:var(--ink-faint);letter-spacing:2px}
.searchwrap{position:relative;margin-left:auto;width:min(340px,40vw)}
#search{width:100%;padding:8px 12px 8px 32px;border:1px solid var(--line-strong);border-radius:8px;background:var(--sheet);color:var(--ink);font-size:13.5px;outline:none;transition:border-color .15s,box-shadow .15s}
#search:focus{border-color:var(--acc);box-shadow:0 0 0 3px var(--acc-soft)}
.searchwrap::before{content:"⌕";position:absolute;left:11px;top:50%;transform:translateY(-54%);color:var(--ink-faint);font-size:15px;pointer-events:none}
#sres{position:absolute;top:calc(100% + 6px);left:0;right:0;display:none;background:var(--sheet);border:1px solid var(--line-strong);border-radius:10px;box-shadow:0 12px 32px rgba(90,66,20,.18);max-height:62vh;overflow:auto;padding:6px;z-index:30}
#sres a{display:block;padding:8px 10px;border-radius:8px;font-size:13.5px;color:var(--ink);text-decoration:none}
#sres a:hover{background:var(--acc-soft)}
#sres .snip{display:block;font-size:12px;color:var(--ink-faint);margin-top:1px}
#top .gh{color:var(--ink-soft);font-size:12.5px;text-decoration:none;white-space:nowrap}
#top .gh:hover{color:var(--acc)}
/* 布局 */
#layout{display:flex;min-height:calc(100vh - var(--header-h))}
#backdrop{display:none}
#side{width:var(--side-w);flex:0 0 var(--side-w);background:var(--side-bg);border-right:1px solid var(--line-strong);position:sticky;top:var(--header-h);height:calc(100vh - var(--header-h));overflow-y:auto;padding:16px 12px 48px}
#side .sec{margin:18px 8px 6px;font-family:var(--serif);font-size:11.5px;font-weight:600;color:var(--acc-strong);letter-spacing:3px}
#side .sec:first-child{margin-top:4px}
#nav a{display:block;padding:6px 10px;margin:1px 0;border-radius:8px;color:#4a4334;text-decoration:none;font-size:13.5px;line-height:1.55;border-left:2px solid transparent}
#nav a:hover{background:rgba(160,90,28,.08);color:var(--ink)}
#nav a.active{background:var(--acc-soft);color:var(--acc-strong);border-left-color:var(--acc);font-weight:600}
/* 正文：纸页 */
#main{flex:1;min-width:0;padding:34px clamp(18px,4vw,52px) 80px}
article{max-width:900px;margin:0 auto;background:var(--sheet);border:1px solid var(--line);border-top:3px solid var(--acc);
border-radius:6px;padding:clamp(24px,4vw,48px) clamp(22px,4.5vw,52px);
box-shadow:0 1px 2px rgba(90,66,20,.05),0 10px 30px rgba(90,66,20,.08)}
h1,h2,h3{font-family:var(--serif);color:var(--ink)}
h1{font-size:clamp(23px,3vw,28px);font-weight:700;margin:0 0 12px;letter-spacing:.5px}
h2{font-size:clamp(18px,2.2vw,21px);margin:40px 0 14px;padding-bottom:9px;border-bottom:3px double var(--line-strong)}
h3{font-size:16.5px;margin:26px 0 10px}
p{margin:10px 0}
a{color:var(--acc-strong);text-decoration:none}
a:hover{text-decoration:underline;color:var(--acc)}
blockquote{margin:18px 0;padding:12px 18px;background:var(--acc-soft);border-left:3px solid var(--acc);border-radius:0 10px 10px 0;color:#57452a;font-size:14.5px}
blockquote p{margin:4px 0}
code{background:#f2ead6;border:1px solid #e0d4b6;border-radius:5px;padding:1px 6px;font-family:var(--mono);font-size:.86em;color:#7c4a12;overflow-wrap:anywhere}
pre.code{background:#f7f2e3;color:#3a3122;border:1px solid var(--line);border-radius:10px;padding:15px 18px;overflow-x:auto;box-shadow:inset 0 0 0 1px rgba(160,122,60,.06)}
pre.code code{background:none;border:none;color:inherit;padding:0;font-size:13px;line-height:1.65;overflow-wrap:normal}
.tablewrap{overflow-x:auto;margin:16px 0;border:1px solid var(--line);border-radius:8px;background:var(--sheet)}
table{border-collapse:collapse;width:100%;font-size:13.5px;line-height:1.7}
th{background:rgba(160,122,60,.07);color:#4a3d26;font-weight:600;text-align:left;font-family:var(--serif)}
th,td{border-bottom:1px solid var(--line);padding:8px 13px;vertical-align:top;overflow-wrap:anywhere}
tbody tr:last-child td{border-bottom:none}
tbody tr:nth-child(even){background:rgba(160,122,60,.035)}
hr{border:none;border-top:3px double var(--line-strong);margin:30px 0}
ul,ol{padding-left:1.5em;margin:10px 0}
li{margin:4px 0}
#foot{max-width:900px;margin:40px auto 0;padding-top:14px;border-top:1px solid var(--line);font-size:12px;color:var(--ink-faint);text-align:center;letter-spacing:.5px}
.deadlink{color:var(--ink-faint);border-bottom:1px dotted #b8ab8b}
/* 窄屏 */
@media(max-width:1200px){:root{--side-w:232px}}
@media(max-width:1024px){
#burger{display:block}
#backdrop{position:fixed;inset:var(--header-h) 0 0 0;background:rgba(70,52,20,.35);z-index:14;opacity:0;pointer-events:none;transition:opacity .2s}
#backdrop.show{opacity:1;pointer-events:auto}
#side{position:fixed;left:calc(-1*var(--side-w) - 24px);top:var(--header-h);transition:left .2s ease;z-index:15;box-shadow:10px 0 28px rgba(90,66,20,.15)}
#side.open{left:0}
#top .gh{display:none}
#top .brand small{display:none}
.searchwrap{width:min(240px,52vw)}
}
@media print{
#top,#side,#backdrop,#foot,#burger,.searchwrap{display:none!important}
body{background:#fff}
#main{padding:0}
article{box-shadow:none;border:none;border-top:none;max-width:100%}
a{color:inherit}
}
"""
JS = """
const $=s=>document.querySelector(s);
const ROOT=%ROOT%; // 站点根相对前缀（按页面深度注入）
// 搜索
let IDX=[];
fetch(ROOT+'search.json').then(r=>r.json()).then(d=>{IDX=d});
const box=$('#search'),res=$('#sres');
box.addEventListener('input',()=>{
  const q=box.value.trim().toLowerCase();
  if(!q){res.style.display='none';return}
  const hits=IDX.filter(p=>p.t.toLowerCase().includes(q)||p.b.toLowerCase().includes(q)).slice(0,20);
  res.innerHTML=hits.map(p=>{
    const i=p.b.toLowerCase().indexOf(q);
    const snip=i>=0?p.b.slice(Math.max(0,i-20),i+50):'';
    return `<a href="${ROOT}${p.u}">${p.t}<span class=snip>…${snip}…</span></a>`
  }).join('')||'<a>无命中</a>';
  res.style.display='block';
});
document.addEventListener('click',e=>{if(!res.contains(e.target)&&e.target!==box)res.style.display='none'});
document.addEventListener('keydown',e=>{
  if(e.key==='/'&&document.activeElement!==box){e.preventDefault();box.focus()}
  if(e.key==='Escape'){res.style.display='none'}
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
"""

def page_shell(title, body_html, nav_html, root_prefix):
    js = JS.replace("%ROOT%", json.dumps(root_prefix))
    title_suffix = "" if title == SITE_NAME else " · %s" % SITE_NAME
    return ("<!doctype html><html lang=zh><head><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>%s%s</title><style>%s</style></head><body>"
            "<header id=top>"
            "<button id=burger aria-label=目录>☰</button>"
            "<a class=brand href=\"%sindex.html\"><b>%s</b><small>%s</small></a>"
            "<div class=searchwrap><input id=search placeholder='搜索…（按 / 聚焦）'><div id=sres></div></div>"
            "<a class=gh href=\"%s\" target=_blank rel=noopener>GitHub ↗</a>"
            "</header>"
            "<div id=layout><aside id=side><nav id=nav>%s</nav></aside>"
            "<main id=main><article>%s</article>"
            "<div id=foot>%s · 纸上得来终觉浅 · 由 tools/build_wiki.py 生成</div>"
            "</main></div>"
            "<div id=backdrop></div>"
            "<script>%s</script></body></html>"
            ) % (html.escape(title), title_suffix, CSS, root_prefix, SITE_NAME, SITE_SUB, SITE_REPO, nav_html, body_html, SITE_NAME, js)

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
    for p in sorted(pages, key=lambda x: (["总览", "Mod开发", "SC引擎", "SC引擎·明细"].index(x["section"]), x["order"])):
        if p["section"] != cur_sec:
            cur_sec = p["section"]
            nav.append('<div class=sec>%s · %d</div>' % (SEC_LABELS[cur_sec], counts[cur_sec]))
        nav.append('<a href="%s">%s</a>' % (p["out"], html.escape(p["src"].stem)))
    nav_html = "".join(nav)

    index_data = []
    for p in pages:
        md = p["src"].read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^#\s+(.+)$", md, re.M)
        title = m.group(1).strip() if m else p["src"].stem
        body = md_to_html(md, p["src"], reg)
        out_path = OUT / p["out"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        root_prefix = "../" * p["out"].count("/")
        out_path.write_text(page_shell(title, body, nav_html, root_prefix), encoding="utf-8")
        text_sample = re.sub(r"[`#>*|\-\[\]()]", "", md)[:26000]
        index_data.append({"t": title, "u": p["out"], "b": text_sample.lower()})
        print("OK", p["out"])

    (OUT / "search.json").write_text(json.dumps(index_data, ensure_ascii=False), encoding="utf-8")
    for abs_p, rel in IMG_COPIES:
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(abs_p.read_bytes())
    print("DONE pages=%d images=%d out=%s" % (len(pages), len(IMG_COPIES), OUT))

if __name__ == "__main__":
    main()
