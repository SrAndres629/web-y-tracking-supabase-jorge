// Reusable Zod Schemas for Antigravity Genkit Flows
import { z } from 'genkit';

/**
 * Standard Status Output
 */
export const StatusSchema = z.object({
  success: z.boolean().describe('True if the operation completed successfully'),
  message: z.string().describe('Readable status message or error description'),
  timestamp: z.string().describe('ISO-8601 timestamp of completion'),
});

/**
 * Generic Entity extraction
 */
export const EntitySchema = z.object({
  name: z.string(),
  type: z.enum(['Person', 'Place', 'Organization', 'Date', 'Concept']),
  relevance: z.number().min(0).max(1).describe('Relevance score to the main topic'),
});

/**
 * Search Query Schema (Optimized for Vector Search)
 */
export const SearchQuerySchema = z.object({
  originalQuery: z.string(),
  refinedQuery: z.string().describe('Optimized query for semantic search'),
  filters: z.record(z.any()).optional(),
  topK: z.number().default(10),
});

/**
 * Evaluation Report
 */
export const EvalReportSchema = z.object({
  score: z.number().min(1).max(5),
  reasoning: z.string(),
  suggestions: z.array(z.string()),
});
