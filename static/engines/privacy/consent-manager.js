/**
 * 🔒 PRIVACY - Consensus Manager
 * Engine for GDPR/CCPA compliant tracking and data collection
 */

export const ConsentConfig = {
    COOKIE_NAME: 'ag_consent',
    VERSION: '1.0',
    EXPIRY_DAYS: 180,
    DOMAINS: {
        analytics: ['google-analytics.com', 'googletagmanager.com'],
        marketing: ['facebook.com', 'connect.facebook.net', 'googleads.g.doubleclick.net'],
        functional: []
    },
    DEFAULT_PREFERENCES: {
        necessary: true,
        functional: true,
        analytics: false,
        marketing: false
    }
};

export const ConsentManager = {
    preferences: { ...ConsentConfig.DEFAULT_PREFERENCES },
    initialized: false,

    init() {
        if (this.initialized) return this;
        this._loadPreferences();
        this.initialized = true;
        return this;
    },

    /**
     * Load preferences from localStorage or cookie
     */
    _loadPreferences() {
        try {
            const stored = localStorage.getItem(ConsentConfig.COOKIE_NAME);
            if (stored) {
                const data = JSON.parse(stored);
                // Version check (nuke old preferences if schema upgraded)
                if (data.version === ConsentConfig.VERSION) {
                    this.preferences = { ...this.preferences, ...data.preferences };
                }
            }
        } catch (e) {
            console.warn('[ConsentManager] Storage read error', e);
        }
    },

    /**
     * Update and save preferences
     */
    update(newPreferences) {
        this.preferences = { ...this.preferences, ...newPreferences };
        this._save();
        this._applyConsent();

        // Dispatch event for other engines
        window.dispatchEvent(new CustomEvent('ag:consent:updated', {
            detail: this.preferences
        }));
    },

    _save() {
        try {
            const payload = {
                version: ConsentConfig.VERSION,
                timestamp: new Date().toISOString(),
                preferences: this.preferences
            };
            localStorage.setItem(ConsentConfig.COOKIE_NAME, JSON.stringify(payload));
        } catch (e) {
            console.warn('[ConsentManager] Storage write error', e);
        }
    },

    /**
     * Apply consent (Enable/Disable tools)
     */
    _applyConsent() {
        // GTM / Meta Pixel Consent Mode
        try {
            if (window.fbq) {
                const consentAction = this.preferences.marketing ? 'grant' : 'revoke';
                window.fbq('consent', consentAction);
            }

            if (window.gtag) {
                window.gtag('consent', 'update', {
                    'analytics_storage': this.preferences.analytics ? 'granted' : 'denied',
                    'ad_storage': this.preferences.marketing ? 'granted' : 'denied'
                });
            }
        } catch (e) {
             console.warn('[ConsentManager] Consent application error', e);
        }

        // Reload page if strictly necessary (usually avoided for UX)
    },

    /**
     * Check if a category is allowed
     */
    canTrack(category = 'analytics') {
        if (category === 'necessary') return true;
        return this.preferences[category] || false;
    },

    hasUserDecided() {
        try {
            return !!localStorage.getItem(ConsentConfig.COOKIE_NAME);
        } catch (e) {
            return false;
        }
    }
};
