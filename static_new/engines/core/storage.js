/**
 * 🔧 CORE - Storage Manager
 * Abstracción para cookies, localStorage y sessionStorage
 */

export const Storage = {
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
   * localStorage con manejo de errores
   */
  local: {
    get(key, defaultValue = null) {
      try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
      } catch (e) {
        console.warn('Storage get error:', e);
        return defaultValue;
      }
    },

    set(key, value) {
      try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
      } catch (e) {
        console.warn('Storage set error:', e);
        return false;
      }
    },

    remove(key) {
      try {
        localStorage.removeItem(key);
      } catch (e) {
        console.warn('Storage remove error:', e);
      }
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
