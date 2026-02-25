# Audit Workflow: CI/CD Integration 🚀

This workflow describes how to perform a professional audit using the Sonatype MCP tools.

## Phase 1: Pre-Installation Check
Before adding a new dependency:
1. Identify the PURL: `pkg:npm/<package>` or `pkg:pypi/<package>`.
2. Run `getRecommendedComponentVersions`.
3. Verify `vulnerabilityCount === 0`.
4. Proceed only if `trustScore > 80`.

## Phase 2: Weekly Security Scan
Every week, or before a release:
1. Enumerate all top-level dependencies in `package.json` and `requirements.txt`.
2. Convert them to a list of PURLs.
3. Invoke `getComponentVersion` (max 20 at a time).
4. Generate a "Vulnerability Report" summarizing any new CVEs.

## Phase 3: Automated Remediation
If a vulnerability is found in an existing package:
1. Use `getRecommendedComponentVersions` for the affected PURL.
2. Identify the target version.
3. Run `npm install <package>@<version>` or update `requirements.txt`.
4. Run integration tests to ensure no regressions.
5. Commit with prefix: `security(deps): patch vulnerability in <package>`.

## Phase 4: Developer Feedback Loop
If the agent (Me) detects a high-risk package being requested:
- **Alert**: Stop execution.
- **Report**: Show CVSS score and description.
- **Suggest**: Offer an alternative library with higher trust scores.
