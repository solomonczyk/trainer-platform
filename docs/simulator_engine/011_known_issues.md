# Known Issues — Layer 011

1. **Mistakes review user answer display**: The user's actual answer text is shown from `feedback_data` which may be a JSON object for complex steps (e.g., ordering). For steps where feedback_data is null or empty, the answer section shows "No answer data available." This is acceptable for initial implementation.

2. **Professional samples are static content**: The professional example content is defined inline in the quest play page. For production, this should be moved to localization files or a separate data source.

3. **Quest skills mapping is manual**: The skills shown in mission intro are manually mapped per quest ID in `QUEST_SKILLS`. For production, this should come from quest metadata.

4. **Step results stored in memory only**: Step results are stored in React state and survive the session via the backend progress API. However, the full step_results with per-step scores are not persisted to the backend — only the final outcome/debrief is stored. A page refresh during the quest resumes from the current step (not mistakes review).

5. **Next action quest link uses client-side navigation**: The "Start Next Quest" card uses `router.push()` for client-side navigation which clears the current quest session from localStorage. This is intentional.

6. **BA quest first quest does not have QA-style closed steps**: The BA `payment_conflict` quest has dialogue steps (step 6) that use AI evaluation. The first BA interaction is multiple choice (step 1) so the non-textarea requirement is met.

7. **ru-RU localized professional samples**: Professional samples are currently in English only. Russian translations should be added when the content is finalized with the subject matter expert.
