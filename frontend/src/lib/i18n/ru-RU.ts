// Russian locale strings for Trainer Platform UI

const ru = {
  // App
  app: {
    name: "Trainer Platform",
    tagline: "Платформа профессиональных тренажёров",
    description: "Практикуйтесь и развивайте навыки с AI-оценкой",
  },

  // Navigation
  nav: {
    home: "Главная",
    domains: "Домены",
    myProgress: "Мой прогресс",
    profile: "Профиль",
    admin: "Администрирование",
    login: "Войти",
    register: "Регистрация",
    logout: "Выйти",
  },

  // Landing
  landing: {
    heroTitle: "Готовьтесь к собеседованиям с AI-тренажёром",
    heroSubtitle: "Практикуйте ответы на реальные вопросы, получайте структурированную оценку и отслеживайте прогресс",
    startButton: "Начать обучение",
    features: "Возможности",
    feature1Title: "Реалистичные сценарии",
    feature1Desc: "Сценарии, основанные на реальных вопросах с собеседований",
    feature2Title: "AI-оценка по рубрикам",
    feature2Desc: "Структурированная оценка с критериями, evidence и рекомендациями",
    feature3Title: "Отслеживание прогресса",
    feature3Desc: "Детальный прогресс по навыкам и темам",
    languages: "ru-RU / en-US",
  },

  // Auth
  auth: {
    email: "Email",
    password: "Пароль",
    confirmPassword: "Подтвердите пароль",
    displayName: "Имя",
    loginTitle: "Вход в аккаунт",
    registerTitle: "Регистрация",
    loginButton: "Войти",
    registerButton: "Зарегистрироваться",
    noAccount: "Нет аккаунта?",
    hasAccount: "Уже есть аккаунт?",
    registerLink: "Зарегистрироваться",
    loginLink: "Войти",
    loginSuccess: "Вы успешно вошли",
    registerSuccess: "Регистрация успешна",
    errorInvalidCredentials: "Неверный email или пароль",
    errorEmailTaken: "Этот email уже зарегистрирован",
  },

  // Domains
  domains: {
    title: "Каталог доменов",
    subtitle: "Выберите домен для начала обучения",
    it: "IT",
    itDescription: "Разработка, тестирование, DevOps и другие IT-направления",
    backToDomains: "К доменам",
    trainersIn: "Тренажёры в домене",
  },

  // Trainer
  trainer: {
    title: "О тренажёре",
    enroll: "Записаться на курс",
    enrolled: "Вы записаны",
    enrolledMessage: "Вы успешно записаны на тренажёр",
    scenarios: "Сценарии",
    startScenario: "Начать сценарий",
    scenarioList: "Список сценариев",
    difficulty: "Сложность",
    duration: "Длительность",
    minutes: "мин",
    skills: "Навыки",
    targetAudience: "Целевая аудитория",
    locale: "Язык",
    backToTrainer: "К тренажёру",
    notEnrolled: "Запишитесь на тренажёр, чтобы начать",
    // Trainer product name localizations
    qa_engineer_interview_trainer: "Тренажёр собеседования QA-инженера",
    business_analyst_interview_trainer: "Тренажёр собеседования бизнес-аналитика",
    // Trainer product description localizations
    qa_engineer_interview_trainer_desc: "Текстовый тренажёр для подготовки к собеседованию на Junior QA. Практикуйте ответы на типовые вопросы с структурированной AI-оценкой.",
    business_analyst_interview_trainer_desc: "Текстовый тренажёр для подготовки к собеседованию бизнес-аналитика. Практикуйте ответы на типовые вопросы с структурированной AI-оценкой.",
    // Trainer target audience labels
    audience_junior_qa_candidate: "Кандидат Junior QA",
    audience_career_switcher: "Смена карьеры",
    audience_trainee_qa: "Стажёр QA",
    audience_junior_ba: "Junior BA",
    audience_middle_ba: "Middle BA",
    audience_senior_ba: "Senior BA",
    audience_ba_career_switcher: "Смена карьеры в BA",
    audience_ba_trainee: "Стажёр BA",
    audience_ba_junior: "Junior BA",
    // Level identifiers
    level_junior: "Junior",
    level_middle: "Middle",
    level_senior: "Senior",
    level_junior_basic: "Junior (Базовый)",
    level_intermediate: "Intermediate",
    level_advanced: "Advanced",
  },

  // Scenario Runner
  scenario: {
    title: "Сценарий",
    start: "Начать прохождение",
    ready: "Вы готовы?",
    intro: "Описание сценария",
    userRole: "Ваша роль",
    aiRole: "Роль AI",
    yourAnswer: "Ваш ответ",
    answerPlaceholder: "Напишите ваш ответ здесь...",
    submit: "Отправить ответ",
    submitting: "Отправка...",
    complete: "Завершить и получить оценку",
    completing: "Завершение...",
    answerSaved: "Ответ сохранён",
    evaluateNow: "Оценить ответ",
    evaluating: "AI оценивает ваш ответ...",
    evaluationFailed: "Оценка временно недоступна",
    evaluationFailedMessage: "Ваш ответ сохранён. Попробуйте запросить оценку позже.",
    retryEvaluation: "Повторить оценку",
    backToList: "К списку сценариев",
    emptyAnswerError: "Ответ не может быть пустым",
    hints: "Подсказки",
    // QA scenario title and goal translations
    qa_self_presentation_v1: {
      title: "Расскажите о себе как о кандидате QA",
      goal: "Оценить способность кандидата профессионально себя представить, структурировать свой опыт и сформулировать мотивацию к работе в QA.",
    },
    qa_test_case_vs_checklist_v1: {
      title: "Тест-кейс vs Чеклист: различия и применение",
      goal: "Оценить понимание кандидатом тестовой документации: разница между тест-кейсами и чеклистами, их структура, когда использовать каждый из них и связанные компромиссы.",
    },
    qa_bug_report_structure_v1: {
      title: "Структура баг-репорта",
      goal: "Оценить знание кандидатом правильной структуры баг-репорта, включая все обязательные поля, классификацию severity vs priority и лучшие практики написания четких шагов воспроизведения.",
    },
    qa_regression_vs_retest_v1: {
      title: "Регрессионное тестирование vs Ретест",
      goal: "Оценить способность кандидата различать регрессионное тестирование и ретест, понимать когда каждый применяется, и объяснять их роль в QA-процессе с практическими примерами.",
    },
    qa_login_form_testing_v1: {
      title: "Тестирование формы логина",
      goal: "Оценить способность кандидата разрабатывать комплексные тестовые сценарии для формы логина, применять техники тест-дизайна, выявлять краевые случаи и логически структурировать тестовое покрытие.",
    },
  },

  // Evaluation Results
  result: {
    title: "Результат оценки",
    overallScore: "Общий балл",
    passed: "Пройдено",
    failed: "Нужна практика",
    criteria: "Критерии оценки",
    criterion: "Критерий",
    score: "Балл",
    evidence: "Обоснование",
    comment: "Комментарий",
    improvement: "Как улучшить",
    strengths: "Сильные стороны",
    weakPoints: "Слабые места",
    criticalErrors: "Критические ошибки",
    noCriticalErrors: "Критических ошибок не обнаружено",
    nextRecommendation: "Что делать дальше",
    retryScenario: "Повторить сценарий",
    nextScenario: "Следующий сценарий",
    toProgress: "К прогрессу",
    progressUpdated: "Прогресс обновлён",
    confidence: "Уверенность оценки",
    disclaimer: "Это симуляция собеседования с AI-оценкой. Результаты не гарантируют реального прохождения собеседования.",
  },

  // Progress
  progress: {
    title: "Мой прогресс",
    noProgress: "У вас пока нет записей о прогрессе",
    averageScore: "Средний балл",
    completedScenarios: "Пройдено сценариев",
    totalAttempts: "Всего попыток",
    readiness: {
      started: "Начато",
      developing: "В развитии",
      ready: "Готов",
      strong: "Уверенный",
    },
    skillScores: "Оценки по навыкам",
    trainerProgress: "Прогресс по тренажёру",
    noSkillData: "Нет данных по навыкам",
    lastActivity: "Последняя активность",
  },

  // Profile
  profile: {
    title: "Профиль",
    email: "Email",
    name: "Имя",
    preferredLocale: "Предпочитаемый язык",
    save: "Сохранить",
    saved: "Профиль обновлён",
    language: "Язык интерфейса",
  },

  // Admin
  admin: {
    title: "Администрирование",
    seedStatus: "Статус сидирования",
    systemHealth: "Здоровье системы",
    evaluationFailures: "Ошибки оценок",
    analytics: "Аналитика",
    domains: "Домены",
    trainers: "Тренажёры",
    scenarios: "Сценарии",
    rubrics: "Рубрики",
    locales: "Локализация",
    skills: "Навыки",
    enrollments: "Записи",
    aiRequests: "AI-запросы",
    totalEvents: "Всего событий",
    refresh: "Обновить",
  },

  // Common
  common: {
    loading: "Загрузка...",
    error: "Произошла ошибка",
    retry: "Повторить",
    save: "Сохранить",
    cancel: "Отмена",
    back: "Назад",
    next: "Далее",
    close: "Закрыть",
    notFound: "Не найдено",
    forbidden: "Доступ запрещён",
    unauthorized: "Требуется авторизация",
    sessionExpired: "Сессия истекла",
    comingSoon: "Скоро",
  },

  // Feature flags
  feature: {
    beta: "Бета-доступ",
    betaMessage: "Эта функция находится в разработке",
  },

  // Disclaimer
  disclaimer: {
    interview: "Это симуляция собеседования. Ответы анализируются AI и не гарантируют реального результата. Не указывайте личные данные (пароли, адреса, номера карт).",
  },

  ba_trainer: {
    name: "Business Analyst Interview Trainer",
    short_name: "BA Trainer",
    domain: "IT",
    module_label: "Модуль",
    activity_label: "Вопрос",
    start: "Начать тренировку",
    continue: "Продолжить",
    submit: "Отправить ответ",
    next: "Следующий вопрос",
    back_to_modules: "К списку модулей",
    result_correct: "Верно!",
    result_partial: "Частично верно",
    result_incorrect: "Неверно",
    score_label: "Результат",
    explanation_label: "Объяснение",
    difficulty_junior: "Junior",
    difficulty_middle: "Middle",
    difficulty_senior: "Senior",
    total_activities: "Всего вопросов",
    completed_activities: "Выполнено",
    progress_label: "Прогресс",
    module_activities: "Вопросы модуля",
    loading: "Загрузка...",
    error_loading: "Ошибка загрузки",
    error_submitting: "Ошибка при отправке ответа",
    no_activities: "В этом модуле пока нет вопросов",
    select_answer: "Выберите ответ",
    type_answer: "Введите ответ",
    match_pairs: "Сопоставьте пары",
    fill_blanks: "Заполните пропуски",
    your_answer: "Ваш ответ",
    correct_answer: "Правильный ответ",
    attempt_count: "Попытка {count}",
    retry: "Попробовать снова",
    modules: "Модули",
    phase_1_badge: "Фаза 1",
    status_staging: "Staging",
  },

  // Phase 2 scenario title translations
  ba_phase2_stakeholder_requirements_title: "Сбор требований от стейкхолдеров в финтех-проекте",
  ba_phase2_process_analysis_title: "Анализ и оптимизация процесса обработки заявлений",
  ba_phase2_documentation_artifacts_title: "Спецификация требований программы лояльности",
  ba_phase2_conflict_resolution_title: "Разрешение конфликта при внедрении WMS",
  ba_phase2_traceability_impact_title: "Анализ влияния изменений интеграционного API",
  ba_phase2_real_case_analysis_title: "Архитектура платформы корпоративного обучения с AI",

  // BA Phase 2
  ba_phase2: {
    title: "Сценарии бизнес-анализа (Фаза 2)",
    description: "Реалистичные задания с AI-оценкой для практики навыков бизнес-анализа",
    phase_2_badge: "Фаза 2 — AI-оценка",
    start: "Начать сценарий",
    how_it_works_title: "Как это работает",
    how_it_works_desc: "Прочитайте бизнес-контекст и задание, напишите развёрнутый ответ, получите структурированную AI-оценку по критериям с обратной связью. До 3 попыток на сценарий.",
    back_to_scenarios: "К списку сценариев",
    business_context: "Бизнес-контекст",
    task: "Задание",
    your_answer: "Ваш ответ",
    answer_placeholder: "Напишите развёрнутый ответ...",
    complete: "Завершить и получить оценку",
    evaluating_title: "AI оценивает ваш ответ",
    evaluating_desc: "DeepSeek анализирует ваш ответ по критериям рубрики. Это может занять до 30 секунд.",
    evaluating_progress: "Оценка выполняется...",
    evaluated_by: "Оценено",
    retry: "Повторить сценарий",
    max_attempts_reached: "Достигнут лимит попыток",
    max_attempts_desc: "Вы использовали все 3 попытки для этого сценария",
    default_role: "Бизнес-аналитик",
  },
};

export default ru;

export type LocaleStrings = typeof ru;
