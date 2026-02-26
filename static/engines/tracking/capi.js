/**
 * 📊 TRACKING - CAPI (Conversions API)
 * Envío de eventos server-side para deduplicación
 */

import { TrackingConfig } from './config.js';
import { IdentityManager } from './identity.js';
import { UTMManager } from './utm.js';

export const CAPI = {
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
      event_id: eventData.event_id || `${eventName.toLowerCase()}_${Date.now()}`,
      external_id: IdentityManager.externalId,
      source_url: window.location.href,
      fbclid: IdentityManager.fbc,
      fbp: IdentityManager.fbp,
      turnstile_token: eventData.turnstile_token || window.turnstileToken || null,
      utm_source: utms.utm_source || null,
      utm_medium: utms.utm_medium || null,
      utm_campaign: utms.utm_campaign || null,
      utm_term: utms.utm_term || null,
      utm_content: utms.utm_content || null,
      custom_data: {
        ...(eventData.custom_data || {}),
        em: eventData.em,
        ph: eventData.ph,
        fn: eventData.fn,
        ln: eventData.ln,
        ct: eventData.ct,
        st: eventData.st,
        zp: eventData.zp,
        country: eventData.country,
        client_user_agent: navigator.userAgent,
        browser_context: UTMManager.detectBrowserContext()
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
