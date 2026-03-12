# Palette's Journal

## 2024-03-12 - Accessibility Initialization
**Learning:** This repo is using Font Awesome icons for social links and mobile menu buttons without proper `aria-label` or `aria-hidden` attributes.
**Action:** When working with FontAwesome icons as buttons/links, ensure the parent has an `aria-label` and the `<i>` tag has `aria-hidden="true"`.
