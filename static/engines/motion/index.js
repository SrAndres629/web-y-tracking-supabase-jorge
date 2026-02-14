/**
 * 🎬 MOTION ENGINE - Entry Point
 * Animation and scroll effects using GSAP + Lenis
 */

import { LenisSetup } from './lenis-setup.js';
import { HeroAnimation } from './hero-animation.js';
import { Parallax } from './parallax.js';
import { Magnetic } from './magnetic.js';
import { Spotlight } from './spotlight.js';

const MotionEngine = {
  initialized: false,
  config: {
    lerp: 0.1,
    parallaxScrub: 1.2,
    magneticPower: 0.4,
    goldAlpha: 0.05
  },

  init(options = {}) {
    if (this.initialized) return;
    this.initialized = true;

    Object.assign(this.config, options);

    // Setup Lenis smooth scroll
    LenisSetup.init();
    
    // Sync with GSAP if available
    if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
      LenisSetup.syncWithGSAP();
    }

    // Hero animation
    HeroAnimation.init();

    // Parallax effects
    Parallax.init();

    // Magnetic buttons
    Magnetic.init();

    // Spotlight effect
    Spotlight.init();

    // Navigation scroll behavior
    this.setupNavigation();

    console.log('🚀 [Motion Engine] Initialized at 60fps');
  },

  setupNavigation() {
    const nav = document.querySelector('.glass-nav-premium');
    if (!nav) return;

    let lastScroll = 0;
    
    window.addEventListener('scroll', () => {
      const currentScroll = window.scrollY;
      
      if (currentScroll > 50) {
        nav.classList.add('scrolled');
      } else {
        nav.classList.remove('scrolled');
      }
      
      lastScroll = currentScroll;
    }, { passive: true });
  }
};

export { MotionEngine, LenisSetup, HeroAnimation, Parallax, Magnetic, Spotlight };
export default MotionEngine;

// Global exposure
if (typeof window !== 'undefined') {
  window.MotionEngine = MotionEngine;
}
