# Genkit Architecture Patterns 🏗️

## 1. The Linear Pipeline (Sequential Flow)
The simplest pattern where data flows in one direction through multiple model calls.
- **Use Case**: Simple text extraction, translation, and summary.
- **Pattern**:
  ```ts
  const result = await step('extraction', async () => ...);
  const translated = await step('translation', async () => ...);
  return translated;
  ```

## 2. The Multi-Agent Router
A "Supervisor" model analyzes the user intent and delegates the task to a specialized "Worker" flow.
- **Use Case**: Customer support bots, multi-tool assistants.
- **Pattern**: 
  - Supervisor: `gemini-pro-3.0` (High reasoning).
  - Workers: `gemini-flash-2.5` (Fast, specific).

## 3. RAG Orchestration (Retrieval-Augmented)
Integrating vector search (Pinecone) within a Genkit flow.
1. **Retrieve**: Call `pinecone.query`.
2. **Augment**: In-context background data.
3. **Generate**: Call `ai.generate`.
- **Optimization**: Use `ai.definePrompt` to manage complex RAG system instructions.

## 4. Controlled Looping (Reflection)
The model generates an output, a validator (or another model) reviews it, and if it fails, it loops back with feedback.
- **Use Case**: Code generation, logic verification.
- **Constraint**: Always implement a `maxIterations` guard to prevent infinite loops and cost spikes.

## 5. Tool-Calling Agents
Defining `tools` directly in `ai.generate` to allow the model to interact with the external world (DBs, APIs).
- **Security**: Always sanitize tool inputs and use RLS (Row Level Security) on DB calls.
