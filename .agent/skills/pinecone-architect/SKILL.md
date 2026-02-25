# Pinecone Architect 🌲

## Goal
Master the management of Pinecone vector databases to provide Antigravity with high-performance long-term memory, hybrid search capabilities, and RAG (Retrieval-Augmented Generation) orchestration.

## **Sincronización de Integridad Global**
- **AI Sync**: Sirve como la base de conocimiento para los flujos de `genkit-orchestrator`.
- **Trace Sync**: Indexa logs críticos de `arize-phoenix-tracer` para análisis histórico.
- **Doc Sync**: Sincroniza vectores con la documentación fresca obtenida vía `context7-expert`.

## Reference Documentation
- **Official SDK**: [Pinecone Python Documentation](https://docs.pinecone.io/guides/get-started/quickstart)
- **MCP Server**: Pinecone MCP Server (Integrated in Antigravity via `pinecone-mcp-server`)

## 🛠 Subskills & Modules

### 1. Index Orchestrator
Manage the lifecycle of Pinecone indexes (Serverless or Pod-based).
- **When to invoke**: When setting up a new project memory, changing embedding dimensions, or performing maintenance.
- **MCP Action**: Use `pinecone_lifecycle` with `action: 'create_index'` or `'list_indexes'`.
- **SDK Pattern**: Use `pc.create_index(name, dimension, spec=ServerlessSpec(...))`.

### 2. Vector Librarian
Handle the storage and retrieval of specific data points.
- **When to invoke**: During event tracking, archiving conversations, or indexing codebase "Knowledge Items" (KIs).
- **Sub-Tasks**:
  - **Upserting**: Metadata-rich vector storage.
  - **Fetching**: Direct ID-based lookup.
  - **Namespace Management**: Segregating data by tenant or data type (e.g., `logs`, `code`, `visitor_behavior`).

### 3. Search Engineer (Hybrid & Semantic)
Perform high-precision retrieval using semantic and keyword matching.
- **When to invoke**: Responding to complex user queries, finding similar code blocks, or auditing past sessions.
- **Elite Pattern**: Implement Hybrid Search using sparse (BM25/SPLADE) and dense (E5/OpenAI) vectors.
- **MCP Action**: `pinecone_data` with `action: 'search'`. Use `pinecone_intelligence` for `rerank`.

---

## 🚀 Professional Usage Prompts

### For Memory Storage:
> "Index the current architecture decisions into the `antigravity-brain` index using the `architecture` namespace. Include metadata for `commit_hash` and `author`."

### For Knowledge Retrieval:
> "Perform a search in the `documentation` namespace. Use `pinecone_data` (action: search) and then `pinecone_intelligence` (action: rerank) using `cohere-rerank-3.5`."

---

## 💡 Practical Integration: Pinecone vs. Supabase

| Feature | Use Pinecone | Use Supabase |
| :--- | :--- | :--- |
| **Data Type** | High-dimensional vectors, embeddings. | Relational data, user profiles, transactional. |
| **Search** | Semantic similarity, "fuzzy" matching. | Filter-based, exact matches, JSONB queries. |
| **Latency** | Optimized for <100ms vector search at scale. | Optimized for ACID compliance and data integrity. |
| **Use Case** | RAG, "What did we talk about last month?", Code search. | "What is the user's email?", "Save this lead to the CRM". |

## 🕹 Example Execution Flow

1.  **Observation**: User asks about a bug resolved two weeks ago.
2.  **Action (Pinecone Architect)**: 
    - Invoke MCP `pinecone_data` (action: search) in index `antigravity-memory`.
    - Query: "bug related to oauth flow connection failure".
    - Filter: `{"category": "bug_report"}`.
3.  **Synthesis**: Retrieve the relevant context and present the solution.

## ⚠️ Constraints
- **Namespace discipline**: Never mix different data types in the default namespace.
- **Metadata limits**: Keep metadata keys under 40kb per vector.
- **Dimension parity**: Ensure query embeddings match the index dimension (default 1024 or 1536).
- **Security**: Never log API keys; use environment variables `PINECONE_API_KEY`.
