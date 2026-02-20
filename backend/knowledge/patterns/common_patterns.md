# Common Search Patterns

## Finding Framework Documentation

**Best approach:**
1. Search for the feature name (e.g., "guardrails", "teams", "workflows")
2. If no results, try related terms (e.g., "validation" for guardrails, "multi-agent" for teams)
3. Read the full document for complete context

**Known sources:**
- Agno Introduction: Overview of the framework, key concepts, getting started
- Agno First Agent: Step-by-step guide to building an agent, configuration options

## Finding Configuration Information

**Best approach:**
1. Search for the specific setting name (e.g., "model_id", "db_url")
2. Search for the feature area (e.g., "authentication", "database")
3. Check the first-agent guide for configuration examples

## Finding API Information

**Best approach:**
1. Search for the endpoint or method name
2. Search for the resource type (e.g., "agent", "team", "workflow")
3. Check introduction docs for API overview

## Search Strategy

When information might be anywhere:

1. **Identify the information type**
   - Framework concepts -> Search "Agno Introduction"
   - How-to guides -> Search "Agno First Agent"
   - PDF/CSV data -> Check loaded documents with list_knowledge_sources

2. **Try specific terms first, then broaden**

3. **Use multiple search approaches**
   - Vector search (automatic, runs before each response)
   - Keyword search via search_content (for exact terms)
   - File browsing via list_files + read_file (for document exploration)

4. **Save what you learn**
   - If a location was surprising -> save_intent_discovery
   - If a search strategy worked well -> save_learning

## Handling "Not Found" Results

1. **Try synonyms** — "auth" vs "authentication" vs "JWT" vs "token"
2. **Broaden the search** — remove specific qualifiers
3. **Check if documents are loaded** — use list_knowledge_sources
4. **Suggest alternatives** — web search agent, loading additional documents
