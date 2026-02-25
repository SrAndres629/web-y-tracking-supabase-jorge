# Instrumentation Strategy: Manual Span Management 🔬

## 1. When to use Manual Spans
Auto-instrumentation captures API calls, but not the **Reasoning** between them. Use manual spans for:
- Complex prompt assembly logic.
- Post-processing of model outputs (e.g., regex extraction, validation).
- Decision-making nodes in a multi-agent system.

## 2. Python (Phoenix) Pattern
```python
from phoenix.trace import SpanKind
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def process_ai_logic(data):
    with tracer.start_as_current_span(
        "BusinessLogic_Processing",
        kind=SpanKind.INTERNAL,
        attributes={"data_size": len(data)}
    ) as span:
        # Your logic here
        result = do_something(data)
        span.set_attribute("result_status", "success")
        return result
```

## 3. Best Practices for Spans
- **Naming**: Use `CamelCase_ActionName`. Avoid generic names like "run" or "process".
- **Attributes**: Include IDs (e.g., `user_id`, `event_id`) but **NEVER** PII (Plain Email/Phone).
- **Exceptions**: Use `span.record_exception(e)` and set span status to `ERROR` to ensure visibility in the Phoenix UI.

## 4. Trace Hierarchy
Always nest sub-operations under a parent "Workflow" span to provide a tree-view of the execution.
- Parent: `Main_Request_Handler`
  - Child: `DB_Lookup`
  - Child: `AI_Generation`
  - Child: `Output_Validation`
