/* =================================================================
   MOTION.JS - Scrollytelling & Creative Motion (Premium Edition)
   Architecture: High-Performance Concurrent Motion Engine
   Dependencies: Lenis, GSAP, ScrollTrigger
   ================================================================= */

// Global State Manager (Singleton)
const MotionEngine = {
    lenis: null,
    initialized: false,

    // Config: Physics & Mathematics
    physics: {
        lerp: 0.07,          // Follow inertia
        parallaxScrub: 1,    // Parallax damping
        magneticPower: 0.35, // Attraction strength
        goldAlpha: 0.07      // Ambient light intensity
    },

    init() {
        if (this.initialized) return;
        this.initialized = true;

        // Sequence of initialization
        this.setupLenis();
        this.setupGSAP();
        this.setupHeroAnimation();  // NEW: Premium hero reveal
        this.setupParallax();
        this.setupMagnetic();
        this.setupSpotlight();
        this.setupNavigation();
        this.setupMobileTriggers();

        console.log('🚀 [Senior Architecture] Motion Engine Initialized at 60fps');
    },

    /**
     * 0. HERO ANIMATION - Apple-Style Cinematic Entrance
     */
    setupHeroAnimation() {
        if (typeof gsap === 'undefined') return;

        const heroPortrait = document.querySelector('.hero-portrait');
        const heroGlow = document.querySelector('.hero-glow');
        const heroBorder = document.querySelector('.hero-border');

        if (!heroPortrait) return;

        // Initial state - slightly scaled down and transparent
        gsap.set(heroPortrait, {
            opacity: 0,
            scale: 0.92,
            y: 30,
            filter: 'blur(8px)'
        });
        gsap.set([heroGlow, heroBorder], { opacity: 0 });

        // Cinematic Reveal Timeline
        const heroTL = gsap.timeline({ delay: 0.4 });

        heroTL
            .to(heroPortrait, {
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

        // Scroll-based Parallax & Glow Intensity
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
                start: 'top 80%',
                end: 'center center',
                scrub: 2
            }
        });

        console.log('🎬 [Hero Animation] Cinematic reveal initialized');
    },


    /**
     * 1. LENIS - Smooth Scroll (Butter Feel)
     */
    setupLenis() {
        if (typeof Lenis === 'undefined' || window.innerWidth < 768) return;

        this.lenis = new Lenis({
            duration: 1.2,
            easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
            touchMultiplier: 1.5,
            smoothWheel: true
        });

        const scrollHandler = (time) => {
            this.lenis.raf(time);
            requestAnimationFrame(scrollHandler);
        };
        requestAnimationFrame(scrollHandler);

        // Sync with GSAP
        if (typeof gsap !== 'undefined') {
            this.lenis.on('scroll', ScrollTrigger.update);
            gsap.ticker.add((time) => {
                this.lenis.raf(time * 1000);
            });
            gsap.ticker.lagSmoothing(0);
        }
    },

    /**
     * 2. GSAP - Staggered Entrances
     */
    setupGSAP() {
        if (typeof gsap === 'undefined') return;
        gsap.registerPlugin(ScrollTrigger);

        // Entrance animation factory
        const animateItems = (selector, start) => {
            const items = document.querySelectorAll(selector);
            if (!items.length) return;

            gsap.fromTo(items,
                { opacity: 0, y: 50, scale: 0.95 },
                {
                    opacity: 1, y: 0, scale: 1,
                    duration: 0.8,
                    stagger: 0.15,
                    ease: "power2.out",
                    scrollTrigger: {
                        trigger: items[0].parentElement,
                        start: start || "top 80%",
                        toggleActions: "play none none reverse"
                    }
                }
            );
        };

        animateItems('.service-card, .process-step, .testimonial-card', "top 75%");
        animateItems('.ba-slider', "top 70%");
    },

    /**
     * 3. PARALLAX - Depth Realism
     */
    setupParallax() {
        const hero = document.querySelector('header img[fetchpriority="high"]');
        if (!hero) return;

        gsap.to(hero, {
            yPercent: 15,
            ease: "none",
            scrollTrigger: {
                trigger: "header",
                start: "top top",
                end: "bottom top",
                scrub: this.physics.parallaxScrub
            }
        });
    },

    /**
     * 4. MAGNETIC BUTTONS (Physics Based)
     */
    setupMagnetic() {
        const buttons = document.querySelectorAll('#whatsappFloat');
        if (!window.matchMedia('(pointer: fine)').matches) return;

        buttons.forEach(btn => {
            btn.addEventListener('mousemove', (e) => {
                const rect = btn.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = e.clientY - rect.top - rect.height / 2;

                gsap.to(btn, {
                    x: x * this.physics.magneticPower,
                    y: y * this.physics.magneticPower,
                    scale: 1.1,
                    duration: 0.3,
                    ease: "power2.out"
                });
            });

            btn.addEventListener('mouseleave', () => {
                gsap.to(btn, {
                    x: 0, y: 0, scale: 1,
                    duration: 0.6,
                    ease: "elastic.out(1, 0.3)"
                });
            });
        });
    },

    /**
     * 5. SPOTLIGHT (Ambient Mathematics)
     */
    setupSpotlight() {
        const spotlight = document.getElementById('mouse-spotlight');
        if (!spotlight || !window.matchMedia('(pointer: fine)').matches) return;

        let mouseX = 0, mouseY = 0;
        let currentX = 0, currentY = 0;

        window.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
        }, { passive: true });

        const animateSpotlight = () => {
            // Lerp physics: target = current + (diff * factor)
            currentX += (mouseX - currentX) * this.physics.lerp;
            currentY += (mouseY - currentY) * this.physics.lerp;

            spotlight.style.background = `radial-gradient(1000px circle at ${currentX}px ${currentY}px, rgba(212, 175, 55, ${this.physics.goldAlpha}), transparent 60%)`;
            requestAnimationFrame(animateSpotlight);
        };
        requestAnimationFrame(animateSpotlight);
    },

    /**
     * 6. NAVIGATION (Sticky Glass Logic)
     */
    setupNavigation() {
        const nav = document.getElementById('mainNav');
        const cta = document.getElementById('navCta');
        if (!nav) return;

        ScrollTrigger.create({
            start: "top -100",
            onUpdate: (self) => {
                const isScrolled = self.scroll() > 100;
                nav.classList.toggle('backdrop-blur-md', isScrolled);
                nav.classList.toggle('bg-luxury-black/95', isScrolled);
                nav.classList.toggle('border-luxury-gold/20', isScrolled);
                nav.classList.toggle('shadow-lg', isScrolled);

                if (cta) {
                    cta.classList.toggle('opacity-100', isScrolled);
                    cta.classList.toggle('translate-y-0', isScrolled);
                    cta.classList.toggle('opacity-0', !isScrolled);
                    cta.classList.toggle('translate-y-[-10px]', !isScrolled);
                }
            }
        });
    },

    /**
     * 7. MOBILE OPTIMIZATION
     */
    setupMobileTriggers() {
        if (window.innerWidth >= 768) return;

        // Optimized target selection for mobile performance
        const targets = document.querySelectorAll('.service-card-skin, .ba-slider, .testimonial-card');
        targets.forEach(target => {
            ScrollTrigger.create({
                trigger: target,
                start: "top center+=100",
                end: "bottom center-=100",
                toggleClass: "mobile-active"
            });
        });
    }
};

// Senior Init Pattern: Avoid DOMContentLoaded if already ready
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    MotionEngine.init();
} else {
    document.addEventListener('DOMContentLoaded', () => MotionEngine.init(), { once: true });
}
