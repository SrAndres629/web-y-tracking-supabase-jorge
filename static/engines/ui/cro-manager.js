/**
 * 🎨 UI - CRO Manager
 * Conversion Rate Optimization elements
 */

export const CROManager = {
  init() {
    this._setupWhatsAppTooltip();
    this._setupStickyCTA();
  },

  _setupWhatsAppTooltip() {
    const tooltip = document.getElementById('whatsappTooltip');
    const badge = document.getElementById('experienceBadge');
    const btn = document.getElementById('whatsappPremium');

    if (!tooltip || !btn) return;

    // Show after 5 seconds
    setTimeout(() => {
      tooltip.classList.add('active');
      if (badge) badge.classList.add('active');
      btn.classList.add('pulse');

      // Hide after 8 seconds
      setTimeout(() => {
        tooltip.classList.remove('active');
        btn.classList.remove('pulse');
      }, 8000);
    }, 5000);

    // Hide on click
    btn.addEventListener('click', () => {
      tooltip.classList.remove('active');
      btn.classList.remove('pulse');
    });
  },

  _setupStickyCTA() {
    const stickyCta = document.querySelector('.sticky-cta');
    if (!stickyCta) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        stickyCta.classList.toggle('visible', !entry.isIntersecting);
      });
    }, { threshold: 0 });

    const heroCta = document.querySelector('.hero-cta');
    if (heroCta) {
      observer.observe(heroCta);
    }
  }
};
