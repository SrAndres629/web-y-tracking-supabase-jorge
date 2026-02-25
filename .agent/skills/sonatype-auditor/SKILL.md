# Sonatype Auditor 🛡️

## Goal
Provide world-class security and quality auditing for project dependencies using the Sonatype OSS Index and Guide. Ensure all external components are safe, up-to-date, and legally compliant.

## Reference Documentation
- **Service**: [Sonatype OSS Index](https://ossindex.sonatype.org/)
- **MCP Server**: Sonatype Guide MCP (Integrated in Antigravity via `sonatype-guide`)
- **PURL Specification**: [Package URL (PURL)](https://github.com/package-url/purl-spec)

## 🛠 Subskills & Modules

### 1. Security Sentry (CVE Audit)
Identify known vulnerabilities and technical risk.
- **When to invoke**: Before installing any new package or during periodic security reviews.
- **Action**: Use `getComponentVersion` with a specific PURL to check for CVEs and severity scores.
- **Goal**: Maintain a Zero-Critical-Vulnerability policy in `app/`.

### 2. Quality Consultant (Health Check)
Evaluate the "Health" of a dependency beyond just security.
- **When to invoke**: Choosing between competing libraries or planning a major upgrade.
- **Action**: Analyze metadata from `getComponentVersion` regarding age, version popularity, and maintenance status.

### 3. Upgrade Architect (Remediation)
Find the safest and most stable upgrade paths.
- **When to invoke**: When a vulnerability is found or when modernize-dependencies tasks are active.
- **Action**: Use `getRecommendedComponentVersions` to identify the "Golden Version" (high trust score, low risk).

---

## 🚀 Professional Usage Prompts

### For Security Auditing:
> "Analyze the current `package.json` and `requirements.txt`. Convert the top 10 dependencies to PURL format and audit them for critical vulnerabilities using Sonatype."

### For Upgrade Planning:
> "Find the recommended upgrade for `pydantic`. Compare my current version with the suggested one based on Developer Trust Score and security fixes."

---

## 💡 Practical Integration: Sonatype vs. NPM Audit

| Feature | Sonatype Auditor (ELITE) | standard `npm audit` |
| :--- | :--- | :--- |
| **Intelligence** | Combined proprietary + public data. | Mostly public records (GHSA/CVE). |
| **Quality Data** | Includes Developer Trust Score and health. | Focuses almost exclusively on security. |
| **Remediation** | Recommends specific "Best" versions. | Suggests `audit fix` (often breaking). |
| **Scope** | Unified (Python + JS + Java + Go). | Language specific (JS only). |

## 🕹 Example Execution Flow

1.  **Trigger**: User wants to add `httpx` to the project.
2.  **Action (Sonatype Auditor)**: 
    - Construct PURL: `pkg:pypi/httpx` (or `pkg:npm/httpx`).
    - Invoke `getLatestComponentVersion`.
    - Review `vulnerabilityCount` and `trustScore`.
3.  **Synthesis**: "I've audited `httpx`. The latest version is `0.28.1` with 0 vulnerabilities and a High Trust Score. Safe to proceed."

## **Sincronización de Integridad Global**
- **Dev Sync**: Bloquea el `gitlab-orchestrator` si se detectan vulnerabilidades críticas.
- **AI Sync**: Provee contexto de riesgo a `genkit-orchestrator` al sugerir librerías externas.
- **Trace Sync**: Monitorea brechas de seguridad reportadas en `arize-phoenix-tracer`.
