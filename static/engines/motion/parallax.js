/**
 * 🎬 MOTION - Parallax Effects
 */

export const Parallax = {
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
