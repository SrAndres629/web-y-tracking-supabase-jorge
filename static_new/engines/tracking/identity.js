/**
 * 📊 TRACKING - Identity Manager
 * Gestión de identificación de usuarios y cookies
 */

import { Storage } from '../core/storage.js';
import { UUID } from '../core/uuid.js';
import { TrackingConfig } from './config.js';

export const IdentityManager = {
  _metaEventId: null,
  _externalId: null,
  _fbc: null,
  _fbp: null,

  /**
   * Inicializa la identidad del usuario
   */
  init() {
    this._hydrateEventId();
    this._hydrateExternalId();
    this._syncFbclid();
    this._hydrateFbp();
    
    // Exponer globalmente para compatibilidad
    window.META_EVENT_ID = this._metaEventId;
    window.EXTERNAL_ID = this._externalId;
    
    return {
      eventId: this._metaEventId,
      externalId: this._externalId,
      fbc: this._fbc,
      fbp: this._fbp
    };
  },

  /**
   * Obtiene o genera el event_id maestro
   */
  _hydrateEventId() {
    if (window.META_EVENT_ID) {
      this._metaEventId = window.META_EVENT_ID;
      return;
    }
    
    const cached = Storage.cookies.get('_event_id_cache');
    if (cached) {
      this._metaEventId = cached;
    } else {
      this._metaEventId = UUID.generate();
      Storage.cookies.set('_event_id_cache', this._metaEventId, TrackingConfig.cookieTTL.eventId);
    }
  },

  /**
   * Obtiene o genera el external_id persistente
   */
  _hydrateExternalId() {
    if (window.EXTERNAL_ID) {
      this._externalId = window.EXTERNAL_ID;
      return;
    }
    
    const stored = Storage.cookies.get('external_id');
    if (stored) {
      this._externalId = stored;
    } else {
      this._externalId = UUID.externalId();
      Storage.cookies.set('external_id', this._externalId, TrackingConfig.cookieTTL.externalId);
    }
  },

  /**
   * Sincroniza fbclid de URL a cookie _fbc
   */
  _syncFbclid() {
    const urlParams = new URLSearchParams(window.location.search);
    const fbclid = urlParams.get('fbclid');
    
    if (fbclid) {
      const creationTime = Math.floor(Date.now());
      this._fbc = `fb.1.${creationTime}.${fbclid}`;
      Storage.cookies.set('_fbc', this._fbc, TrackingConfig.cookieTTL.fbc);
      Storage.session.set('tracking_fbclid', fbclid);
    } else {
      this._fbc = Storage.cookies.get('_fbc');
    }
  },

  /**
   * Obtiene el _fbp de cookies
   */
  _hydrateFbp() {
    const cookies = document.cookie.split('; ');
    const fbpCookie = cookies.find(row => row.startsWith('_fbp='));
    this._fbp = fbpCookie ? fbpCookie.split('=')[1] : null;
  },

  // Getters públicos
  get eventId() { return this._metaEventId; },
  get externalId() { return this._externalId; },
  get fbc() { return this._fbc; },
  get fbp() { return this._fbp; },
  
  /**
   * Genera un nuevo event_id para eventos específicos
   */
  generateEventId(prefix = 'event') {
    return `${prefix}_${UUID.generate()}`;
  }
};
