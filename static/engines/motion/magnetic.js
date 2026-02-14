/**
 * 🎬 MOTION - Magnetic Effect
 * Elements that follow cursor
 */

export const Magnetic = {
  elements: [],
  isTouch: window.matchMedia('(pointer: coarse)').matches,

  init() {
    if (this.isTouch) return; // Disable on touch devices

    this.elements = document.querySelectorAll('[data-magnetic]');
    if (this.elements.length === 0) return;

    this.elements.forEach(el => {
      el.addEventListener('mousemove', this.onMouseMove.bind(this));
      el.addEventListener('mouseleave', this.onMouseLeave.bind(this));
    });
  },

  onMouseMove(e) {
    const el = e.currentTarget;
    const rect = el.getBoundingClientRect();
    const strength = parseFloat(el.dataset.magnetic) || 0.4;
    
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    
    el.style.transform = `translate(${x * strength}px, ${y * strength}px)`;
  },

  onMouseLeave(e) {
    const el = e.currentTarget;
    el.style.transform = '';
    el.style.transition = 'transform 0.3s ease';
    
    setTimeout(() => {
      el.style.transition = '';
    }, 300);
  }
};
