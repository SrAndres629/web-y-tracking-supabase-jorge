/**
 * 🎨 UI - Navigation Manager
 * Navbar glass effect y scroll behavior
 */

export const NavManager = {
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
