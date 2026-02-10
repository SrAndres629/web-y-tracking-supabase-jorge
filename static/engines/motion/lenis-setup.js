/**
 * 🎬 MOTION - Lenis Smooth Scroll Setup
 */

export const LenisSetup = {
  lenis: null,

  init() {
    if (typeof Lenis === 'undefined') {
      console.warn('Lenis not loaded');
      return null;
    }

    this.lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
    });

    // RAF loop
    const raf = (time) => {
      this.lenis.raf(time);
      requestAnimationFrame(raf);
    };
    requestAnimationFrame(raf);

    // Expose globally
    window.lenis = this.lenis;
    
    return this.lenis;
  },

  /**
   * Sync with GSAP ScrollTrigger
   */
  syncWithGSAP() {
    if (!this.lenis || typeof ScrollTrigger === 'undefined') return;

    this.lenis.on('scroll', ScrollTrigger.update);
    
    gsap.ticker.add((time) => {
      this.lenis.raf(time * 1000);
    });
    
    gsap.ticker.lagSmoothing(0);
  }
};
