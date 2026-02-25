# Genkit Orchestrator 🤖

## Goal
Design, execute, and debug production-grade agentic workflows using Firebase Genkit. This skill enables Antigravity to build complex AI pipelines with robust observability and schema validation.

## **Sincronización de Integridad Global**
- **Memory Sync**: Sincroniza el contexto de los flujos con `pinecone-architect` (Long-term Memory).
- **Observability Sync**: Envía telemetría detallada a `arize-phoenix-tracer`.
- **Consistency Sync**: Valida que las respuestas de la IA sigan el manual de `marca`.

## Reference Documentation
- **Service**: [Firebase Genkit](https://firebase.google.com/docs/genkit)
- **MCP Server**: Genkit Master Orchestrator (Consolidated as `genkit-mcp-server`)

## 🛠 Subskills & Modules

### 1. Flow Architect (Design & Build)
Create structured, type-safe AI workflows using `ai.defineFlow`.
- **When to invoke**: When building a new AI feature.
- **Action**: Use `genkit_registry` with `action: 'list_flows'` to discover existing ones.

### 2. Runtime Manager (Lifecycle)
Manage the Genkit development environment.
- **Action**: Use `genkit_runtime` with `action: 'start'` and the project's dev command.

### 3. Trace Investigator (Observability)
Debug and optimize model performance using execution traces.
- **Action**: Use `genkit_execution` with `action: 'get_trace'` and the `traceId`.
- **Integration**: Leverage Phoenix (Arize) for long-term trace storage and evaluation.

---

## 🚀 Professional Usage Prompts

### For Flow Creation:
> "Define a new Genkit flow named `emailSummarizer`. Use `gemini-2.5-flash` for high-speed extraction. Ensure the output schema includes `summary`, `priority`, and `actionItems`."

### For Debugging:
> "Fetch the trace for the last `textToSpeechFlow` execution. Identify which step caused the 2.5s latency and check if the prompt was correctly formatted."

---

## 💡 Practical Integration: Genkit vs. Simple Prompting

| Feature | Genkit Orchestrator (ELITE) | standard `ai.generate` |
| :--- | :--- | :--- |
| **Structure** | Multi-step workflows with schemas. | Single-turn text generation. |
| **Observability** | Full execution traces and timing. | No visibility into internal steps. |
| **Safety** | Schema-enforced inputs/outputs. | Unstructured string responses. |
| **Local Dev** | Dedicated Dev UI for testing flows. | Console logging only. |

## 🕹 Example Execution Flow

1.  **Trigger**: User wants a workflow to generate social media posts from a blog URL.
2.  **Action (Genkit Orchestrator)**: 
    - Scaffold `src/index.ts` with Genkit initialization.
    - Define `socialPostFlow` with Zod schema.
    - Invoke `start_runtime` to register the new flow.
3.  **Synthesis**: "Flow `socialPostFlow` is ready. Run `genkit start` to test it in the UI."

## ⚠️ Constraints
- **Single File**: Maintain the project’s current structure; do not split Genkit logic across multiple files unless strictly necessary and supported.
- **Model Versions**: Prefer `gemini-2.5-flash` for GA use cases; use `gemini-3.0-flash-preview` only if explicitly requested.
- **Prompt Isolation**: Use `ai.definePrompt` for complex prompts to keep them decoupled from flow logic.
