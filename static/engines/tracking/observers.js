/**
 * 📊 TRACKING - Observers
 * ViewContent tracking y slider interactions
 */

import { DOM } from '../core/dom.js';
import { TrackingConfig } from './config.js';
import { PixelBridge } from './pixel-bridge.js';
import { CAPI } from './capi.js';
import { IdentityManager } from './identity.js';

export const TrackingObservers = {
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
