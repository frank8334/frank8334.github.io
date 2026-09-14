# -*- coding: utf-8 -*-
"""把 _build/posts/<slug>.md 轉成 /blog/<slug>/index.html。

每篇 md 的 frontmatter 需含：topic / title / h1 / desc / badge / date / kicker，
並可含 faq（問答清單）與 sources（查核來源）。
文章本文用一般 Markdown 撰寫，支援標題、段落、表格、清單、引用、粗體。

用法：python _build/article.py          # 全部重建
      python _build/article.py <slug>   # 只建一篇
"""
import io, os, re, sys, json, html

import xlink

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, '_build', 'posts')
DATA = os.path.join(ROOT, '_build', 'blog-data.json')
SITE = 'https://starbright-integrated.com'

CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--navy:#1C3A5E;--blue:#2563EB;--teal:#0891B2;--green:#059669;--light:#F0F7FF;--gray:#F8FAFC;--text:#1E293B;--muted:#64748B;--white:#FFF;--gold:#B45309;--red:#DC2626}
html{scroll-behavior:smooth}
body{font-family:-apple-system,'PingFang TC','Microsoft JhengHei','Heiti TC','Noto Sans CJK TC',sans-serif;color:var(--text);line-height:1.85;background:var(--white)}
nav{position:sticky;top:0;z-index:100;background:var(--navy);padding:0 5%;display:flex;align-items:center;justify-content:space-between;height:64px;box-shadow:0 2px 12px rgba(0,0,0,.25)}
.nav-logo{display:flex;align-items:center;gap:12px;text-decoration:none}
.nav-logo img{height:40px;width:40px;object-fit:contain;filter:brightness(0) invert(1)}
.nav-logo span{color:#fff;font-weight:700;font-size:1.05rem;letter-spacing:.04em}
.nav-right{display:flex;align-items:center;gap:18px}
.nav-right a{color:rgba(255,255,255,.85);text-decoration:none;font-size:.9rem;font-weight:600}
.nav-right a:hover{color:#fff}
.nav-cta{background:var(--green);color:#fff!important;border-radius:6px;padding:9px 20px;font-weight:700}
.nav-cta:hover{background:#047857}
.wrap{max-width:820px;margin:0 auto;padding:0 5%}
.meta{background:var(--gray);border-bottom:1px solid #E2E8F0;padding:20px 0 18px}
.crumb{font-size:.82rem;color:var(--muted);margin-bottom:10px}
.crumb a{color:var(--teal);text-decoration:none}
.crumb a:hover{text-decoration:underline}
.kicker{display:inline-block;background:#DBEAFE;color:var(--navy);font-size:.76rem;font-weight:700;padding:3px 11px;border-radius:20px;margin-right:10px}
.byline{font-size:.82rem;color:var(--muted)}
article{padding:34px 0 10px}
article h1{font-size:clamp(1.5rem,2.9vw,2rem);font-weight:900;color:var(--navy);line-height:1.42;margin-bottom:22px}
article h2{font-size:1.22rem;font-weight:800;color:var(--navy);margin:38px 0 14px;padding-left:12px;border-left:5px solid var(--teal)}
article h3{font-size:1.04rem;font-weight:700;color:var(--navy);margin:24px 0 10px}
article p{margin:13px 0;font-size:1rem}
article ul,article ol{margin:13px 0 13px 24px}
article li{margin:7px 0}
article strong{color:#0F172A}
article a{color:var(--blue)}
.lede{background:var(--light);border-left:5px solid var(--blue);border-radius:0 10px 10px 0;padding:18px 20px;margin:0 0 24px;font-size:.98rem;color:#334155}
.tablewrap{overflow-x:auto;margin:18px 0}
table{width:100%;border-collapse:collapse;font-size:.93rem;min-width:480px}
th,td{border:1px solid #CBD5E1;padding:9px 12px;text-align:left;vertical-align:top}
th{background:#E8EDF5;font-weight:700;color:var(--navy)}
blockquote{margin:18px 0;padding:14px 18px;background:#FFFBEB;border-left:5px solid #F59E0B;border-radius:0 8px 8px 0;font-size:.95rem;color:#78350F}
blockquote p{margin:6px 0}
.warn{background:#FEF2F2;border-left:5px solid var(--red);color:#7F1D1D}
.faq-wrap{margin:40px 0 0}
.faq-wrap h2{margin-bottom:16px}
.faq{border:1px solid #E2E8F0;border-radius:10px;margin-bottom:12px;overflow:hidden}
.faq summary{cursor:pointer;padding:15px 18px;font-weight:700;color:var(--navy);background:var(--gray);font-size:.97rem;list-style:none}
.faq summary::-webkit-details-marker{display:none}
.faq summary::before{content:"▸ ";color:var(--teal)}
.faq[open] summary::before{content:"▾ "}
.faq .ans{padding:14px 18px;font-size:.95rem;color:#334155;border-top:1px solid #E2E8F0}
.src{margin-top:38px;padding:18px 20px;background:var(--gray);border-radius:10px;font-size:.86rem;color:var(--muted)}
.src b{color:var(--navy)}
.src ul{margin:8px 0 0 20px}
.xlink{color:var(--blue);text-decoration:none;border-bottom:1px solid #BFDBFE;font-weight:600;padding-bottom:1px}
.xlink:hover{border-bottom-color:var(--blue);background:var(--light)}
.related{margin-top:38px}
.related h2{font-size:1.08rem;font-weight:800;color:var(--navy);margin-bottom:14px}
.related a{display:block;background:var(--light);border:1px solid #DBEAFE;border-radius:10px;padding:14px 16px;margin-bottom:10px;text-decoration:none;color:var(--navy);font-weight:600;font-size:.95rem}
.related a:hover{border-color:var(--blue)}
.related a span{display:block;font-weight:400;color:var(--muted);font-size:.85rem;margin-top:4px}
.cta{margin:42px 0 8px;background:linear-gradient(135deg,var(--navy) 0%,#1e4d8c 100%);color:#fff;border-radius:14px;padding:36px 30px;text-align:center}
.cta h2{font-size:1.2rem;font-weight:900;margin-bottom:10px;color:#fff;border:0;padding:0}
.cta p{color:rgba(255,255,255,.8);margin-bottom:20px;font-size:.93rem}
.cta .btn{display:inline-block;background:var(--green);color:#fff;padding:13px 30px;border-radius:8px;text-decoration:none;font-weight:700}
.cta .btn:hover{background:#047857}
.cta .info{margin-top:16px;font-size:.85rem;color:rgba(255,255,255,.65)}
footer{background:#0F1E35;color:rgba(255,255,255,.5);text-align:center;padding:28px 5%;font-size:.82rem;margin-top:46px}
footer a{color:rgba(255,255,255,.5);text-decoration:none}
footer a:hover{color:#fff}
@media(max-width:768px){nav .nav-logo span{display:none}}
"""

NAV = """<nav>
  <a class="nav-logo" href="/">
    <img src="/assets/logo.png" alt="星耀整合顧問 Logo" width="40" height="40" />
    <span>星耀整合顧問</span>
  </a>
  <div class="nav-right">
    <a href="/blog/">專欄</a>
    <a class="nav-cta" href="/#contact">免費預約諮詢</a>
  </div>
</nav>"""

FOOT = """<footer>
  <p><a href="/">回首頁</a>　｜　<a href="/blog/">勞資法規專欄</a>　｜　<a href="/#contact">預約諮詢</a></p>
  <p style="margin-top:8px">© 2026 星耀整合顧問 Starbright-Integrated Consultant｜賴力瑀 Frank</p>
</footer>"""

e = html.escape


def inline(t):
    t = e(t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    return t


def md2html(md):
    lines = md.split('\n')
    out = []
    i, n = 0, len(lines)
    while i < n:
        s = lines[i].strip()
        if not s:
            i += 1; continue
        m = re.match(r'^(#{2,4})\s+(.*)$', s)
        if m:
            lv = len(m.group(1))
            out.append('<h%d>%s</h%d>' % (lv, inline(m.group(2)), lv)); i += 1; continue
        if s.startswith('|'):
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                rows.append(lines[i].strip()); i += 1
            if len(rows) >= 2 and re.match(r'^\|[\s:|-]+\|$', rows[1]):
                cel = lambda r: [c.strip() for c in r.strip('|').split('|')]
                out.append('<div class="tablewrap"><table><thead><tr>' +
                           ''.join('<th>%s</th>' % inline(c) for c in cel(rows[0])) +
                           '</tr></thead><tbody>')
                for r in rows[2:]:
                    out.append('<tr>' + ''.join('<td>%s</td>' % inline(c) for c in cel(r)) + '</tr>')
                out.append('</tbody></table></div>')
            continue
        if s.startswith('>'):
            buf = []
            warn = False
            while i < n and lines[i].strip().startswith('>'):
                b = lines[i].strip().lstrip('>').strip()
                if b.startswith('!!'):
                    warn = True; b = b[2:].strip()
                buf.append(b); i += 1
            cls = ' class="warn"' if warn else ''
            out.append('<blockquote%s>%s</blockquote>' % (
                cls, ''.join('<p>%s</p>' % inline(b) for b in buf if b)))
            continue
        if re.match(r'^\d+\.\s+', s) or s.startswith('- '):
            tag = 'ol' if re.match(r'^\d+\.\s+', s) else 'ul'
            out.append('<%s>' % tag)
            while i < n:
                s2 = lines[i].strip()
                if tag == 'ol' and re.match(r'^\d+\.\s+', s2):
                    out.append('<li>%s</li>' % inline(re.sub(r'^\d+\.\s+', '', s2)))
                elif tag == 'ul' and s2.startswith('- '):
                    out.append('<li>%s</li>' % inline(s2[2:]))
                else:
                    break
                i += 1
            out.append('</%s>' % tag); continue
        buf = []
        while i < n and lines[i].strip() and not re.match(r'^(#{2,4}\s|\||>|-\s|\d+\.\s)', lines[i].strip()):
            buf.append(lines[i].strip()); i += 1
        if buf:
            out.append('<p>%s</p>' % inline(''.join(buf)))
    return '\n'.join(out)


def parse(path):
    raw = io.open(path, encoding='utf-8').read()
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', raw, re.S)
    fm = json.loads(m.group(1))
    return fm, m.group(2)


def build(only=None):
    d = json.load(io.open(DATA, encoding='utf-8'))
    topics = {t['slug']: t for t in d['topics']}
    posts = {p['slug']: p for p in d['posts']}
    made = []
    for fn in sorted(os.listdir(POSTS)):
        if not fn.endswith('.md'):
            continue
        slug = fn[:-3]
        if only and slug != only:
            continue
        fm, body = parse(os.path.join(POSTS, fn))
        t = topics[fm['topic']]
        can = '%s/blog/%s/' % (SITE, slug)
        # 同主題的其他文章
        rel = [p for p in d['posts'] if p['topic'] == fm['topic'] and p['slug'] != slug][:3]
        rel_html = ''
        if rel:
            rel_html = '<div class="related"><h2>同主題其他文章</h2>' + ''.join(
                '<a href="/blog/%s/">%s<span>%s</span></a>' % (r['slug'], e(r['title']), e(r['excerpt']))
                for r in rel) + '</div>'
        # 內文互鏈：別篇的代表詞在本篇首次出現時連過去
        body_html, _xlinked = xlink.apply(md2html(body), slug, d['posts'])
        faq_html = ''
        if fm.get('faq'):
            faq_html = '<div class="faq-wrap"><h2>常見問題</h2>' + ''.join(
                '<details class="faq"><summary>%s</summary><div class="ans">%s</div></details>'
                % (e(q['q']), inline(q['a'])) for q in fm['faq']) + '</div>'
        src_html = ''
        if fm.get('sources'):
            src_html = ('<div class="src"><b>本文依據的一手法源</b><ul>' +
                        ''.join('<li>%s</li>' % inline(s) for s in fm['sources']) +
                        '</ul><p style="margin-top:10px">法規以主管機關最新公告為準；'
                        '個案適用性請洽主管機關或專業顧問確認。</p></div>')
        graph = [{
            "@type": "Article", "headline": fm['h1'], "description": fm['desc'],
            "datePublished": fm['date'] + "T08:00:00+08:00",
            "dateModified": fm.get('modified', fm['date']) + "T08:00:00+08:00",
            "author": {"@type": "Person", "name": "賴力瑀 Frank"},
            "publisher": {"@type": "Organization", "name": "星耀整合顧問", "url": SITE},
            "mainEntityOfPage": can, "articleSection": t['name']}]
        if fm.get('faq'):
            graph.append({"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q['q'],
                 "acceptedAnswer": {"@type": "Answer", "text": re.sub(r'\*\*|`', '', q['a'])}}
                for q in fm['faq']]})
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首頁", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": "勞資法規專欄", "item": SITE + "/blog/"},
            {"@type": "ListItem", "position": 3, "name": t['name'],
             "item": "%s/blog/topic/%s/" % (SITE, t['slug'])},
            {"@type": "ListItem", "position": 4, "name": fm['h1'], "item": can}]})
        doc = f"""<!DOCTYPE html>
<html lang="zh-Hant-TW">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{e(fm['title'])}</title>
<meta name="description" content="{e(fm['desc'])}" />
<meta name="theme-color" content="#1C3A5E" />
<link rel="canonical" href="{can}" />
<meta property="og:title" content="{e(fm['h1'])}" />
<meta property="og:description" content="{e(fm['desc'])}" />
<meta property="og:type" content="article" />
<meta property="og:site_name" content="星耀整合顧問" />
<meta property="og:url" content="{can}" />
<script type="application/ld+json">
{json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)}
</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="meta"><div class="wrap">
  <div class="crumb"><a href="/">首頁</a> ／ <a href="/blog/">勞資法規專欄</a> ／ <a href="/blog/topic/{t['slug']}/">{e(t['name'])}</a></div>
  <span class="kicker">{e(fm['kicker'])}</span>
  <span class="byline">作者：賴力瑀 Frank｜發布：{e(fm['date'])}</span>
</div></div>

<div class="wrap">
<article>
  <h1>{e(fm['h1'])}</h1>
  <div class="lede">{inline(fm['lede'])}</div>
{body_html}
{faq_html}
{src_html}
{rel_html}
  <div class="cta">
    <h2>看完還是不確定自己公司的狀況？</h2>
    <p>初次諮詢 30 分鐘免費。說明你的狀況，我來評估最適合的處理方式。</p>
    <a class="btn" href="/#contact">預約免費 30 分鐘諮詢</a>
    <div class="info">星耀整合顧問｜賴力瑀 Frank｜0905-732-500｜LINE：@907qijtp<br>
    職業安全衛生管理師（甲級）・就業服務乙級技術士・勞資關係管理師</div>
  </div>
</article>
</div>
{FOOT}
</body>
</html>
"""
        od = os.path.join(ROOT, 'blog', slug)
        os.makedirs(od, exist_ok=True)
        io.open(os.path.join(od, 'index.html'), 'w', encoding='utf-8', newline='').write(doc)
        made.append(slug)
    for m_ in made:
        print('  blog/%s/index.html' % m_)
    print('共 %d 篇' % len(made))


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else None)
