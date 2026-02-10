/**
 * 🎬 MOTION - Hero Animation
 * Apple-style cinematic entrance
 */

export const HeroAnimation = {
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
