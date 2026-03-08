## 2026-03-08 - Added ARIA labels to icon-only action elements
**Learning:** Icon-only elements like social links or closing x marks can cause screen readers to read unintelligible content (e.g. font-awesome classes or generic symbols).
**Action:** When implementing an action element that only contains an icon or a symbol, always include an `aria-label` attribute describing the action or link destination on the parent tag, and add `aria-hidden="true"` to the inner icon element to hide it from the accessibility tree.
