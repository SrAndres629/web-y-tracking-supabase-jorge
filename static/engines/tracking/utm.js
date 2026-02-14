/**
 * 📊 TRACKING - UTM Manager
 * Persistencia y recuperación de parámetros UTM
 */

import { Storage } from '../core/storage.js';

const UTM_FIELDS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'fbclid'];
const STORAGE_PREFIX = 'tracking_';

export const UTMManager = {
  /**
   * Captura y persiste UTMs desde la URL actual
   */
  capture() {
    const urlParams = new URLSearchParams(window.location.search);
    const captured = {};
    
    UTM_FIELDS.forEach(field => {
      const value = urlParams.get(field);
      if (value) {
        captured[field] = value;
        Storage.session.set(`${STORAGE_PREFIX}${field}`, value);
      }
    });
    
    return captured;
  },

  /**
   * Obtiene un parámetro UTM
   */
  get(field) {
    return Storage.session.get(`${STORAGE_PREFIX}${field}`);
  },

  /**
   * Obtiene todos los UTMs capturados
   */
  getAll() {
    const result = {};
    UTM_FIELDS.forEach(field => {
      const value = this.get(field);
      if (value) {
        result[field] = value;
      }
    });
    return result;
  },

  /**
   * Detecta fuente de tráfico principal
   */
  getTrafficSource() {
    return this.get('utm_source') || 'direct';
  },

  /**
   * Detecta si es in-app browser (Instagram/TikTok)
   */
  detectBrowserContext() {
    const ua = navigator.userAgent || navigator.vendor || window.opera;
    const isInApp = /FBAN|FBAV|Instagram|TikTok/i.test(ua);
    return isInApp ? 'in_app' : 'browser';
  },

  /**
   * Limpia UTMs almacenados
   */
  clear() {
    UTM_FIELDS.forEach(field => {
      try {
        sessionStorage.removeItem(`${STORAGE_PREFIX}${field}`);
      } catch (e) {
        // Ignore
      }
    });
  }
};
