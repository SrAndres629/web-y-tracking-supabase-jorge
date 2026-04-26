## 2024-04-26 - Accessible Icon-Only Social Links
**Learning:** Icon-only social links (like those in the footer using font-awesome icons) lack explicit ARIA labels and focus states, making them inaccessible to screen readers and keyboard users.
**Action:** When adding or modifying icon-only links, ensure they include `aria-label` attributes on the anchor tag, `aria-hidden="true"` on the inner icon tag, and explicitly define `focus-visible` styles (e.g., `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-gold`) for keyboard navigation.
