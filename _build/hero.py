# -*- coding: utf-8 -*-
"""替每篇文章產生 1200x630 封面圖（文章頁首圖＋社群分享預覽圖 og:image）。

輸出：assets/blog/<slug>.jpg（社群分享用，相容性最好）
      assets/blog/<slug>.webp（文章頁顯示用，檔案小）
內容：主題圖示與名稱、文章標題、一句重點（blog-data.json 的 hero_line）、品牌與官方 LINE。
用瀏覽器排版中文，避免 Pillow 斷字與字距問題。

用法：python _build/hero.py          # 全部重建
      python _build/hero.py <slug>   # 只建一篇
"""
import io, os, sys, json, html, tempfile

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, '_build', 'blog-data.json')
OUT = os.path.join(ROOT, 'assets', 'blog')

# 各主題的強調色（與文章頁的海軍藍為底搭配）
ACCENT = {
    'workplace-bullying': '#F59E0B',
    'labor-inspection': '#38BDF8',
    'occupational-injury': '#F87171',
    'hr-system': '#34D399',
    'termination-dispute': '#A78BFA',
    'funding': '#FBBF24',
}

TPL = """<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1200px;height:630px;font-family:'Source Han Sans TW','Noto Sans TC','Microsoft JhengHei',sans-serif;
 background:radial-gradient(circle at 85% 30%, #24476F 0%, #132A47 45%, #0B1B30 100%);color:#fff;position:relative;overflow:hidden}
.bar{position:absolute;left:0;top:0;bottom:0;width:14px;background:{accent}}
.icon{position:absolute;right:70px;top:110px;width:300px;height:300px;border-radius:50%;
 background:rgba(255,255,255,.06);border:2px solid rgba(255,255,255,.12);display:flex;align-items:center;justify-content:center;
 font-family:'Segoe UI Emoji','Apple Color Emoji',sans-serif;font-size:150px}
.wrap{position:absolute;left:80px;top:70px;width:690px}
.tag{display:inline-block;background:{accent};color:#0B1B30;font-weight:800;font-size:26px;padding:6px 20px;border-radius:30px}
h1{margin-top:28px;font-size:{tsize}px;line-height:1.32;font-weight:900;letter-spacing:.01em}
.line{margin-top:26px;font-size:28px;line-height:1.5;color:#CBD5E1;border-left:5px solid {accent};padding-left:18px}
.foot{position:absolute;left:80px;right:70px;bottom:40px;display:flex;justify-content:space-between;
 font-size:24px;color:#94A3B8;border-top:1px solid rgba(255,255,255,.15);padding-top:20px}
.foot b{color:#fff}
</style></head><body>
<div class="bar"></div>
<div class="icon">{icon}</div>
<div class="wrap">
 <span class="tag">{topic}</span>
 <h1>{title}</h1>
 <div class="line">{line}</div>
</div>
<div class="foot"><span><b>星耀整合顧問</b>｜勞資法規專欄</span><span>starbright-integrated.com｜LINE @907qijtp</span></div>
</body></html>"""


def build(only=None):
    d = json.load(io.open(DATA, encoding='utf-8'))
    topics = {t['slug']: t for t in d['topics']}
    os.makedirs(OUT, exist_ok=True)
    e = html.escape
    made = 0
    with sync_playwright() as p:
        try:
            br = p.chromium.launch()
        except Exception:
            br = p.chromium.launch(channel='chrome')
        pg = br.new_page(viewport={'width': 1200, 'height': 630})
        for post in d['posts']:
            if only and post['slug'] != only:
                continue
            t = topics[post['topic']]
            title = post['title'].split('｜')[0]
            # 標題越長字越小，維持在三行內
            tsize = 54 if len(title) <= 22 else 46 if len(title) <= 32 else 40
            line = post.get('hero_line') or post.get('excerpt', '')
            if len(line) > 60:
                line = line[:58].rstrip('，、；——') + '…'
            doc = (TPL.replace('{accent}', ACCENT.get(t['slug'], '#F59E0B'))
                      .replace('{tsize}', str(tsize))
                      .replace('{icon}', e(t.get('icon', '')))
                      .replace('{topic}', e(t['name']))
                      .replace('{title}', e(title))
                      .replace('{line}', e(line)))
            tmp = os.path.join(tempfile.gettempdir(), 'sb_hero.html')
            io.open(tmp, 'w', encoding='utf-8').write(doc)
            pg.goto('file:///' + tmp.replace('\\', '/'))
            pg.wait_for_timeout(150)
            png = pg.screenshot(type='png')
            im = Image.open(io.BytesIO(png)).convert('RGB')
            im.save(os.path.join(OUT, post['slug'] + '.jpg'), quality=86, optimize=True, progressive=True)
            im.save(os.path.join(OUT, post['slug'] + '.webp'), quality=82, method=6)
            made += 1
        br.close()
    print('  封面圖 %d 張 → assets/blog/' % made)


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else None)
