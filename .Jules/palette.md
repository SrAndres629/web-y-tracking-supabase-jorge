
## 2025-02-19 - Accessibility of Icon-Only Buttons and Links
**Learning:** Icon-only navigation and interaction elements (such as social media links and mobile menu toggles) are inaccessible to screen readers by default. The specific pattern requires adding `aria-label` to the parent interactive element (`<a href...>` or `<button>`) to provide descriptive action, and `aria-hidden="true"` to the inner visual element (e.g., `<i class="...">`) to prevent screen readers from reading meaningless CSS class characters or icon font glyphs.
**Action:** Always add an `aria-label` attribute on the parent tag and `aria-hidden="true"` on the inner icon element when dealing with icon-only elements such as social links in `footer.html` and mobile menus in `navbar.html`.
