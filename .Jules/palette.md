# Palette's Journal - UX & Accessibility Learnings

## 2026-02-25 - Icon-Only Link Patterns in Footer and Navbar
**Learning:** The application uses font-awesome icons for social links and simple characters (like `&times;`) for close buttons without any textual alternative or `aria-label`. This creates a completely silent or confusing experience for screen reader users on key navigation elements. The pattern of "visual-only" interactive elements is prevalent in the layout components.
**Action:** When auditing components, specifically check all icon-based buttons and links (especially in `footer.html` and `navbar.html`). Default to adding `aria-label` that describes the destination or action, not just the icon name.
