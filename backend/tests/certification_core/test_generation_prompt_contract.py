"""Tests for generation prompt contract — versioned prompt construction."""

from __future__ import annotations

import hashlib

import pytest

from app.certification_core.services.prompt_package import (
    build_generation_prompt,
    hash_prompt,
    hash_payload,
    extract_json_from_response,
    GENERATION_OUTPUT_SCHEMA,
    PROMPT_TEMPLATE_VERSION,
    GENERATION_POLICY_VERSION,
    SCHEMA_VERSION,
)


class TestPromptContract:
    """Prove versioned prompt construction."""

    def test_prompt_template_versions(self):
        assert PROMPT_TEMPLATE_VERSION == "1.0.0"
        assert GENERATION_POLICY_VERSION == "1.0.0"
        assert SCHEMA_VERSION == "1.0.0"

    def test_prompt_package_contains_domain_and_competency(self):
        system_prompt, user_prompt, combined = build_generation_prompt(
            domain="Software Testing",
            competency="Test Design Techniques",
            difficulty="medium",
            locale="en-US",
        )
        assert "Software Testing" in combined
        assert "Test Design Techniques" in combined
        assert "medium" in combined
        assert "en-US" in combined

    def test_prompt_contains_output_schema(self):
        _, _, combined = build_generation_prompt(
            domain="QA",
            competency="Test Design",
            difficulty="easy",
            locale="en-US",
        )
        assert "Output Schema" in combined
        assert "answer_key" in combined
        assert "rationale" in combined

    def test_prompt_contains_generation_rules(self):
        _, _, combined = build_generation_prompt(
            domain="QA",
            competency="Test Design",
            difficulty="easy",
            locale="en-US",
        )
        assert "correct option ID" in combined
        assert "source citations" in combined
        assert "valid JSON" in combined

    def test_prompt_hash_deterministic(self):
        _, _, combined = build_generation_prompt(
            domain="QA",
            competency="Testing",
            difficulty="hard",
            locale="en-US",
        )
        hash1 = hash_prompt(combined)
        hash2 = hash_prompt(combined)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length

    def test_different_prompts_different_hashes(self):
        _, _, combined_a = build_generation_prompt(domain="A", competency="X", difficulty="easy", locale="en-US")
        _, _, combined_b = build_generation_prompt(domain="B", competency="Y", difficulty="hard", locale="en-US")
        assert hash_prompt(combined_a) != hash_prompt(combined_b)

    def test_prompt_contains_forbidden_patterns_instruction(self):
        _, _, combined = build_generation_prompt(
            domain="QA",
            competency="Testing",
            difficulty="medium",
            locale="en-US",
        )
        assert "Do NOT" in combined or "do not" in combined

    def test_output_schema_valid_json_schema(self):
        assert "type" in GENERATION_OUTPUT_SCHEMA
        assert "properties" in GENERATION_OUTPUT_SCHEMA
        assert "items" in GENERATION_OUTPUT_SCHEMA["properties"]
        assert "required" in GENERATION_OUTPUT_SCHEMA["properties"]["items"]["items"]
        assert "stem" in GENERATION_OUTPUT_SCHEMA["properties"]["items"]["items"]["required"]

    def test_payload_hash(self):
        payload = {"item_type": "multiple_choice", "stem": "Test?"}
        h = hash_payload(payload)
        assert len(h) == 64

    def test_extract_json_from_markdown(self):
        content = "```json\n{\"items\": [{\"item_type\": \"multiple_choice\"}]}\n```"
        result = extract_json_from_response(content)
        assert result["items"][0]["item_type"] == "multiple_choice"

    def test_extract_json_plain(self):
        content = '{"items": [{"item_type": "single_choice"}]}'
        result = extract_json_from_response(content)
        assert result["items"][0]["item_type"] == "single_choice"
