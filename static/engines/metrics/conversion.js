/**
 * 📊 TRACKING - Conversion Handler
 * Gestión de conversiones WhatsApp y redirecciones
 */

import { TrackingConfig } from './config.js';
import { PixelBridge } from './pixel-bridge.js';
import { CAPI } from './ui-observer.js';
import { IdentityManager } from './identity.js';

export const ConversionHandler = {
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
export function handleConversion(source) {
  return ConversionHandler.handle(source);
}
