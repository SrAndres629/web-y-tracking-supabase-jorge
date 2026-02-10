/**
 * 🔄 LEGACY ADAPTER
 * Compatibility layer for old static/js/*.js files
 * 
 * This adapter allows gradual migration from the old monolithic
 * files to the new modular system.
 * 
 * Usage: Replace old script tags with:
 *   <script type="module" src="/static_new/engines/legacy-adapter.js"></script>
 */

import { TrackingEngine, handleConversion } from './tracking/index.js';
import { UIEngine } from './ui/index.js';
import { MotionEngine } from './motion/index.js';

// Initialize all engines
function initLegacy() {
  // Check for debug mode
  const debug = new URLSearchParams(window.location.search).has('debug');
  
  // Initialize engines
  if (!window.TrackingEngine) {
    TrackingEngine.init({ debug });
  }
  
  if (!window.UIEngine) {
    UIEngine.init();
  }
  
  if (!window.MotionEngine && typeof gsap !== 'undefined') {
    MotionEngine.init();
  }

  console.log('✅ [Legacy Adapter] All engines initialized');
}

// Auto-init when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initLegacy);
} else {
  initLegacy();
}

// Expose globals for inline scripts (compatibilidad con sistema antiguo)
window.handleConversion = handleConversion;
window.TrackingEngine = TrackingEngine;
window.UIEngine = UIEngine;
window.MotionEngine = MotionEngine;

// Turnstile callback (Anti-Bot) - requerido por templates
window.onTurnstileSuccess = function(token) {
  if (TrackingEngine.initialized) {
    TrackingEngine.turnstileToken = token;
    TrackingEngine.isHuman = true;
  }
  console.log('🤖 Turnstile Verified: User is Human');
};

// TrackingEngine properties para compatibilidad
Object.defineProperty(TrackingEngine, 'turnstileToken', {
  value: null,
  writable: true,
  configurable: true
});

Object.defineProperty(TrackingEngine, 'isHuman', {
  value: false,
  writable: true,
  configurable: true
});

export { TrackingEngine, UIEngine, MotionEngine, handleConversion };
