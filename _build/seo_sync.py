"""同步公開頁面追蹤、首頁文章數與官網資料說明。"""
from pathlib import Path
import json, re
ROOT = Path(__file__).resolve().parent.parent
TRACKING = '''<!-- 官網 GA4 與聯絡事件 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-W87BYE0KYL"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','G-W87BYE0KYL',{cookie_domain:'starbright-integrated.com'});</script>
<script defer src="/assets/analytics.js?v=20261014"></script>
'''
def sync():
    data = json.loads((ROOT / '_build/blog-data.json').read_text(encoding='utf-8'))
    paths = [ROOT / 'index.html', *sorted((ROOT / 'blog').rglob('index.html')), *sorted((ROOT / 'tools').rglob('index.html')), ROOT / 'website-privacy/index.html']
    changed = 0
    for path in paths:
        if not path.exists(): continue
        original = path.read_text(encoding='utf-8')
        text = original
        if 'G-W87BYE0KYL' not in text:
            text = text.replace('</head>', TRACKING + '</head>', 1)
        else:
            text = re.sub(r'src="/assets/analytics\.js(?:\?[^\"]*)?"', 'src="/assets/analytics.js?v=20261014"', text)
        if path == ROOT / 'index.html':
            if 'rel="canonical"' not in text:
                text = text.replace('</head>', '<link rel="canonical" href="https://starbright-integrated.com/" />\n</head>', 1)
            text = re.sub(r'共 \d+ 篇，依主題分類', f"共 {len(data['posts'])} 篇，依主題分類", text)
            for topic in data['topics']:
                count = sum(p['topic'] == topic['slug'] for p in data['posts'])
                pattern = r'(<a class="blog-card" href="/blog/topic/' + re.escape(topic['slug']) + r'/">.*?<div class="blog-n">)\d+( 篇文章</div>)'
                text = re.sub(pattern, lambda m: m[1] + str(count) + m[2], text, flags=re.S)
        if '<footer' in text and 'href="/website-privacy/"' not in text:
            text = text.replace('</footer>', '<p><a href="/website-privacy/">官網資料使用說明</a></p>\n</footer>', 1)
        elif '<footer' not in text and 'href="/website-privacy/"' not in text:
            text = text.replace('</body>', '<footer style="text-align:center;padding:24px"><a href="/website-privacy/">官網資料使用說明</a></footer>\n</body>', 1)
        if text != original:
            path.write_text(text, encoding='utf-8', newline='')
            changed += 1
    print(f'官網追蹤及首頁統計同步：{changed} 頁更新')
if __name__ == '__main__': sync()
