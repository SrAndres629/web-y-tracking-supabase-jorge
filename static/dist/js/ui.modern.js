/**
 * 🎨 UI - Navigation Manager
 * Navbar glass effect y scroll behavior
 */

const NavManager = {
  nav: null,
  isScrolled: false,

  init() {
    this.nav = document.querySelector('.glass-nav-premium');
    if (!this.nav) return;

    this._setupScrollListener();
    this._setupMobileMenu();
  },

  _setupScrollListener() {
    const handleScroll = () => {
      const shouldBeScrolled = window.scrollY > 50;
      
      if (shouldBeScrolled !== this.isScrolled) {
        this.isScrolled = shouldBeScrolled;
        this.nav.classList.toggle('scrolled', shouldBeScrolled);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll(); // Initial state
  },

  _setupMobileMenu() {
    const toggle = document.querySelector('.mobile-menu-toggle');
    const menu = document.querySelector('.mobile-menu');
    
    if (toggle && menu) {
      toggle.addEventListener('click', () => {
        menu.classList.toggle('open');
        toggle.setAttribute('aria-expanded', menu.classList.contains('open'));
      });
    }
  }
};

/**
 * 🎨 UI - Slider Manager
 * Before/After slider interactions
 */

const SliderManager = {
  sliders: [],
  observer: null,

  init() {
    const containers = document.querySelectorAll('.slider-container');
    if (!containers.length) return;

    this._setupObserver();
    containers.forEach(el => this.observer.observe(el));

    // Resize handler
    window.addEventListener('resize', this._debounce(() => {
      this.sliders.forEach(s => s.update && s.update());
    }, 250), { passive: true });
  },

  _setupObserver() {
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this._setupSlider(entry.target);
          this.observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: '100px' });
  },

  _setupSlider(container) {
    if (container.dataset.initialized) return;

    const slider = container.querySelector('.ba-slider');
    const range = container.querySelector('.slider-range');
    const resizeImg = container.querySelector('.resize');

    if (!slider || !range || !resizeImg) return;

    const updateSlider = () => {
      const value = range.value;
      resizeImg.style.width = `${value}%`;
      slider.classList.toggle('show-after', value > 50);
    };

    range.addEventListener('input', updateSlider);
    updateSlider();

    // Arrow controls
    const leftArrow = container.querySelector('.slider-arrow.left');
    const rightArrow = container.querySelector('.slider-arrow.right');

    if (leftArrow) {
      leftArrow.addEventListener('click', () => {
        range.value = 25;
        updateSlider();
      });
    }

    if (rightArrow) {
      rightArrow.addEventListener('click', () => {
        range.value = 75;
        updateSlider();
      });
    }

    container.dataset.initialized = 'true';
    this.sliders.push({ update: updateSlider });
  },

  _debounce(fn, wait) {
    let timeout;
    return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn.apply(this, args), wait);
    };
  }
};

/**
 * 🎨 UI - CRO Manager
 * Conversion Rate Optimization elements
 */

const CROManager = {
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

/**
 * 🎨 UI ENGINE - Entry Point
 * User Interface interactions and enhancements
 */


const UIEngine = {
  initialized: false,
  
  // Exponer managers para compatibilidad con sistema antiguo
  NavManager,
  SliderManager,
  CROManager,

  init() {
    if (this.initialized) return;
    this.initialized = true;

    // Core UI
    this.NavManager.init();
    this.SliderManager.init();

    // Deferred init for non-critical elements
    if ('requestIdleCallback' in window) {
      requestIdleCallback(() => this._deferredInit());
    } else {
      setTimeout(() => this._deferredInit(), 50);
    }

    console.log('✨ [UI Engine] Active');
  },

  _deferredInit() {
    this.CROManager.init();
  }
};

// Global
if (typeof window !== 'undefined') {
  window.UIEngine = UIEngine;
}

export { CROManager, NavManager, SliderManager, UIEngine, UIEngine as default };
//# sourceMappingURL=ui.modern.js.map
