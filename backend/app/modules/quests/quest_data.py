"""Quest content data: QA and BA immersive quests for Layer 010.

Each quest is a complete professional simulation with:
- Role and mission
- Story context
- Characters/stakeholders
- Varied interaction types
- Deterministic evaluation for closed questions
- AI rubric evaluation for free-text
- Branching decisions with consequences
- Multiple outcomes
- Educational debrief
"""

from __future__ import annotations

from app.modules.quests import QuestDefinition


# ============================================================================
# QA QUEST — Critical Payment Defect Before Release
# ============================================================================

QA_QUEST = QuestDefinition(
    quest_id="qa_payment_defect_release",
    trainer_slug="qa_engineer_interview_trainer",
    version="1.0.0",
    locale="ru-RU",
    title_key="quest.qa.payment_defect.title",
    summary_key="quest.qa.payment_defect.summary",
    learner_role_key="quest.qa.payment_defect.role",
    mission_key="quest.qa.payment_defect.mission",
    setting_key="quest.qa.payment_defect.setting",
    estimated_minutes=25,
    tags=["qa", "defect_triage", "release_decision", "payment"],
    characters=[
        {
            "id": "product_manager",
            "name_key": "quest.qa.payment_defect.characters.pm",
            "role_key": "quest.qa.payment_defect.characters.pm_role",
        },
        {
            "id": "developer",
            "name_key": "quest.qa.payment_defect.characters.dev",
            "role_key": "quest.qa.payment_defect.characters.dev_role",
        },
        {
            "id": "customer_support",
            "name_key": "quest.qa.payment_defect.characters.support",
            "role_key": "quest.qa.payment_defect.characters.support_role",
        },
        {
            "id": "payment_specialist",
            "name_key": "quest.qa.payment_defect.characters.payment_spec",
            "role_key": "quest.qa.payment_defect.characters.payment_spec_role",
        },
    ],
    initial_state={
        "risk": 30,
        "time_remaining": 100,
        "team_trust": 80,
        "client_trust": 70,
        "evidence_quality": 0,
        "decision_quality": 0,
    },
    steps=[
        # ---- Step 1: Story Introduction + Single Choice ----
        {
            "step_id": "qa_step_01_priority",
            "step_type": "single_choice",
            "story_context_key": "quest.qa.payment_defect.step01.context",
            "prompt_key": "quest.qa.payment_defect.step01.prompt",
            "interaction": {
                "options": [
                    {
                        "id": "check_logs",
                        "text_key": "quest.qa.payment_defect.step01.opt_check_logs",
                        "is_correct": True,
                        "consequence": {"risk": -10, "evidence_quality": 20, "time_remaining": -5, "team_trust": 5},
                    },
                    {
                        "id": "call_meeting",
                        "text_key": "quest.qa.payment_defect.step01.opt_call_meeting",
                        "is_correct": False,
                        "consequence": {"risk": 15, "time_remaining": -20, "team_trust": -5, "evidence_quality": 5},
                    },
                    {
                        "id": "ask_repro",
                        "text_key": "quest.qa.payment_defect.step01.opt_ask_repro",
                        "is_correct": False,
                        "consequence": {"risk": 5, "time_remaining": -10, "evidence_quality": 10, "team_trust": 5},
                    },
                    {
                        "id": "escalate_immediately",
                        "text_key": "quest.qa.payment_defect.step01.opt_escalate",
                        "is_correct": False,
                        "consequence": {"risk": 20, "time_remaining": -5, "team_trust": -20, "client_trust": -15},
                    },
                ]
            },
            "evaluation_mode": "deterministic",
            "consequences": {"risk": 5, "time_remaining": -10},
            "next_step_rules": {"default": "qa_step_02_evidence"},
            "learning_objectives": ["quest.qa.payment_defect.lo.triage"],
            "skill_bindings": ["defect_triage", "critical_thinking"],
        },
        # ---- Step 2: Multiple Choice Evidence Selection ----
        {
            "step_id": "qa_step_02_evidence",
            "step_type": "evidence_select",
            "story_context_key": "quest.qa.payment_defect.step02.context",
            "prompt_key": "quest.qa.payment_defect.step02.prompt",
            "interaction": {
                "evidence_items": [
                    {"id": "payment_gateway_logs", "text_key": "quest.qa.payment_defect.step02.ev_payment_logs", "is_relevant": True, "category": "logs"},
                    {"id": "recent_deploy_notes", "text_key": "quest.qa.payment_defect.step02.ev_deploy_notes", "is_relevant": True, "category": "deploy"},
                    {"id": "browser_console_logs", "text_key": "quest.qa.payment_defect.step02.ev_browser_logs", "is_relevant": False, "category": "client"},
                    {"id": "transaction_db_query", "text_key": "quest.qa.payment_defect.step02.ev_transaction_db", "is_relevant": True, "category": "data"},
                    {"id": "server_uptime_report", "text_key": "quest.qa.payment_defect.step02.ev_uptime", "is_relevant": False, "category": "ops"},
                    {"id": "customer_error_reports", "text_key": "quest.qa.payment_defect.step02.ev_error_reports", "is_relevant": True, "category": "reports"},
                    {"id": "office_wifi_logs", "text_key": "quest.qa.payment_defect.step02.ev_wifi", "is_relevant": False, "category": "network"},
                ],
                "min_select": 2,
                "max_select": 5,
            },
            "evaluation_mode": "deterministic",
            "consequences": {"evidence_quality": 10},
            "next_step_rules": {"default": "qa_step_03_ordering"},
            "learning_objectives": ["quest.qa.payment_defect.lo.evidence"],
            "skill_bindings": ["evidence_collection", "analytical_thinking"],
        },
        # ---- Step 3: Ordering Investigation Steps ----
        {
            "step_id": "qa_step_03_ordering",
            "step_type": "ordering",
            "story_context_key": "quest.qa.payment_defect.step03.context",
            "prompt_key": "quest.qa.payment_defect.step03.prompt",
            "interaction": {
                "items": [
                    {"id": "reproduce", "text_key": "quest.qa.payment_defect.step03.item_reproduce", "correct_order": 1},
                    {"id": "check_logs_step", "text_key": "quest.qa.payment_defect.step03.item_check_logs", "correct_order": 2},
                    {"id": "identify_pattern", "text_key": "quest.qa.payment_defect.step03.item_identify", "correct_order": 3},
                    {"id": "determine_severity", "text_key": "quest.qa.payment_defect.step03.item_severity", "correct_order": 4},
                    {"id": "communicate_findings", "text_key": "quest.qa.payment_defect.step03.item_communicate", "correct_order": 5},
                ],
                "shuffle": True,
            },
            "evaluation_mode": "deterministic",
            "consequences": {"decision_quality": 10},
            "next_step_rules": {"default": "qa_step_04_decision"},
            "learning_objectives": ["quest.qa.payment_defect.lo.investigation"],
            "skill_bindings": ["investigation", "methodology"],
        },
        # ---- Step 4: Branching Decision about Release Risk ----
        {
            "step_id": "qa_step_04_decision",
            "step_type": "decision",
            "story_context_key": "quest.qa.payment_defect.step04.context",
            "prompt_key": "quest.qa.payment_defect.step04.prompt",
            "interaction": {
                "options": [
                    {
                        "id": "block_release",
                        "text_key": "quest.qa.payment_defect.step04.opt_block",
                        "consequence": {"risk": -25, "time_remaining": 0, "team_trust": -10, "client_trust": -5, "decision_quality": 30},
                        "next_step_id": "qa_step_05_bug_report",
                    },
                    {
                        "id": "release_with_monitoring",
                        "text_key": "quest.qa.payment_defect.step04.opt_monitor",
                        "consequence": {"risk": 20, "time_remaining": 0, "team_trust": 10, "client_trust": 10, "decision_quality": -10},
                        "next_step_id": "qa_step_05_bug_report",
                    },
                    {
                        "id": "delay_for_analysis",
                        "text_key": "quest.qa.payment_defect.step04.opt_delay",
                        "consequence": {"risk": -10, "time_remaining": -30, "team_trust": -5, "client_trust": -15, "decision_quality": 15},
                        "next_step_id": "qa_step_05_bug_report",
                    },
                ]
            },
            "evaluation_mode": "deterministic",
            "next_step_rules": {
                "default": "qa_step_05_bug_report",
                "by_choice": {
                    "block_release": "qa_step_05_bug_report",
                    "release_with_monitoring": "qa_step_05_bug_report",
                    "delay_for_analysis": "qa_step_05_bug_report",
                },
            },
            "learning_objectives": ["quest.qa.payment_defect.lo.decision"],
            "skill_bindings": ["risk_assessment", "decision_making"],
        },
        # ---- Step 5: Free-Text Bug Report ----
        {
            "step_id": "qa_step_05_bug_report",
            "step_type": "free_text",
            "story_context_key": "quest.qa.payment_defect.step05.context",
            "prompt_key": "quest.qa.payment_defect.step05.prompt",
            "interaction": {
                "max_length": 3000,
                "min_length": 100,
                "placeholder_key": "quest.qa.payment_defect.step05.placeholder",
                "guidance_key": "quest.qa.payment_defect.step05.guidance",
                "ai_rubric": {
                    "rubric_version": "1.0.0",
                    "criteria": [
                        {"criterion_id": "bug_structure", "weight": 0.3, "description_key": "quest.qa.payment_defect.rubric.structure", "max_score": 100},
                        {"criterion_id": "severity_priority", "weight": 0.2, "description_key": "quest.qa.payment_defect.rubric.severity", "max_score": 100},
                        {"criterion_id": "reproduction_steps", "weight": 0.3, "description_key": "quest.qa.payment_defect.rubric.reproduction", "max_score": 100},
                        {"criterion_id": "environment_details", "weight": 0.2, "description_key": "quest.qa.payment_defect.rubric.environment", "max_score": 100},
                    ],
                    "minimum_pass_score": 60,
                    "evaluation_prompt_key": "quest.qa.payment_defect.rubric.eval_prompt",
                    "system_prompt_key": "quest.qa.payment_defect.rubric.system_prompt",
                },
            },
            "evaluation_mode": "ai_rubric",
            "next_step_rules": {"default": "qa_step_06_dialogue"},
            "learning_objectives": ["quest.qa.payment_defect.lo.bug_report"],
            "skill_bindings": ["bug_reporting", "technical_writing"],
        },
        # ---- Step 6: Dialogue with Manager ----
        {
            "step_id": "qa_step_06_dialogue",
            "step_type": "dialogue",
            "story_context_key": "quest.qa.payment_defect.step06.context",
            "prompt_key": "quest.qa.payment_defect.step06.prompt",
            "interaction": {
                "character_says_key": "quest.qa.payment_defect.step06.character_says",
                "options": [
                    {
                        "id": "explain_risk",
                        "text_key": "quest.qa.payment_defect.step06.opt_explain_risk",
                        "consequence": {"team_trust": 10, "decision_quality": 15, "risk": -5},
                        "next_step_id": "__terminal__",
                    },
                    {
                        "id": "compromise",
                        "text_key": "quest.qa.payment_defect.step06.opt_compromise",
                        "consequence": {"team_trust": 15, "client_trust": 10, "risk": 10, "decision_quality": -5},
                        "next_step_id": "__terminal__",
                    },
                    {
                        "id": "stand_firm",
                        "text_key": "quest.qa.payment_defect.step06.opt_stand_firm",
                        "consequence": {"team_trust": -5, "client_trust": -5, "risk": -15, "decision_quality": 20},
                        "next_step_id": "__terminal__",
                    },
                ],
                "allow_free_text": False,
            },
            "evaluation_mode": "deterministic",
            "next_step_rules": {"default": "__terminal__"},
            "learning_objectives": ["quest.qa.payment_defect.lo.communication"],
            "skill_bindings": ["communication", "stakeholder_management"],
        },
    ],
    outcomes=[
        {
            "outcome_id": "qa_success",
            "title_key": "quest.qa.payment_defect.outcome.success.title",
            "summary_key": "quest.qa.payment_defect.outcome.success.summary",
            "min_decision_quality": 60,
            "min_team_trust": 60,
        },
        {
            "outcome_id": "qa_partial",
            "title_key": "quest.qa.payment_defect.outcome.partial.title",
            "summary_key": "quest.qa.payment_defect.outcome.partial.summary",
            "min_decision_quality": 40,
            "min_team_trust": 40,
            "is_default": True,
        },
        {
            "outcome_id": "qa_failure",
            "title_key": "quest.qa.payment_defect.outcome.failure.title",
            "summary_key": "quest.qa.payment_defect.outcome.failure.summary",
            "min_decision_quality": 0,
            "min_team_trust": 0,
        },
    ],
    debrief_contract={
        "sections": [
            "strengths",
            "mistakes",
            "missed_risks",
            "decision_consequences",
            "professional_recommendation",
            "practical_takeaways",
            "skill_profile",
            "suggested_next_practice",
        ],
        "skill_dimensions": [
            "defect_triage",
            "evidence_collection",
            "risk_assessment",
            "bug_reporting",
            "stakeholder_communication",
            "release_decision",
        ],
    },
)


# ============================================================================
# BA QUEST — Conflicting Requirements for Payment Feature
# ============================================================================

BA_QUEST = QuestDefinition(
    quest_id="ba_payment_requirements_conflict",
    trainer_slug="business_analyst_interview_trainer",
    version="1.0.0",
    locale="ru-RU",
    title_key="quest.ba.payment_conflict.title",
    summary_key="quest.ba.payment_conflict.summary",
    learner_role_key="quest.ba.payment_conflict.role",
    mission_key="quest.ba.payment_conflict.mission",
    setting_key="quest.ba.payment_conflict.setting",
    estimated_minutes=30,
    tags=["ba", "requirements", "stakeholder", "payment", "conflict_resolution"],
    characters=[
        {
            "id": "product_owner",
            "name_key": "quest.ba.payment_conflict.characters.po",
            "role_key": "quest.ba.payment_conflict.characters.po_role",
        },
        {
            "id": "compliance_specialist",
            "name_key": "quest.ba.payment_conflict.characters.compliance",
            "role_key": "quest.ba.payment_conflict.characters.compliance_role",
        },
        {
            "id": "tech_lead",
            "name_key": "quest.ba.payment_conflict.characters.tech_lead",
            "role_key": "quest.ba.payment_conflict.characters.tech_lead_role",
        },
        {
            "id": "customer_rep",
            "name_key": "quest.ba.payment_conflict.characters.customer",
            "role_key": "quest.ba.payment_conflict.characters.customer_role",
        },
    ],
    initial_state={
        "risk": 40,
        "time_remaining": 100,
        "team_trust": 70,
        "client_trust": 60,
        "evidence_quality": 0,
        "decision_quality": 0,
    },
    steps=[
        # ---- Step 1: Identify Stakeholders (Multiple Choice) ----
        {
            "step_id": "ba_step_01_stakeholders",
            "step_type": "multiple_choice",
            "story_context_key": "quest.ba.payment_conflict.step01.context",
            "prompt_key": "quest.ba.payment_conflict.step01.prompt",
            "interaction": {
                "choices": [
                    {"id": "product_owner", "text_key": "quest.ba.payment_conflict.step01.opt_po", "is_correct": True},
                    {"id": "compliance", "text_key": "quest.ba.payment_conflict.step01.opt_compliance", "is_correct": True},
                    {"id": "tech_lead", "text_key": "quest.ba.payment_conflict.step01.opt_tech_lead", "is_correct": True},
                    {"id": "customer", "text_key": "quest.ba.payment_conflict.step01.opt_customer", "is_correct": True},
                    {"id": "office_manager", "text_key": "quest.ba.payment_conflict.step01.opt_office_mgr", "is_correct": False},
                    {"id": "intern_designer", "text_key": "quest.ba.payment_conflict.step01.opt_intern", "is_correct": False},
                    {"id": "cfo", "text_key": "quest.ba.payment_conflict.step01.opt_cfo", "is_correct": True},
                    {"id": "marketing_social", "text_key": "quest.ba.payment_conflict.step01.opt_marketing", "is_correct": False},
                ],
                "min_selections": 3,
                "max_selections": 8,
            },
            "evaluation_mode": "deterministic",
            "consequences": {"risk": -5, "evidence_quality": 10, "decision_quality": 5},
            "next_step_rules": {"default": "ba_step_02_matching"},
            "learning_objectives": ["quest.ba.payment_conflict.lo.stakeholders"],
            "skill_bindings": ["stakeholder_identification", "business_context"],
        },
        # ---- Step 2: Match Stakeholders to Interests ----
        {
            "step_id": "ba_step_02_matching",
            "step_type": "matching",
            "story_context_key": "quest.ba.payment_conflict.step02.context",
            "prompt_key": "quest.ba.payment_conflict.step02.prompt",
            "interaction": {
                "left_items": [
                    "quest.ba.payment_conflict.step02.left_po",
                    "quest.ba.payment_conflict.step02.left_compliance",
                    "quest.ba.payment_conflict.step02.left_tech",
                    "quest.ba.payment_conflict.step02.left_customer",
                ],
                "right_items": [
                    "quest.ba.payment_conflict.step02.right_speed",
                    "quest.ba.payment_conflict.step02.right_security",
                    "quest.ba.payment_conflict.step02.right_scalability",
                    "quest.ba.payment_conflict.step02.right_usability",
                ],
                "correct_mappings": {
                    "quest.ba.payment_conflict.step02.left_po": "quest.ba.payment_conflict.step02.right_speed",
                    "quest.ba.payment_conflict.step02.left_compliance": "quest.ba.payment_conflict.step02.right_security",
                    "quest.ba.payment_conflict.step02.left_tech": "quest.ba.payment_conflict.step02.right_scalability",
                    "quest.ba.payment_conflict.step02.left_customer": "quest.ba.payment_conflict.step02.right_usability",
                },
            },
            "evaluation_mode": "deterministic",
            "consequences": {"evidence_quality": 15, "decision_quality": 10},
            "next_step_rules": {"default": "ba_step_03_ordering"},
            "learning_objectives": ["quest.ba.payment_conflict.lo.stakeholder_interests"],
            "skill_bindings": ["stakeholder_analysis", "requirements_elicitation"],
        },
        # ---- Step 3: Order Requirement-Analysis Steps ----
        {
            "step_id": "ba_step_03_ordering",
            "step_type": "ordering",
            "story_context_key": "quest.ba.payment_conflict.step03.context",
            "prompt_key": "quest.ba.payment_conflict.step03.prompt",
            "interaction": {
                "items": [
                    {"id": "gather_stakeholder_input", "text_key": "quest.ba.payment_conflict.step03.item_gather", "correct_order": 1},
                    {"id": "identify_conflicts", "text_key": "quest.ba.payment_conflict.step03.item_conflicts", "correct_order": 2},
                    {"id": "analyze_impact", "text_key": "quest.ba.payment_conflict.step03.item_impact", "correct_order": 3},
                    {"id": "propose_solution", "text_key": "quest.ba.payment_conflict.step03.item_solution", "correct_order": 4},
                    {"id": "validate_with_stakeholders", "text_key": "quest.ba.payment_conflict.step03.item_validate", "correct_order": 5},
                    {"id": "document_requirements", "text_key": "quest.ba.payment_conflict.step03.item_document", "correct_order": 6},
                ],
                "shuffle": True,
            },
            "evaluation_mode": "deterministic",
            "consequences": {"decision_quality": 10, "risk": -5},
            "next_step_rules": {"default": "ba_step_04_decision"},
            "learning_objectives": ["quest.ba.payment_conflict.lo.analysis_process"],
            "skill_bindings": ["process_analysis", "methodology"],
        },
        # ---- Step 4: Decision - Resolve Stakeholder Conflict ----
        {
            "step_id": "ba_step_04_decision",
            "step_type": "decision",
            "story_context_key": "quest.ba.payment_conflict.step04.context",
            "prompt_key": "quest.ba.payment_conflict.step04.prompt",
            "interaction": {
                "options": [
                    {
                        "id": "facilitate_workshop",
                        "text_key": "quest.ba.payment_conflict.step04.opt_workshop",
                        "consequence": {"team_trust": 15, "client_trust": 10, "decision_quality": 20, "risk": -10, "time_remaining": -15},
                        "next_step_id": "ba_step_05_free_text",
                    },
                    {
                        "id": "prioritize_po",
                        "text_key": "quest.ba.payment_conflict.step04.opt_prioritize_po",
                        "consequence": {"team_trust": -5, "client_trust": -10, "decision_quality": -5, "risk": 15, "time_remaining": -5},
                        "next_step_id": "ba_step_05_free_text",
                    },
                    {
                        "id": "escalate_to_sponsor",
                        "text_key": "quest.ba.payment_conflict.step04.opt_escalate",
                        "consequence": {"team_trust": -10, "client_trust": 5, "decision_quality": 5, "risk": 5, "time_remaining": -10},
                        "next_step_id": "ba_step_05_free_text",
                    },
                ]
            },
            "evaluation_mode": "deterministic",
            "next_step_rules": {
                "default": "ba_step_05_free_text",
                "by_choice": {
                    "facilitate_workshop": "ba_step_05_free_text",
                    "prioritize_po": "ba_step_05_free_text",
                    "escalate_to_sponsor": "ba_step_05_free_text",
                },
            },
            "learning_objectives": ["quest.ba.payment_conflict.lo.conflict_resolution"],
            "skill_bindings": ["conflict_resolution", "facilitation"],
        },
        # ---- Step 5: Free-Text - Write Acceptance Criterion ----
        {
            "step_id": "ba_step_05_free_text",
            "step_type": "free_text",
            "story_context_key": "quest.ba.payment_conflict.step05.context",
            "prompt_key": "quest.ba.payment_conflict.step05.prompt",
            "interaction": {
                "max_length": 3000,
                "min_length": 100,
                "placeholder_key": "quest.ba.payment_conflict.step05.placeholder",
                "guidance_key": "quest.ba.payment_conflict.step05.guidance",
                "ai_rubric": {
                    "rubric_version": "1.0.0",
                    "criteria": [
                        {"criterion_id": "acceptance_structure", "weight": 0.25, "description_key": "quest.ba.payment_conflict.rubric.structure", "max_score": 100},
                        {"criterion_id": "stakeholder_balance", "weight": 0.25, "description_key": "quest.ba.payment_conflict.rubric.balance", "max_score": 100},
                        {"criterion_id": "testability", "weight": 0.25, "description_key": "quest.ba.payment_conflict.rubric.testability", "max_score": 100},
                        {"criterion_id": "business_value", "weight": 0.25, "description_key": "quest.ba.payment_conflict.rubric.business_value", "max_score": 100},
                    ],
                    "minimum_pass_score": 60,
                    "evaluation_prompt_key": "quest.ba.payment_conflict.rubric.eval_prompt",
                    "system_prompt_key": "quest.ba.payment_conflict.rubric.system_prompt",
                },
            },
            "evaluation_mode": "ai_rubric",
            "next_step_rules": {"default": "ba_step_06_dialogue"},
            "learning_objectives": ["quest.ba.payment_conflict.lo.acceptance_criteria"],
            "skill_bindings": ["acceptance_criteria", "requirements_documentation"],
        },
        # ---- Step 6: Dialogue - Defend Decision ----
        {
            "step_id": "ba_step_06_dialogue",
            "step_type": "dialogue",
            "story_context_key": "quest.ba.payment_conflict.step06.context",
            "prompt_key": "quest.ba.payment_conflict.step06.prompt",
            "interaction": {
                "character_says_key": "quest.ba.payment_conflict.step06.character_says",
                "allow_free_text": True,
                "max_length": 2000,
                "min_length": 50,
                "placeholder_key": "quest.ba.payment_conflict.step06.placeholder",
                "guidance_key": "quest.ba.payment_conflict.step06.guidance",
                "ai_rubric": {
                    "rubric_version": "1.0.0",
                    "criteria": [
                        {"criterion_id": "argument_clarity", "weight": 0.3, "description_key": "quest.ba.payment_conflict.rubric.clarity", "max_score": 100},
                        {"criterion_id": "stakeholder_empathy", "weight": 0.3, "description_key": "quest.ba.payment_conflict.rubric.empathy", "max_score": 100},
                        {"criterion_id": "professional_tone", "weight": 0.2, "description_key": "quest.ba.payment_conflict.rubric.tone", "max_score": 100},
                        {"criterion_id": "solution_oriented", "weight": 0.2, "description_key": "quest.ba.payment_conflict.rubric.solution", "max_score": 100},
                    ],
                    "minimum_pass_score": 60,
                    "evaluation_prompt_key": "quest.ba.payment_conflict.rubric.eval_prompt_dialogue",
                    "system_prompt_key": "quest.ba.payment_conflict.rubric.system_prompt_dialogue",
                },
            },
            "evaluation_mode": "hybrid",
            "next_step_rules": {"default": "__terminal__"},
            "learning_objectives": ["quest.ba.payment_conflict.lo.communication"],
            "skill_bindings": ["communication", "stakeholder_management", "negotiation"],
        },
    ],
    outcomes=[
        {
            "outcome_id": "ba_success",
            "title_key": "quest.ba.payment_conflict.outcome.success.title",
            "summary_key": "quest.ba.payment_conflict.outcome.success.summary",
            "min_decision_quality": 65,
            "min_team_trust": 65,
            "min_client_trust": 60,
        },
        {
            "outcome_id": "ba_partial",
            "title_key": "quest.ba.payment_conflict.outcome.partial.title",
            "summary_key": "quest.ba.payment_conflict.outcome.partial.summary",
            "min_decision_quality": 40,
            "min_team_trust": 40,
            "min_client_trust": 40,
            "is_default": True,
        },
        {
            "outcome_id": "ba_failure",
            "title_key": "quest.ba.payment_conflict.outcome.failure.title",
            "summary_key": "quest.ba.payment_conflict.outcome.failure.summary",
            "min_decision_quality": 0,
            "min_team_trust": 0,
        },
    ],
    debrief_contract={
        "sections": [
            "strengths",
            "mistakes",
            "missed_risks",
            "decision_consequences",
            "professional_recommendation",
            "practical_takeaways",
            "skill_profile",
            "suggested_next_practice",
        ],
        "skill_dimensions": [
            "stakeholder_analysis",
            "requirements_elicitation",
            "conflict_resolution",
            "acceptance_criteria",
            "communication",
            "business_analysis",
        ],
    },
)


# Registry of all quests by quest_id
QUEST_REGISTRY: dict[str, QuestDefinition] = {
    "qa_payment_defect_release": QA_QUEST,
    "ba_payment_requirements_conflict": BA_QUEST,
}
