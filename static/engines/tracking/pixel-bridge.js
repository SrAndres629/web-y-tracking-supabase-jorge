/**
 * 📊 TRACKING - Pixel Bridge
 * Abstracción para enviar eventos a Zaraz/Meta Pixel
 */

import { TrackingConfig } from './config.js';

export const PixelBridge = {
  _retryQueue: [],
  _retryTimer: null,
  _debugMode: false,
  _userData: {},

  /**
   * Inicializa el bridge
   */
  init(options = {}) {
    this._debugMode = options.debug || new URLSearchParams(window.location.search).has('debug_pixel');

    // Capturar external_id inicial si existe
    if (window.EXTERNAL_ID) {
      this._userData.external_id = window.EXTERNAL_ID;
    }
  },

  /**
   * Actualiza los datos de usuario para Advanced Matching (Manual)
   * @param {Object} data - Datos sin hashear (email, phone, etc.)
   */
  async setUserData(data) {
    const hashedData = { ...this._userData };

    // Meta requiere SHA-256 para email y phone
    if (data.email) hashedData.em = await this._hashData(data.email);
    if (data.phone) hashedData.ph = await this._hashData(data.phone);
    if (data.external_id) hashedData.external_id = data.external_id;
    if (data.firstName) hashedData.fn = await this._hashData(data.firstName);
    if (data.lastName) hashedData.ln = await this._hashData(data.lastName);

    this._userData = hashedData;
    this._log('👤 Updated Advanced Matching Data:', this._userData);

    // Zaraz handles initialization by default. If we have PII, we set it in Zaraz.
    if (this._isZarazReady()) {
      if (data.email) window.zaraz.set('user_email', data.email);
      if (data.phone) window.zaraz.set('user_phone', data.phone);
      if (data.external_id) window.zaraz.set('external_id', data.external_id);
    }

    // Actualizar Zaraz si está disponible
    if (this._isZarazReady()) {
      if (data.email) window.zaraz.set('user_email', data.email);
    }
  },

  /**
   * Helper para hashear datos (SHA-256)
   */
  async _hashData(text) {
    if (!text) return null;
    try {
      const cleanText = text.trim().toLowerCase();
      const msgBuffer = new TextEncoder().encode(cleanText);
      const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    } catch (e) {
      console.warn('Hashing failed, using fallback', e);
      return text; // Fallback al original si falla el crypto (browsers antiguos)
    }
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
      Logger.debug(message, data || '');
    }
  }
};
