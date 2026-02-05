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

    isHuman: false, // Turnstile Status

    init() {
        if (this.initialized) return;
        this.initialized = true;

        // 🚀 HYBRID ARCHITECTURE (Client-Side Identity)
        // Since HTML is cached at Edge, we must generate unique IDs here if missing.
        if (!window.META_EVENT_ID) {
            window.META_EVENT_ID = `pageview_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            this.log('🆔 Generated Client-Side Event ID:', window.META_EVENT_ID);
        }

        if (!window.EXTERNAL_ID) {
            // Check cookie first, else generate
            const storedId = this.getCookie('external_id');
            window.EXTERNAL_ID = storedId || `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            if (!storedId) this.setCookie('external_id', window.EXTERNAL_ID, 30); // 30 days
            this.log('👤 Hydrated Identity:', window.EXTERNAL_ID);
        }

        // Auto-enable debug if specific parameter exists
        if (new URLSearchParams(window.location.search).has('debug_pixel')) {
            this.debugMode = true;
            this.log('🐛 Debug Mode Enabled');
        }

        this.persistUTMs(); // Priority: Capture campaign data immediately
        // 🚀 ZARAZ MIGRATION: Pixel setup removed here as it's now handled at the Edge by Cloudflare Zaraz.
        this.setupViewContentObserver();
        this.setupSliderListeners();

        this.log('📊 [Senior Architecture] Tracking Engine Active (Hybrid Mode: Edge Cache + Client Identity)');
    },

    // Cookie Helpers
    setCookie(name, value, days) {
        let expires = "";
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "") + expires + "; path=/; SameSite=Lax";
    },

    getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) == ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
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

    /**
     * 🛡️ PIXEL SAFETY WRAPPER (Prevents Race Conditions)
     */
    safeFbq(method, eventName, data, options) {
        if (window.fbq) {
            fbq(method, eventName, data, options);
            this.log(`✅ Pixel Fired: ${eventName}`);
        } else {
            // Retry logic for async loading (Zaraz/Partytown)
            this.retryQueue = this.retryQueue || [];
            this.retryQueue.push({ method, eventName, data, options, time: Date.now() });

            if (!this.retryTimer) {
                this.log(`⏳ Pixel not ready. Queuing event: ${eventName}`);
                this.retryTimer = setInterval(() => {
                    if (window.fbq) {
                        this.log(`🚀 Pixel loaded! Replaying ${this.retryQueue.length} events.`);
                        this.retryQueue.forEach(e => fbq(e.method, e.eventName, e.data, e.options));
                        this.retryQueue = [];
                        clearInterval(this.retryTimer);
                        this.retryTimer = null;
                    }
                    // Stop trying after 10 seconds
                    else if (this.retryQueue.length > 0 && (Date.now() - this.retryQueue[0].time > 10000)) {
                        this.warn('❌ Pixel failed to load. Aborting retries.');
                        clearInterval(this.retryTimer);
                        this.retryTimer = null;
                    }
                }, 500);
            }
        }
    },

    trackIndividualView(sectionId) {
        const serviceData = this.config.services[sectionId] || { name: sectionId, category: 'General', price: 0 };
        const eventId = `vc_${Date.now()}_${sectionId}`;

        // 🚀 ZARAZ MIGRATION: Safe Wrapper
        this.safeFbq('track', 'ViewContent', {
            content_name: serviceData.name,
            content_category: serviceData.category,
            content_ids: [sectionId],
            content_type: 'product',
            value: serviceData.price,
            currency: 'USD'
        }, { eventID: eventId });

        // CAPI
        this.trackEvent('ViewContent', {
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
        // Updated: Use Data Attributes for Robustness (Index is fallback)
        const fallbackNames = ['Microblading 3D', 'Delineado Permanente', 'Labios Full Color'];
        const fallbackIds = ['microblading_3d', 'delineado_ojos', 'labios_full'];

        sliders.forEach((slider, index) => {
            const trackInteraction = () => {
                if (slider.dataset.tracked) return;
                slider.dataset.tracked = "true";

                // Get ID from HTML or Fallback
                const serviceId = slider.dataset.serviceCategory || fallbackIds[index] || `slider_${index}`;
                // Derive readable name from ID or Fallback
                let serviceName = fallbackNames[index] || 'Servicio Desconocido';
                if (slider.dataset.serviceCategory) {
                    serviceName = slider.dataset.serviceCategory.replace(/_/g, ' ').toUpperCase();
                }

                if (window.fbq || true) { // Force usage of safeFbq
                    this.safeFbq('trackCustom', 'SliderInteraction', {
                        content_name: serviceName,
                        content_id: serviceId,
                        interaction_type: 'compare_before_after'
                    }, { eventID: `slider_${Date.now()}_${serviceId}` });
                }

                this.trackEvent('SliderInteraction', {
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

        // Send to Pixel (via Zaraz if available)
        // Send to Pixel (via Zaraz if available)
        // 🚀 SAFE TRACKING: Auto-retries if Pixel is late
        this.safeFbq('track', 'Contact', {
            content_name: data.name,
            content_category: data.intent,
            content_ids: [data.id],
            lead_source: 'whatsapp',
            trigger_location: source
        }, { eventID: eventId });

        // CAPI
        this.trackEvent('Contact', {
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

        // 🚀 SMART NAVIGATION (Silicon Valley Pattern)
        // Check if the trigger is an Anchor Tag (<a>). If so, we let the BROWSER handle the navigation instantly.
        const evt = window.event;
        const isSemanticLink = evt && evt.target && evt.target.closest('a');

        if (!isSemanticLink) {
            // Unblocks UI immediately while tracking fires in background
            setTimeout(() => {
                window.open(whatsappUrl, '_blank');
            }, 300);
        } else {
            this.log('🔗 Navigation handled natively by Browser (Zero Latency)');
        }
    },

    /**
     * 5. CAPI HELPER
     */
    async trackEvent(eventName, eventData = {}) {
        // High-performance background tracking (Zero Latency)
        if ('requestIdleCallback' in window) {
            requestIdleCallback(() => this._dispatch(eventName, eventData));
        } else {
            setTimeout(() => this._dispatch(eventName, eventData), 10);
        }
    },

    async _dispatch(eventName, eventData) {
        // Extract _fbp cookie (Meta Browser ID)
        const fbp = document.cookie.split('; ').find(row => row.startsWith('_fbp='))?.split('=')[1] || this.getUTM('fbp');

        // Enriched Payload with UTMs
        // Detect In-App Browsers (Instagram/TikTok) for ROI Analysis
        const ua = navigator.userAgent || navigator.vendor || window.opera;
        const isInApp = (ua.indexOf("FBAN") > -1) || (ua.indexOf("FBAV") > -1) || (ua.indexOf("Instagram") > -1) || (ua.indexOf("TikTok") > -1);

        const payload = {
            event_name: eventName,
            event_time: Math.floor(Date.now() / 1000),
            event_id: eventData.event_id || `${eventName.toLowerCase()}_${Date.now()}`,
            event_source_url: window.location.href,
            action_source: "website",
            user_data: {
                external_id: window.EXTERNAL_ID || '',
                fbc: this.getUTM('fbclid') ? `fb.1.${Math.floor(Date.now() / 1000)}.${this.getUTM('fbclid')}` : null,
                fbp: fbp
            },
            custom_data: {
                ...eventData,
                fbclid: this.getUTM('fbclid'),
                fbp,
                utm_source: this.getUTM('utm_source'),
                utm_medium: this.getUTM('utm_medium'),
                utm_campaign: this.getUTM('utm_campaign'),
                utm_term: this.getUTM('utm_term'),
                utm_content: this.getUTM('utm_content'),
                browser_context: isInApp ? 'in_app' : 'browser' // Critical for ROI analysis
            }
        };

        try {
            // 🚀 BEACON API (Guaranteed Delivery on Mobile Exit)
            if (navigator.sendBeacon && eventName === 'Contact') {
                const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
                navigator.sendBeacon('/track/event', blob);
                this.log(`📡 [Beacon] Sent critical event: ${eventName}`);
                return;
            }

            // Standard Fetch for others
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

// Turnstile Callback (Anti-Bot)
window.onTurnstileSuccess = function (token) {
    TrackingEngine.isHuman = true;
    TrackingEngine.log('🤖 Turnstile Verified: User is Human');
    TrackingEngine.turnstileToken = token;
};

// Initialize with safe DOM check
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    TrackingEngine.init();
} else {
    document.addEventListener('DOMContentLoaded', () => TrackingEngine.init(), { once: true });
}
