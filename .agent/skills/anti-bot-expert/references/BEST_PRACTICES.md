# Cloudflare Turnstile: Best Practices

## 1. User Experience (UX)
- **Invisible Mode**: Always prefer `data-size="invisible"`. It provides the best conversion rates as it doesn't require user interaction unless suspicious behavior is detected.
- **Fail-Open Path**: If the user's connection to Cloudflare is blocked (common in some regions or restrictive corporate networks), ensure your application allows the submission while logging the event for later review.

## 2. Security
- **Server-Side Validation**: Never trust client-side success callbacks alone. Always verify the `cf-turnstile-response` token on your server using your `SECRET_KEY`.
- **Secret Key Rotation**: Treat your `TURNSTILE_SECRET_KEY` like a password. If compromised, rotate it in the Cloudflare dashboard and update your `.env` immediately.

## 3. Accessibility
- **WCAG Compliance**: Turnstile is designed to be accessible. If a challenge is presented, it supports screen readers and keyboard navigation. Ensure your container doesn't hide the widget if a challenge is triggered.
