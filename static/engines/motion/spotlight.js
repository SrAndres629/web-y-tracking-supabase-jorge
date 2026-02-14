/**
 * 🎬 MOTION - Spotlight Effect
 * Mouse-following ambient light
 */

export const Spotlight = {
  spotlight: null,
  rafId: null,
  mouseX: 0,
  mouseY: 0,
  currentX: 0,
  currentY: 0,
  isTouch: window.matchMedia('(pointer: coarse)').matches,

  init() {
    if (this.isTouch) return; // Disable on touch devices

    this.spotlight = document.getElementById('mouse-spotlight');
    if (!this.spotlight) return;

    // Track mouse
    document.addEventListener('mousemove', (e) => {
      this.mouseX = e.clientX;
      this.mouseY = e.clientY;
    }, { passive: true });

    // Start animation loop
    this.animate();
  },

  animate() {
    // Lerp for smooth following
    this.currentX += (this.mouseX - this.currentX) * 0.1;
    this.currentY += (this.mouseY - this.currentY) * 0.1;

    if (this.spotlight) {
      this.spotlight.style.background = `radial-gradient(circle at ${this.currentX}px ${this.currentY}px, rgba(197, 160, 89, 0.08) 0%, transparent 50%)`;
    }

    this.rafId = requestAnimationFrame(() => this.animate());
  },

  destroy() {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
    }
  }
};
