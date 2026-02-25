# Arize Phoenix Tracer 🔬

## Goal
Implement and manage high-fidelity observability and evaluation for LLMs and AI Agents using Arize Phoenix and OpenTelemetry. This skill ensures Antigravity's "Chain of Thought" is transparent, measurable, and optimizable.

## Reference Documentation
- **Local Observability**: [Phoenix Documentation](https://docs.arize.com/phoenix/)
- **Cloud Observability**: [Arize Documentation](https://docs.arize.com/arize/)
- **MCP Server**: Arize Tracing Assistant (Integrated in Antigravity via `arize-tracing-assistant`)

## 🛠 Subskills & Modules

### 1. Auto-Instrumentor (Zero-Code Tracing)
Enable automatic collection of spans for popular frameworks (OpenAI, LangChain, LlamaIndex).
- **When to invoke**: At project startup or when adding a new AI provider.
- **Action**: Use `arize_phoenix.otel.register()` or `phoenix.trace.openai.instrument()`.
- **Goal**: Full visibility into model parameters, token counts, and costs without manual code changes.

### 2. Manual Span Master (Deep Debugging)
Instrument custom business logic and complex reasoning steps.
- **When to invoke**: When a flow has multiple logic branches or external tool calls that are not automatically tracked.
- **Action**: Use the `@trace` decorator (Python) or `tracer.start_as_current_span()` (OpenTelemetry standard).
- **Pattern**: Group related operations into parent spans to visualize nested workflows.

### 3. Evaluator (Quality Benchmarking)
Assess the quality of model outputs using deterministic or LLM-as-a-judge metrics.
- **When to invoke**: After implementing a new prompt or before a production release.
- **Action**: Setup `Phoenix` evaluation experiments to measure "Relevance", "Hallucination", and "QA Correctness".

---

## 🚀 Professional Usage Prompts

### For Auto-Instrumentation:
> "Enable OpenAI auto-instrumentation for the current Python environment. Point the traces to the local Phoenix collector at `http://localhost:6006`."

### For Manual Tracing:
> "Add a manual tracing span to the `TrackEventHandler.handle()` method. Name the span 'Post-Processing_Logic' and include attributes for `event_name` and `processing_time`."

---

## 💡 Practical Integration: Phoenix vs. Standard Logging

| Feature | Arize Phoenix Tracer (ELITE) | standard `structlog` / `logging` |
| :--- | :--- | :--- |
| **Structure** | Trace/Span hierarchy (Visual). | Flat text lines (Sequential). |
| **Context** | Input/Output payloads + Metadata. | Mostly error messages or state changes. |
| **Evaluation** | Integrated quality scoring. | No built-in way to score quality. |
| **UX** | Rich browser-based tracing UI. | Terminal pager or text logs only. |

## 🕹 Example Execution Flow

1.  **Trigger**: User reports that "Summaries are too short".
2.  **Action (Arize Phoenix Tracer)**: 
    - Open Phoenix UI (`localhost:6006`).
    - Locate the specific trace for the summary request.
    - Inspect the `system_prompt` and `model_response` spans.
    - Run an evaluation experiment with different `max_tokens` settings.
3.  **Synthesis**: "I found the issue in the trace: `max_tokens` was capped at 100. Increasing it to 500 resolved the brevity problem."

## **Sincronización de Integridad Global**
- **AI Sync**: Provee trazas en tiempo real a `genkit-orchestrator` para auto-optimización de prompts.
- **Dev Sync**: Integra hallazgos de errores en el ciclo de `gitlab-orchestrator` para reparaciones automáticas vía Jules.
- **Master Sync**: Reporta el "System Health" global al `master-architect`.
- **Performance Leak**: Ensure tracing is asynchronous; never let telemetry collection block the main request thread.
- **PII Protection**: Mask sensitive user data (emails, passwords) before exporting spans to Arize Cloud.
- **Endpoint Awareness**: Check if `PHOENIX_COLLECTOR_URL` is configured before initializing exporters.
