// English locale strings for Trainer Platform UI

const en = {
  app: {
    name: "Trainer Platform",
    tagline: "Professional Training Platform",
    description: "Practice and develop skills with AI-powered evaluation",
  },

  nav: {
    home: "Home",
    domains: "Domains",
    myProgress: "My Progress",
    profile: "Profile",
    admin: "Admin",
    login: "Log In",
    register: "Register",
    logout: "Log Out",
  },

  landing: {
    heroTitle: "Prepare for Interviews with AI Trainer",
    heroSubtitle: "Practice answering real questions, get structured evaluation, and track your progress",
    startButton: "Start Learning",
    features: "Features",
    feature1Title: "Realistic Scenarios",
    feature1Desc: "Scenarios based on real interview questions",
    feature2Title: "AI Rubric Evaluation",
    feature2Desc: "Structured evaluation with criteria, evidence, and recommendations",
    feature3Title: "Progress Tracking",
    feature3Desc: "Detailed skill and topic progress tracking",
    languages: "ru-RU / en-US",
  },

  auth: {
    email: "Email",
    password: "Password",
    confirmPassword: "Confirm Password",
    displayName: "Display Name",
    loginTitle: "Log In",
    registerTitle: "Register",
    loginButton: "Log In",
    registerButton: "Register",
    noAccount: "Don't have an account?",
    hasAccount: "Already have an account?",
    registerLink: "Register",
    loginLink: "Log In",
    loginSuccess: "Logged in successfully",
    registerSuccess: "Registration successful",
    errorInvalidCredentials: "Invalid email or password",
    errorEmailTaken: "This email is already registered",
  },

  domains: {
    title: "Domain Catalog",
    subtitle: "Select a domain to start learning",
    it: "IT",
    itDescription: "Development, testing, DevOps, and other IT fields",
    backToDomains: "Back to Domains",
    trainersIn: "Trainers in domain",
  },

  trainer: {
    title: "About Trainer",
    enroll: "Enroll in Trainer",
    enrolled: "You are enrolled",
    enrolledMessage: "Successfully enrolled in the trainer",
    scenarios: "Scenarios",
    startScenario: "Start Scenario",
    scenarioList: "Scenario List",
    startQuest: "Start Quest",
    questCatalog: "Quest Catalog",
    questCatalogDesc: "Professional immersive simulations with varied interaction types",
    questsAvailable: "Quests available",
    immersiveExperience: "Immersive Learning Format",
    immersiveExperienceDesc: "Complete professional quests with different question types, decision consequences, and educational debrief",
    difficulty: "Difficulty",
    duration: "Duration",
    minutes: "min",
    skills: "Skills",
    targetAudience: "Target Audience",
    locale: "Language",
    backToTrainer: "Back to Trainer",
    notEnrolled: "Enroll in the trainer to start",
    // Trainer product name localizations (keys match trainer_product_id slugs)
    qa_engineer_interview_trainer: "QA Engineer Interview Trainer",
    business_analyst_interview_trainer: "Business Analyst Interview Trainer",
    // Trainer product description localizations
    qa_engineer_interview_trainer_desc: "Text-based interview trainer for Junior QA candidates. Practice answering common QA interview questions with structured AI evaluation.",
    business_analyst_interview_trainer_desc: "Text-based interview trainer for Business Analyst candidates. Practice answering common BA interview questions with structured AI evaluation.",
    // Trainer target audience labels
    audience_junior_qa_candidate: "Junior QA Candidate",
    audience_career_switcher: "Career Switcher",
    audience_trainee_qa: "QA Trainee",
    audience_junior_ba: "Junior BA",
    audience_middle_ba: "Middle BA",
    audience_senior_ba: "Senior BA",
    audience_ba_career_switcher: "Career Switcher to BA",
    audience_ba_trainee: "BA Trainee",
    audience_ba_junior: "Junior BA",
    // Level identifiers
    level_junior: "Junior",
    level_middle: "Middle",
    level_senior: "Senior",
    level_junior_basic: "Junior (Basic)",
    level_intermediate: "Intermediate",
    level_advanced: "Advanced",
  },

  scenario: {
    title: "Scenario",
    start: "Start Scenario",
    ready: "Are you ready?",
    intro: "Scenario Introduction",
    userRole: "Your Role",
    aiRole: "AI Role",
    yourAnswer: "Your Answer",
    answerPlaceholder: "Write your answer here...",
    submit: "Submit Answer",
    submitting: "Submitting...",
    complete: "Complete & Get Evaluation",
    completing: "Completing...",
    answerSaved: "Answer saved",
    evaluateNow: "Evaluate Answer",
    evaluating: "AI is evaluating your answer...",
    evaluationFailed: "Evaluation temporarily unavailable",
    evaluationFailedMessage: "Your answer has been saved. Try requesting evaluation later.",
    retryEvaluation: "Retry Evaluation",
    backToList: "Back to Scenario List",
    emptyAnswerError: "Answer cannot be empty",
    hints: "Hints",
    // QA scenario title and goal translations
    qa_self_presentation_v1: {
      title: "Tell Me About Yourself as a QA Candidate",
      goal: "Evaluate the candidate's ability to present themselves professionally, structure their background, and articulate their motivation for pursuing a QA role.",
    },
    qa_test_case_vs_checklist_v1: {
      title: "Test Case vs Checklist: Differences and Use Cases",
      goal: "Evaluate the candidate's understanding of test documentation: the difference between test cases and checklists, their structure, when to use each, and the trade-offs involved.",
    },
    qa_bug_report_structure_v1: {
      title: "Bug Report Structure",
      goal: "Evaluate the candidate's knowledge of proper bug report structure, including all required fields, severity vs priority classification, and best practices for writing clear reproduction steps.",
    },
    qa_regression_vs_retest_v1: {
      title: "Regression Testing vs Retesting",
      goal: "Evaluate the candidate's ability to distinguish between regression testing and retesting, understand when each is applied, and explain their roles in the QA process with practical examples.",
    },
    qa_login_form_testing_v1: {
      title: "Login Form Testing Scenarios",
      goal: "Evaluate the candidate's ability to design comprehensive test scenarios for a login form, applying test design techniques, identifying edge cases, and structuring their test coverage logically.",
    },
  },

  result: {
    title: "Evaluation Result",
    overallScore: "Overall Score",
    passed: "Passed",
    failed: "Needs Practice",
    criteria: "Evaluation Criteria",
    criterion: "Criterion",
    score: "Score",
    evidence: "Evidence",
    comment: "Comment",
    improvement: "How to Improve",
    strengths: "Strengths",
    weakPoints: "Weak Points",
    criticalErrors: "Critical Errors",
    noCriticalErrors: "No critical errors detected",
    nextRecommendation: "Next Steps",
    retryScenario: "Retry Scenario",
    nextScenario: "Next Scenario",
    toProgress: "View Progress",
    progressUpdated: "Progress Updated",
    confidence: "Evaluation Confidence",
    disclaimer: "This is an interview simulation with AI evaluation. Results do not guarantee actual interview success.",
  },

  progress: {
    title: "My Progress",
    noProgress: "No progress records yet",
    averageScore: "Average Score",
    completedScenarios: "Completed Scenarios",
    totalAttempts: "Total Attempts",
    readiness: {
      started: "Started",
      developing: "Developing",
      ready: "Ready",
      strong: "Strong",
    },
    skillScores: "Skill Scores",
    trainerProgress: "Trainer Progress",
    noSkillData: "No skill data available",
    lastActivity: "Last Activity",
  },

  profile: {
    title: "Profile",
    email: "Email",
    name: "Name",
    preferredLocale: "Preferred Language",
    save: "Save",
    saved: "Profile updated",
    language: "Interface Language",
  },

  admin: {
    title: "Administration",
    seedStatus: "Seed Status",
    systemHealth: "System Health",
    evaluationFailures: "Evaluation Failures",
    analytics: "Analytics",
    domains: "Domains",
    trainers: "Trainers",
    scenarios: "Scenarios",
    rubrics: "Rubrics",
    locales: "Localizations",
    skills: "Skills",
    enrollments: "Enrollments",
    aiRequests: "AI Requests",
    totalEvents: "Total Events",
    refresh: "Refresh",
  },

  common: {
    loading: "Loading...",
    error: "An error occurred",
    retry: "Retry",
    save: "Save",
    cancel: "Cancel",
    back: "Back",
    next: "Next",
    close: "Close",
    notFound: "Not Found",
    forbidden: "Access Denied",
    unauthorized: "Authentication Required",
    sessionExpired: "Session Expired",
    comingSoon: "Coming Soon",
  },

  feature: {
    beta: "Beta Access",
    betaMessage: "This feature is in development",
  },

  disclaimer: {
    interview: "This is an interview simulation. Answers are analyzed by AI and do not guarantee actual results. Do not share personal data (passwords, addresses, card numbers).",
  },

  ba_trainer: {
    name: "Business Analyst Interview Trainer",
    short_name: "BA Trainer",
    domain: "IT",
    module_label: "Module",
    activity_label: "Question",
    start: "Start Training",
    continue: "Continue",
    submit: "Submit Answer",
    next: "Next Question",
    back_to_modules: "Back to Modules",
    result_correct: "Correct!",
    result_partial: "Partially Correct",
    result_incorrect: "Incorrect",
    score_label: "Score",
    explanation_label: "Explanation",
    difficulty_junior: "Junior",
    difficulty_middle: "Middle",
    difficulty_senior: "Senior",
    total_activities: "Total Questions",
    completed_activities: "Completed",
    progress_label: "Progress",
    module_activities: "Module Questions",
    loading: "Loading...",
    error_loading: "Error loading",
    error_submitting: "Error submitting answer",
    no_activities: "No questions in this module yet",
    select_answer: "Select answer",
    type_answer: "Type answer",
    match_pairs: "Match pairs",
    fill_blanks: "Fill in the blanks",
    your_answer: "Your answer",
    correct_answer: "Correct answer",
    attempt_count: "Attempt {count}",
    retry: "Try Again",
    modules: "Modules",
    phase_1_badge: "Phase 1",
    status_staging: "Staging",
  },

  // Phase 2 scenario title translations
  ba_phase2_stakeholder_requirements_title: "Stakeholder Requirements Elicitation in Fintech",
  ba_phase2_process_analysis_title: "Process Analysis and Optimization for Claims Processing",
  ba_phase2_documentation_artifacts_title: "Requirements Specification for Loyalty Program",
  ba_phase2_conflict_resolution_title: "Conflict Resolution in WMS Implementation",
  ba_phase2_traceability_impact_title: "Impact Analysis of API Integration Changes",
  ba_phase2_real_case_analysis_title: "Corporate Learning Platform Architecture with AI",

  // BA Phase 2
  ba_phase2: {
    title: "Business Analysis Scenarios (Phase 2)",
    description: "Realistic BA assignments with AI-powered evaluation",
    phase_2_badge: "Phase 2 — AI Evaluation",
    start: "Start Scenario",
    how_it_works_title: "How It Works",
    how_it_works_desc: "Read the business context and task, write a detailed answer, receive structured AI evaluation with per-criterion feedback. Up to 3 attempts per scenario.",
    back_to_scenarios: "Back to Scenarios",
    business_context: "Business Context",
    task: "Task",
    your_answer: "Your Answer",
    answer_placeholder: "Write your detailed answer here...",
    complete: "Complete & Get Evaluation",
    evaluating_title: "AI is evaluating your answer",
    evaluating_desc: "DeepSeek is analyzing your answer against rubric criteria. This may take up to 30 seconds.",
    evaluating_progress: "Evaluation in progress...",
    evaluated_by: "Evaluated by",
    retry: "Retry Scenario",
    max_attempts_reached: "Maximum attempts reached",
    max_attempts_desc: "You have used all 3 attempts for this scenario",
    default_role: "Business Analyst",
  },

  // ---------------------------------------------------------------------------
  // Quest Engine (Layer 010 — Immersive Simulator)
  // ---------------------------------------------------------------------------
  quest: {
    // Navigation
    back_to_trainer: "Back to Trainer",
    start_quest: "Start Quest",
    continue_quest: "Continue",
    my_quests: "My Quests",

    // Quest list
    quest_catalog: "Quest Catalog",
    quest_catalog_desc: "Choose a professional scenario to practice",
    for_trainer: "For {trainer}",
    interaction_types: "Interaction Types",
    outcomes: "Outcomes",
    characters: "Characters",
    estimated_time: "Estimated time",
    steps_count: "{count} steps",
    no_quests: "No quests available for this trainer",

    // Narrative display
    mission: "Mission",
    your_role: "Your Role",
    setting: "Setting",
    story_context: "Story",
    progress: "Progress",
    step_of: "Step {current} of {total}",
    narrative_state: "Your Status",
    risk: "Risk",
    time_remaining: "Time Remaining",
    team_trust: "Team Trust",
    client_trust: "Client Trust",
    evidence_quality: "Evidence Quality",
    decision_quality: "Decision Quality",

    // Consequences
    consequences: "Consequences",
    consequence_applied: "Changes to your status",
    risk_increased: "Risk increased by {value}",
    risk_decreased: "Risk decreased by {value}",
    trust_gained: "Trust gained",
    trust_lost: "Trust lost",

    // Step types
    step_single_choice: "Choose one option",
    step_multiple_choice: "Select all that apply",
    step_free_text: "Write your response",
    step_ordering: "Arrange in correct order",
    step_matching: "Match the pairs",
    step_evidence_select: "Select relevant evidence",
    step_decision: "Make a decision",
    step_dialogue: "Respond to character",
    step_branching: "Choose your path",

    // Single choice
    select_one: "Select one option",

    // Multiple choice
    select_multiple: "Select all that apply",
    min_select: "Select at least {n}",
    max_select: "Select up to {n}",

    // Free text
    write_answer: "Write your answer",
    answer_placeholder: "Type your answer here...",
    min_length: "Minimum {n} characters",
    remaining_chars: "{n} characters remaining",

    // Ordering
    drag_to_reorder: "Drag items to reorder",
    item_up: "Move up",
    item_down: "Move down",

    // Matching
    match_pairs: "Match items from left to right",

    // Evidence select
    select_evidence: "Select the evidence you need",

    // Dialogue
    character_says: "{character} says:",
    write_response: "Write your response",

    // Decision
    make_decision: "Choose your decision",
    decision_warning: "This decision will affect your quest outcome",

    // Evaluation
    submitting: "Submitting your answer...",
    evaluating: "AI is evaluating your response...",
    evaluating_desc: "This may take up to 45 seconds",
    evaluation_complete: "Evaluation complete",
    evaluation_failed: "Evaluation failed",
    evaluation_timed_out: "Evaluation took longer than expected",
    evaluation_timed_out_desc: "Your answer has been saved. You can retry evaluation.",
    retry_evaluation: "Retry Evaluation",
    answer_saved: "Your answer has been saved",
    score: "Score: {score}/{max}",
    correct: "Correct!",
    incorrect: "Not quite right",
    partial: "Partially correct",
    feedback: "Feedback",

    // Outcome
    quest_complete: "Quest Complete!",
    outcome: "Outcome",
    view_debrief: "View Educational Debrief",

    // Debrief
    debrief_title: "Educational Debrief",
    strengths: "Your Strengths",
    mistakes: "Areas for Improvement",
    missed_risks: "Risks You Missed",
    decision_consequences: "How Your Decisions Mattered",
    professional_recommendation: "Professional Recommendation",
    practical_takeaways: "Practical Takeaways",
    skill_profile: "Your Skill Profile",
    suggested_next_practice: "Suggested Next Practice",
    skill_level_practiced: "Practiced",
    skill_level_observed: "Observed",
    recommended_next: "Recommended Next Quest",

    // Actions
    next_step: "Next Step",
    complete_quest: "Complete Quest",
    back_to_catalog: "Back to Quest Catalog",
    try_again: "Try Again",

    // Errors
    error_starting: "Could not start quest",
    error_submitting: "Could not submit answer",
    error_loading: "Could not load quest",
    quest_not_found: "Quest not found",
    session_not_found: "Session not found",
    invalid_step: "Invalid step",

    // Feedback keys
    result_correct: "That's correct!",
    result_incorrect: "That's not quite right.",
    result_partial: "You got some of them right.",
    result_no_answer: "Please provide an answer.",
    result_no_correct_defined: "No correct answer configured.",
    result_no_items: "No items to order.",
    result_no_mappings: "No mappings defined.",
    result_no_evidence: "No evidence items available.",
    result_ordering_correct: "Perfect order!",
    result_ordering_partial: "Some items are in the right position.",
    result_ordering_incorrect: "The order needs work.",
    result_matching_correct: "All pairs matched correctly!",
    result_matching_partial: "Some pairs are correct.",
    result_matching_incorrect: "The pairings are not correct.",
    result_evidence_correct: "You selected the right evidence!",
    result_evidence_partial: "Some evidence choices need review.",
    result_decision_made: "Decision recorded.",
    result_branch_selected: "Path chosen.",
    result_ai_evaluated: "Your response has been evaluated.",
    result_ai_needs_improvement: "Your response needs more development.",
    result_ai_timeout: "Evaluation timed out. Your answer is saved.",
    result_ai_failed: "Evaluation failed. Your answer is saved.",
  },

  // ---------------------------------------------------------------------------
  // QA Payment Defect Quest
  // ---------------------------------------------------------------------------
  "quest.qa.payment_defect": {
    title: "Critical Payment Defect Before Release",
    summary: "A customer reports that payments fail intermittently. You have 40 minutes before the release. Make the right decisions.",
    role: "QA Engineer",
    mission: "Investigate the payment defect and make a release decision with 40 minutes until deployment.",
    setting: "You are the only QA engineer on duty. A critical release is scheduled in 40 minutes. Customer support reports that users are experiencing intermittent payment failures. The development team is waiting for your assessment.",

    characters: {
      pm: "Alex (Product Manager)",
      pm_role: "Wants to release on time — pressure is high",
      dev: "Maria (Developer)",
      dev_role: "Wrote the payment module — may be defensive",
      support: "Dmitry (Customer Support)",
      support_role: "Has collected user reports — wants answers fast",
      payment_spec: "Ivan (Payment Specialist)",
      payment_spec_role: "Understands the payment gateway — technical expert",
    },

    // Step 1: Single choice
    step01: {
      context: "You get a Slack message from customer support: 'Users are reporting payment failures on checkout — intermittent, about 15% of transactions. The release is in 40 minutes. What do you do first?'",
      prompt: "What is your FIRST action?",
      opt_check_logs: "Check payment gateway logs for error patterns",
      opt_call_meeting: "Call an emergency meeting with the full team",
      opt_ask_repro: "Ask support for detailed reproduction steps",
      opt_escalate: "Escalate immediately to the engineering director",
    },

    // Step 2: Evidence selection
    step02: {
      context: "The payment team shares several data sources. You need to identify which evidence is relevant to the investigation.",
      prompt: "Select the evidence items that are relevant to your investigation:",
      ev_payment_logs: "Payment gateway error logs (last 2 hours)",
      ev_deploy_notes: "Recent deployment notes for the payment module",
      ev_browser_logs: "Browser console logs from the user's machine",
      ev_transaction_db: "Transaction database query results",
      ev_uptime: "Server uptime report from DevOps",
      ev_error_reports: "Customer error report summaries",
      ev_wifi: "Office WiFi connection logs",
    },

    // Step 3: Ordering
    step03: {
      context: "You've collected initial evidence. Now plan your investigation steps in the correct professional order.",
      prompt: "Arrange the investigation steps in the correct order:",
      item_reproduce: "Reproduce the issue in staging environment",
      item_check_logs: "Check payment gateway error logs for patterns",
      item_identify: "Identify affected transaction types and user segments",
      item_severity: "Determine severity and business impact",
      item_communicate: "Communicate findings to the team",
    },

    // Step 4: Decision
    step04: {
      context: "Your investigation reveals that a recent deployment introduced a race condition in the payment callback handler. It affects ~15% of transactions. The product manager asks: 'Can we still release?'",
      prompt: "What is your decision?",
      opt_block: "Block the release — defect is critical for payments",
      opt_monitor: "Release with monitoring — rollback if errors increase",
      opt_delay: "Delay release for deeper analysis and targeted fix",
    },

    // Step 5: Free text — Bug report
    step05: {
      context: "The team accepts your decision. Now write a professional bug report for the payment defect so the developer can fix it.",
      prompt: "Write a detailed bug report with all required fields, steps to reproduce, environment details, severity, and priority classification.",
      placeholder: "Write your bug report here...",
      guidance: "Include: title, description, environment, steps to reproduce, actual vs expected result, severity, priority.",
    },

    // Step 6: Dialogue
    step06: {
      context: "The product manager approaches you: 'I understand the risk, but the VP is asking why we can't release. Can you explain the situation to me?'",
      prompt: "How do you respond to the product manager?",
      character_says: "Alex (PM): 'I know you recommended blocking, but I need to explain this to the VP. What exactly is the risk, and is there any safe path forward?'",
      opt_explain_risk: "Explain the race condition clearly with data — show why it's critical",
      opt_compromise: "Suggest a compromise: release with the fix delayed but with feature flag",
      opt_stand_firm: "Stand firm — explain that payment reliability is non-negotiable",
    },

    // Rubric
    rubric: {
      structure: "Bug report structure and required fields",
      severity: "Severity and priority classification",
      reproduction: "Quality of reproduction steps",
      environment: "Environment details completeness",
      eval_prompt: "Evaluate the QA engineer's bug report for completeness, structure, severity classification, and reproduction steps.",
      system_prompt: "You are an expert QA lead evaluating a bug report written by a QA engineer in a release-critical situation.",
    },

    // Learning objectives
    lo: {
      triage: "Prioritize investigation steps under time pressure",
      evidence: "Select relevant evidence from multiple data sources",
      investigation: "Follow a structured investigation process",
      decision: "Make a risk-based release decision",
      bug_report: "Write a clear, complete bug report",
      communication: "Communicate technical findings to stakeholders",
    },

    // Outcomes
    outcome: {
      success: {
        title: "Release Successfully Blocked — Defect Found",
        summary: "You correctly identified the critical payment defect, communicated the risk effectively, and prevented a production incident. Your bug report will help the team fix the issue before the next release window.",
      },
      partial: {
        title: "Partial Success — Defect Identified, Communication Needs Work",
        summary: "You identified the payment issue but your decisions or communication could have been stronger. Review the debrief for specific areas to improve.",
      },
      failure: {
        title: "High Risk — Payment Defect Could Reach Production",
        summary: "Your investigation and decisions left significant risk unaddressed. Review the debrief to understand what went wrong and how to handle similar situations in the future.",
      },
    },
  },

  // ---------------------------------------------------------------------------
  // BA Payment Requirements Conflict Quest
  // ---------------------------------------------------------------------------
  "quest.ba.payment_conflict": {
    title: "Conflicting Requirements for a Payment Feature",
    summary: "Stakeholders disagree on requirements for a new payment feature. Resolve conflicts, write acceptance criteria, and defend your decisions.",
    role: "Business Analyst",
    mission: "Analyze conflicting stakeholder requirements for a payment feature and produce clear, balanced acceptance criteria.",
    setting: "Your company is building a new payment feature for the platform. Four key stakeholders have different priorities and expectations. The project timeline is tight, and the stakeholders are growing impatient.",
    characters: {
      po: "Elena (Product Owner)",
      po_role: "Wants fast delivery — prioritize speed to market",
      compliance: "Sergei (Compliance Specialist)",
      compliance_role: "Requires full regulatory compliance — no shortcuts",
      tech_lead: "Mikhail (Technical Lead)",
      tech_lead_role: "Concerned about scalability and architecture",
      customer: "Anna (Customer Representative)",
      customer_role: "Wants the feature to be user-friendly and intuitive",
    },

    step01: {
      context: "The project kickoff reveals four stakeholders with conflicting priorities for the payment feature. Before proceeding, you need to identify who the actual stakeholders are.",
      prompt: "Select ALL the stakeholders who should be involved in requirements for the payment feature:",
      opt_po: "Product Owner (Elena)",
      opt_compliance: "Compliance Specialist (Sergei)",
      opt_tech_lead: "Technical Lead (Mikhail)",
      opt_customer: "Customer Representative (Anna)",
      opt_office_mgr: "Office Manager",
      opt_intern: "Intern Designer",
      opt_cfo: "CFO",
      opt_marketing: "Marketing Social Media Manager",
    },

    step02: {
      context: "Now match each stakeholder to their primary concern or risk area for the payment feature.",
      prompt: "Match each stakeholder to their primary concern:",
      left_po: "Product Owner",
      left_compliance: "Compliance Specialist",
      left_tech: "Technical Lead",
      left_customer: "Customer Representative",
      right_speed: "Time to market",
      right_security: "Regulatory compliance",
      right_scalability: "System architecture",
      right_usability: "User experience",
    },

    step03: {
      context: "Before resolving the conflicts, you need to follow a structured requirements analysis process.",
      prompt: "Arrange the requirements analysis steps in the correct order:",
      item_gather: "Gather input from all stakeholders",
      item_conflicts: "Identify conflicting requirements",
      item_impact: "Analyze impact of each requirement",
      item_solution: "Propose compromise solution",
      item_validate: "Validate solution with stakeholders",
      item_document: "Document final requirements",
    },

    step04: {
      context: "The Product Owner wants fast delivery with basic payment support. Compliance insists on full PCI-DSS certification before launch. The Tech Lead is concerned about scaling to 10K TPS. The Customer Rep wants a smooth UX.",
      prompt: "How do you resolve this conflict?",
      opt_workshop: "Facilitate a structured workshop to find a balanced approach",
      opt_prioritize_po: "Prioritize the Product Owner — deliver fast, add compliance later",
      opt_escalate: "Escalate to project sponsor for a top-down decision",
    },

    step05: {
      context: "After the workshop, stakeholders agree on a phased approach. Now write an acceptance criterion for the first phase that balances the key concerns.",
      prompt: "Write a clear acceptance criterion for the payment feature's first phase. It should address the key concerns: transaction processing, compliance basics, and usability.",
      placeholder: "Write your acceptance criterion here...",
      guidance: "Use the Given/When/Then format or a structured business rule. Address: what happens when a payment is submitted, how errors are handled, what compliance checks run, and how the user is informed.",
    },

    step06: {
      context: "The Product Owner reads your acceptance criterion and asks: 'This seems to add a lot of checks. Won't this slow us down?'",
      prompt: "Defend your acceptance criterion professionally, explaining why these checks are necessary.",
      character_says: "Elena (PO): 'I see you've added compliance checks, fallback handling, and retry logic. Won't this significantly delay our first release? How do you justify it?'",
      placeholder: "Write your response to Elena...",
      guidance: "Explain the business value of each requirement. Address the trade-off between speed and quality. Propose a practical implementation approach.",
    },

    rubric: {
      structure: "Acceptance criterion structure and clarity",
      balance: "Balance of stakeholder concerns",
      testability: "Testability and precision of the criterion",
      business_value: "Business value justification",
      clarity: "Clarity of argument and structure",
      empathy: "Stakeholder empathy and understanding",
      tone: "Professional tone and communication",
      solution: "Solution-oriented approach",
      eval_prompt: "Evaluate the business analyst's acceptance criterion for structure, stakeholder balance, testability, and business value.",
      eval_prompt_dialogue: "Evaluate the business analyst's response to the Product Owner for clarity, stakeholder empathy, professional tone, and solution orientation.",
      system_prompt: "You are an experienced BA mentor evaluating a junior business analyst's work in a requirements conflict scenario.",
      system_prompt_dialogue: "You are an experienced BA mentor evaluating a junior BA's stakeholder communication.",
    },

    lo: {
      stakeholders: "Identify relevant project stakeholders",
      stakeholder_interests: "Map stakeholders to their interests and concerns",
      analysis_process: "Follow a structured requirements analysis process",
      conflict_resolution: "Resolve stakeholder conflicts professionally",
      acceptance_criteria: "Write clear, balanced acceptance criteria",
      communication: "Defend requirements decisions to stakeholders",
    },

    outcome: {
      success: {
        title: "Conflicts Resolved — Balanced Requirements Approved",
        summary: "You successfully navigated the stakeholder conflicts, produced balanced acceptance criteria, and defended your decisions professionally. Your approach balances business speed, compliance, scalability, and user experience.",
      },
      partial: {
        title: "Partial Success — Requirements Drafted, Gaps Remain",
        summary: "You made progress on the requirements but some stakeholder concerns remain unaddressed. Review the debrief to identify which areas need more attention.",
      },
      failure: {
        title: "Stakeholder Conflict Unresolved — Requirements at Risk",
        summary: "The stakeholder conflicts remain largely unresolved. Your acceptance criteria do not adequately address the key concerns. Review the debrief for guidance on improving stakeholder analysis and requirements documentation.",
      },
    },
  },

  // ---------------------------------------------------------------------------
  // QA Bug Report Structure Quest
  // ---------------------------------------------------------------------------
  "quest.qa.bug_report": {
    title: "Bug Report Structure",
    summary: "Test your knowledge of proper bug report structure: required fields, severity vs priority, and writing a professional bug report.",
    role: "QA Engineer",
    mission: "Demonstrate your understanding of bug report structure and write a professional bug report based on provided evidence.",
    setting: "You are a QA Engineer on an e-commerce platform using JIRA for bug tracking. The QA team values well-structured bug reports as they work with distributed teams across time zones. The QA Lead asked you to verify your knowledge.",
    characters: {
      lead: "Alex (QA Lead)",
      lead_role: "Wants to make sure the team writes quality bug reports",
    },
    step01: {
      context: "The QA Lead asks: 'What fields are mandatory in a well-written bug report?'",
      prompt: "Select ALL required fields of a professional bug report:",
      opt_title: "Title (brief problem description)",
      opt_description: "Description (detailed explanation)",
      opt_environment: "Environment (OS, browser, app version)",
      opt_steps: "Steps to Reproduce",
      opt_actual: "Actual Result",
      opt_expected: "Expected Result",
      opt_severity: "Severity (system impact)",
      opt_priority: "Priority (business urgency)",
      opt_assignee: "Assignee Name",
      opt_sprint: "Sprint Name",
      opt_estimate: "Developer Estimate in hours",
    },
    step02: {
      context: "Great! Now arrange the bug report fields in the correct logical sequence.",
      prompt: "Arrange the bug report fields in the correct order:",
      item_title: "Title",
      item_env: "Environment",
      item_precond: "Preconditions",
      item_steps: "Steps to Reproduce",
      item_actual: "Actual Result",
      item_expected: "Expected Result",
      item_attach: "Attachments (screenshots, logs)",
    },
    step03: {
      context: "The QA Lead asks: 'How do you differentiate Severity from Priority?'",
      prompt: "Select the correct definition:",
      opt_severity: "Severity is system impact (how bad), Priority is business urgency (how soon to fix)",
      opt_urgency: "Severity is urgency to fix, Priority is system impact",
      opt_same: "Severity and Priority are the same thing",
    },
    step04: {
      context: "Here is a fragment of a poorly written bug report from an intern. Find all the defects:",
      prompt: "Select all issues you can identify in this bug report:",
      ev_missing_env: "Missing environment information",
      ev_vague_steps: "Steps to reproduce are too vague",
      ev_no_expected: "Expected result is missing",
      ev_subjective: "Subjective language ('seems like', 'possibly')",
      ev_missing_severity: "Severity is not specified",
      ev_good_title: "Title is well written (not an issue)",
      ev_correct_format: "Format follows standards (not an issue)",
    },
    step05: {
      context: "Apply your knowledge from previous steps and write a professional bug report:",
      prompt: "Write a bug report for the following issue: 'User reports that after updating to version 2.5.1, the 'Place Order' button in Chrome 120 does not respond to clicks. Before the update everything worked. OS: Windows 11. Other browsers work correctly.'",
      placeholder: "Write your bug report here...",
      guidance: "Include: title, environment, steps to reproduce, actual result, expected result, severity and priority with justification.",
    },
    outcome: {
      excellent: {
        title: "Excellent Knowledge of Bug Report Structure!",
        summary: "You demonstrated deep understanding of all aspects of a professional bug report: from required fields to writing clear reproduction steps.",
      },
      good: {
        title: "Good Knowledge of Bug Report Structure",
        summary: "You have a solid foundation. Pay attention to details: environment, severity/priority, and clarity of wording.",
      },
      needs_practice: {
        title: "Needs Practice",
        summary: "Review bug report structure, required fields, and the difference between severity and priority.",
      },
    },
    rubric: {
      structure: "Bug report structure and completeness",
      severity: "Severity and Priority",
      reproduction: "Steps to reproduce",
      environment: "Environment details",
      eval_prompt: "Evaluate the bug report quality by criteria: correct structure (all required fields), correct severity and priority classification, clarity of reproduction steps, completeness of environment information.",
      system_prompt: "You are a QA Lead evaluating bug report quality. Evaluate strictly but constructively. Point out what was done well and what can be improved.",
    },
    lo: {
      fields: "Know required fields of a bug report",
      structure: "Understand logical bug report structure",
      severity_priority: "Differentiate severity and priority",
      evidence: "Identify problems in bug reports",
      artifact: "Write professional bug reports",
    },
  },

  // ---------------------------------------------------------------------------
  // Quest debrief strings
  // ---------------------------------------------------------------------------
  "quest.debrief": {
    strength_decision_quality: "Strong decision-making — you evaluated options carefully",
    strength_evidence_quality: "Thorough evidence collection and analysis",
    strength_team_trust: "Maintained good working relationships with the team",
    strength_client_trust: "Kept client interests in focus",
    mistake_decision_quality: "Decision-making could be more systematic",
    mistake_evidence_quality: "Evidence collection could be more thorough",
    risk_high: "Risk escalated to concerning levels during the quest",
    time_low: "Time management needs attention — you ran low on time",
  },
};

export default en;
