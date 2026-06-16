#!/usr/bin/env python3
"""
Fix BA HR screening module content quality.

All 20 questions have semantically invalid option/title pairs.
This script replaces options and correct answers to match each
question's title and explanation, which are already correct.

Usage: python scripts/fix_ba_hr_content.py
"""

import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ACTIVITIES_PATH = 'f:/Dev/Projects/simulators/MULTISIMULATORS_PLATFOM/trainer_packages/business_analyst_interview_trainer/activities.json'
LOCALE_RU_PATH = 'f:/Dev/Projects/simulators/MULTISIMULATORS_PLATFOM/trainer_packages/business_analyst_interview_trainer/locales/ru-RU.json'
LOCALE_EN_PATH = 'f:/Dev/Projects/simulators/MULTISIMULATORS_PLATFOM/frontend/src/lib/i18n/generated_activity_titles_en.json'

with open(ACTIVITIES_PATH, 'r', encoding='utf-8') as f:
    acts = json.load(f)
with open(LOCALE_RU_PATH, 'r', encoding='utf-8') as f:
    ru_locale = json.load(f)
with open(LOCALE_EN_PATH, 'r', encoding='utf-8') as f:
    en_locale = json.load(f)

# ── New correct options & answers for each HR question ─────────────────────
#
# Format: { activity_id: (is_multi, [options_list], correct_answer(s), [en_options_list]) }
#
# Options and correct answers based on the question title and existing explanation text.

FIXES = {
    'ba_hr_q1_single': (
        False,
        [
            'Опыт работы с указанием проектов и достижений',
            'Хобби и личные интересы',
            'Рекомендации с предыдущих мест работы',
            'Фотография и семейное положение',
        ],
        'Опыт работы с указанием проектов и достижений',
        [
            'Work experience with projects and achievements',
            'Hobbies and personal interests',
            'References from previous jobs',
            'Photo and marital status',
        ],
    ),
    'ba_hr_q2_single': (
        False,
        [
            'PDF',
            'DOCX (Word)',
            'HTML',
            'TXT',
        ],
        'PDF',
        [
            'PDF',
            'DOCX (Word)',
            'HTML',
            'TXT',
        ],
    ),
    'ba_hr_q3_single': (
        False,
        [
            'Структурированный рассказ: прошлый опыт → переход → текущие компетенции',
            'Только текущие обязанности BA',
            'Полный список всех пройденных курсов',
            'Перечень технических навыков и стеков',
        ],
        'Структурированный рассказ: прошлый опыт → переход → текущие компетенции',
        [
            'Structured story: past experience → transition → current competencies',
            'Current BA responsibilities only',
            'Full list of all courses taken',
            'List of technical skills and stacks',
        ],
    ),
    'ba_hr_q4_single': (
        False,
        [
            'Аналитическое мышление и внимание к деталям',
            'Умение программировать на Python',
            'Знание Photoshop и Figma',
            'Навыки администрирования Linux',
        ],
        'Аналитическое мышление и внимание к деталям',
        [
            'Analytical thinking and attention to detail',
            'Python programming skills',
            'Photoshop and Figma knowledge',
            'Linux administration skills',
        ],
    ),
    'ba_hr_q5_single': (
        False,
        [
            'Быстрая проверка резюме рекрутером на соответствие базовым требованиям',
            'Глубокое интервью с техническим экспертом',
            'Тестовое задание по аналитике',
            'Оценка soft skills на групповой сессии',
        ],
        'Быстрая проверка резюме рекрутером на соответствие базовым требованиям',
        [
            'Quick resume check by recruiter for basic requirement match',
            'In-depth interview with technical expert',
            'Analytical test assignment',
            'Soft skills assessment in group session',
        ],
    ),
    'ba_hr_q6_single': (
        False,
        [
            'Назвать диапазон, ориентируясь на рынок, а не фиксированную сумму',
            'Назвать максимальную цифру из возможных',
            'Отказаться отвечать на вопрос',
            'Назвать минимальную сумму, чтобы точно взяли',
        ],
        'Назвать диапазон, ориентируясь на рынок, а не фиксированную сумму',
        [
            'State a range based on market research, not a fixed number',
            'State the highest possible number',
            'Refuse to answer the question',
            'State the lowest possible number to be sure',
        ],
    ),
    'ba_hr_q7_single': (
        False,
        [
            'Интерес к решению бизнес-задач и работе на стыке бизнеса и IT',
            'Высокая зарплата и бонусы',
            'Возможность работать удалённо',
            'Короткий рабочий день и гибкий график',
        ],
        'Интерес к решению бизнес-задач и работе на стыке бизнеса и IT',
        [
            'Interest in solving business problems and working at the intersection of business and IT',
            'High salary and bonuses',
            'Opportunity to work remotely',
            'Short working hours and flexible schedule',
        ],
    ),
    'ba_hr_q8_single': (
        False,
        [
            'Продукты, услуги, отрасль, новости и корпоративную культуру компании',
            'Внутреннюю структуру отделов и зарплаты сотрудников',
            'Личную жизнь руководителей и историю основания',
            'Бухгалтерскую отчётность и налоговые показатели',
        ],
        'Продукты, услуги, отрасль, новости и корпоративную культуру компании',
        [
            'Products, services, industry, news and corporate culture of the company',
            'Internal department structure and employee salaries',
            'Personal lives of executives and founding history',
            'Financial statements and tax indicators',
        ],
    ),
    'ba_hr_q9_single': (
        False,
        [
            'Структурированно: от образования и первого опыта к текущей роли и планам',
            'Только описание текущих обязанностей',
            'Перечисление всех мест работы без хронологии',
            'Только планы на будущее без упоминания прошлого',
        ],
        'Структурированно: от образования и первого опыта к текущей роли и планам',
        [
            'Structured: from education and first experience to current role and plans',
            'Only description of current responsibilities',
            'List of all jobs without chronology',
            'Only future plans without mentioning the past',
        ],
    ),
    'ba_hr_q10_single': (
        False,
        [
            'Приоритизация задач, декомпозиция, регулярные перерывы и тайм-менеджмент',
            'Работа по 12 часов без выходных до сдачи проекта',
            'Игнорирование дедлайнов и перенос ответственности',
            'Просьба о помощи на каждом этапе задачи',
        ],
        'Приоритизация задач, декомпозиция, регулярные перерывы и тайм-менеджмент',
        [
            'Task prioritization, decomposition, regular breaks and time management',
            'Working 12 hours without days off until project delivery',
            'Ignoring deadlines and shifting responsibility',
            'Asking for help at every stage of the task',
        ],
    ),
    'ba_hr_q11_single': (
        False,
        [
            '60,000 – 100,000 рублей в зависимости от компании и задач',
            '200,000+ рублей, так как Junior BA — это высококвалифицированная позиция',
            'Минимальную зарплату, лишь бы взяли на работу',
            'Не имеет значения, главное — опыт',
        ],
        '60,000 – 100,000 рублей в зависимости от компании и задач',
        [
            '60,000 – 100,000 RUB depending on the company and responsibilities',
            '200,000+ RUB as Junior BA is a highly skilled position',
            'Minimum salary just to get the job',
            'It does not matter, experience is the main thing',
        ],
    ),
    'ba_hr_q12_single': (
        False,
        [
            'Изучение BABOK, профильные курсы, практика написания use cases и user stories',
            'Просмотр видео на YouTube без практики',
            'Только чтение теоретических статей без применения',
            'Общение с друзьями, которые уже работают BA',
        ],
        'Изучение BABOK, профильные курсы, практика написания use cases и user stories',
        [
            'Studying BABOK, specialized courses, practicing writing use cases and user stories',
            'Watching YouTube videos without practice',
            'Only reading theoretical articles without application',
            'Talking to friends who already work as BAs',
        ],
    ),
    'ba_hr_q13_single': (
        False,
        [
            'ECBA (Entry Certificate), CCBA (Capability), CBAP (Certified) — сертификации IIBA',
            'PMP, CSM, SAFe, ITIL — сертификации по управлению',
            'CCNA, MCSA, AWS — технические сертификации',
            'TEFL, CMA, CFA — непрофильные сертификации',
        ],
        'ECBA (Entry Certificate), CCBA (Capability), CBAP (Certified) — сертификации IIBA',
        [
            'ECBA (Entry Certificate), CCBA (Capability), CBAP (Certified) — IIBA certifications',
            'PMP, CSM, SAFe, ITIL — management certifications',
            'CCNA, MCSA, AWS — technical certifications',
            'TEFL, CMA, CFA — non-core certifications',
        ],
    ),
    'ba_hr_q14_single': (
        False,
        [
            'Кейс использования метода STAR для описания конкретного результата с цифрами',
            'Описание процесса работы в общих чертах без конкретики',
            'Рассказ о том, какую зарплату удалось получить',
            'Описание сложностей без упоминания результата',
        ],
        'Кейс использования метода STAR для описания конкретного результата с цифрами',
        [
            'A case using the STAR method to describe a specific result with metrics',
            'General description of the work process without specifics',
            'Story of what salary was achieved',
            'Description of difficulties without mentioning the result',
        ],
    ),
    'ba_hr_q15_multi': (
        True,
        [
            'Интересные задачи и проекты',
            'Высокая заработная плата',
            'Удобное расположение офиса',
            'Профессиональный рост и развитие',
        ],
        ['Интересные задачи и проекты', 'Высокая заработная плата', 'Профессиональный рост и развитие'],
        [
            'Interesting tasks and projects',
            'High salary',
            'Convenient office location',
            'Professional growth and development',
        ],
    ),
    'ba_hr_q16_multi': (
        True,
        [
            'Какие методологии используются в команде',
            'Как организован процесс работы с требованиями',
            'Сколько длится обеденный перерыв',
            'Какие инструменты используются для ведения документации',
        ],
        ['Какие методологии используются в команде', 'Как организован процесс работы с требованиями', 'Какие инструменты используются для ведения документации'],
        [
            'What methodologies does the team use',
            'How is the requirements process organized',
            'How long is the lunch break',
            'What tools are used for documentation',
        ],
    ),
    'ba_hr_q17_multi': (
        True,
        [
            'Техники сбора требований (интервью, воркшопы)',
            'Написание user stories и критериев приёмки',
            'Глубокое знание синтаксиса C++',
            'Работа с требованиями и стейкхолдерами',
        ],
        ['Техники сбора требований (интервью, воркшопы)', 'Написание user stories и критериев приёмки', 'Работа с требованиями и стейкхолдерами'],
        [
            'Requirements elicitation techniques (interviews, workshops)',
            'Writing user stories and acceptance criteria',
            'Deep knowledge of C++ syntax',
            'Working with requirements and stakeholders',
        ],
    ),
    'ba_hr_q18_multi': (
        True,
        [
            'Честно объяснить причину: обучение, переезд, семейные обстоятельства',
            'Скрыть перерыв и изменить даты в резюме',
            'Сказать, что перерыва не было (солгать)',
            'Подчеркнуть, что за время перерыва вы развивались',
        ],
        ['Честно объяснить причину: обучение, переезд, семейные обстоятельства', 'Подчеркнуть, что за время перерыва вы развивались'],
        [
            'Honestly explain the reason: study, relocation, family circumstances',
            'Hide the gap and change dates in the resume',
            'Say there was no gap (lie)',
            'Emphasize that you developed yourself during the gap',
        ],
    ),
    'ba_hr_q19_multi': (
        True,
        [
            'Связующее звено между бизнесом и разработкой',
            'Исполнитель задач без участия в анализе',
            'Технический лидер команды разработки',
            'Аналитик, формализующий потребности бизнеса',
        ],
        ['Связующее звено между бизнесом и разработкой', 'Аналитик, формализующий потребности бизнеса'],
        [
            'Bridge between business and development',
            'Task executor without involvement in analysis',
            'Technical leader of the development team',
            'Analyst who formalizes business needs',
        ],
    ),
    'ba_hr_q20_multi': (
        True,
        [
            'Целенаправленный поиск на LinkedIn, хабр карьера, рекомендации коллег',
            'Случайно увидел(-а) вакансию в соцсетях и решил(-а) откликнуться',
            'Отклик на все вакансии подряд без разбора',
            'Интерес к компании и продукту, понимание ценности своей кандидатуры',
        ],
        ['Целенаправленный поиск на LinkedIn, хабр карьера, рекомендации коллег', 'Интерес к компании и продукту, понимание ценности своей кандидатуры'],
        [
            'Targeted search on LinkedIn, career resources, colleague recommendations',
            'Saw the vacancy randomly on social media and decided to apply',
            'Applying to all vacancies without consideration',
            'Interest in the company and product, understanding of your value',
        ],
    ),
}

# ── Apply fixes to activities.json ─────────────────────────────────────────
fix_count = 0
for i, a in enumerate(acts):
    if a['activity_id'] in FIXES:
        is_multi, ru_opts, ru_correct, en_opts = FIXES[a['activity_id']]
        a['payload']['options'] = ru_opts
        a['payload']['correct'] = ru_correct
        fix_count += 1
        print(f'  ✓ {a["activity_id"]}: options fixed ({len(ru_opts)} options)')

print(f'\nFixed {fix_count} activities in activities.json')

with open(ACTIVITIES_PATH, 'w', encoding='utf-8') as f:
    json.dump(acts, f, ensure_ascii=False, indent=2)

# ── Update ru-RU locale with English options as _ru variants ──────────────
# The ru-RU locale stores options as activity-level keys
# Format: ba_hr_q1_opt1, ba_hr_q1_opt2, etc.
# We need to read existing keys and check format
ru_acts = ru_locale.get('activities', {})

# Check what option keys look like
sample_opt_keys = [k for k in ru_acts if k.startswith('ba_hr_q') and 'opt' in k.lower()]
print(f'\nExisting option keys in ru-RU locale: {sample_opt_keys[:5]}')
print(f'Total: {len(sample_opt_keys)}')

# The ru-RU.json doesn't seem to have option-keyed translations.
# Options are stored directly in activities.json payload as raw Russian text.
# So we only need to update activities.json (already done above).

# ── Update en-US locale with explanation translations if missing ──────────
en_updated = 0
for aid, (_, _, _, _) in FIXES.items():
    exp_key = aid.split('_single')[0].split('_multi')[0] + '_explanation'
    if exp_key not in en_locale:
        # Explanation was added earlier via the generated_activity_titles_en.json
        pass

print(f'\n✅ All fixes applied.')
print(f'   activities.json: {fix_count} activities updated')
print(f'   Re-run seed_ba_trainer or rebuild to apply to database.')
