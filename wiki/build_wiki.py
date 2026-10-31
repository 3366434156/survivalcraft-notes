# -*- coding: utf-8 -*-
"""
SC完全学习笔记 wiki 生成器（零依赖，纯标准库）
- 只渲染 SC 原版库（SC完全学习笔记\），不含任何私有mod项目内容。
- 输出自包含静态站 wiki\site\（无CDN，离线可开，可随仓库上传/GitHub Pages）。
- 重新生成：python "E:\数据\生存战争系列\SC完全学习笔记\wiki\build_wiki.py"
"""
import html
import json
import os
import re
import sys
from pathlib import Path

SC_ROOT = Path(r"E:\数据\生存战争系列\SC完全学习笔记")
PW_ROOT = Path(r"E:\数据\生存战争系列\库外私有笔记")
OUT = SC_ROOT / "docs"  # GitHub Pages 从 /docs 目录部署

# ---------- 收集源文件（10-SC引擎 若尚未迁入 SC 库，则临时回退到主库，标记预览） ----------
def collect_sources():
    pages = []  # (section, title_order_key, src_path, out_rel)
    def add(section, src, out_rel, order):
        pages.append({"section": section, "src": src, "out": out_rel, "order": order})

    overview = [
        ("总览", SC_ROOT / "README.md", "index.html", 0),
        ("总览", SC_ROOT / "45-SC原版范例菜谱.md", "45-SC原版范例菜谱.html", 1),
        ("总览", SC_ROOT / "00-页面模板与规则.md", "00-页面模板与规则.html", 2),
    ]
    for sec, p, o, k in overview:
        if p.exists():
            add(sec, p, o, k)

    engine_dir = SC_ROOT / "10-SC引擎"
    preview = False
    if not engine_dir.exists():
        engine_dir = PW_ROOT / "10-SC引擎"
        preview = True
    if engine_dir.exists():
        mains, details = [], []
        for f in sorted(engine_dir.glob("*.md")):
            if re.match(r"^\d+[ab]-", f.name):
                details.append(f)
            else:
                mains.append(f)
        for f in mains:
            add("SC引擎", f, "10-SC引擎/" + f.name.replace(".md", ".html"), f.name)
        for f in details:
            add("SC引擎·明细", f, "10-SC引擎/" + f.name.replace(".md", ".html"), f.name)
    return pages, preview

# ---------- 最小 GFM 转换器 ----------
CODE_RE = re.compile(r"`([^`]+)`")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
ITAL_RE = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")

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
    return ("dead", None)  # 库外私有笔记/不存在 → 置灰不可点

def inline(text, src_file, reg):
    text = html.escape(text, quote=False)
    # 已有实体（&lt; 等）在 escape 后变成 &amp;lt;，还原
    text = text.replace("&amp;lt;", "&lt;").replace("&amp;gt;", "&gt;").replace("&amp;amp;", "&amp;")
    spans = []
    def stash(m):
        spans.append("<code>%s</code>" % html.escape(m.group(1)))
        return "\x00%d\x00" % (len(spans) - 1)
    text = CODE_RE.sub(stash, text)
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
:root{--bg:#f7f5f0;--side:#211d18;--sidefg:#cfc8bb;--ink:#2b2620;--acc:#8a6d3b;--acc2:#4a7a6f;--codebg:#23201b;--line:#e2dccc}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font-family:"Microsoft YaHei UI","Microsoft YaHei",system-ui,sans-serif;background:var(--bg);color:var(--ink);font-size:15px;line-height:1.75}
#layout{display:flex;min-height:100vh}
#side{width:300px;flex:0 0 300px;background:var(--side);color:var(--sidefg);position:sticky;top:0;height:100vh;overflow-y:auto;padding:18px 14px 40px}
#side h1{font-size:19px;color:#f0e9da;margin:2px 6px 10px;letter-spacing:1px}
#side h1 small{display:block;font-size:11px;color:#8d8577;font-weight:normal;letter-spacing:2px}
#search{width:100%;padding:8px 10px;margin:6px 0 14px;border:1px solid #4a4438;border-radius:6px;background:#2d2822;color:#f0e9da;font-size:13px;outline:none}
#search:focus{border-color:var(--acc)}
.sec{margin:14px 6px 4px;font-size:12px;color:#8d8577;letter-spacing:3px;border-bottom:1px solid #3a342b;padding-bottom:4px}
#nav a{display:block;padding:5px 10px;margin:1px 0;border-radius:6px;color:var(--sidefg);text-decoration:none;font-size:13.5px}
#nav a:hover{background:#332d25;color:#fff}
#nav a.active{background:var(--acc);color:#fff}
#nav a .st{float:right;font-size:10px;color:#7fb8a8;opacity:.85}
#main{flex:1;min-width:0;padding:34px 48px 90px;max-width:980px}
#main article{background:#fffdf8;border:1px solid var(--line);border-radius:12px;padding:38px 46px;box-shadow:0 2px 14px rgba(60,45,20,.06)}
h1{font-size:26px;color:#3a3128;border-bottom:2px solid var(--acc);padding-bottom:10px;margin-top:0}
h2{font-size:20px;color:#4a3f30;border-left:4px solid var(--acc2);padding-left:10px;margin-top:34px}
h3{font-size:17px;color:#5a4c38;margin-top:26px}
blockquote{margin:14px 0;padding:10px 16px;background:#f4efe2;border-left:4px solid var(--acc);border-radius:0 8px 8px 0;color:#5c5142;font-size:14px}
code{background:#efe9da;border-radius:4px;padding:1px 6px;font-family:Consolas,monospace;font-size:13px;color:#7a4d12}
pre.code{background:var(--codebg);color:#e8e0cf;border-radius:10px;padding:14px 18px;overflow-x:auto}
pre.code code{background:none;color:inherit;padding:0;font-size:13px;line-height:1.6}
.tablewrap{overflow-x:auto;margin:14px 0}
table{border-collapse:collapse;width:100%;font-size:13.5px;background:#fff}
th{background:#efe8d6;color:#4a3c28;text-align:left}
th,td{border:1px solid var(--line);padding:7px 11px;vertical-align:top}
tbody tr:nth-child(even){background:#faf7ee}
a{color:#28615a;text-decoration:none}a:hover{text-decoration:underline;color:var(--acc)}
.deadlink{color:#9a8f7c;border-bottom:1px dotted #b7ab92}
hr{border:none;border-top:1px dashed var(--line);margin:26px 0}
#foot{margin-top:22px;font-size:12px;color:#9a8f7c;text-align:center}
#sres{position:fixed;inset:80px 18% auto;display:none;background:#fffdf8;border:1px solid var(--line);border-radius:10px;box-shadow:0 10px 40px rgba(0,0,0,.25);max-height:70vh;overflow:auto;z-index:9;padding:8px}
#sres a{display:block;padding:7px 12px;border-radius:6px;font-size:14px}
#sres a:hover{background:#f2ecdc}
#sres .snip{font-size:12px;color:#8a7d68;margin-left:8px}
@media(max-width:900px){#side{position:fixed;left:-320px;transition:.2s;z-index:10}#side.open{left:0}#main{padding:20px}}
"""
JS = """
const $=s=>document.querySelector(s);
// 搜索
let IDX=[];
fetch('search.json').then(r=>r.json()).then(d=>{IDX=d});
const box=$('#search'),res=$('#sres');
box.addEventListener('input',()=>{
  const q=box.value.trim().toLowerCase();
  if(!q){res.style.display='none';return}
  const hits=IDX.filter(p=>p.t.toLowerCase().includes(q)||p.b.toLowerCase().includes(q)).slice(0,20);
  res.innerHTML=hits.map(p=>{
    const i=p.b.toLowerCase().indexOf(q);
    const snip=i>=0?p.b.slice(Math.max(0,i-20),i+50):'';
    return `<a href="${p.u}">${p.t}<span class=snip>…${snip}…</span></a>`
  }).join('')||'<a>无命中</a>';
  res.style.display='block';
});
document.addEventListener('click',e=>{if(!res.contains(e.target)&&e.target!==box)res.style.display='none'});
document.addEventListener('keydown',e=>{
  if(e.key==='/'&&document.activeElement!==box){e.preventDefault();box.focus()}
  if(e.key==='Escape'){res.style.display='none'}
});
// 高亮当前页
const here=location.pathname.split('/').pop();
document.querySelectorAll('#nav a').forEach(a=>{if(a.getAttribute('href').endsWith(here))a.classList.add('active')});
"""

def page_shell(title, body_html, nav_html, preview):
    banner = ('<div style="background:#fdf3d9;border:1px solid #e8d48a;border-radius:8px;padding:8px 14px;margin-bottom:16px;font-size:13px;color:#7a6320">'
              '⏳ 预览版：SC引擎页尚在主库，目录迁移后重新生成本站即归位。</div>') if preview else ''
    return ("<!doctype html><html lang=zh><head><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>%s · SC学习笔记</title><style>%s</style></head><body>"
            "<div id=layout><aside id=side><h1>SC 完全学习笔记<small>SURVIVALCRAFT · 原版引擎</small></h1>"
            "<input id=search placeholder='搜索…（按 / 聚焦）'>"
            "<nav id=nav>%s</nav></aside>"
            "<main id=main><article>%s%s</article>"
            "<div id=foot>由 wiki/build_wiki.py 生成 · 零依赖静态站 · 重新生成：python wiki/build_wiki.py</div>"
            "</main></div><div id=sres></div><script>%s</script></body></html>"
            ) % (html.escape(title), CSS, nav_html, banner, body_html, JS)

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    pages, preview = collect_sources()
    if not pages:
        print("no sources"); return
    reg = build_registry(pages)
    OUT.mkdir(parents=True, exist_ok=True)
    nav = []
    cur_sec = None
    for p in sorted(pages, key=lambda x: (["总览", "SC引擎", "SC引擎·明细"].index(x["section"]), x["order"])):
        if p["section"] != cur_sec:
            cur_sec = p["section"]
            nav.append("<div class=sec>%s</div>" % cur_sec)
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
        out_path.write_text(page_shell(title, body, nav_html, preview), encoding="utf-8")
        text_sample = re.sub(r"[`#>*|\-\[\]()]", "", md)[:26000]
        index_data.append({"t": title, "u": p["out"], "b": text_sample.lower()})
        print("OK", p["out"])

    (OUT / "search.json").write_text(json.dumps(index_data, ensure_ascii=False), encoding="utf-8")
    print("DONE pages=%d preview=%s out=%s" % (len(pages), preview, OUT))

if __name__ == "__main__":
    main()
