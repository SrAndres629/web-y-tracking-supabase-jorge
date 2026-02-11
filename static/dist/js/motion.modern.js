/**
 * 🎬 MOTION - Lenis Smooth Scroll Setup
 */

const LenisSetup = {
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

/**
 * 🎬 MOTION - Hero Animation
 * Apple-style cinematic entrance
 */

const HeroAnimation = {
  init() {
    if (typeof gsap === 'undefined') return;

    const heroPortrait = document.querySelector('.hero-portrait');
    const heroGlow = document.querySelector('.hero-glow');
    const heroBorder = document.querySelector('.hero-border');

    if (!heroPortrait) return;

    // Initial state
    gsap.set([heroGlow, heroBorder], { opacity: 0 });

    // Timeline
    const tl = gsap.timeline({ delay: 0.4 });

    tl.to(heroPortrait, {
      opacity: 1,
      scale: 1,
      y: 0,
      filter: 'blur(0px)',
      duration: 1.4,
      ease: "power3.out"
    })
    .to(heroBorder, {
      opacity: 1,
      duration: 0.8,
      ease: "power2.inOut"
    }, "-=0.6")
    .to(heroGlow, {
      opacity: 0.6,
      duration: 1.2,
      ease: "power2.out"
    }, "-=0.4");

    // Scroll parallax
    gsap.to(heroPortrait, {
      y: -40,
      scrollTrigger: {
        trigger: '.hero-image-container',
        start: 'top center',
        end: 'bottom top',
        scrub: 1.5
      }
    });

    // Glow intensifies on scroll
    gsap.to(heroGlow, {
      opacity: 1,
      scale: 1.1,
      scrollTrigger: {
        trigger: '.hero-image-container',
        start: 'top center',
        end: 'bottom top',
        scrub: true
      }
    });
  }
};

/**
 * 🎬 MOTION - Parallax Effects
 */

const Parallax = {
  init() {
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;

    // Elements with parallax
    const parallaxElements = document.querySelectorAll('[data-parallax]');
    
    parallaxElements.forEach(el => {
      const speed = parseFloat(el.dataset.parallax) || 0.5;
      
      gsap.to(el, {
        y: () => -100 * speed,
        ease: "none",
        scrollTrigger: {
          trigger: el,
          start: "top bottom",
          end: "bottom top",
          scrub: true
        }
      });
    });

    // Gold dust particles
    this.setupGoldDust();
  },

  setupGoldDust() {
    const containers = document.querySelectorAll('.gold-dust-container');
    
    containers.forEach(container => {
      const particleCount = parseInt(container.dataset.particles) || 20;
      
      for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'gold-dust-particle';
        
        const size = Math.random() * 4 + 2;
        particle.style.cssText = `
          width: ${size}px;
          height: ${size}px;
          left: ${Math.random() * 100}%;
          top: ${Math.random() * 100}%;
          --particle-x: ${(Math.random() - 0.5) * 200}px;
          --particle-y: ${(Math.random() - 0.5) * 200}px;
          --particle-duration: ${Math.random() * 3 + 4}s;
          --particle-delay: ${Math.random() * 5}s;
        `;
        
        container.appendChild(particle);
      }
    });
  }
};

/**
 * 🎬 MOTION - Magnetic Effect
 * Elements that follow cursor
 */

const Magnetic = {
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

/**
 * 🎬 MOTION - Spotlight Effect
 * Mouse-following ambient light
 */

const Spotlight = {
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

/**
 * 🎬 MOTION ENGINE - Entry Point
 * Animation and scroll effects using GSAP + Lenis
 */


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
    
    window.addEventListener('scroll', () => {
      const currentScroll = window.scrollY;
      
      if (currentScroll > 50) {
        nav.classList.add('scrolled');
      } else {
        nav.classList.remove('scrolled');
      }
    }, { passive: true });
  }
};

// Global exposure
if (typeof window !== 'undefined') {
  window.MotionEngine = MotionEngine;
}

export { HeroAnimation, LenisSetup, Magnetic, MotionEngine, Parallax, Spotlight, MotionEngine as default };
//# sourceMappingURL=motion.modern.js.map
