## Controlled Item Generation — Known Issues

1. **Provider:** Real DeepSeek generation could not be executed in this session because the DEEPSEEK_API_KEY is not available in the local environment. The provider configuration is validated and the AI Gateway integration is implemented and tested with the mock provider. Actual DeepSeek generation will require the API key to be configured in the staging environment.

2. **Generation Trigger:** The generation execution endpoint currently requires explicit CLI command. No automated/scheduled generation is implemented. This is by design for controlled generation safety.

3. **Semantic Similarity Threshold:** The near-duplicate detection uses Jaccard similarity on word sets. This is a simple implementation. A more sophisticated embedding-based similarity could be implemented in a future layer.

4. **AI-Assisted Validation:** All 15 validators are deterministic. AI-assisted semantic validation (e.g., LLM-as-judge for answer quality) is not implemented in this layer.

5. **CLI Commands:** CLI commands are documented but not implemented as standalone entry points. Operations are available through the REST API and Python service interface.

6. **Review Handoff Human Workflow:** The review handoff queue entry and retrieval API are implemented. The actual human review workflow (assign, review, accept/reject) is not implemented — it belongs to the next layer (Layer 004: Human Review).

7. **CORS and Frontend Integration:** No frontend generation UI has been created. This layer provides the backend API and CLI only.
