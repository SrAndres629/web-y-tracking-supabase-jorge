/**
 * 🛡️ CORE LOGGER - Silicon Valley Standard
 * Centralized logging system with environment awareness.
 * 
 * Usage:
 *   import { Logger } from './logger.js';
 *   Logger.debug('Something happened', { data: 123 });
 */

const isProduction = window.location.hostname !== 'localhost' &&
    !window.location.search.includes('debug=1') &&
    !new URLSearchParams(window.location.search).has('debug_pixel');

export const Logger = {
    /**
     * Log for development/debugging
     */
    debug(message, ...args) {
        if (!isProduction) {
            console.log(`[DEBUG] ${message}`, ...args);
        }
    },

    /**
     * Log info (visible in prod if needed, but usually filtered)
     */
    info(message, ...args) {
        if (!isProduction || window.DEBUG_MODE) {
            console.info(`[INFO] ${message}`, ...args);
        }
    },

    /**
     * Log warnings (always visible)
     */
    warn(message, ...args) {
        console.warn(`[WARN] ${message}`, ...args);
    },

    /**
     * Log errors
     */
    error(message, ...args) {
        console.error(`[ERROR] ${message}`, ...args);
    }
};

export default Logger;
