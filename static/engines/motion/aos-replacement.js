/**
 * 🎨 MOTION - AOS Replacement (GSAP ScrollTrigger)
 * Reemplaza AOS (Animate On Scroll) con GSAP nativo
 * Menos dependencies, mejor performance
 */

export const AOSReplacement = {
  initialized: false,

  /**
   * Inicializa animaciones de scroll
   */
  init() {
    if (this.initialized) return;
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
      console.warn('[AOSReplacement] GSAP o ScrollTrigger no disponibles');
      return;
    }

    this.initialized = true;
    
    // Verificar prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
      Logger.debug('[AOSReplacement] Reduced motion enabled - skipping animations');
      // Hacer elementos visibles inmediatamente
      document.querySelectorAll('[data-aos]').forEach(el => {
        el.style.opacity = '1';
        el.style.transform = 'none';
      });
      return;
    }

    this._setupAnimations();
  },

  /**
   * Configura animaciones para elementos [data-aos]
   */
  _setupAnimations() {
    const elements = document.querySelectorAll('[data-aos]');
    const isMobile = window.matchMedia("(pointer: coarse)").matches;
    
    elements.forEach(el => {
      const animationType = el.dataset.aos || 'fade-up';
      const delay = parseInt(el.dataset.aosDelay) || 0;
      const duration = parseFloat(el.dataset.aosDuration) || 0.8;
      const easing = el.dataset.aosEasing || 'power2.out';
      
      // Configuración inicial (oculto)
      gsap.set(el, this._getInitialState(animationType));
      
      // Verificar si ya está en viewport para disparar inmediatamente (evitar parpadeo/bloqueo)
      const rect = el.getBoundingClientRect();
      const inViewport = (rect.top <= (window.innerHeight || document.documentElement.clientHeight) * 0.9);
      
      // Animación al entrar en viewport
      gsap.to(el, {
        ...this._getFinalState(animationType),
        duration: duration,
        delay: inViewport ? (delay / 2000) : (delay / 1000), // Disparo más rápido si ya está visible
        ease: easing,
        scrollTrigger: {
          trigger: el,
          start: isMobile ? 'top 95%' : 'top 85%', // Más agresivo en mobile
          toggleActions: 'play none none none',
          once: true
        }
      });
    });

    Logger.debug(`[AOSReplacement] ${elements.length} elementos animados. Mobile: ${isMobile}`);
  },

  /**
   * Obtiene estado inicial según tipo de animación
   */
  _getInitialState(type) {
    const states = {
      'fade': { opacity: 0 },
      'fade-up': { opacity: 0, y: 50 },
      'fade-down': { opacity: 0, y: -50 },
      'fade-left': { opacity: 0, x: -50 },
      'fade-right': { opacity: 0, x: 50 },
      'zoom-in': { opacity: 0, scale: 0.9 },
      'zoom-out': { opacity: 0, scale: 1.1 },
      'flip-up': { opacity: 0, rotateX: 90 },
    };
    return states[type] || states['fade-up'];
  },

  /**
   * Obtiene estado final (visible) según tipo de animación
   */
  _getFinalState(type) {
    const states = {
      'fade': { opacity: 1 },
      'fade-up': { opacity: 1, y: 0 },
      'fade-down': { opacity: 1, y: 0 },
      'fade-left': { opacity: 1, x: 0 },
      'fade-right': { opacity: 1, x: 0 },
      'zoom-in': { opacity: 1, scale: 1 },
      'zoom-out': { opacity: 1, scale: 1 },
      'flip-up': { opacity: 1, rotateX: 0 },
    };
    return states[type] || states['fade-up'];
  },

  /**
   * Refresca animaciones (útil para contenido dinámico)
   */
  refresh() {
    if (typeof ScrollTrigger !== 'undefined') {
      ScrollTrigger.refresh();
    }
  }
};

// Auto-inicializar cuando DOM esté listo
if (typeof window !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => AOSReplacement.init());
  } else {
    // DOM ya cargado
    setTimeout(() => AOSReplacement.init(), 100);
  }
}

export default AOSReplacement;
