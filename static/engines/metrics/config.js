/**
 * 📊 TRACKING - Configuration
 * Configuración centralizada del sistema de tracking
 */

export const TrackingConfig = {
  // Servicios configurados (inyectado desde backend)
  services: window.SERVICES_CONFIG || {},
  
  // Configuración de contacto
  phone: (window.CONTACT_CONFIG && window.CONTACT_CONFIG.phone) || "59164714751",
  
  // WhatsApp base URL
  whatsappBaseUrl: "https://wa.me/",
  
  // Endpoints
  endpoints: {
    track: '/api/v1/telemetry',
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
