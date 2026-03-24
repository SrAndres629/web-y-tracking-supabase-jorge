## 2024-03-24 - Accessibility for Icon-only Interactive Elements
**Learning:** Icon-only elements, such as social links and mobile menu close buttons, must include an `aria-label` attribute on the parent tag and `aria-hidden="true"` on the inner icon element to ensure accessibility without breaking screen reader functionality or creating redundant announcements.
**Action:** Always add explicit `aria-label` to parent anchors/buttons and hide purely visual icons from screen readers using `aria-hidden="true"`.
