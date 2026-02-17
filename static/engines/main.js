/**
 * 🚀 MAIN ENGINE ENTRY POINT - ES6 Modules
 * Punto de entrada único para todos los engines
 * Reemplaza al bundle desactualizado
 */

import { TrackingEngine } from './tracking/index.js';
import { SliderManager } from './ui/slider-manager.js';
import { AOSReplacement } from './motion/aos-replacement.js';

// Configuración global
const DEBUG = new URLSearchParams(window.location.search).has('debug');

/**
 * Inicializa todos los engines cuando el DOM está listo
 */
function init() {
  if (DEBUG) console.log('[MainEngine] Initializing...');

  try {
    // 1. Tracking (Zaraz + CAPI)
    if (typeof TrackingEngine !== 'undefined') {
      TrackingEngine.init({ debug: DEBUG });
      if (DEBUG) console.log('[MainEngine] ✅ TrackingEngine initialized');
    }

    // 2. Sliders (Before/After)
    if (typeof SliderManager !== 'undefined') {
      SliderManager.init();
      if (DEBUG) console.log('[MainEngine] ✅ SliderManager initialized');
    }

    // 3. Animaciones (AOS replacement con GSAP)
    // Se inicializa automáticamente en el propio módulo, pero forzamos refresh
    setTimeout(() => {
      if (typeof AOSReplacement !== 'undefined') {
        AOSReplacement.refresh();
        if (DEBUG) console.log('[MainEngine] ✅ AOSReplacement refreshed');
      }
    }, 100);

    if (DEBUG) console.log('[MainEngine] 🚀 All engines initialized');

  } catch (error) {
    console.error('[MainEngine] ❌ Initialization error:', error);
  }
}

// Inicializar cuando DOM esté listo
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  // DOM ya cargado
  init();
}

// Exponer globalmente para debugging
if (DEBUG || typeof window !== 'undefined') {
  window.MainEngine = {
    init,
    TrackingEngine,
    SliderManager,
    AOSReplacement
  };
}
