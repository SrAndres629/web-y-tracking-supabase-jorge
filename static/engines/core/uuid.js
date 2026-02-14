/**
 * 🔧 CORE - UUID Generator
 * RFC 4122 compliant UUID v4
 */

export const UUID = {
  /**
   * Genera UUID v4
   */
  generate() {
    return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
      (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
  },

  /**
   * Genera ID corto para uso interno
   */
  short(prefix = 'id') {
    return `${prefix}_${Math.random().toString(36).substr(2, 9)}`;
  },

  /**
   * Genera external_id consistente
   */
  externalId() {
    return `user_${this.generate().substring(0, 18)}`;
  }
};
