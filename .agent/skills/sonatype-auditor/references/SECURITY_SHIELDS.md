# Security Shields & Policies 🛡️

## 1. Vulnerability Classification
We use the CVSS (Common Vulnerability Scoring System) v3.x to determine response urgency.

| Severity | CVSS Score | Antigravity Policy | Action Required |
| :------- | :--------- | :----------------- | :-------------- |
| **Critical** | 9.0 - 10.0 | **ZERO TOLERANCE** | Immediate block/removal. |
| **High** | 7.0 - 8.9  | **FIX REQUIRED**   | Patch within 48 hours. |
| **Medium** | 4.0 - 6.9  | **MONITOR**        | Evaluate impact; update if non-breaking. |
| **Low** | 0.1 - 3.9  | **INFO ONLY**      | Update during routine maintenance. |

## 2. Trust Score Thresholds
Beyond security, we evaluate the "Health" of a component via its Developer Trust Score.
- **Score > 80**: Green light. Safe for core production logic.
- **Score 50 - 79**: Caution. Review maintenance patterns and alternative libraries.
- **Score < 50**: Red flag. Avoid using in production; find an alternative.

## 3. License Compliance
- **Allowed**: MIT, Apache-2.0, BSD-3-Clause, ISC.
- **Restricted**: GPLv3, AGPL (Requires legal review/isolation).
- **Prohibited**: Unlicensed or proprietary without explicit contract.

## 4. Remediation Strategy
1. **Always prefer the "Golden Version"** recommended by Sonatype Guide.
2. If the Golden Version is breaking, evaluate the minimum version that clears the Critical/High vulnerability.
3. Document all "Risk Acceptances" (e.g., dev-only tool with a medium exploit).
