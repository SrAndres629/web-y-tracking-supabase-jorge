# Auditing Principles: Strategic Filter

## 1. Bias Detection
- **Over-Optimization**: Is the plan trying to solve 10 things when the user asked for 1?
- **Assumption Trap**: Is the agent assuming the user wants a design change?
- **Technical Bloat**: Does the plan introduce unnecessary dependencies?

## 2. Brand Preservation
- Does the plan align with the **Quiet Luxury** aesthetic?
- Are colors matching the `tokens/colors.css`?

## 3. Risk Assessment
- **Breaking Changes**: Does the plan modify critical legacy routes without unit tests?
- **Infra Risk**: Are there unconfirmed changes to Cloudflare or Vercel?
- **Data Loss**: Does the plan risk breaking tracking events?

## 4. Verdict Logic
- **APPROVED**: Plan is minimal, strategic, and safe.
- **CONDITIONALLY APPROVED**: Needs specific guardrails (e.g., "Add a screenshot check").
- **REJECTED**: Plan is risky, off-brand, or out of scope.
