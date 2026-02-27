## 2025-10-26 - Accessibility in Footer Social Links
**Learning:** Icon-only links (like social media icons in the footer) are invisible to screen readers without explicit labels. Visual affordance is not enough for accessibility.
**Action:** Always add `aria-label` to anchor tags that rely solely on icons for context. Ensure the label is in the site's primary language (Spanish in this case).
