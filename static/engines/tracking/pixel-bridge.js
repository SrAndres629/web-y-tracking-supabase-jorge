/**
 * 📊 TRACKING - Pixel Bridge
 * Abstracción para enviar eventos a Zaraz/Meta Pixel
 */

import { TrackingConfig } from './config.js';

export const PixelBridge = {
  _retryQueue: [],
  _retryTimer: null,
  _debugMode: false,

  /**
   * Inicializa el bridge
   */
  init(options = {}) {
    this._debugMode = options.debug || new URLSearchParams(window.location.search).has('debug_pixel');
  },

  /**
   * Envía evento a Zaraz/Pixel con fallback
   */
  track(eventName, data = {}, options = {}) {
    const eventId = options.eventId || this._generateEventId();
    const payload = { ...data, eventID: eventId };

    // Intento 1: Zaraz (preferido)
    if (this._isZarazReady()) {
      this._sendToZaraz(eventName, payload);
      return { success: true, channel: 'zaraz', eventId };
    }

    // Intento 2: fbq legacy
    if (this._isFbqReady()) {
      this._sendToFbq('track', eventName, data, { eventID: eventId });
      return { success: true, channel: 'fbq', eventId };
    }

    // Fallback: Encolar para retry
    this._queueEvent('track', eventName, data, { eventID: eventId });
    return { success: false, channel: 'queued', eventId };
  },

  /**
   * Track custom event
   */
  trackCustom(eventName, data = {}, options = {}) {
    const eventId = options.eventId || this._generateEventId();
    
    if (this._isZarazReady()) {
      window.zaraz.track(eventName, { ...data, eventID: eventId });
      return { success: true, channel: 'zaraz', eventId };
    }

    if (this._isFbqReady()) {
      window.fbq('trackCustom', eventName, data, { eventID: eventId });
      return { success: true, channel: 'fbq', eventId };
    }

    this._queueEvent('trackCustom', eventName, data, { eventID: eventId });
    return { success: false, channel: 'queued', eventId };
  },

  /**
   * Verifica si Zaraz está disponible
   */
  _isZarazReady() {
    return window.zaraz && typeof window.zaraz.track === 'function';
  },

  /**
   * Verifica si fbq está disponible
   */
  _isFbqReady() {
    return typeof window.fbq === 'function';
  },

  /**
   * Envía a Zaraz
   */
  _sendToZaraz(eventName, payload) {
    window.zaraz.track(eventName, payload);
    this._log(`✅ Zaraz Edge Event: ${eventName}`, payload);
  },

  /**
   * Envía a fbq
   */
  _sendToFbq(method, eventName, data, options) {
    window.fbq(method, eventName, data, options);
    this._log(`✅ Pixel Fired (Legacy): ${eventName}`);
  },

  /**
   * Encola evento para retry
   */
  _queueEvent(method, eventName, data, options) {
    this._retryQueue.push({
      method,
      eventName,
      data,
      options,
      time: Date.now()
    });

    if (!this._retryTimer) {
      this._log(`⏳ Zaraz/Pixel not ready. Queuing event: ${eventName}`);
      this._startRetryLoop();
    }
  },

  /**
   * Inicia loop de retry
   */
  _startRetryLoop() {
    const { retry } = TrackingConfig;
    
    this._retryTimer = setInterval(() => {
      // Verificar si hay trackers disponibles
      const hasZaraz = this._isZarazReady();
      const hasFbq = this._isFbqReady();

      if (hasZaraz || hasFbq) {
        const channel = hasZaraz ? 'zaraz' : 'fbq';
        this._log(`🚀 ${channel} loaded! Replaying ${this._retryQueue.length} events.`);

        this._retryQueue.forEach(event => {
          if (hasZaraz) {
            window.zaraz.track(event.eventName, { ...event.data, ...event.options });
          } else {
            window.fbq(event.method, event.eventName, event.data, event.options);
          }
        });

        this._retryQueue = [];
        clearInterval(this._retryTimer);
        this._retryTimer = null;
      }

      // Timeout: abandonar eventos antiguos
      if (this._retryQueue.length > 0 && 
          (Date.now() - this._retryQueue[0].time > retry.timeout)) {
        console.warn('❌ Zaraz/Pixel failed to load. Aborting retries.');
        this._retryQueue = [];
        clearInterval(this._retryTimer);
        this._retryTimer = null;
      }
    }, retry.interval);
  },

  /**
   * Genera ID de evento
   */
  _generateEventId() {
    return `evt_${Math.random().toString(36).substr(2, 9)}`;
  },

  /**
   * Log condicional
   */
  _log(message, data) {
    if (this._debugMode) {
      console.log(message, data || '');
    }
  }
};
