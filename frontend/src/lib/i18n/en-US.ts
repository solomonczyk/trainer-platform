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
    showPassword: "Show password",
    hidePassword: "Hide password",
    passwordPlaceholder: "At least 6 characters",
    confirmPasswordPlaceholder: "Repeat password",
    // Email verification
    verifyEmailCheckTitle: "Check Your Email",
    verifyEmailCheckDesc: "We sent a verification link to your email address. Please click the link to verify your account and access the simulator.",
    verifyEmailVerifying: "Verifying your email...",
    verifyEmailSuccessTitle: "Email Verified!",
    verifyEmailSuccessDesc: "Your email has been verified. Redirecting to the simulator...",
    verifyEmailAlreadyTitle: "Already Verified",
    verifyEmailAlreadyDesc: "This email has already been verified. Please log in.",
    verifyEmailExpiredTitle: "Link Expired",
    verifyEmailExpiredDesc: "This verification link has expired. Enter your email below to receive a new one.",
    verifyEmailResendButton: "Resend Email",
    verifyEmailResendCooldown: "Wait {seconds}s before resending",
    verifyEmailCheckStatus: "I've Verified — Check Status",
    verifyEmailBackToLogin: "Back to Login",
    verifyEmailSentTitle: "Email Sent!",
    verifyEmailSentDesc: "A new verification link has been sent. Please check your inbox and spam folder.",
    verifyEmailResendPrompt: "Didn't receive the email?",
    verifyEmailCheckInbox: "Please open the link in the email we sent you.",
    verifyEmailSpamHint: "Check your spam folder if you don't see it.",
    verificationRequiredTitle: "Email Verification Required",
    verificationRequiredDesc: "Please verify your email address before accessing the simulator. Check your inbox for the verification link.",
    resendVerificationButton: "Resend Verification Email",
    verificationResent: "Verification email sent. Please check your inbox.",
    backToLogin: "Back to Login",
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
    notEnrolled: {
      title: "Access Required",
      description: "You need to enroll in this trainer before you can access this content.",
      action: "Back to Trainer",
    },
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
    activity_label_one: "question",
    activity_label_few: "questions",
    activity_label_many: "questions",
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

    // Short trainer abbreviations
    short_qa: "QA",
    short_ba: "BA",

    // Collapsible module list
    show_less_modules: "Show fewer modules",
    show_n_modules: "Show all {n} modules",

    // Interaction type badges
    activity_type_single_choice: "Single Choice",
    activity_type_multiple_choice: "Multiple Choice",
    activity_type_matching: "Matching",
    activity_type_ordering: "Ordering",
    activity_type_evidence_select: "Evidence Select",
    activity_type_free_text: "Free Text",
    activity_type_fill_blanks: "Fill Blanks",
    activity_type_numeric: "Numeric",
  },

  // BA HR screening question titles (top-level keys, used directly as t(key))
  ba_hr_q1_title: "What sections should a BA resume include?",

  // Module title/description translations (root-level dotted keys, resolved via t())
  "modules.ba_hr_screening.title": "HR Screening & Self-Presentation",
  "modules.ba_hr_screening.description": "HR questions, self-presentation, motivation, salary expectations",
  "modules.ba_basics_stakeholders.title": "BA Basics & Stakeholders",
  "modules.ba_basics_stakeholders.description": "Role of BA, BABOK, stakeholder types, RACI matrix",
  "modules.ba_requirements_elicitation.title": "Requirements Elicitation & Analysis",
  "modules.ba_requirements_elicitation.description": "Elicitation techniques, requirements analysis, validation",
  "modules.ba_documentation_artifacts.title": "Documentation & Artifacts",
  "modules.ba_documentation_artifacts.description": "User stories, Use cases, BRD, SRS, Acceptance criteria",
  "modules.ba_process_data_modeling.title": "Process & Data Modeling",
  "modules.ba_process_data_modeling.description": "BPMN, UML, ERD, Data Flow Diagrams, Event Storming",
  "modules.ba_methodologies.title": "Methodologies",
  "modules.ba_methodologies.description": "Scrum, Kanban, SAFe, Waterfall, methodology comparison",
  "modules.ba_metrics_prioritization.title": "Metrics, Estimation & Prioritization",
  "modules.ba_metrics_prioritization.description": "MoSCoW, Kano, WSJF, Story Points, ROI, NPV",
  "modules.ba_communication_conflict.title": "Communication & Conflict",
  "modules.ba_communication_conflict.description": "Facilitation, negotiation, expectation management, conflict resolution",
  "modules.ba_technical_aspects.title": "Technical Aspects (SQL, API, Prototypes)",
  "modules.ba_technical_aspects.description": "SQL queries, REST API, JSON, prototyping, architecture",
  "modules.ba_real_cases.title": "Real-World Case Studies",
  "modules.ba_real_cases.description": "Complex scenarios with full analysis cycle",

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
    step_single_choice: "Single Choice",
    step_multiple_choice: "Multiple Choice",
    step_free_text: "Free Text",
    step_ordering: "Ordering",
    step_matching: "Matching",
    step_evidence_select: "Evidence Select",
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
    feedback_why: "Why?",
    feedback_correct_approach: "Correct approach",
    feedback_takeaway: "Takeaway",
    feedback_continue: "Continue",

    next_step: "Next Step",
    complete_quest: "Complete Quest",
    back_to_catalog: "Back to Quest Catalog",
    try_again: "Try Again",

    // Navigation within quest
    previous_step: "Previous Step",
    next_step_button: "Next Step",

    // Character prompts
    choose_response: "Choose a response:",

    // Text input hints
    min_characters: "Minimum {n} characters",
    characters_remaining: "{n} characters remaining",

    // Badges
    ai_evaluated: "AI Evaluated",

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
      feedback_incorrect: "Logs are the first data source when troubleshooting failures. Meetings or escalation without data only waste time and increase panic.",
      feedback_correct_approach: "First, check the payment gateway logs — this reveals whether there's a systematic error, its frequency, and likely root cause. Only after collecting data should you call the team.",
      feedback_reinforcement: "A professional QA engineer starts with data, not meetings. Gateway logs are the primary source of truth for payment failures.",
      feedback_takeaway: "When you receive a defect report, first check available data (logs, metrics), then gather the team.",
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
      feedback_missing: "Not all selected items are relevant, or you missed important sources. Browser logs, uptime reports, and WiFi logs won't help find a payment defect.",
      feedback_correct_approach: "Relevant sources: payment gateway logs, deployment notes, transaction database, and customer error reports. They are directly related to the payment process.",
      feedback_reinforcement: "You correctly identified the relevant sources. A good QA engineer focuses on data directly tied to the problem, ignoring noise.",
      feedback_takeaway: "When investigating a defect, choose sources directly connected to the affected system. Operational and infrastructure data rarely help find a logic error.",
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
      feedback_incorrect: "Order matters in an investigation. You can't determine severity before reproducing, and you communicate only after full analysis.",
      feedback_correct_approach: "Correct order: reproduce → check logs → identify affected segments → assess severity → communicate. Each step builds on the previous one's findings.",
      feedback_reinforcement: "A structured investigation approach is a key QA skill. You built a logical sequence from reproduction through to communication.",
      feedback_takeaway: "Any investigation follows this principle: first reproduce, collect data, analyze impact, then communicate the result.",
    },

    // Step 4: Decision
    step04: {
      context: "Your investigation reveals that a recent deployment introduced a race condition in the payment callback handler. It affects ~15% of transactions. The product manager asks: 'Can we still release?'",
      prompt: "What is your decision?",
      opt_block: "Block the release — defect is critical for payments",
      opt_monitor: "Release with monitoring — rollback if errors increase",
      opt_delay: "Delay release for deeper analysis and targeted fix",
      feedback_incorrect: "A payment defect affecting 15% of transactions is a critical risk. Monitoring won't prevent financial losses and customer trust damage.",
      feedback_correct_approach: "A race condition in payments is a Critical severity defect. Blocking the release is the only professional decision that protects customers and the business.",
      feedback_reinforcement: "Correct decision. Blocking the release on a critical payment defect demonstrates QA maturity and understanding of business risk.",
      feedback_takeaway: "Critical defects in payment functionality require release blocking. Payment reliability is not a compromise.",
    },

    // Step 5a: Multiple choice — Select required bug report fields
    step05a: {
      context: "The team accepts your decision. Now assemble a professional bug report for the payment defect.",
      prompt: "Select ALL the fields that a professional bug report MUST contain:",
      opt_title: "Title",
      opt_environment: "Environment (OS, browser, app version)",
      opt_preconditions: "Preconditions",
      opt_steps: "Steps to Reproduce",
      opt_actual: "Actual Result",
      opt_expected: "Expected Result",
      opt_severity: "Severity & Priority classification",
      opt_evidence: "Evidence / Attachments (logs, screenshots)",
      opt_impact: "Impact assessment",
      opt_assignee: "Assignee name",
      opt_sprint: "Sprint name",
      feedback_missing: "You didn't select all required fields or selected extra ones. Assignee name and sprint name are JIRA task fields, not bug report fields.",
      feedback_correct_approach: "Required fields: title, environment, preconditions, steps, actual result, expected result, severity/priority, evidence, impact assessment. Everything needed to understand and reproduce the bug.",
      feedback_reinforcement: "Excellent! You selected all key fields of a professional bug report. A good bug report contains everything needed to reproduce and prioritize the defect.",
      feedback_takeaway: "A bug report should answer: what, where, under what conditions, how to reproduce, what was expected, and how serious it is.",
    },
    // Step 5b: Single choice — Classify severity and priority
    step05b: {
      context: "Based on your investigation, classify the payment defect correctly.",
      prompt: "What is the correct classification for this payment defect?",
      opt_critical_critical: "Severity = Critical — payment failures block core transactions; Priority = Critical — fix before next release",
      opt_major_high: "Severity = Major — significant functionality broken; Priority = High — fix in next sprint",
      opt_minor_low: "Severity = Minor — cosmetic or edge case; Priority = Low — fix when time permits",
      feedback_incorrect: "A payment defect causing 15% transaction failures is Critical, not Major or Minor. It blocks core business operations.",
      feedback_correct_approach: "Race condition in the payment handler with 15% transaction loss — Severity Critical (data/money loss) and Priority Critical (fix before next release).",
      feedback_reinforcement: "Correct! Severity Critical — because the defect causes transaction loss (financial impact). Priority Critical — because it affects a core business function.",
      feedback_takeaway: "Severity = system impact (how bad). Priority = business urgency (how soon). Payments are always critical.",
    },
    // Step 5c: Short optional free text — Bug report title
    step05c: {
      context: "A professional bug report includes all selected fields with clear, concise information.",
      prompt: "Write a short, clear bug report title (1-2 sentences):",
      placeholder: "Optional: enter a concise bug report title...",
    },

    // Step 6: Dialogue
    step06: {
      context: "The product manager approaches you: 'I understand the risk, but the VP is asking why we can't release. Can you explain the situation to me?'",
      prompt: "How do you respond to the product manager?",
      character_says: "Alex (PM): 'I know you recommended blocking, but I need to explain this to the VP. What exactly is the risk, and is there any safe path forward?'",
      opt_explain_risk: "Explain the race condition clearly with data — show why it's critical",
      opt_compromise: "Suggest a compromise: release with the fix delayed but with feature flag",
      opt_stand_firm: "Stand firm — explain that payment reliability is non-negotiable",
      feedback_incorrect: "Communicating with a PM requires more than firmness — it needs data-backed arguments. Explain the business impact so the PM can convey the risk to the VP.",
      feedback_correct_approach: "The best response is to explain the race condition in business terms: what percentage of transactions are affected, how much money is at risk, and why this isn't a compromise.",
      feedback_reinforcement: "Great communication! You explained a technical problem through business risks. That's how QA engineers talk to management.",
      feedback_takeaway: "Speak to management in business language: losses, risks, customer impact. Technical details come after you've shown the big picture.",
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
      feedback_missing: "You incorrectly identified the stakeholders. Office manager, intern, and marketing are not involved in payment feature requirements.",
      feedback_correct_approach: "Key stakeholders: Product Owner, Compliance, Technical Lead, Customer Representative, and CFO. Each has a stake in the payment feature.",
      feedback_reinforcement: "Great! You correctly identified all stakeholders involved in payment feature requirements.",
      feedback_takeaway: "Stakeholders are those with an interest or influence over the outcome. Not every project participant is a stakeholder for requirements.",
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
      feedback_missing: "Some pairs are matched incorrectly. Each stakeholder has a primary area of responsibility that determines their project interest.",
      feedback_correct_approach: "Product Owner → Time to market. Compliance → Regulatory compliance. Tech Lead → System architecture. Customer Rep → User experience.",
      feedback_reinforcement: "Correct! You matched stakeholders to their primary concerns well. Understanding each stakeholder's motivation is key to resolving conflicts.",
      feedback_takeaway: "Each stakeholder has their own priorities. The BA's job is to understand them and find balance, not pick sides.",
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
      feedback_incorrect: "The requirements analysis order is wrong. You can't propose a solution before gathering data, and you shouldn't document before validation.",
      feedback_correct_approach: "Correct sequence: gather → identify conflicts → analyze impact → propose solution → validate → document. Each step builds on the previous one.",
      feedback_reinforcement: "Excellent! You know the correct requirements analysis process. Documentation is the last step, after validation.",
      feedback_takeaway: "Requirements analysis is an iterative process: first understand the problem, find solutions, validate, and only then formalize.",
    },

    step04: {
      context: "The Product Owner wants fast delivery with basic payment support. Compliance insists on full PCI-DSS certification before launch. The Tech Lead is concerned about scaling to 10K TPS. The Customer Rep wants a smooth UX.",
      prompt: "How do you resolve this conflict?",
      opt_workshop: "Facilitate a structured workshop to find a balanced approach",
      opt_prioritize_po: "Prioritize the Product Owner — deliver fast, add compliance later",
      opt_escalate: "Escalate to project sponsor for a top-down decision",
      feedback_incorrect: "Picking one side in a stakeholder conflict or escalating is not the best BA strategy. The analyst's role is to find a balanced solution.",
      feedback_correct_approach: "The best approach is a structured workshop where each stakeholder voices priorities and the group finds a compromise. The BA acts as facilitator.",
      feedback_reinforcement: "Correct! A structured workshop is a professional BA tool for resolving conflicts. You facilitate dialogue rather than pick sides.",
      feedback_takeaway: "A BA should not choose between stakeholders. The goal is to create space for dialogue and find a solution that addresses key concerns of all parties.",
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
      feedback_missing: "You didn't select all required fields or added extra ones. Assignee name, sprint, and estimate are task-tracking fields, not bug report fields.",
      feedback_correct_approach: "Required fields: title, description, environment, steps to reproduce, actual result, expected result, severity, priority.",
      feedback_reinforcement: "Excellent! You know all required fields of a professional bug report. A good bug report contains everything needed to reproduce and prioritize.",
      feedback_takeaway: "A bug report should let a developer reproduce the issue and understand its severity. Administrative fields are not needed for that.",
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
      feedback_incorrect: "The logical sequence is wrong. Start with context (environment, preconditions), then steps, results, and finally attachments.",
      feedback_correct_approach: "Correct order: title → environment → preconditions → steps → actual result → expected result → attachments. The reader goes from general to specific.",
      feedback_reinforcement: "Correct! The bug report is structured from context through reproduction to results — following the logic of an investigation.",
      feedback_takeaway: "A good bug report guides the reader from context through reproduction to results. The sequence helps quickly understand the issue.",
    },
    step03: {
      context: "The QA Lead asks: 'How do you differentiate Severity from Priority?'",
      prompt: "Select the correct definition:",
      opt_severity: "Severity is system impact (how bad), Priority is business urgency (how soon to fix)",
      opt_urgency: "Severity is urgency to fix, Priority is system impact",
      opt_same: "Severity and Priority are the same thing",
      feedback_incorrect: "Severity and Priority are different metrics. Severity = system impact; Priority = business urgency. Do not confuse them.",
      feedback_correct_approach: "Severity measures technical impact (how bad), Priority measures business urgency (how soon to fix). A Critical bug can have Low priority if it's in a rarely-used feature.",
      feedback_reinforcement: "Correct! Severity = technical impact, Priority = business urgency. Understanding the difference is a fundamental QA skill.",
      feedback_takeaway: "Severity (impact) and Priority (urgency) are independent metrics. A bug can be Minor severity but High priority, or vice versa.",
    },
    step04: {
      context: "Here is a fragment of a poorly written bug report from an intern. Find all the defects:",
      prompt: "Select all issues you can identify in this bug report:",
      panel: "Title: Place Order button not working\n\nSteps to Reproduce:\n1. Go to the website\n2. Try to place an order\n3. The button seems like it doesn't respond sometimes\n\nActual Result:\nThe button possibly does nothing when you click it. I tried a few times and sometimes it works.\n\nExpected Result:\n(not specified)\n\nEnvironment:\n(not specified)\n\nSeverity:\n(not specified)\n\nPriority:\n(not specified)\n\nAttachments:\n(none)",
      ev_missing_env: "Missing environment information",
      ev_vague_steps: "Steps to reproduce are too vague",
      ev_no_expected: "Expected result is missing",
      ev_subjective: "Subjective language ('seems like', 'possibly')",
      ev_missing_severity: "Severity is not specified",
      ev_good_title: "Title is well written (not an issue)",
      ev_correct_format: "Format follows standards (not an issue)",
      feedback_missing: "You missed some issues or marked things that aren't defects. Carefully check each bug report field.",
      feedback_correct_approach: "Issues: missing environment, vague steps, subjective language, no expected result, no severity/priority. The title and format are fine.",
      feedback_reinforcement: "Great! You identified all the problems correctly. Noticing subjective language is especially important — it makes a bug report unreproducible.",
      feedback_takeaway: "A good bug report is objective and precise. Avoid words like 'seems', 'possibly', 'sometimes'. If unsure, verify again.",
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
  // First quest recommendation
  // ---------------------------------------------------------------------------
  recommended_quest: {
    title: "Recommended First Quest",
    for_qa: "Bug Report Structure",
    for_qa_reason: "You will learn how to identify missing bug report fields, prioritize severity, and write a professional report.",
    for_qa_skills: "Bug report structure, severity vs priority, professional writing",
    for_qa_why: "This quest covers the fundamentals every QA engineer needs: understanding bug report structure, severity vs priority classification, and writing professional reports. It uses multiple question types (multiple choice, ordering, free text) to reinforce learning.",
    for_ba: "Conflicting Requirements for a Payment Feature",
    for_ba_reason: "You will learn how to identify stakeholders, resolve requirements conflicts, and write balanced acceptance criteria.",
    for_ba_skills: "Stakeholder analysis, conflict resolution, acceptance criteria",
    for_ba_why: "This quest introduces core BA skills: stakeholder identification, conflict resolution, requirements prioritization, and writing acceptance criteria. It uses varied interaction types to build practical competence.",
    start_recommended: "Start Recommended Quest",
    browse_all: "Browse All Quests",
    why_this_title: "Why this quest?",
    estimated_time_label: "~{minutes} min",
    steps_label: "{count} steps",
  },

  // ---------------------------------------------------------------------------
  // Mission intro enhancements
  // ---------------------------------------------------------------------------
  mission_intro: {
    skills_trained: "Skills Trained",
    estimated_time: "Estimated Time",
    how_feedback_works: "How Feedback Works",
    how_feedback_desc: "After each answer, you will see whether it is correct or needs improvement, with a detailed explanation and practical takeaway. Review all your results in the final educational debrief.",
    expected_artifact: "Expected Artifact",
    start_mission: "Start Mission",
    skills_list: "Skills you will practice in this quest",
    interaction_types_label: "Interaction Types",
    estimated_time_short: "{minutes} min",
  },

  // ---------------------------------------------------------------------------
  // Feedback enhancements
  // ---------------------------------------------------------------------------
  feedback_details: {
    your_answer: "Your Answer",
    correct_answer: "Correct Answer",
    what_was_missed: "What Was Missed",
    why_explanation: "Why",
    correct_approach: "Correct Approach",
    practical_takeaway: "Practical Takeaway",
    step_result: "Result",
  },

  // ---------------------------------------------------------------------------
  // Mistakes review
  // ---------------------------------------------------------------------------
  mistakes_review: {
    title: "Mistakes Review",
    subtitle: "Review each step to understand what you did well and what can be improved",
    step_label: "Step {number}",
    your_answer: "Your Answer",
    correct_answer: "Correct Answer",
    explanation: "Explanation",
    takeaway: "Takeaway",
    step_n_show: "Show Step {number}",
    step_n_hide: "Hide Step {number}",
    of_total: "Step {current} of {total}",
    score: "Score: {score}%",
    result_correct: "Correct",
    result_partial: "Partially Correct",
    result_incorrect: "Incorrect",
    no_mistakes: "No mistakes to review — great job!",
    back_to_debrief: "Back to Debrief",
  },

  // ---------------------------------------------------------------------------
  // Debrief enhancements
  // ---------------------------------------------------------------------------
  debrief_enhanced: {
    professional_sample: "Professional Example",
    professional_sample_desc: "Here is how a professional would approach this task:",
    skills_summary: "Skills Summary",
    what_to_repeat: "What to Repeat",
    what_to_repeat_desc: "Practice these areas to strengthen your skills:",
    next_quest: "Next Recommended Quest",
    next_quest_reason: "Ready for more? Try this quest next:",
    view_mistakes_review: "View Mistakes Review",
    complete_debrief: "Complete Review",
    final_score: "Final Score",
    quest_skills: "Skills Trained in This Quest",
    no_professional_sample: "Review your results above for guidance on improvement areas.",
  },

  // ---------------------------------------------------------------------------
  // Next action
  // ---------------------------------------------------------------------------
  next_action: {
    title: "What's Next?",
    repeat_weak_topic: "Repeat This Quest",
    repeat_weak_topic_desc: "Review the areas you missed and try again",
    start_next_quest: "Start Next Quest",
    start_next_quest_desc: "Build on your knowledge with a new challenge",
    return_to_catalog: "Return to Catalog",
    return_to_catalog_desc: "Browse all available quests and choose your own path",
    continue_path: "Continue {trainer} Path",
    continue_path_desc: "Continue your training journey with more quests and scenarios",
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
