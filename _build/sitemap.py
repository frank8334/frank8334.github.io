# -*- coding: utf-8 -*-
"""依 blog-data.json 產生 sitemap.xml 與 robots.txt。

⛔ /admin/ 是 Decap CMS 的後台登入頁，不納入 sitemap，
   並在 robots.txt 明確 Disallow。

由 gen.py 自動呼叫；也可單獨執行：python _build/sitemap.py
"""
import io, os, json, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, '_build', 'blog-data.json')
SITE = 'https://starbright-integrated.com'

# 不得出現在 sitemap 的路徑
EXCLUDE = {'admin'}

ROBOTS = """User-agent: *
Allow: /

# CMS 後台，不應被索引
Disallow: /admin/

Sitemap: {site}/sitemap.xml
"""


def build(d=None):
    if d is None:
        d = json.load(io.open(DATA, encoding='utf-8'))
    topics, posts = d['topics'], d['posts']
    by_topic = {t['slug']: [p for p in posts if p['topic'] == t['slug']] for t in topics}
    today = datetime.date.today().isoformat()

    # (網址, lastmod, priority, changefreq)
    urls = [(SITE + '/', today, '1.0', 'weekly'),
            (SITE + '/blog/', today, '0.9', 'weekly')]

    for t in topics:
        if by_topic[t['slug']]:
            urls.append(('%s/blog/topic/%s/' % (SITE, t['slug']), today, '0.8', 'weekly'))

    for p in posts:
        lastmod = p.get('modified') or p.get('date') or today
        urls.append(('%s/blog/%s/' % (SITE, p['slug']), lastmod, '0.7', 'monthly'))

    for leg in ('privacy', 'terms'):
        if leg in EXCLUDE:
            continue
        if os.path.exists(os.path.join(ROOT, leg, 'index.html')):
            urls.append(('%s/%s/' % (SITE, leg), today, '0.3', 'yearly'))

    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod, pri, cf in urls:
        parts.append('  <url>')
        parts.append('    <loc>%s</loc>' % loc)
        parts.append('    <lastmod>%s</lastmod>' % lastmod)
        parts.append('    <changefreq>%s</changefreq>' % cf)
        parts.append('    <priority>%s</priority>' % pri)
        parts.append('  </url>')
    parts.append('</urlset>')

    io.open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8', newline='').write(
        '\n'.join(parts) + '\n')
    io.open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf-8', newline='').write(
        ROBOTS.format(site=SITE))

    print('  sitemap.xml（%d 筆網址，已排除 %s）' % (len(urls), '、'.join('/%s/' % x for x in sorted(EXCLUDE))))
    print('  robots.txt')
    return len(urls)


if __name__ == '__main__':
    build()
