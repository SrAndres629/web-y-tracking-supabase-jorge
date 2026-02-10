/**
 * 📊 TRACKING ENGINE - Entry Point
 * Sistema de tracking modular (Zaraz + CAPI)
 * 
 * Uso:
 *   import { TrackingEngine } from './engines/tracking/index.js';
 *   TrackingEngine.init();
 */

import { IdentityManager } from './identity.js';
import { UTMManager } from './utm.js';
import { PixelBridge } from './pixel-bridge.js';
import { CAPI } from './capi.js';
import { TrackingObservers } from './observers.js';
import { ConversionHandler, handleConversion } from './conversion.js';

const TrackingEngine = {
  initialized: false,
  debugMode: false,

  /**
   * Inicializa el sistema de tracking
   */
  init(options = {}) {
    if (this.initialized) return this;
    this.initialized = true;

    this.debugMode = options.debug || new URLSearchParams(window.location.search).has('debug_pixel');

    // 1. Identity (UUIDs, cookies)
    const identity = IdentityManager.init();
    this._log('🆔 Identity:', identity.externalId);

    // 2. UTM Capture
    const utms = UTMManager.capture();
    this._log('📡 Traffic Source:', UTMManager.getTrafficSource(), utms);

    // 3. Pixel Bridge
    PixelBridge.init({ debug: this.debugMode });

    // 4. Observers (ViewContent, Sliders)
    TrackingObservers.init();

    // 5. Track PageView via CAPI (Zaraz handles Pixel side)
    CAPI.trackAsync('PageView', { 
      event_id: identity.eventId 
    });

    this._log('📊 [Tracking Engine] Active (Zaraz + CAPI)');

    return this;
  },

  /**
   * Track event (convenience method)
   */
  track(eventName, data, options = {}) {
    const eventId = options.eventId || IdentityManager.generateEventId();
    
    // Client-side
    PixelBridge.track(eventName, data, { eventId });
    
    // Server-side
    CAPI.trackAsync(eventName, { ...data, event_id: eventId });
    
    return { eventId };
  },

  /**
   * Track custom event
   */
  trackCustom(eventName, data, options = {}) {
    const eventId = options.eventId || IdentityManager.generateEventId();
    
    PixelBridge.trackCustom(eventName, data, { eventId });
    CAPI.trackAsync(eventName, { ...data, event_id: eventId });
    
    return { eventId };
  },

  /**
   * Handle conversion (WhatsApp)
   */
  convert(source) {
    return ConversionHandler.handle(source);
  },

  /**
   * Logger condicional
   */
  _log(message, ...args) {
    if (this.debugMode) {
      console.log(message, ...args);
    }
  }
};

// Exportar API pública
export { TrackingEngine, IdentityManager, UTMManager, PixelBridge, CAPI, ConversionHandler, handleConversion };

// Exportar global para compatibilidad
if (typeof window !== 'undefined') {
  window.TrackingEngine = TrackingEngine;
  window.handleConversion = handleConversion;
}

export default TrackingEngine;
