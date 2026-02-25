# Pinecone Best Practices 🌲

## 1. Index Configuration
- **Serverless vs Pods**: Use **Serverless** for most Antigravity tasks (Cost-effective, scales to zero). Use Pods only for static, high-throughput low-latency requirements.
- **Metric Selection**: Use `cosine` for most text embeddings (normalized vectors). Use `dotproduct` only if vectors are already normalized and you need every microsecond of speed.
- **Dimension Parity**: Always match the dimension of your embedding model (e.g., 1024 for `multilingual-e5-large`, 1536 for `text-embedding-3-small`).

## 2. Resource Optimization
- **Namespaces**: Segregate data types (e.g., `codebase`, `conversations`, `logs`). This reduces searching overhead and improves relevance.
- **Metadata Filtering**: Index only selective metadata fields. Avoid storing large blobs in metadata; store the `UUID` and fetch full content from Supabase.
- **Batching**: Upsert in batches of 100-200 vectors to avoid network timeouts and optimize API throughput.

## 3. Cost Management
- **Retention Policy**: Implement a TTL (Time-To-Live) for ephemeral data like session logs using a `timestamp` metadata field and periodic deletion.
- **Monitoring**: Use the `describe_index_stats` MCP tool to monitor index fullness and vector counts.

## 4. Query Performance
- **Hybrid Search**: Combine semantic search with keyword filters for high precision (e.g., `filter={'category': 'auth'}`).
- **Top-K Selection**: Start with `top_k=10` and use a Reranker (e.g., `cohere-rerank-3.5`) to select the top 3-5 results for the LLM context.
