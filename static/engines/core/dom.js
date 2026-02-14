/**
 * 🔧 CORE - DOM Utilities
 * Helpers para manipulación de DOM segura y performante
 */

export const DOM = {
  /**
   * Selecciona elementos con verificación de existencia
   */
  $(selector, context = document) {
    return context.querySelector(selector);
  },

  $$
(selector, context = document) {
    return Array.from(context.querySelectorAll(selector));
  },

  /**
   * Verifica si un elemento existe en el DOM
   */
  exists(selector) {
    return document.querySelector(selector) !== null;
  },

  /**
   * Ejecuta callback cuando DOM está listo
   */
  ready(callback) {
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
      callback();
    } else {
      document.addEventListener('DOMContentLoaded', callback, { once: true });
    }
  },

  /**
   * Crea un IntersectionObserver con opciones por defecto
   */
  observe(element, callback, options = {}) {
    const defaultOptions = {
      threshold: 0.6,
      rootMargin: '100px',
      ...options
    };
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(callback);
    }, defaultOptions);
    
    if (element) {
      observer.observe(element);
    }
    
    return observer;
  },

  /**
   * Throttle para eventos de scroll/resize
   */
  throttle(fn, wait = 100) {
    let lastTime = 0;
    return (...args) => {
      const now = Date.now();
      if (now - lastTime >= wait) {
        lastTime = now;
        fn.apply(this, args);
      }
    };
  },

  /**
   * Debounce para inputs/eventos frecuentes
   */
  debounce(fn, wait = 250) {
    let timeout;
    return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn.apply(this, args), wait);
    };
  }
};
