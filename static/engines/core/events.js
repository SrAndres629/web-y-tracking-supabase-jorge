/**
 * 🔧 CORE - Event System
 * Sistema de eventos centralizado con namespacing
 */

export const EventBus = {
  _events: new Map(),

  /**
   * Suscribe a un evento
   */
  on(event, callback, once = false) {
    if (!this._events.has(event)) {
      this._events.set(event, []);
    }
    
    this._events.get(event).push({ callback, once });
  },

  /**
   * Suscribe una sola vez
   */
  once(event, callback) {
    this.on(event, callback, true);
  },

  /**
   * Emite un evento
   */
  emit(event, data = null) {
    if (!this._events.has(event)) return;
    
    const listeners = this._events.get(event);
    this._events.set(event, listeners.filter(({ callback, once }) => {
      callback(data);
      return !once;
    }));
  },

  /**
   * Cancela suscripción
   */
  off(event, callback) {
    if (!this._events.has(event)) return;
    
    const listeners = this._events.get(event);
    this._events.set(event, listeners.filter(l => l.callback !== callback));
  }
};

/**
 * Eventos globales pre-definidos
 */
export const Events = {
  TRACKING_READY: 'tracking:ready',
  TRACKING_EVENT: 'tracking:event',
  CONVERSION: 'tracking:conversion',
  SLIDER_INTERACTION: 'ui:slider',
  NAV_SCROLL: 'ui:nav:scroll',
  HERO_VISIBLE: 'motion:hero:visible',
  TURNSTILE_SUCCESS: 'security:turnstile:success'
};
