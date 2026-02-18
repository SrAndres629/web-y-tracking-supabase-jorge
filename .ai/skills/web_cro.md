# ⚡ SKILL: High-Performance CRO Architecture

## Objective
To eliminate "Bounce Rate" tax. If a user clicks an ad (spending money) but leaves before load, valid budget is incinerated.

## 1. The 1.5 Second Rule
For Meta traffic (mobile, in-app browser), sites loading > 1.5s lose 30% of traffic.
*   **Action**: Use `rel="preload"` for LCP images.
*   **Action**: Inline critical CSS (Tailwind).
*   **Action**: Defer heavy tracking scripts (GTM) until hydration.

## 2. The Trust Funnel (Psychology)
Users from ads are "Cold Traffic". They don't trust you.
*   **Above the Fold**: Clear Value Prop + Hero Image + "As Seen On" (Authority).
*   **Middle**: Transformational results (Before/After).
*   **Bottom**: Risk Reversal (Guarantee) + Urgent CTA.

## 3. Technical Implementation
*   **Image Optimization**: Use WebP/AVIF format automatically.
*   **Layout Shift**: Reserve space for images to prevent CLS (Cumulative Layout Shift) which destroys UX.
