/**
 * 🎨 UI - Slider Manager
 * Before/After slider interactions
 */

export const SliderManager = {
  sliders: [],
  observer: null,

  init() {
    const containers = document.querySelectorAll('.slider-container, .ba-slider');
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

    const range = container.querySelector('.slider-range');
    const resizeImg = container.querySelector('.foreground-img');
    const thumb = container.querySelector('.slider-thumb');

    // ✅ Robust Validation: Log error if crucial elements are missing
    if (!range) {
      console.error('[SliderManager] .slider-range NOT FOUND in container', container);
      return;
    }
    if (!resizeImg) {
      console.error('[SliderManager] .foreground-img NOT FOUND in container', container);
      return;
    }

    const updateSlider = () => {
      const value = range.value;

      // Update clip-path of foreground image
      resizeImg.style.clipPath = `polygon(0 0, ${value}% 0, ${value}% 100%, 0 100%)`;

      // Update thumb position
      if (thumb) {
        thumb.style.left = `${value}%`;
      }
    };

    range.addEventListener('input', updateSlider);

    // Initial call to set positions
    updateSlider();

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
