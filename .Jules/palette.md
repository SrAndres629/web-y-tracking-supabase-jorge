## 2024-04-28 - Footer Social Links Accessibility
**Learning:** Icon-only social links in footer templates were missing accessible names, leading to poor screen reader experiences.
**Action:** Always add `aria-label` to `<a>` tags containing only decorative icons (like FontAwesome), apply `aria-hidden="true"` to the inner `<i>` tags, and ensure keyboard navigation visibility using `focus-visible` utility classes (e.g., `focus-visible:ring-luxury-gold`).
