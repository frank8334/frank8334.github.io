// GA4 Conversion Event Tracking – deferred (runs after page load)
(function() {
  if (typeof gtag !== 'function') return;

  document.addEventListener('DOMContentLoaded', function() {
    var navCta = document.querySelector('nav .nav-cta');
    if (navCta) navCta.addEventListener('click', function() {
      gtag('event', 'cta_click', { location: 'navbar', label: '免費預約諮詢' });
    });
    var heroBtn = document.querySelector('.hero .btn-primary');
    if (heroBtn) heroBtn.addEventListener('click', function() {
      gtag('event', 'cta_click', { location: 'hero', label: '預約免費30分鐘諮詢' });
    });
    var lineBtn = document.querySelector('.line-cta');
    if (lineBtn) lineBtn.addEventListener('click', function() {
      gtag('event', 'line_click', { location: 'contact_section', label: '加LINE立即諮詢' });
    });
    var phoneLink = document.querySelector('a[href^="tel:"]');
    if (phoneLink) phoneLink.addEventListener('click', function() {
      gtag('event', 'phone_click', { location: 'contact_section', label: '0905-732-500' });
    });
    document.querySelectorAll('a[href^="mailto:"]').forEach(function(el) {
      el.addEventListener('click', function() {
        gtag('event', 'email_click', { location: 'contact_section', label: el.href });
      });
    });
    var servicesSeen = false, servicesEl = document.getElementById('services');
    var contactSeen = false, contactEl = document.getElementById('contact');
    window.addEventListener('scroll', function() {
      if (!servicesSeen && servicesEl && servicesEl.getBoundingClientRect().top < window.innerHeight * 0.8) {
        servicesSeen = true;
        gtag('event', 'scroll_to_services', { label: '瀏覽服務項目' });
      }
      if (!contactSeen && contactEl && contactEl.getBoundingClientRect().top < window.innerHeight * 0.8) {
        contactSeen = true;
        gtag('event', 'scroll_to_contact', { label: '抵達聯絡區塊' });
      }
    }, { passive: true });
  });
})();
