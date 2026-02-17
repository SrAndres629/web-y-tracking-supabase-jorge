/**
 * 🔒 PRIVACY - Cookie Banner (UI)
 * Simple, non-intrusive consent UI
 */

const TEMPLATE = `
<div id="ag-consent-banner" class="fixed bottom-0 left-0 right-0 bg-black/90 backdrop-blur-md text-white p-6 z-50 transform translate-y-full transition-transform duration-500 ease-in-out border-t border-luxury-gold/20">
  <div class="container mx-auto max-w-7xl flex flex-col md:flex-row items-center justify-between gap-6">
    <div class="flex-1 text-sm text-gray-300 space-y-2">
      <h3 class="font-serif text-lg text-luxury-gold mb-1">Tu privacidad es importante</h3>
      <p>
        Utilizamos cookies para mejorar tu experiencia y ofrecerte contenido relevante sobre micropigmentación.
        Al continuar, aceptas nuestras <a href="/privacy" class="text-luxury-gold hover:underline">políticas de privacidad</a>.
      </p>
    </div>
    <div class="flex items-center gap-4 text-xs font-semibold">
      <button id="ag-consent-reject" class="text-gray-400 hover:text-white transition-colors uppercase tracking-wider">
        Solo necesarias
      </button>
      <button id="ag-consent-accept" class="bg-luxury-gold text-black px-6 py-3 rounded-full hover:bg-yellow-500 transition-all uppercase tracking-wider shadow-lg shadow-luxury-gold/20">
        Aceptar
      </button>
      <button id="ag-consent-customize" class="sr-only">Personalizar</button>
    </div>
  </div>
</div>
`;

export const ConsentBanner = {
    manager: null,

    init(manager) {
        this.manager = manager;
        if (!this.manager.hasUserDecided()) {
            this._show();
        }
    },

    _show() {
        if (document.getElementById('ag-consent-banner')) return;

        document.body.insertAdjacentHTML('beforeend', TEMPLATE);
        const banner = document.getElementById('ag-consent-banner');

        // Wait for next tick to animate
        requestAnimationFrame(() => {
            banner.classList.remove('translate-y-full');
        });

        this._bindEvents();
    },

    _hide() {
        const banner = document.getElementById('ag-consent-banner');
        if (banner) {
            banner.classList.add('translate-y-full');
            setTimeout(() => banner.remove(), 500);
        }
    },

    _bindEvents() {
        document.getElementById('ag-consent-accept').addEventListener('click', () => {
            this.manager.update({
                functional: true,
                analytics: true,
                marketing: true
            });
            this._hide();
        });

        document.getElementById('ag-consent-reject').addEventListener('click', () => {
            this.manager.update({
                functional: true,
                analytics: false,
                marketing: false
            });
            this._hide();
        });
    }
};
