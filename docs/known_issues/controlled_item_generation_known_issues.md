## Controlled Item Generation — Known Issues

1. **Provider:** Real DeepSeek generation could not be executed in this session because the DEEPSEEK_API_KEY is not available in the local environment. The provider configuration is validated, the AI Gateway integration is implemented, and the OpenAIProviderAdapter correctly resolves to `provider_name='deepseek'` and `base_url='https://api.deepseek.com'`. Actual DeepSeek generation will require the API key to be configured in the environment (via `.env`, Railway secret, or environment variable).

2. **Generation Trigger:** The generation execution endpoint currently requires explicit CLI command. No automated/scheduled generation is implemented. This is by design for controlled generation safety.

3. **Semantic Similarity Threshold:** The near-duplicate detection uses Jaccard similarity on word sets. This is a simple implementation. A more sophisticated embedding-based similarity could be implemented in a future layer.

4. **AI-Assisted Validation:** All 15 validators are deterministic. AI-assisted semantic validation (e.g., LLM-as-judge for answer quality) is not implemented in this layer.

5. **CLI Commands:** CLI commands are documented but not implemented as standalone entry points. Operations are available through the REST API and Python service interface.

6. **Review Handoff Human Workflow:** The review handoff queue entry and retrieval API are implemented. The actual human review workflow (assign, review, accept/reject) is not implemented — it belongs to the next layer (Layer 004: Human Review).

7. **CORS and Frontend Integration:** No frontend generation UI has been created. This layer provides the backend API and CLI only.

8. **Regression Fix — Migration 005 Container Reference:** The `test_migration_005_execution.py` test was fixed to use the running Docker container `trainer-migration-pg` instead of the previous `trainer-item-bank-migration-005` container that no longer exists. Database name updated to `trainer_platform`. The test now accepts the current alembic head (006) as the final revision after the upgrade cycle. These are fixture-isolation and migration-conflict fixes, not production policy changes.
