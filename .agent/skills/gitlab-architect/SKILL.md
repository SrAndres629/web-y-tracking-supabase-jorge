---
name: gitlab-architect
description: Data Armored Architecture & DevSecOps Master. Manages GitLab Ultimate features, Security CI/CD pipelines, and GitLab Agent for Kubernetes.
---

# GitLab Architect

## Goal
To orchestrate and optimize GitLab environments using the "maximum potential" of GitLab Ultimate. This includes implementing advanced Security CI/CD, managing Cloud Agents (Kubernetes), and leveraging GitLab Duo (Agentic AI) for automated DevSecOps.

## Instructions

### 1. DevSecOps & Security (Ultimate Tier)
Implement shifting security left using GitLab's pre-defined templates.
- **SAST & Secret Detection**: Mandatory for every repository. Use `Security/SAST.gitlab-ci.yml` and `Security/Secret-Detection.gitlab-ci.yml`.
- **Dependency Scanning**: Monitor `npm`, `pip`, `go`, etc., for vulnerable packages. Use `Security/Dependency-Scanning.gitlab-ci.yml`.
- **Infrastructure as Code (IaC) Scanning**: Scan Terraform, Kubernetes, and CloudFormation for misconfigurations.
- **Reference**: [GitLab Security Scanning Documentation](https://docs.gitlab.com/ee/user/application_security/)

### 2. Cloud Agent & Kubernetes Integration
Deploy and manage the **GitLab Agent for Kubernetes** (agentk) for secure, pull-based GitOps or push-based CI/CD.
- **Architecture**: Always use `KAS` (GitLab Agent Server) for bi-directional gRPC tunnels.
- **Configuration**: Use `.gitlab/agents/<name>/config.yaml` to manage manifest synchronization and remote workspaces.
- **Reference**: [GitLab Agent for Kubernetes](https://docs.gitlab.com/ee/user/clusters/agent/)

### 3. CI/CD Orchestration
Optimize pipelines for speed and reliability in Ultimate environments.
- **Merge Trains**: Prevent broken `main` branches by verifying integration before merging.
- **Multi-project Pipelines**: Orchestrate deployments across different repositories.
- **Compliance Pipelines**: Enforce security jobs across all projects in a group.
- **Reference**: [GitLab CI/CD Orchestration](https://docs.gitlab.com/ee/ci/pipelines/pipeline_architectures.html)

### 4. GitLab Duo & AI (Agentic Potential)
Leverage the GitLab Duo Agent Platform for autonomous task execution.
- **Root Cause Analysis**: Use AI to explain CI/CD job failures.
- **Vulnerability Remediation**: Use Duo to explain security findings and suggest fixes.
- **Automation**: Interface with GitLab via API using Personal Access Tokens (PAT) with `api` and `write_repository` scopes.

## Examples

### Input: "Activate maximum security for this project"
**Output**: 
1. Create/Modify `.gitlab-ci.yml`.
2. Include SAST, Secret Detection, Dependency Scanning, and Container Scanning templates.
3. Configure `allow_failure: true` for security jobs to provide feedback without blocking rapid development, OR `allow_failure: false` for high-compliance environments.

### Input: "Configure a cloud agent for my cluster"
**Output**:
1. Guide the user to generate an Agent Token in GitLab UI (*Infrastructure > Kubernetes clusters*).
2. Provide the `helm` command to install `agentk`.
3. Scaffold the `.gitlab/agents/my-agent/config.yaml` file.

## Constraints
- **Authentic Only**: Never store raw tokens in CI/CD files; always use CI/CD Variables.
- **HTTPS Priority**: In WSL/Hybrid environments, favor authenticated HTTPS Git remotes over SSH when keys are misconfigured.
- **Scope Awareness**: When requesting a token from the user, specify the REQUIRED scopes (`api`, `read_repository`, `write_repository`).
- **Official-First**: Always cross-reference [docs.gitlab.com](https://docs.gitlab.com/ee/) for the latest template syntax.
