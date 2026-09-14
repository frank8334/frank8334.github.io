# -*- coding: utf-8 -*-
"""內文互鏈：把別篇文章的代表詞，在本篇內文首次出現時自動連過去。

為什麼要自動做：手動加內鏈在 4 篇時還行，12 篇就會開始漏，
而且每加一篇新文章，舊文章都應該有機會連到它——手動不可能回頭補。

⚠️ 刻意的限制（自動內鏈做過頭反而傷閱讀與 SEO）：
  - 每個目標文章在同一篇內**最多連一次**（連第二次沒有額外價值）
  - 每篇文章**最多 MAX_LINKS 條**自動內鏈
  - 只在 <p>、<li>、<td> 的內文動手；標題、表頭、FAQ、既有連結、程式碼一律跳過
  - 不連自己
"""
import re

# 站上文章數成長後略為放寬：12 篇時 4 條，23 篇時 5 條。
# 這個數字的意義是「一篇文章最多分出去幾條注意力」，不是越多越好。
MAX_LINKS = 5

# 這些標籤之內不得插入連結
SKIP_TAGS = ('a', 'h1', 'h2', 'h3', 'h4', 'code', 'summary', 'th')

_TAG = re.compile(r'<[^>]+>')


def _segments(html):
    """把 HTML 切成 (是否為標籤, 內容, 目前所在標籤堆疊) 的序列。"""
    pos, stack = 0, []
    for m in _TAG.finditer(html):
        if m.start() > pos:
            yield False, html[pos:m.start()], tuple(stack)
        tag = m.group(0)
        name = re.match(r'</?\s*([a-zA-Z0-9]+)', tag)
        if name:
            nm = name.group(1).lower()
            if tag.startswith('</'):
                if nm in stack:
                    # 退到最近的同名標籤
                    while stack and stack.pop() != nm:
                        pass
            elif not tag.endswith('/>'):
                stack.append(nm)
        yield True, tag, tuple(stack)
        pos = m.end()
    if pos < len(html):
        yield False, html[pos:], tuple(stack)


def apply(body_html, slug, posts):
    """posts 為 blog-data.json 的 posts 清單；回傳 (新 HTML, 實際連出的 slug 清單)。"""
    # 代表詞長的先比對，避免「創業貸款」搶走「青年創業貸款」
    targets = []
    for p in posts:
        if p['slug'] == slug:
            continue
        for term in p.get('link_terms', []):
            targets.append((term, p['slug'], p['title']))
    targets.sort(key=lambda x: -len(x[0]))

    used_slugs, linked = set(), []
    out = []
    for is_tag, chunk, stack in _segments(body_html):
        if is_tag or len(linked) >= MAX_LINKS:
            out.append(chunk)
            continue
        if any(t in stack for t in SKIP_TAGS):
            out.append(chunk)
            continue
        # 只在段落、清單項目與表格儲存格內加連結
        if not ({'p', 'li', 'td'} & set(stack)):
            out.append(chunk)
            continue
        # 先在「原始」字串上決定要改哪幾段，最後一次拼接。
        # 邊改邊找會讓後面的詞比對到自己剛插入的 title 屬性內容。
        hits = []          # (起, 迄, slug, title, term)
        taken = []         # 已佔用的區間，用來擋重疊
        for term, tslug, title in targets:
            if tslug in used_slugs or len(hits) + len(linked) >= MAX_LINKS:
                continue
            idx = chunk.find(term)
            if idx < 0:
                continue
            end = idx + len(term)
            if any(idx < b and a < end for a, b in taken):
                continue   # 與已選的詞重疊，讓長的那個贏
            hits.append((idx, end, tslug, title, term))
            taken.append((idx, end))
            used_slugs.add(tslug)

        if hits:
            hits.sort()
            buf, last = [], 0
            for a, b, tslug, title, term in hits:
                buf.append(chunk[last:a])
                buf.append('<a class="xlink" href="/blog/%s/" title="%s">%s</a>'
                           % (tslug, title.replace('"', '&quot;'), term))
                last = b
                linked.append(tslug)
            buf.append(chunk[last:])
            chunk = ''.join(buf)
        out.append(chunk)
    return ''.join(out), linked
