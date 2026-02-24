# Diamond Standard: QA & Audit Checklist

## 1. Visual Integrity (The 8px Grid)
- [ ] No "Magic Numbers" in CSS.
- [ ] Paddings and Margins are multiples of 8.
- [ ] Layout matches the Figma/Design tokens.

## 2. Responsivity
- [ ] No horizontal scroll at 320px.
- [ ] Images scale correctly without distortion.
- [ ] Buttons are large enough for mobile thumbs (min 44x44px).

## 3. SEO & Semantic HTML
- [ ] One `h1` per page.
- [ ] Logical heading hierarchy (`h1` -> `h2` -> `h3`).
- [ ] All images have `alt` tags.
- [ ] Internal links are dynamic (`url_for`).

## 4. Accessibility (WCAG 2.1)
- [ ] Contrast ratio > 4.5:1 for normal text.
- [ ] Form elements have associated labels.
- [ ] ARIA landmarks are used correctly (`main`, `nav`, `footer`).

## 5. Performance
- [ ] LCP < 2.5s.
- [ ] CLS < 0.1.
- [ ] FID < 100ms.
