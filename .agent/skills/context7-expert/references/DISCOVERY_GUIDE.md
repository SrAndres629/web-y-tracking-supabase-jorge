# Discovery Guide: Advanced Research 📚

## 1. Effective Library Resolution
To find the exact documentation you need, follow this sequence:
1. **Name Search**: Start with the common name (e.g., `gsap`, `fastapi`). 
2. **Narrow Scope**: If multiple matches appear, prioritize those with high **Source Reputation** and **Benchmark Scores**.
3. **Version Specificity**: If you need an older version, look for library IDs that include the version tag (e.g., `/vercel/next.js/v14.0.0`).

## 2. Granular Querying
Don't ask generic questions. Use "Action-Context-Target" queries:
- **Bad**: "how to use tailwind"
- **Good**: "How to configure dark mode using CSS variables in Tailwind CSS v3.4"
- **Bad**: "supabase auth"
- **Good**: "Implementation of PKCE Auth flow with Supabase Auth JS helpers in Next.js App Router"

## 3. Dealing with Knowledge Gaps
If `query-docs` doesn't return a direct answer:
- **Check Sub-libraries**: Many large projects split docs (e.g., `@tanstack/react-query` vs `@tanstack/query-core`).
- **Semantic Pivot**: Try synonyms (e.g., "middleware" vs "interceptors").
- **External Fallback**: If Context7 lacks a specific library, use `search_web` to find the official docs URL and read it using `read_url_content`.

## 4. Citation Workflow
Always cite your source!
> "According to the Context7 documentation for `/pinecone-io/pinecone-python-client`, the `upsert` method now expects a `VectorType.DENSE` flag."
