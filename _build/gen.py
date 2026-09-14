# -*- coding: utf-8 -*-
"""從 blog-data.json 產生 /blog/index.html 與 /blog/topic/<slug>/index.html。

以後新增文章只要在 blog-data.json 的 posts 加一筆，重跑本檔即可，
不必手改任何導覽或聚合頁。

用法：python _build/gen.py
"""
import io, json, os, sys, html

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, '_build', 'blog-data.json')
SITE = 'https://starbright-integrated.com'

CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--navy:#1C3A5E;--blue:#2563EB;--teal:#0891B2;--green:#059669;--light:#F0F7FF;--gray:#F8FAFC;--text:#1E293B;--muted:#64748B;--white:#FFF;--gold:#B45309}
html{scroll-behavior:smooth}
body{font-family:-apple-system,'PingFang TC','Microsoft JhengHei','Heiti TC','Noto Sans CJK TC',sans-serif;color:var(--text);line-height:1.7;background:var(--white)}
nav{position:sticky;top:0;z-index:100;background:var(--navy);padding:0 5%;display:flex;align-items:center;justify-content:space-between;height:64px;box-shadow:0 2px 12px rgba(0,0,0,.25)}
.nav-logo{display:flex;align-items:center;gap:12px;text-decoration:none}
.nav-logo img{height:40px;width:40px;object-fit:contain;filter:brightness(0) invert(1)}
.nav-logo span{color:var(--white);font-weight:700;font-size:1.05rem;letter-spacing:.04em}
.nav-right{display:flex;align-items:center;gap:18px}
.nav-right a{color:rgba(255,255,255,.85);text-decoration:none;font-size:.9rem;font-weight:600}
.nav-right a:hover{color:#fff}
.nav-cta{background:var(--green);color:#fff!important;border-radius:6px;padding:9px 20px;font-weight:700}
.nav-cta:hover{background:#047857}
.hero{background:linear-gradient(135deg,var(--navy) 0%,#1e4d8c 60%,#0e7490 100%);color:var(--white);padding:54px 5% 50px}
.crumb{font-size:.82rem;color:rgba(255,255,255,.6);margin-bottom:14px}
.crumb a{color:rgba(255,255,255,.75);text-decoration:none}
.crumb a:hover{color:#fff;text-decoration:underline}
.hero .label{font-size:.8rem;font-weight:700;letter-spacing:.12em;color:#67E8F9;text-transform:uppercase;margin-bottom:10px}
.hero h1{font-size:clamp(1.55rem,3vw,2.15rem);font-weight:900;margin-bottom:14px;line-height:1.4}
.hero p{font-size:1rem;color:rgba(255,255,255,.85);max-width:680px;line-height:1.8}
main{padding:52px 5% 70px;max-width:1120px;margin:0 auto}
.sec-label{font-size:.8rem;font-weight:700;letter-spacing:.12em;color:var(--teal);text-transform:uppercase;margin-bottom:8px}
.sec-title{font-size:1.45rem;font-weight:900;color:var(--navy);margin-bottom:8px}
.sec-sub{color:var(--muted);font-size:.95rem;margin-bottom:26px}
.topics{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px;margin-bottom:56px}
.topic{background:var(--gray);border:1px solid #E2E8F0;border-radius:12px;padding:24px 22px;text-decoration:none;display:flex;flex-direction:column;transition:transform .2s,box-shadow .2s,border-color .2s}
.topic:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(37,99,235,.12);border-color:var(--blue)}
.topic .ic{font-size:1.7rem;margin-bottom:10px}
.topic h3{font-size:1.05rem;font-weight:800;color:var(--navy);margin-bottom:5px}
.topic .tag{font-size:.83rem;color:var(--teal);font-weight:700;margin-bottom:9px}
.topic p{font-size:.87rem;color:var(--muted);line-height:1.7;flex:1}
.topic .n{margin-top:13px;font-size:.8rem;color:var(--muted)}
.topic .n b{color:var(--navy)}
.topic.soon{opacity:.55;cursor:default}
.topic.soon:hover{transform:none;box-shadow:none;border-color:#E2E8F0}
.topic.soon .n{color:#94A3B8;font-weight:700}
.posts{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:24px}
.post{background:var(--light);border:1px solid #DBEAFE;border-radius:12px;padding:25px 23px;display:flex;flex-direction:column;transition:transform .2s,box-shadow .2s}
.post:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(37,99,235,.12)}
.post .badge{align-self:flex-start;background:#DCFCE7;color:#166534;font-size:.73rem;font-weight:700;padding:3px 11px;border-radius:20px;margin-bottom:12px}
.post .badge.hot{background:#FEF3C7;color:var(--gold)}
.post h3{font-size:1.04rem;font-weight:700;color:var(--navy);line-height:1.55;margin-bottom:9px}
.post h3 a{color:inherit;text-decoration:none}
.post h3 a:hover{color:var(--blue)}
.post p{font-size:.87rem;color:var(--muted);line-height:1.75;flex:1;margin-bottom:15px}
.post .foot{display:flex;justify-content:space-between;align-items:center;font-size:.82rem}
.post .more{font-weight:700;color:var(--teal);text-decoration:none}
.post .more:hover{text-decoration:underline}
.post .topiclink{color:var(--muted);text-decoration:none}
.post .topiclink:hover{color:var(--blue)}
.empty{background:var(--gray);border:1px dashed #CBD5E1;border-radius:12px;padding:30px 24px;color:var(--muted);font-size:.9rem}
.cta{margin-top:56px;background:linear-gradient(135deg,var(--navy) 0%,#1e4d8c 100%);color:var(--white);border-radius:14px;padding:44px 36px;text-align:center}
.cta h2{font-size:1.35rem;font-weight:900;margin-bottom:10px}
.cta p{color:rgba(255,255,255,.78);margin-bottom:24px;font-size:.94rem}
.cta a{display:inline-block;background:var(--green);color:#fff;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:700}
.cta a:hover{background:#047857}
.others{margin-top:48px;padding-top:28px;border-top:1px solid #E2E8F0}
.others h2{font-size:1.05rem;font-weight:800;color:var(--navy);margin-bottom:14px}
.others ul{list-style:none;display:flex;flex-wrap:wrap;gap:10px}
.others a{display:inline-block;background:var(--gray);border:1px solid #E2E8F0;border-radius:20px;padding:7px 15px;font-size:.86rem;color:var(--navy);text-decoration:none;font-weight:600}
.others a:hover{border-color:var(--blue);color:var(--blue)}
footer{background:#0F1E35;color:rgba(255,255,255,.5);text-align:center;padding:28px 5%;font-size:.82rem}
footer a{color:rgba(255,255,255,.5);text-decoration:none}
footer a:hover{color:#fff}
@media(max-width:768px){nav .nav-logo span{display:none}main{padding:38px 5% 54px}}
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

CTA = """<div class="cta">
    <h2>文章看完了，但自己公司的狀況還是不確定？</h2>
    <p>初次諮詢 30 分鐘免費，說明你的狀況，我來評估最適合的處理方式。</p>
    <a href="/#contact">預約免費 30 分鐘諮詢</a>
  </div>"""

e = html.escape


def page(title, desc, canonical, body, schema):
    return f"""<!DOCTYPE html>
<html lang="zh-Hant-TW">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}" />
<meta name="theme-color" content="#1C3A5E" />
<link rel="canonical" href="{canonical}" />
<meta property="og:title" content="{e(title)}" />
<meta property="og:description" content="{e(desc)}" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="星耀整合顧問" />
<meta property="og:url" content="{canonical}" />
<script type="application/ld+json">
{json.dumps(schema, ensure_ascii=False, indent=1)}
</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
{body}
{FOOT}
</body>
</html>
"""


def post_card(p, topics_by_slug, show_topic=True):
    t = topics_by_slug[p['topic']]
    badge_cls = 'badge hot' if p.get('hot') else 'badge'
    topic_line = (f'<a class="topiclink" href="/blog/topic/{t["slug"]}/">{e(t["icon"])} {e(t["name"])}</a>'
                  if show_topic else '<span></span>')
    return f"""    <article class="post">
      <span class="{badge_cls}">{e(p.get('badge','專欄'))}</span>
      <h3><a href="/blog/{p['slug']}/">{e(p['title'])}</a></h3>
      <p>{e(p['excerpt'])}</p>
      <div class="foot">
        {topic_line}
        <a class="more" href="/blog/{p['slug']}/">閱讀全文 →</a>
      </div>
    </article>"""


def build():
    d = json.load(io.open(DATA, encoding='utf-8'))
    topics, posts = d['topics'], d['posts']
    by_slug = {t['slug']: t for t in topics}
    by_topic = {t['slug']: [p for p in posts if p['topic'] == t['slug']] for t in topics}

    # ── /blog/index.html ──
    # 沒有文章的主題不產生聚合頁（薄內容對 SEO 是負分），
    # 索引上仍列出但顯示為「準備中」且不可點，等文章補上自動點亮。
    tcards = []
    for t in topics:
        n = len(by_topic[t['slug']])
        inner = f"""      <div class="ic">{e(t['icon'])}</div>
      <h3>{e(t['name'])}</h3>
      <div class="tag">{e(t['tagline'])}</div>
      <p>{e(t['desc'])}</p>"""
        if n:
            tcards.append(f'''    <a class="topic" href="/blog/topic/{t["slug"]}/">
{inner}
      <div class="n"><b>{n}</b> 篇文章</div>
    </a>''')
        else:
            tcards.append(f'''    <div class="topic soon">
{inner}
      <div class="n">準備中</div>
    </div>''')
    cards = [post_card(p, by_slug) for p in posts]
    body = f"""<section class="hero">
  <div class="label">勞資法規專欄</div>
  <h1>法規變了，你的制度跟上了嗎？</h1>
  <p>專為 50 人以內、沒有專職人資的中小企業雇主撰寫。<br />
  每篇都對照法條原文與主管機關公告，講清楚「你到底要做什麼」，不是抄法規。</p>
</section>

<main>
  <div class="sec-label">依主題瀏覽</div>
  <div class="sec-title">你現在遇到的是哪一類問題？</div>
  <div class="sec-sub">六個主題對應中小企業最常踩到的六種狀況，點進去看該主題的全部文章。</div>
  <div class="topics">
{chr(10).join(tcards)}
  </div>

  <div class="sec-label">全部文章</div>
  <div class="sec-title">最新文章</div>
  <div class="sec-sub">共 {len(posts)} 篇。</div>
  <div class="posts">
{chr(10).join(cards)}
  </div>

  {CTA}
</main>"""
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Blog", "@id": f"{SITE}/blog/#blog", "name": "星耀整合顧問 勞資法規專欄",
             "url": f"{SITE}/blog/",
             "description": "專為 50 人以內中小企業雇主撰寫的勞動法令與人事制度實務解析。",
             "publisher": {"@type": "Organization", "name": "星耀整合顧問", "url": SITE}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "首頁", "item": SITE},
                {"@type": "ListItem", "position": 2, "name": "勞資法規專欄", "item": f"{SITE}/blog/"}]}
        ]}
    out = os.path.join(ROOT, 'blog', 'index.html')
    io.open(out, 'w', encoding='utf-8', newline='').write(
        page("勞資法規專欄｜星耀整合顧問 - 中小企業人事制度與勞動法令",
             "星耀整合顧問勞資法規專欄：職場霸凌新法、勞動檢查應對、職災認定、人事制度建置、解僱爭議與創業貸款，專為 50 人以內中小企業雇主撰寫。",
             f"{SITE}/blog/", body, schema))
    made = [out]

    # ── /blog/topic/<slug>/index.html ──
    for t in topics:
        ps = by_topic[t['slug']]
        if not ps:
            continue  # 空主題不出頁
        if ps:
            inner = f"""  <div class="posts">
{chr(10).join(post_card(p, by_slug, show_topic=False) for p in ps)}
  </div>"""
        else:
            inner = """  <div class="empty">這個主題的文章正在整理中。若你現在就有相關問題，
  歡迎直接<a href="/#contact">預約 30 分鐘免費諮詢</a>。</div>"""
        others = ''.join(
            f'<li><a href="/blog/topic/{o["slug"]}/">{e(o["icon"])} {e(o["name"])}</a></li>'
            for o in topics if o['slug'] != t['slug'] and by_topic[o['slug']])
        body = f"""<section class="hero">
  <div class="crumb"><a href="/">首頁</a> ／ <a href="/blog/">勞資法規專欄</a> ／ {e(t['name'])}</div>
  <div class="label">{e(t['icon'])} {e(t['tagline'])}</div>
  <h1>{e(t['name'])}</h1>
  <p>{e(t['desc'])}</p>
</section>

<main>
  <div class="sec-label">本主題文章</div>
  <div class="sec-title">共 {len(ps)} 篇</div>
  <div class="sec-sub">&nbsp;</div>
{inner}

  <div class="others">
    <h2>其他主題</h2>
    <ul>{others}</ul>
  </div>

  {CTA}
</main>"""
        can = f"{SITE}/blog/topic/{t['slug']}/"
        schema = {"@context": "https://schema.org", "@graph": [
            {"@type": "CollectionPage", "@id": can + "#page", "name": f"{t['name']}｜星耀整合顧問",
             "url": can, "description": t['desc'],
             "isPartOf": {"@id": f"{SITE}/blog/#blog"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "首頁", "item": SITE},
                {"@type": "ListItem", "position": 2, "name": "勞資法規專欄", "item": f"{SITE}/blog/"},
                {"@type": "ListItem", "position": 3, "name": t['name'], "item": can}]}
        ]}
        d2 = os.path.join(ROOT, 'blog', 'topic', t['slug'])
        os.makedirs(d2, exist_ok=True)
        o = os.path.join(d2, 'index.html')
        io.open(o, 'w', encoding='utf-8', newline='').write(
            page(f"{t['name']}｜勞資法規專欄｜星耀整合顧問",
                 t['desc'], can, body, schema))
        made.append(o)

    for m in made:
        print('  ' + os.path.relpath(m, ROOT).replace('\\', '/'))
    print('共 %d 個頁面（%d 主題 / %d 文章）' % (len(made), len(topics), len(posts)))

    # sitemap 與 robots 一併重建，確保與文章清單同步
    import sitemap
    sitemap.build(d)



if __name__ == '__main__':
    # 文章頁要先產生，索引與聚合頁連過去才不會是死鏈
    import article
    article.build()
    build()
