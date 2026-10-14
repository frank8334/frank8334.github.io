// 委派監聽涵蓋文章、工具頁及動態更新的聯絡連結。
(function () {
  if (window.__starbrightAnalyticsBound) return;
  window.__starbrightAnalyticsBound = true;
  function track(name, location) {
    if (typeof window.gtag === 'function') {
      window.gtag('event', name, { location: location, page_path: window.location.pathname });
    }
  }
  document.addEventListener('click', function (event) {
    var link = event.target.closest && event.target.closest('a[href]');
    if (!link) return;
    var url;
    try { url = new URL(link.href, window.location.href); } catch (_) { return; }
    var location = link.closest('footer') ? 'footer' : link.closest('nav') ? 'navbar' :
      link.closest('.hero') ? 'hero' : link.closest('#contact') ? 'contact_section' : 'content';
    // 不送出電話、email、諮詢文字或網址查詢參數。
    if (url.hostname === 'line.me' || url.hostname === 'lin.ee') track('line_click', location);
    else if (url.protocol === 'tel:') track('phone_click', location);
    else if (url.protocol === 'mailto:') track('email_click', location);
    else if (link.matches('nav .nav-cta, .hero .btn-primary')) track('cta_click', location);
  });
  function bindScroll() {
    var seen = {};
    function inspect() {
      ['services', 'contact'].forEach(function (id) {
        var element = document.getElementById(id);
        if (!seen[id] && element && element.getBoundingClientRect().top < window.innerHeight * 0.8) {
          seen[id] = true;
          track('scroll_to_' + id, id === 'contact' ? 'contact_section' : 'content');
        }
      });
    }
    window.addEventListener('scroll', inspect, { passive: true });
    inspect();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bindScroll, { once: true });
  else bindScroll();
})();
