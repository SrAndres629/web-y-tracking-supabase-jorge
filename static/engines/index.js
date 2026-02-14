/**
 * ⚡ ENGINES - Master Entry Point
 * Inicializa todos los motores de la aplicación
 * 
 * Uso en HTML:
 *   <script type="module">
 *     import { initEngines } from './engines/index.js';
 *     initEngines();
 *   </script>
 */

import TrackingEngine from './tracking/index.js';
import UIEngine from './ui/index.js';

/**
 * Inicializa todos los engines
 */
export function initEngines(options = {}) {
  // Tracking (analytics)
  if (options.tracking !== false) {
    TrackingEngine.init({ debug: options.debug });
  }

  // UI (interactions)
  if (options.ui !== false) {
    UIEngine.init();
  }

  // Motion se carga por separado ya que depende de GSAP/Lenis
  if (options.motion !== false && window.MotionEngine) {
    window.MotionEngine.init();
  }

  return {
    tracking: TrackingEngine,
    ui: UIEngine
  };
}

// Auto-init si no es módulo
if (typeof window !== 'undefined') {
  window.initEngines = initEngines;
  
 // Deferred auto-init para compatibilidad
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      if (!window.enginesManualInit) {
        initEngines();
      }
    });
  }
}

export { TrackingEngine, UIEngine };
export default { init: initEngines, TrackingEngine, UIEngine };
