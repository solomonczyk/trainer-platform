-- Seed documented candidate data for corrective revalidation
-- This restores the known state of cand-c1a83dade217 from layer 003 evidence

DO $$
DECLARE
    v_gen_id UUID := gen_random_uuid();
    v_prov_run_id UUID := gen_random_uuid();
    v_cand_id UUID := gen_random_uuid();
    v_orig_vr_id UUID := gen_random_uuid();
    v_prov_id UUID := gen_random_uuid();
    v_raw_id UUID := gen_random_uuid();
    v_binding_id UUID := gen_random_uuid();
    v_payload_hash TEXT;
    v_raw_hash TEXT := 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855';
    v_prompt_hash TEXT := '888fd326154cf69945df6ffffad60c1d0b4eaadc4dad5d184053d320c471e7e0';
BEGIN

    -- Delete any existing records for this candidate (clean slate)
    DELETE FROM cert_candidate_review_handoffs
    WHERE candidate_id IN (SELECT id FROM cert_generated_candidates WHERE candidate_id = 'cand-c1a83dade217');
    DELETE FROM cert_candidate_provenance
    WHERE candidate_id IN (SELECT id FROM cert_generated_candidates WHERE candidate_id = 'cand-c1a83dade217');
    DELETE FROM cert_candidate_validation_results
    WHERE validation_run_id IN (SELECT id FROM cert_candidate_validation_runs WHERE candidate_id IN (SELECT id FROM cert_generated_candidates WHERE candidate_id = 'cand-c1a83dade217'));
    DELETE FROM cert_candidate_validation_runs
    WHERE candidate_id IN (SELECT id FROM cert_generated_candidates WHERE candidate_id = 'cand-c1a83dade217');
    DELETE FROM cert_generated_candidates WHERE candidate_id = 'cand-c1a83dade217';
    DELETE FROM cert_generation_raw_responses WHERE provider_run_id IN (SELECT id FROM cert_generation_provider_runs WHERE generation_request_id = (SELECT id FROM cert_generation_requests WHERE request_id = 'gen-6db686968c0d'));
    DELETE FROM cert_generation_provider_runs WHERE generation_request_id = (SELECT id FROM cert_generation_requests WHERE request_id = 'gen-6db686968c0d');
    DELETE FROM cert_generation_source_bindings WHERE generation_request_id = (SELECT id FROM cert_generation_requests WHERE request_id = 'gen-6db686968c0d');
    DELETE FROM cert_candidate_provenance WHERE candidate_id IN (SELECT id FROM cert_generated_candidates WHERE candidate_id = 'cand-c1a83dade217');
    DELETE FROM cert_generation_requests WHERE request_id = 'gen-6db686968c0d';
    DELETE FROM cert_audit_events WHERE entity_id = 'cand-c1a83dade217';

    -- Generation request
    INSERT INTO cert_generation_requests (id, request_id, requested_by_user_id, requested_by_role, domain_id, competency_id, difficulty, locale, item_family_id, requested_candidate_count, trusted_source_version_ids, generation_policy_version, prompt_template_version, provider, model, status, correlation_id, created_at, updated_at)
    VALUES (v_gen_id, 'gen-6db686968c0d', 'requester-documented', 'content_author', 'ba_software_development', 'ba_requirements_analysis', 'medium', 'ru-RU', 'ba_multiple_choice', 1, '["src-ba-swdev-v1.0"]'::jsonb, '1.0.0', '1.0.0', 'deepseek', 'deepseek-v4-flash', 'generated', 'corr-documented-001', NOW(), NOW());

    -- Source binding
    INSERT INTO cert_generation_source_bindings (id, binding_id, generation_request_id, source_version_id, source_checksum, source_title, source_locale, source_status, retrieval_method, context_fragment_hashes, created_at, updated_at)
    VALUES (v_binding_id, 'gsb-documented-001', v_gen_id, 'src-ba-swdev-v1.0', 'abc123def456', 'BA Software Development Best Practices v1.0', 'ru-RU', 'active', 'registry', '["frag-hash-001","frag-hash-002"]'::jsonb, NOW(), NOW());

    -- Provider run
    INSERT INTO cert_generation_provider_runs (id, run_id, generation_request_id, provider, model, provider_request_id, prompt_tokens, completion_tokens, total_tokens, cost_usd, latency_ms, status, raw_response_hash, prompt_package_hash, created_at, updated_at)
    VALUES (v_prov_run_id, 'pr-documented-001', v_gen_id, 'deepseek', 'deepseek-v4-flash', 'deepseek-req-documented', 500, 800, 1300, 0.0015, 8000, 'completed', v_raw_hash, v_prompt_hash, NOW(), NOW());

    -- Raw response
    INSERT INTO cert_generation_raw_responses (id, provider_run_id, raw_response, raw_response_hash, secret_material_absent, created_at, updated_at)
    VALUES (v_raw_id, v_prov_run_id, '{"items":[{"item_type":"multiple_choice","stem":"Каков основной принцип анализа требований в разработке ПО?","options":[{"id":"A","text":"Сбор требований от заинтересованных сторон"},{"id":"B","text":"Написание кода без документации"},{"id":"C","text":"Тестирование после завершения разработки"},{"id":"D","text":"Использование только одной методологии"}],"answer_key":{"correct_option_id":"A","explanation":"...","type":"single_choice"},"rationale":"Основной принцип анализа требований — это систематический сбор и документирование потребностей заинтересованных сторон.","rubric":{"criteria":[{"criterion_id":"c1","max_score":1}]},"source_citations":[{"source_id":"BA_SD_BP_v1.0","label":"BA_SD_BP_v1.0"}],"difficulty":"medium","locale":"ru-RU","competency_id":"ba_requirements_analysis","domain_id":"ba_software_development","item_family_id":"ba_multiple_choice"}]}'::jsonb, v_raw_hash, true, NOW(), NOW());

    -- Compute payload hash
    v_payload_hash := encode(sha256('{"answer_key":{"correct_option_id":"A","explanation":"...","type":"single_choice"},"competency_id":"ba_requirements_analysis","difficulty":"medium","domain_id":"ba_software_development","item_family_id":"ba_multiple_choice","item_type":"multiple_choice","locale":"ru-RU","options":[{"id":"A","text":"Сбор требований от заинтересованных сторон"},{"id":"B","text":"Написание кода без документации"},{"id":"C","text":"Тестирование после завершения разработки"},{"id":"D","text":"Использование только одной методологии"}],"rationale":"Основной принцип анализа требований — это систематический сбор и документирование потребностей заинтересованных сторон.","rubric":{"criteria":[{"criterion_id":"c1","max_score":1}]},"source_citations":[{"source_id":"BA_SD_BP_v1.0","label":"BA_SD_BP_v1.0"}],"stem":"Каков основной принцип анализа требований в разработке ПО?"}'::bytea), 'hex');

    -- Generated candidate
    INSERT INTO cert_generated_candidates (id, candidate_id, generation_request_id, provider_run_id, item_family_id, domain_id, competency_id, difficulty, locale, item_type, stem, options, answer_key, rationale, rubric, source_citations, provider, model, raw_response_hash, normalized_payload_hash, normalized_payload, status, validation_status, created_at, updated_at)
    VALUES (v_cand_id, 'cand-c1a83dade217', v_gen_id, v_prov_run_id, 'ba_multiple_choice', 'ba_software_development', 'ba_requirements_analysis', 'medium', 'ru-RU', 'multiple_choice', 'Каков основной принцип анализа требований в разработке ПО?',
        '[{"id":"A","text":"Сбор требований от заинтересованных сторон"},{"id":"B","text":"Написание кода без документации"},{"id":"C","text":"Тестирование после завершения разработки"},{"id":"D","text":"Использование только одной методологии"}]'::jsonb,
        '{"correct_option_id":"A","explanation":"...","type":"single_choice"}'::jsonb,
        'Основной принцип анализа требований — это систематический сбор и документирование потребностей заинтересованных сторон.',
        '{"criteria":[{"criterion_id":"c1","max_score":1}]}'::jsonb,
        '[{"source_id":"BA_SD_BP_v1.0","label":"BA_SD_BP_v1.0"}]'::jsonb,
        'deepseek', 'deepseek-v4-flash', v_raw_hash, v_payload_hash,
        '{"item_type":"multiple_choice","stem":"Каков основной принцип анализа требований в разработке ПО?","options":[{"id":"A","text":"Сбор требований от заинтересованных сторон"},{"id":"B","text":"Написание кода без документации"},{"id":"C","text":"Тестирование после завершения разработки"},{"id":"D","text":"Использование только одной методологии"}],"answer_key":{"correct_option_id":"A","explanation":"...","type":"single_choice"},"rationale":"Основной принцип анализа требований — это систематический сбор и документирование потребностей заинтересованных сторон.","rubric":{"criteria":[{"criterion_id":"c1","max_score":1}]},"source_citations":[{"source_id":"BA_SD_BP_v1.0","label":"BA_SD_BP_v1.0"}],"difficulty":"medium","locale":"ru-RU","competency_id":"ba_requirements_analysis","domain_id":"ba_software_development","item_family_id":"ba_multiple_choice"}'::jsonb,
        'validation_failed', 'failed', NOW(), NOW());

    -- Original validation run (V10 false positive, V3 warning)
    INSERT INTO cert_candidate_validation_runs (id, validation_run_id, candidate_id, validation_policy_version, total_validators, passed_count, failed_count, warning_count, not_run_count, critical_failures, major_failures, decision, created_at, updated_at, started_at, completed_at)
    VALUES (v_orig_vr_id, 'vr-orig-documented-001', v_cand_id, '1.0.0', 15, 13, 1, 1, 0, 0, 1, 'VALIDATION_FAILED', NOW(), NOW(), NOW(), NOW());

    -- Original V1-V15 results
    INSERT INTO cert_candidate_validation_results (id, validation_run_id, validator_code, validator_version, status, severity, reason_code, details, executed_at, created_at, updated_at) VALUES
    (gen_random_uuid(), v_orig_vr_id, 'V1', '1.0.0', 'passed', 'info', NULL, NULL, NOW(), NOW(), NOW()),
    (gen_random_uuid(), v_orig_vr_id, 'V2', '1.0.0', 'passed', 'info', NULL, NULL, NOW(), NOW(), NOW()),
    (gen_random_uuid(), v_orig_vr_id, 'V3', '1.0.0', 'warning', 'minor', 'CITATION_SOURCE_MISMATCH', '{"citation_sources":["BA_SD_BP_v1.0"],"expected_sources":["src-ba-swdev-v1.0"]}'::jsonb, NOW(), NOW(), NOW()),
    (gen_random_uuid(), v_orig_vr_id, 'V4', '1.0.0', 'passed', 'info', NULL, NULL, NOW(), NOW(), NOW()),
    (gen_random_uuid(), v_orig_vr_id, 'V5', '1.0.0', 'passed', 'info', NULL, NULL, NOW(), NOW(), NOW()),
    (gen_random_uuid(), v_orig_vr_id, 'V6', '1.0.0', 'passed', 'info', NULL, NULL, NOW(), NOW(), NOW()),
    (gen_random_uuid(), v_orig_vr_id, 'V7', '1.0.0', 'passed', 'info', NULL, NULL, NOW(), NOW(), NOW()),
    (gen_random_uuid(), v_orig_vr_id, 'V8', '1.0.0', 'passed', 'info', NULL, NULL, NOW(), NOW(), NOW()),
    (gen_random_uuid(), v_orig_vr_id, 'V9', '1.0.0', 'passed', 'info', NULL, NULL, NOW(), NOW(), NOW()),
    (gen_random_uuid(), v_orig_vr_id, 'V10', '1.0.0', 'failed', 'major', 'EXACT_DUPLICATE', '{"existing_candidate_id":"cand-c1a83dade217","similarity":1.0}'::jsonb, NOW(), NOW(), NOW()),
    (gen_random_uuid(), v_orig_vr_id, 'V11', '1.0.0', 'passed', 'info', NULL, NULL, NOW(), NOW(), NOW()),
    (gen_random_uuid(), v_orig_vr_id, 'V12', '1.0.0', 'passed', 'info', NULL, NULL, NOW(), NOW(), NOW()),
    (gen_random_uuid(), v_orig_vr_id, 'V13', '1.0.0', 'passed', 'info', NULL, NULL, NOW(), NOW(), NOW()),
    (gen_random_uuid(), v_orig_vr_id, 'V14', '1.0.0', 'passed', 'info', NULL, NULL, NOW(), NOW(), NOW()),
    (gen_random_uuid(), v_orig_vr_id, 'V15', '1.0.0', 'passed', 'info', NULL, NULL, NOW(), NOW(), NOW());

    -- Provenance
    INSERT INTO cert_candidate_provenance (id, provenance_id, candidate_id, provider, model, source_version_ids, source_checksums, prompt_template_version, prompt_hash, generation_policy_version, schema_version, raw_response_hash, candidate_hash, validator_versions, correlation_id, request_timestamp, response_timestamp, created_at, updated_at)
    VALUES (v_prov_id, 'prov-documented-001', v_cand_id, 'deepseek', 'deepseek-v4-flash', '["src-ba-swdev-v1.0"]'::jsonb, '["abc123def456"]'::jsonb, '1.0.0', v_prompt_hash, '1.0.0', '1.0.0', v_raw_hash, v_payload_hash, '{"V1":"1.0.0","V2":"1.0.0","V3":"1.0.0","V4":"1.0.0","V5":"1.0.0","V6":"1.0.0","V7":"1.0.0","V8":"1.0.0","V9":"1.0.0","V10":"1.0.0","V11":"1.0.0","V12":"1.0.0","V13":"1.0.0","V14":"1.0.0","V15":"1.0.0"}'::jsonb, 'corr-documented-001', NOW(), NOW(), NOW(), NOW());

    RAISE NOTICE 'Seed complete: candidate=cand-c1a83dade217, payload_hash=%', v_payload_hash;
END $$;
