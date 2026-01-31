/* =================================================================
   TRACKING.JS - Meta Pixel & CAPI Universal Engine (Senior Edition)
   Architecture: Idempotent Single-Instance Tracker + UTM Persistence
   ================================================================= */

const TrackingEngine = {
    initialized: false,
    viewedSections: new Set(),
    debugMode: false,

    config: {
        services: window.SERVICES_CONFIG || {},
        phone: (window.CONTACT_CONFIG && window.CONTACT_CONFIG.phone) || "59164714751",
    },

    init() {
        if (this.initialized) return;
        this.initialized = true;

        // Auto-enable debug if specific parameter exists
        if (new URLSearchParams(window.location.search).has('debug_pixel')) {
            this.debugMode = true;
            this.log('🐛 Debug Mode Enabled');
        }

        this.persistUTMs(); // Priority: Capture campaign data immediately
        this.setupPixel();
        this.setupViewContentObserver();
        this.setupSliderListeners();

        this.log('📊 [Senior Architecture] Tracking Engine Active (Pixel + CAPI + UTMs)');
    },

    /**
     * UTILITY: Internal Logger
     */
    log(message, data = null) {
        if (!this.debugMode) return;
        if (data) console.log(message, data);
        else console.log(message);
    },

    warn(message) {
        if (!this.debugMode) return;
        console.warn(message);
    },

    /**
     * 0. DATA PERSISTENCE LAYER (UTMs)
     */
    persistUTMs() {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const utmFields = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'fbclid'];

            // Capture and store if present in URL
            utmFields.forEach(field => {
                const value = urlParams.get(field);
                if (value) {
                    sessionStorage.setItem(`tracking_${field}`, value);
                }
            });

            // Debug Log
            const source = this.getUTM('utm_source') || 'direct';
            this.log(`📡 Traffic Source Identified: ${source}`);
        } catch (e) {
            this.warn('Error persisting UTMs');
        }
    },

    getUTM(field) {
        // Priority: Session Storage > Default null
        return sessionStorage.getItem(`tracking_${field}`) || null;
    },

    /**
     * 1. META PIXEL INITIALIZATION
     */
    setupPixel() {
        if (window.fbq) return;

        !function (f, b, e, v, n, t, s) {
            if (f.fbq) return; n = f.fbq = function () {
                n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments)
            }; if (!f._fbq) f._fbq = n;
            n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = []; t = b.createElement(e); t.async = !0;
            t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s)
        }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');

        if (window.META_PIXEL_ID) {
            const initData = window.EXTERNAL_ID ? { external_id: window.EXTERNAL_ID } : {};
            fbq('init', window.META_PIXEL_ID, initData);
            fbq('track', 'PageView', {}, { eventID: window.META_EVENT_ID });
        }
    },

    /**
     * 2. VIEWCONTENT OBSERVER (Specific Interest)
     */
    setupViewContentObserver() {
        // Only run if IntersectionObserver is supported
        if (!('IntersectionObserver' in window)) return;

        const observerOptions = { threshold: 0.6 };
        this.viewTimers = {}; // Store timers for dwell time

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const sectionId = entry.target.dataset.serviceCategory || entry.target.dataset.trackingId;
                if (!sectionId) return;

                if (entry.isIntersecting) {
                    // Start 3-second timer (Dwell Time)
                    if (!this.viewedSections.has(sectionId) && !this.viewTimers[sectionId]) {
                        this.log(`⏳ Section visible: ${sectionId}. Waiting 3s for valid signal...`);
                        this.viewTimers[sectionId] = setTimeout(() => {
                            this.viewedSections.add(sectionId);
                            this.trackIndividualView(sectionId);
                            delete this.viewTimers[sectionId]; // Cleanup
                        }, 3000); // 3 Seconds Dwell Time
                    }
                } else {
                    // User scrolled away - Cancel timer
                    if (this.viewTimers[sectionId]) {
                        this.log(`❌ Scrolled away too fast: ${sectionId}. Signal cancelled.`);
                        clearTimeout(this.viewTimers[sectionId]);
                        delete this.viewTimers[sectionId];
                    }
                }
            });
        }, observerOptions);

        document.querySelectorAll('[data-service-category]').forEach(el => observer.observe(el));
    },

    trackIndividualView(sectionId) {
        const serviceData = this.config.services[sectionId] || { name: sectionId, category: 'General', price: 0 };
        const eventId = `vc_${Date.now()}_${sectionId}`;

        // Pixel
        if (window.fbq) {
            fbq('track', 'ViewContent', {
                content_name: serviceData.name,
                content_category: serviceData.category,
                content_ids: [sectionId],
                content_type: 'product',
                value: serviceData.price,
                currency: 'USD'
            }, { eventID: eventId });
        }

        // CAPI
        this.sendToCAPI('ViewContent', {
            event_id: eventId,
            service: serviceData.name,
            category: serviceData.category,
            price: serviceData.price
        });
    },

    /**
     * 3. SLIDER INTERACTION LISTENERS
     */
    setupSliderListeners() {
        const sliders = document.querySelectorAll('.ba-slider');
        const serviceNames = ['Microblading 3D', 'Cejas Sombra', 'Delineado Permanente', 'Labios Full Color'];
        const serviceIds = ['microblading_3d', 'cejas_sombra', 'delineado_ojos', 'labios_full'];

        sliders.forEach((slider, index) => {
            const trackInteraction = () => {
                if (slider.dataset.tracked) return;
                slider.dataset.tracked = "true";

                const serviceName = serviceNames[index] || 'Servicio Desconocido';
                const serviceId = serviceIds[index] || 'unknown';

                if (window.fbq) {
                    fbq('trackCustom', 'SliderInteraction', {
                        content_name: serviceName,
                        content_id: serviceId,
                        interaction_type: 'compare_before_after'
                    });
                }

                this.sendToCAPI('SliderInteraction', {
                    event_id: `slider_${Date.now()}_${serviceId}`,
                    service_name: serviceName,
                    service_id: serviceId,
                    interaction_type: 'compare_before_after'
                });
            };

            slider.addEventListener('click', trackInteraction, { passive: true });
            slider.addEventListener('touchmove', trackInteraction, { passive: true });
        });
    },

    /**
     * 4. CONVERSION HANDLER (WhatsApp Leads)
     */
    async handleConversion(source) {
        const triggerMap = {
            'Hero CTA': { name: 'Diseño de Cejas', id: 'hero_offer', intent: 'discovery' },
            'Sticky Header': { name: 'Consulta General', id: 'sticky_bar', intent: 'convenience' },
            'Floating Button': { name: 'Consulta WhatsApp', id: 'float_btn', intent: 'convenience' },
            'Galería CTA': { name: 'Transformación Completa', id: 'gallery_cta', intent: 'inspiration' },
            'CTA Final': { name: 'Oferta Limitada', id: 'final_offer', intent: 'urgency' },
            'Servicio Cejas': { name: 'Microblading 3D', id: 'service_brows', intent: 'service_interest' },
            'Servicio Ojos': { name: 'Delineado Ojos', id: 'service_eyes', intent: 'service_interest' },
            'Servicio Labios': { name: 'Labios Full Color', id: 'service_lips', intent: 'service_interest' },
            'Sticky Mobile CTA': { name: 'Cita VIP Móvil', id: 'mobile_sticky', intent: 'convenience' }
        };

        const eventId = `contact_${Date.now()}`;
        const data = triggerMap[source] || { name: source, id: 'unknown', intent: 'general' };

        // 🛡️ [Senior optimization]
        // 1. We fire 'Contact' instead of 'Lead' in the frontend to avoid "Click Illusion"
        // 2. The backend will fire the real 'Lead' when the message actually is sent.

        // Pixel
        if (window.fbq) {
            fbq('track', 'Contact', {
                content_name: data.name,
                content_category: data.intent,
                content_ids: [data.id],
                lead_source: 'whatsapp',
                trigger_location: source
            }, { eventID: eventId });
        }

        // CAPI
        this.sendToCAPI('Contact', {
            event_id: eventId,
            source: source,
            service_data: data
        });

        // Google Analytics / GTM
        if (window.dataLayer) {
            window.dataLayer.push({
                'event': 'whatsapp_contact',
                'conversion_value': data.intent,
                'lead_source': source,
                'service_name': data.name
            });
        }

        // WhatsApp Redirect implementation with [Ref Tag] for match quality
        const refTag = window.EXTERNAL_ID ? ` [Ref: ${window.EXTERNAL_ID.substring(0, 8)}]` : "";
        let message = `Hola Jorge 👋`;
        if (source === 'Floating Button') {
            message = "Hola Jorge, estoy visitando tu web y me interesa una valoración para maquillaje permanente. ¿Podrían asesorarme?";
        } else if (data.intent === 'service_interest') {
            message += ` Me interesa el *${data.name}*. ¿Podría ver si soy candidata?`;
        } else if (data.intent === 'urgency') {
            message += ` Quisiera aprovechar la *Oferta Limitada* de valoración gratuita.`;
        } else {
            message += ` Quisiera información sobre sus servicios de maquillaje permanente.`;
        }

        message += refTag;

        const whatsappUrl = `https://wa.me/${this.config.phone}?text=${encodeURIComponent(message)}`;

        // Use timeout to ensure tracking fires before redirect, but don't block too long
        // 300ms is usually enough for asynchronous fires to be queued by browser
        setTimeout(() => {
            window.open(whatsappUrl, '_blank');
        }, 300);
    },

    /**
     * 5. CAPI HELPER
     */
    async sendToCAPI(eventName, customData) {
        // Extract _fbp cookie (Meta Browser ID)
        const fbp = document.cookie.split('; ').find(row => row.startsWith('_fbp='))?.split('=')[1] || this.getUTM('fbp');

        // Enriched Payload with UTMs
        const payload = {
            event_name: eventName,
            event_time: Math.floor(Date.now() / 1000),
            event_id: customData.event_id || `${eventName.toLowerCase()}_${Date.now()}`,
            event_source_url: window.location.href,
            action_source: "website",
            user_data: {
                external_id: window.EXTERNAL_ID || '',
                fbc: this.getUTM('fbclid') ? `fb.1.${Math.floor(Date.now() / 1000)}.${this.getUTM('fbclid')}` : null,
                fbp: fbp
            },
            custom_data: {
                ...customData,
                fbclid,
                fbp,
                utm_source: this.getUTM('utm_source'),
                utm_medium: this.getUTM('utm_medium'),
                utm_campaign: this.getUTM('utm_campaign'),
                utm_term: this.getUTM('utm_term'),
                utm_content: this.getUTM('utm_content')
            }
        };

        try {
            const response = await fetch('/track/event', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
                keepalive: true
            });
            if (!response.ok) {
                this.warn(`[CAPI] Server Error: ${response.status}`);
            }
        } catch (e) {
            this.warn(`[CAPI] Network Error for ${eventName}`, e);
        }
    }
};

// Global Exposure for UI clicks
window.handleConversion = (source) => TrackingEngine.handleConversion(source);

// Initialize with safe DOM check
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    TrackingEngine.init();
} else {
    document.addEventListener('DOMContentLoaded', () => TrackingEngine.init(), { once: true });
}
