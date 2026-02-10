/**
 * 🎨 UI - Slider Manager
 * Before/After slider interactions
 */

export const SliderManager = {
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
