# Palette's Journal - Critical UX/A11y Learnings

This journal contains critical learnings about UX and accessibility constraints and patterns within this repository.

## 2025-01-31 - Initial Setup

**Learning:** Initializing the journal as requested in constraints.
**Action:** Always document significant UX and accessibility findings in this file.

## 2025-03-01 - Social Icons & Controls A11y

**Learning:** Icon-only elements such as social links (in the footer) and generic UI controls (like the mobile menu close `&times;` icon) do not inherently communicate their purpose to screen readers. This is a common accessibility gap in component patterns relying solely on visual icons.
**Action:** Consistently verify and add `aria-label` attributes to any icon-only anchors or buttons across all components to ensure assistive technology can announce their function.