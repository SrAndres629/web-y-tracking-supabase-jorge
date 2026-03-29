1. **Analyze UX/A11y Opportunities**
   - The user has requested to find and implement ONE micro-UX improvement that makes the interface more intuitive, accessible, or pleasant to use.
   - Based on `.Jules/palette.md` memory context: "Icon-only elements, such as social links in `api/templates/components/footer.html` and mobile menu close buttons, must include an `aria-label` attribute on the parent tag and `aria-hidden="true"` on the inner icon element to ensure accessibility."
   - Looking at `api/templates/components/footer.html`, the social media links (Facebook, Instagram, TikTok) are icon-only `<a>` tags with missing `aria-label`.
   - In `api/templates/components/navbar.html`, the mobile menu close button is a `<button>` with no `aria-label` containing an `&times;` character.
   - We need to add these ARIA labels.

2. **Refine Scope to One Clear Improvement**
   - The social media links in `api/templates/components/footer.html` are a classic example of missing ARIA labels for icon-only links.
   - Adding `aria-label="Facebook"`, `aria-label="Instagram"`, and `aria-label="TikTok"` on the `<a>` tags, and `aria-hidden="true"` on the `<i>` tags will improve screen reader accessibility without changing any visual styling.
   - Same for the mobile menu close button in `api/templates/components/navbar.html`, adding `aria-label="Cerrar menú"` and `aria-hidden="true"` to the `&times;` (maybe wrapping it in a span).

3. **Implementation Plan**
   - In `api/templates/components/footer.html`: Add `aria-label` to the Facebook, Instagram, and TikTok anchor tags, and `aria-hidden="true"` to the inner `<i>` tags.
   - In `api/templates/components/navbar.html`: Add `aria-label="Cerrar menú"` to the close mobile menu `<button>` and `aria-hidden="true"` on an inner span wrapping the `&times;`.
   - Update `.Jules/palette.md` to record this learning as per instructions.
   - Complete pre-commit steps.
   - Submit PR.
