(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports) :
  typeof define === 'function' && define.amd ? define(['exports'], factory) :
  (global = typeof globalThis !== 'undefined' ? globalThis : global || self, factory(global.TrackingEngine = {}));
})(this, (function (exports) { 'use strict';

  /**
   * 🔧 CORE - Storage Manager
   * Abstracción para cookies, localStorage y sessionStorage
   */

  const Storage = {
    /**
     * Cookie operations
     */
    cookies: {
      get(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
          let c = ca[i].trim();
          if (c.indexOf(nameEQ) === 0) {
            return c.substring(nameEQ.length);
          }
        }
        return null;
      },

      set(name, value, days = 30, options = {}) {
        const { path = '/', sameSite = 'Lax', secure = false } = options;
        let expires = '';
        
        if (days) {
          const date = new Date();
          date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
          expires = '; expires=' + date.toUTCString();
        }
        
        let cookieString = name + '=' + encodeURIComponent(value) + expires + '; path=' + path + '; SameSite=' + sameSite;
        if (secure || window.location.protocol === 'https:') {
          cookieString += '; Secure';
        }
        
        document.cookie = cookieString;
      },

      delete(name) {
        this.set(name, '', -1);
      }
    },

    /**
     * sessionStorage con manejo de errores
     */
    session: {
      get(key, defaultValue = null) {
        try {
          const item = sessionStorage.getItem(key);
          return item ? item : defaultValue;
        } catch (e) {
          return defaultValue;
        }
      },

      set(key, value) {
        try {
          sessionStorage.setItem(key, value);
          return true;
        } catch (e) {
          return false;
        }
      }
    }
  };

  /**
   * 🔧 CORE - UUID Generator
   * RFC 4122 compliant UUID v4
   */

  const UUID = {
    /**
     * Genera UUID v4
     */
    generate() {
      return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
      );
    },

    /**
     * Genera ID corto para uso interno
     */
    short(prefix = 'id') {
      return `${prefix}_${Math.random().toString(36).substr(2, 9)}`;
    },

    /**
     * Genera external_id consistente
     */
    externalId() {
      return `user_${this.generate().substring(0, 18)}`;
    }
  };

  /**
   * 📊 TRACKING - Configuration
   * Configuración centralizada del sistema de tracking
   */

  const TrackingConfig = {
    // Servicios configurados (inyectado desde backend)
    services: window.SERVICES_CONFIG || {},
    
    // Configuración de contacto
    phone: (window.CONTACT_CONFIG && window.CONTACT_CONFIG.phone) || "59164714751",
    
    // WhatsApp base URL
    whatsappBaseUrl: "https://wa.me/",
    
    // Endpoints
    endpoints: {
      track: '/track/event',
      identity: '/api/identity/google'
    },
    
    // Tiempo de cache para eventos (minutos)
    eventCacheMinutes: 15,
    
    // TTL para cookies (días)
    cookieTTL: {
      eventId: 0.01,      // 15 minutos
      externalId: 365,    // 1 año
      fbc: 90,            // 3 meses (Meta standard)
      fbclid: 30          // 1 mes
    },
    
    // Mapa de conversiones para WhatsApp
    conversionMap: {
      'Hero CTA': { name: 'Diseño de Cejas', id: 'hero_offer', intent: 'discovery' },
      'Sticky Header': { name: 'Consulta General', id: 'sticky_bar', intent: 'convenience' },
      'Floating Button': { name: 'Consulta WhatsApp', id: 'float_btn', intent: 'convenience' },
      'Galería CTA': { name: 'Transformación Completa', id: 'gallery_cta', intent: 'inspiration' },
      'CTA Final': { name: 'Oferta Limitada', id: 'final_offer', intent: 'urgency' },
      'Servicio Cejas': { name: 'Microblading 3D', id: 'service_brows', intent: 'service_interest' },
      'Servicio Ojos': { name: 'Delineado Ojos', id: 'service_eyes', intent: 'service_interest' },
      'Servicio Labios': { name: 'Labios Full Color', id: 'service_lips', intent: 'service_interest' },
      'Sticky Mobile CTA': { name: 'Cita VIP Móvil', id: 'mobile_sticky', intent: 'convenience' }
    },
    
    // Nombres de servicios fallback para sliders
    sliderServices: {
      names: ['Microblading 3D', 'Delineado Permanente', 'Labios Full Color'],
      ids: ['microblading_3d', 'delineado_ojos', 'labios_full']
    },
    
    // Tiempo de dwell para ViewContent (ms)
    viewContentDwellTime: 3000,
    
    // Retry configuration
    retry: {
      maxAttempts: 20,
      interval: 500,
      timeout: 10000
    }
  };

  /**
   * 📊 TRACKING - Identity Manager
   * Gestión de identificación de usuarios y cookies
   */


  const IdentityManager = {
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

  /**
   * 📊 TRACKING - UTM Manager
   * Persistencia y recuperación de parámetros UTM
   */


  const UTM_FIELDS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'fbclid'];
  const STORAGE_PREFIX = 'tracking_';

  const UTMManager = {
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

  /**
   * 📊 TRACKING - Pixel Bridge
   * Abstracción para enviar eventos a Zaraz/Meta Pixel
   */


  const PixelBridge = {
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

  /**
   * 📊 TRACKING - CAPI (Conversions API)
   * Envío de eventos server-side para deduplicación
   */


  const CAPI = {
    /**
     * Envía evento al backend
     */
    async track(eventName, eventData = {}) {
      const payload = this._buildPayload(eventName, eventData);

      try {
        // Usar Beacon API para eventos críticos (Contact)
        if (navigator.sendBeacon && eventName === 'Contact') {
          const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
          navigator.sendBeacon(TrackingConfig.endpoints.track, blob);
          return { success: true, method: 'beacon' };
        }

        // Standard fetch para otros eventos
        const response = await fetch(TrackingConfig.endpoints.track, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
          keepalive: true
        });

        if (!response.ok) {
          console.warn(`[CAPI] Server Error: ${response.status}`);
          return { success: false, error: `HTTP ${response.status}` };
        }

        return { success: true, method: 'fetch' };
      } catch (e) {
        console.warn(`[CAPI] Network Error for ${eventName}`, e);
        return { success: false, error: e.message };
      }
    },

    /**
     * Construye payload para CAPI
     */
    _buildPayload(eventName, eventData) {
      const utms = UTMManager.getAll();
      
      return {
        event_name: eventName,
        event_time: Math.floor(Date.now() / 1000),
        event_id: eventData.event_id || `${eventName.toLowerCase()}_${Date.now()}`,
        event_source_url: window.location.href,
        action_source: "website",
        user_data: {
          external_id: IdentityManager.externalId,
          fbc: IdentityManager.fbc,
          fbp: IdentityManager.fbp
        },
        custom_data: {
          ...eventData,
          fbclid: utms.fbclid,
          fbp: IdentityManager.fbp,
          utm_source: utms.utm_source,
          utm_medium: utms.utm_medium,
          utm_campaign: utms.utm_campaign,
          utm_term: utms.utm_term,
          utm_content: utms.utm_content,
          browser_context: UTMManager.detectBrowserContext(),
          turnstile_token: window.turnstileToken || null
        }
      };
    },

    /**
     * Envía evento en background (non-blocking)
     */
    trackAsync(eventName, eventData) {
      if ('requestIdleCallback' in window) {
        requestIdleCallback(() => this.track(eventName, eventData));
      } else {
        setTimeout(() => this.track(eventName, eventData), 10);
      }
    }
  };

  /**
   * 🔧 CORE - DOM Utilities
   * Helpers para manipulación de DOM segura y performante
   */

  const DOM = {
    /**
     * Selecciona elementos con verificación de existencia
     */
    $(selector, context = document) {
      return context.querySelector(selector);
    },

    $$
  (selector, context = document) {
      return Array.from(context.querySelectorAll(selector));
    },

    /**
     * Verifica si un elemento existe en el DOM
     */
    exists(selector) {
      return document.querySelector(selector) !== null;
    },

    /**
     * Ejecuta callback cuando DOM está listo
     */
    ready(callback) {
      if (document.readyState === 'complete' || document.readyState === 'interactive') {
        callback();
      } else {
        document.addEventListener('DOMContentLoaded', callback, { once: true });
      }
    },

    /**
     * Crea un IntersectionObserver con opciones por defecto
     */
    observe(element, callback, options = {}) {
      const defaultOptions = {
        threshold: 0.6,
        rootMargin: '100px',
        ...options
      };
      
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(callback);
      }, defaultOptions);
      
      if (element) {
        observer.observe(element);
      }
      
      return observer;
    },

    /**
     * Throttle para eventos de scroll/resize
     */
    throttle(fn, wait = 100) {
      let lastTime = 0;
      return (...args) => {
        const now = Date.now();
        if (now - lastTime >= wait) {
          lastTime = now;
          fn.apply(this, args);
        }
      };
    },

    /**
     * Debounce para inputs/eventos frecuentes
     */
    debounce(fn, wait = 250) {
      let timeout;
      return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn.apply(this, args), wait);
      };
    }
  };

  /**
   * 📊 TRACKING - Observers
   * ViewContent tracking y slider interactions
   */


  const TrackingObservers = {
    _viewedSections: new Set(),
    _viewTimers: {},

    /**
     * Inicializa todos los observers
     */
    init() {
      this._setupViewContentObserver();
      this._setupSliderListeners();
    },

    /**
     * Observer para ViewContent (servicios visibles)
     */
    _setupViewContentObserver() {
      if (!('IntersectionObserver' in window)) return;

      const options = { threshold: 0.6 };
      
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          const sectionId = entry.target.dataset.serviceCategory || entry.target.dataset.trackingId;
          if (!sectionId) return;

          if (entry.isIntersecting) {
            this._startViewTimer(sectionId, entry.target);
          } else {
            this._cancelViewTimer(sectionId);
          }
        });
      }, options);

      // Observar elementos con data-service-category
      DOM.$$('[data-service-category]').forEach(el => observer.observe(el));
    },

    /**
     * Inicia timer de dwell time
     */
    _startViewTimer(sectionId, element) {
      if (this._viewedSections.has(sectionId) || this._viewTimers[sectionId]) return;

      this._viewTimers[sectionId] = setTimeout(() => {
        this._viewedSections.add(sectionId);
        this._trackViewContent(sectionId);
        delete this._viewTimers[sectionId];
      }, TrackingConfig.viewContentDwellTime);
    },

    /**
     * Cancela timer si el usuario se va antes
     */
    _cancelViewTimer(sectionId) {
      if (this._viewTimers[sectionId]) {
        clearTimeout(this._viewTimers[sectionId]);
        delete this._viewTimers[sectionId];
      }
    },

    /**
     * Trackea ViewContent
     */
    _trackViewContent(sectionId) {
      const services = TrackingConfig.services;
      const serviceData = services[sectionId] || { 
        name: sectionId, 
        category: 'General', 
        price: 0 
      };
      
      const eventId = IdentityManager.generateEventId('vc');

      // Pixel
      PixelBridge.track('ViewContent', {
        content_name: serviceData.name,
        content_category: serviceData.category,
        content_ids: [sectionId],
        content_type: 'product',
        value: serviceData.price,
        currency: 'USD'
      }, { eventId });

      // CAPI
      CAPI.trackAsync('ViewContent', {
        event_id: eventId,
        service: serviceData.name,
        category: serviceData.category,
        price: serviceData.price
      });
    },

    /**
     * Listeners para sliders (Before/After)
     */
    _setupSliderListeners() {
      const sliders = DOM.$$('.ba-slider');
      const { names: fallbackNames, ids: fallbackIds } = TrackingConfig.sliderServices;

      sliders.forEach((slider, index) => {
        const trackInteraction = () => {
          if (slider.dataset.tracked) return;
          slider.dataset.tracked = "true";

          const serviceId = slider.dataset.serviceCategory || fallbackIds[index] || `slider_${index}`;
          const serviceName = slider.dataset.serviceCategory 
            ? slider.dataset.serviceCategory.replace(/_/g, ' ').toUpperCase()
            : fallbackNames[index] || 'Servicio Desconocido';

          const eventId = IdentityManager.generateEventId('slider');

          // Track interaction
          PixelBridge.trackCustom('SliderInteraction', {
            content_name: serviceName,
            content_id: serviceId,
            interaction_type: 'compare_before_after'
          }, { eventId });

          CAPI.trackAsync('SliderInteraction', {
            event_id: eventId,
            service_name: serviceName,
            service_id: serviceId,
            interaction_type: 'compare_before_after'
          });
        };

        slider.addEventListener('click', trackInteraction, { passive: true });
        slider.addEventListener('touchmove', trackInteraction, { passive: true });
      });
    }
  };

  /**
   * 📊 TRACKING - Conversion Handler
   * Gestión de conversiones WhatsApp y redirecciones
   */


  const ConversionHandler = {
    /**
     * Maneja conversión de WhatsApp
     */
    handle(source) {
      const conversionData = this._getConversionData(source);
      const eventId = IdentityManager.generateEventId('contact');

      // Track Contact event
      PixelBridge.track('Contact', {
        content_name: conversionData.name,
        content_category: conversionData.intent,
        content_ids: [conversionData.id],
        lead_source: 'whatsapp',
        trigger_location: source
      }, { eventId });

      // CAPI
      CAPI.trackAsync('Contact', {
        event_id: eventId,
        source: source,
        service_data: conversionData
      });

      // Redirigir a WhatsApp
      this._redirectToWhatsApp(source, conversionData);
    },

    /**
     * Obtiene datos de conversión según el source
     */
    _getConversionData(source) {
      return TrackingConfig.conversionMap[source] || { 
        name: source, 
        id: 'unknown', 
        intent: 'general' 
      };
    },

    /**
     * Construye mensaje de WhatsApp contextual
     */
    _buildMessage(source, data) {
      const refTag = IdentityManager.externalId 
        ? ` [Ref: ${IdentityManager.externalId.substring(0, 8)}]` 
        : "";

      let message = 'Hola Jorge 👋';

      if (source === 'Floating Button') {
        message = "Hola Jorge, estoy visitando tu web y me interesa una valoración para maquillaje permanente. ¿Podrían asesorarme?";
      } else if (data.intent === 'service_interest') {
        message += ` Me interesa el *${data.name}*. ¿Podría ver si soy candidata?`;
      } else if (data.intent === 'urgency') {
        message += ` Quisiera aprovechar la *Oferta Limitada* de valoración gratuita.`;
      } else {
        message += ` Quisiera información sobre sus servicios de maquillaje permanente.`;
      }

      return message + refTag;
    },

    /**
     * Redirige a WhatsApp
     */
    _redirectToWhatsApp(source, data) {
      const message = this._buildMessage(source, data);
      const whatsappUrl = `${TrackingConfig.whatsappBaseUrl}${TrackingConfig.phone}?text=${encodeURIComponent(message)}`;

      // Smart navigation: detectar si es click en <a>
      const evt = window.event;
      const isSemanticLink = evt && evt.target && evt.target.closest('a');

      if (!isSemanticLink) {
        // Navegación programada con delay para permitir tracking
        setTimeout(() => {
          window.open(whatsappUrl, '_blank');
        }, 300);
      }
      // Si es <a>, el navegador maneja la navegación nativamente
    }
  };

  /**
   * Función global para templates (compatibilidad)
   */
  function handleConversion(source) {
    return ConversionHandler.handle(source);
  }

  /**
   * 📊 TRACKING ENGINE - Entry Point
   * Sistema de tracking modular (Zaraz + CAPI)
   * 
   * Uso:
   *   import { TrackingEngine } from './engines/tracking/index.js';
   *   TrackingEngine.init();
   */


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
        console.log(message, ...args);
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

  // Exportar global para compatibilidad
  if (typeof window !== 'undefined') {
    window.TrackingEngine = TrackingEngine;
    window.handleConversion = handleConversion;
  }

  exports.CAPI = CAPI;
  exports.ConversionHandler = ConversionHandler;
  exports.IdentityManager = IdentityManager;
  exports.PixelBridge = PixelBridge;
  exports.TrackingEngine = TrackingEngine;
  exports.UTMManager = UTMManager;
  exports.default = TrackingEngine;
  exports.handleConversion = handleConversion;

  Object.defineProperty(exports, '__esModule', { value: true });

}));
//# sourceMappingURL=tracking.legacy.js.map
