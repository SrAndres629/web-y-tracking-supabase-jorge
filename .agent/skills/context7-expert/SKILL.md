# Context7 Expert 📚

## Goal
Master the retrieval of up-to-date documentation and high-quality code examples using the Context7 API. This skill ensures Antigravity always uses the latest library versions and follows modern implementation patterns, bypassing the knowledge cutoff of base LLM models.

## Reference Documentation
- **Service**: [Context7 Search](https://context7.com/)
- **MCP Server**: Context7 MCP (Integrated in Antigravity via `context7`)

## 🛠 Subskills & Modules

### 1. Library Resolver (Discovery)
Find the exact `/org/project` identifier for any framework or package.
- **When to invoke**: When starting work with a library you Haven't used in this session or when you need a specific version.
- **Action**: Use `resolve-library-id` with the library name.
- **Goal**: Obtain a valid `libraryId` to enable deep querying.

### 2. Document Researcher (Synthesis)
Extract specific implementation details, API signatures, and code snippets.
- **When to invoke**: Before writing code for a non-trivial feature or when debugging a "Version Conflict" error.
- **Action**: Use `query-docs` with the resolved `libraryId`.
- **Constraint**: Be specific in the query (e.g., "React 19 useActionState hook examples" vs "react hooks").

### 3. Version Watcher (Parity)
Ensure code parity with the latest GA (General Availability) releases.
- **When to invoke**: During a `modernize-dependencies` task or when a user asks to "upgrade to the latest".
- **Action**: Use Context7 to compare current project versions with the latest documentation available.

---

## 🚀 Professional Usage Prompts

### For Library Research:
> "Research the latest documentation for `gsap`. I specifically need to know how to use the `ScrollTrigger` plugin with `Lenis` in a Next.js 15 environment."

### For Error Resolution:
> "I'm getting a 'module not found' for `pydantic.v1`. Check Context7 for the Pydantic v2 migration guide and show me how to update the validators in `app/models.py`."

---

## 💡 Practical Integration: Context7 vs. Base Knowledge

| Feature | Context7 Expert (ELITE) | Base LLM Knowledge |
| :--- | :--- | :--- |
| **Recency** | Real-time (documents from today). | Limited to training cutoff. |
| **Precision** | Actual code snippets from official docs. | Potential for "halucinated" API methods. |
| **Depth** | Access to full library file structures. | Summary-level knowledge. |
| **Verification** | Can cite specific doc URLs. | General "Common Knowledge" only. |

## 🕹 Example Execution Flow

1.  **Trigger**: User wants to implement "Cloudflare Turnstile" in the login page.
2.  **Action (Context7 Expert)**: 
    - Resolve ID: `resolve-library-id("cloudflare-turnstile")`.
    - Result: `/cloudflare/turnstile-docs`.
    - Query: `query-docs(libraryId="/cloudflare/turnstile-docs", query="Server-side validation in Python FastAPI")`.
3.  **Synthesis**: "According to the latest docs, you need to use the `siteverify` endpoint. Here is the implementation using `httpx`."

## **Sincronización de Integridad Global**
- **AI Sync**: Provee documentación fresca a `genkit-orchestrator` para implementaciones de vanguardia.
- **Memory Sync**: Alimenta la memoria long-term de `pinecone-architect` con ejemplos de código validados.
- **Security Sync**: Verifica patrones de uso seguro documentados para `sonatype-auditor`.
