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
import { UUID } from '../core/uuid.js';
import { Storage } from '../core/storage.js';
import { Logger } from '../core/logger.js';
import { ConsentManager } from '../privacy/consent-manager.js';
import { ConsentBanner } from '../privacy/cookie-banner.js';

const TrackingEngine = {
  initialized: false,
  debugMode: false,

  // Propiedades para compatibilidad con sistema antiguo
  turnstileToken: null,
  isHuman: false,

  /**
   * Inicializa el sistema de tracking
   */
  init(options = {}) {
    if (this.initialized) return this;
    this.initialized = true;

    this.debugMode = options.debug || new URLSearchParams(window.location.search).has('debug_pixel');

    // 0. Privacy & Consent (Blocking)
    const consent = ConsentManager.init();
    ConsentBanner.init(consent);

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

    // 5. PageView - Fire Pixel (Frontend) with shared eventId for Deduplication
    // Note: Zaraz handles Pixel PageView automatically. We send to CAPI manually for robustness.

    // ✅ Send to CAPI (Server-Side)
    // Always send PageView (legitimate interest for security/analytics) BUT respect flags if strictly required
    // For MVP: Send CAPI event, let backend filter based on flags
    CAPI.track('PageView', {
      event_id: identity.eventId,
      source: 'landing',
      consent: consent.preferences // Pass consent state to backend
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
   * Handle conversion - alias para compatibilidad
   * @deprecated Usar handleConversion() global o convert()
   */
  handleConversion(source) {
    return ConversionHandler.handle(source);
  },

  /**
   * Logger condicional
   */
  _log(message, ...args) {
    if (this.debugMode) {
      Logger.debug(message, ...args);
    }
  },

  /**
   * Track event - alias para compatibilidad
   * @deprecated Usar track()
   */
  trackEvent(eventName, eventData = {}) {
    return this.track(eventName, eventData);
  },

  /**
   * Generate UUID - utility para compatibilidad
   */
  generateUUID() {
    return UUID.generate();
  },

  /**
   * Set cookie - utility para compatibilidad
   */
  setCookie(name, value, days) {
    Storage.cookies.set(name, value, days);
  },

  /**
   * Get cookie - utility para compatibilidad
   */
  getCookie(name) {
    return Storage.cookies.get(name);
  },

  /**
   * Safe FBQ wrapper - utility para compatibilidad
   */
  safeFbq(method, eventName, data, options) {
    return PixelBridge.track(eventName, data, options);
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
