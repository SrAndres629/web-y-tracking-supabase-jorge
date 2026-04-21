
## 2025-04-21 - Keyboard Accessibility Focus Rings in Tailwind
**Learning:** By default, interactive elements (like icon buttons and links) might not have visible focus rings when navigating via keyboard, making accessibility poor. Additionally, Tailwind's standard `focus:` modifier applies styles on mouse click as well, which can be visually jarring for pointer users.
**Action:** Use the `focus-visible:` modifier (e.g., `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-gold`) instead of standard `focus:` to ensure focus rings are primarily displayed during keyboard navigation and not during mouse interactions.
