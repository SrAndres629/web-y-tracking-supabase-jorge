/**
 * 🎨 UI ENGINE - Entry Point
 * User Interface interactions and enhancements
 */

import { NavManager } from './nav-manager.js';
import { SliderManager } from './slider-manager.js';
import { CROManager } from './cro-manager.js';

const UIEngine = {
  initialized: false,

  init() {
    if (this.initialized) return;
    this.initialized = true;

    // Core UI
    NavManager.init();
    SliderManager.init();

    // Deferred init for non-critical elements
    if ('requestIdleCallback' in window) {
      requestIdleCallback(() => this._deferredInit());
    } else {
      setTimeout(() => this._deferredInit(), 50);
    }

    console.log('✨ [UI Engine] Active');
  },

  _deferredInit() {
    CROManager.init();
  }
};

export { UIEngine, NavManager, SliderManager, CROManager };
export default UIEngine;

// Global
if (typeof window !== 'undefined') {
  window.UIEngine = UIEngine;
}
