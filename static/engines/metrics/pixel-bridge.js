/**
 * 📊 TRACKING - Pixel Bridge (Zaraz Native)
 * Abstracción para enviar eventos exclusivamente a Cloudflare Zaraz
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
   * Actualiza los datos de usuario para Advanced Matching
   * Zaraz enviará esto automáticamente al CAPI
   */
  async setUserData(data) {
    const hashedData = { ...this._userData };

    if (data.email) hashedData.em = await this._hashData(data.email);
    if (data.phone) hashedData.ph = await this._hashData(data.phone);
    if (data.external_id) hashedData.external_id = data.external_id;
    if (data.firstName) hashedData.fn = await this._hashData(data.firstName);
    if (data.lastName) hashedData.ln = await this._hashData(data.lastName);

    this._userData = hashedData;
    this._log('👤 Updated Advanced Matching Data:', this._userData);

    // Actualizar perfil de usuario en Zaraz si está listo
    if (this._isZarazReady()) {
      if (data.email) window.zaraz.set('user_email', data.email);
      if (data.phone) window.zaraz.set('user_phone', data.phone);
      if (data.external_id) window.zaraz.set('external_id', data.external_id);
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
      return text;
    }
  },

  /**
   * Envía evento a Zaraz Edge
   */
  track(eventName, data = {}, options = {}) {
    const eventId = options.eventId || this._generateEventId();
    const payload = { ...data, event_id: eventId };

    if (this._isZarazReady()) {
      window.zaraz.track(eventName, payload);
      this._log(`✅ Zaraz Edge Event: ${eventName}`, payload);
      return { success: true, channel: 'zaraz', eventId };
    }

    // Fallback: Encolar para cuando Zaraz cargue
    this._queueEvent('track', eventName, data, { event_id: eventId });
    return { success: false, channel: 'queued', eventId };
  },

  /**
   * Track custom event via Zaraz Edge
   */
  trackCustom(eventName, data = {}, options = {}) {
    const eventId = options.eventId || this._generateEventId();

    if (this._isZarazReady()) {
      window.zaraz.track(eventName, { ...data, event_id: eventId });
      this._log(`✅ Zaraz Custom Edge Event: ${eventName}`, { ...data, event_id: eventId });
      return { success: true, channel: 'zaraz', eventId };
    }

    this._queueEvent('trackCustom', eventName, data, { event_id: eventId });
    return { success: false, channel: 'queued', eventId };
  },

  /**
   * Verifica si Cloudflare Zaraz está disponible
   */
  _isZarazReady() {
    return window.zaraz && typeof window.zaraz.track === 'function';
  },

  /**
   * Encola evento para retry si la API de Zaraz aún no ha cargado
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
      this._log(`⏳ Zaraz not ready. Queuing event: ${eventName}`);
      this._startRetryLoop();
    }
  },

  /**
   * Inicia loop de retry estricto para Zaraz
   */
  _startRetryLoop() {
    const { retry } = TrackingConfig;

    this._retryTimer = setInterval(() => {
      if (this._isZarazReady()) {
        this._log(`🚀 Zaraz loaded! Replaying ${this._retryQueue.length} events.`);

        this._retryQueue.forEach(event => {
          window.zaraz.track(event.eventName, { ...event.data, ...event.options });
        });

        this._retryQueue = [];
        clearInterval(this._retryTimer);
        this._retryTimer = null;
      }

      // Timeout: abandonar eventos antiguos si Zaraz es bloqueado por adblockers extremos
      if (this._retryQueue.length > 0 &&
        (Date.now() - this._retryQueue[0].time > retry.timeout)) {
        console.warn('❌ Zaraz completely blocked. Aborting retries.');
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
      window.Logger ? window.Logger.debug(message, data || '') : console.debug(message, data || '');
    }
  }
};
