#!/usr/bin/env python3
"""Generate activities.json for the BA Interview Trainer Phase 1.

Creates 164 deterministic activities across 10 modules.
Uses the locale file for title/explanation keys.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent.parent / "trainer_packages" / "business_analyst_interview_trainer"


def load_locale():
    with open(PACKAGE_DIR / "locales" / "ru-RU.json", "r", encoding="utf-8") as f:
        return json.load(f)


def make_migration_meta(source_q: str) -> dict:
    return {
        "source_repository": "solomonczyk/bi-trainer-local",
        "source_question_id": source_q,
        "migration_date": "2026-06-06",
        "migration_version": "0.1.0",
    }


def single_choice(aid: str, mod: str, diff: str, title_key: str, expl_key: str, order: int,
                  options: list[str], correct: str, source_q: str = "unknown") -> dict:
    return {
        "activity_id": aid,
        "module_id": mod,
        "activity_type": "single_choice",
        "evaluation_mode": "deterministic",
        "difficulty": diff,
        "title_key": title_key,
        "description_key": None,
        "payload": {"options": options, "correct": correct},
        "explanation_key": expl_key,
        "order": order,
        "version": "0.1.0",
        "migration_metadata": make_migration_meta(source_q),
    }


def multiple_choice(aid: str, mod: str, diff: str, title_key: str, expl_key: str, order: int,
                    options: list[str], correct: list[str], source_q: str = "unknown") -> dict:
    return {
        "activity_id": aid,
        "module_id": mod,
        "activity_type": "multiple_choice",
        "evaluation_mode": "deterministic",
        "difficulty": diff,
        "title_key": title_key,
        "description_key": None,
        "payload": {"options": options, "correct": correct},
        "explanation_key": expl_key,
        "order": order,
        "version": "0.1.0",
        "migration_metadata": make_migration_meta(source_q),
    }


def numeric(aid: str, mod: str, diff: str, title_key: str, expl_key: str, order: int,
            correct: int, tolerance: int = 0, source_q: str = "unknown") -> dict:
    return {
        "activity_id": aid,
        "module_id": mod,
        "activity_type": "numeric",
        "evaluation_mode": "deterministic",
        "difficulty": diff,
        "title_key": title_key,
        "description_key": None,
        "payload": {"correct": correct, "tolerance": tolerance},
        "explanation_key": expl_key,
        "order": order,
        "version": "0.1.0",
        "migration_metadata": make_migration_meta(source_q),
    }


def fill_blanks(aid: str, mod: str, diff: str, title_key: str, expl_key: str, order: int,
                template: str, blanks: list[dict], correct: list[str], source_q: str = "unknown") -> dict:
    return {
        "activity_id": aid,
        "module_id": mod,
        "activity_type": "fill_blanks",
        "evaluation_mode": "deterministic",
        "difficulty": diff,
        "title_key": title_key,
        "description_key": None,
        "payload": {"template": template, "blanks": blanks, "correct": correct},
        "explanation_key": expl_key,
        "order": order,
        "version": "0.1.0",
        "migration_metadata": make_migration_meta(source_q),
    }


def matching(aid: str, mod: str, diff: str, title_key: str, expl_key: str, order: int,
             left_items: list[str], right_items: list[str], pairs: list[dict], source_q: str = "unknown") -> dict:
    return {
        "activity_id": aid,
        "module_id": mod,
        "activity_type": "matching",
        "evaluation_mode": "deterministic",
        "difficulty": diff,
        "title_key": title_key,
        "description_key": None,
        "payload": {"left_items": left_items, "right_items": right_items, "pairs": pairs},
        "explanation_key": expl_key,
        "order": order,
        "version": "0.1.0",
        "migration_metadata": make_migration_meta(source_q),
    }


def main():
    locale_data = load_locale()
    activities = locale_data.get("activities", {})

    acts = []
    order_counter = {}  # module_id -> order

    def next_order(mod: str) -> int:
        o = order_counter.get(mod, 0) + 1
        order_counter[mod] = o
        return o

    # ============================
    # MODULE 1: ba_hr_screening (20 activities: 14 single + 6 multi)
    # ============================
    mod = "ba_hr_screening"
    acts.append(single_choice("ba_hr_q1_single", mod, "junior", "ba_hr_q1_title", "ba_hr_q1_explanation", next_order(mod),
        ["Проверка навыков и опыта", "Быстрый просмотр резюме на соответствие базовым требованиям", "Телефонное интервью", "Проверка рекомендаций"],
        "Быстрый просмотр резюме на соответствие базовым требованиям", "module-1-Q1"))
    acts.append(single_choice("ba_hr_q2_single", mod, "junior", "ba_hr_q2_title", "ba_hr_q2_explanation", next_order(mod),
        ["HR-менеджер", "Team Lead", "Бизнес-аналитик", "Project Manager"],
        "Бизнес-аналитик", "module-1-Q2"))
    acts.append(single_choice("ba_hr_q3_single", mod, "junior", "ba_hr_q3_title", "ba_hr_q3_explanation", next_order(mod),
        ["HR-менеджер", "Руководитель отдела", "Бизнес-аналитик", "Заказчик"], "Бизнес-аналитик", "module-1-Q3"))
    acts.append(single_choice("ba_hr_q4_single", mod, "junior", "ba_hr_q4_title", "ba_hr_q4_explanation", next_order(mod),
        ["Technical Interview", "Screening (скрининг)", "Case Interview", "Stress Interview"], "Screening (скрининг)", "module-1-Q4"))
    acts.append(single_choice("ba_hr_q5_single", mod, "junior", "ba_hr_q5_title", "ba_hr_q5_explanation", next_order(mod),
        ["Мотивация, карьерные цели, ожидания по зарплате", "Технические навыки работы с SQL", "Опыт работы с BPMN", "Знание BABOK"],
        "Мотивация, карьерные цели, ожидания по зарплате", "module-1-Q5"))
    acts.append(single_choice("ba_hr_q6_single", mod, "middle", "ba_hr_q6_title", "ba_hr_q6_explanation", next_order(mod),
        ["STAR (Situation, Task, Action, Result)", "PARLA (Problem, Action, Result, Lesson, Application)", "CAR (Context, Action, Result)", "SOAR (Situation, Obstacle, Action, Result)"],
        "STAR (Situation, Task, Action, Result)", "module-1-Q6"))
    acts.append(single_choice("ba_hr_q7_single", mod, "junior", "ba_hr_q7_title", "ba_hr_q7_explanation", next_order(mod),
        ["Сильные стороны (Strengths)", "Слабые стороны (Weaknesses)", "Возможности (Opportunities)", "Угрозы (Threats)"],
        "Сильные стороны (Strengths)", "module-1-Q7"))
    acts.append(single_choice("ba_hr_q8_single", mod, "junior", "ba_hr_q8_title", "ba_hr_q8_explanation", next_order(mod),
        ["Должностная инструкция", "Резюме", "Сопроводительное письмо", "Профиль в LinkedIn"],
        "Должностная инструкция", "module-1-Q8"))
    acts.append(single_choice("ba_hr_q9_single", mod, "middle", "ba_hr_q9_title", "ba_hr_q9_explanation", next_order(mod),
        ["Опыт работы с требованиями и стейкхолдерами", "Знание языков программирования", "Наличие сертификата PMP", "Опыт разработки ПО"],
        "Опыт работы с требованиями и стейкхолдерами", "module-1-Q9"))
    acts.append(single_choice("ba_hr_q10_single", mod, "junior", "ba_hr_q10_title", "ba_hr_q10_explanation", next_order(mod),
        ["Собеседование с заказчиком", "Анализ требований", "Оценка затрат и сроков", "Составление отчёта"],
        "Оценка затрат и сроков", "module-1-Q10"))
    acts.append(single_choice("ba_hr_q11_single", mod, "junior", "ba_hr_q11_title", "ba_hr_q11_explanation", next_order(mod),
        ["Чётко и структурированно, с примерами", "Кратко, односложно", "Техническими терминами", "В виде резюме"],
        "Чётко и структурированно, с примерами", "module-1-Q11"))
    acts.append(single_choice("ba_hr_q12_single", mod, "middle", "ba_hr_q12_title", "ba_hr_q12_explanation", next_order(mod),
        ["Проектная работа (Project Work)", "Работа в найме (Employment)", "Фриланс (Freelance)", "Стажировка (Internship)"],
        "Проектная работа (Project Work)", "module-1-Q12"))
    acts.append(single_choice("ba_hr_q13_single", mod, "junior", "ba_hr_q13_title", "ba_hr_q13_explanation", next_order(mod),
        ["Управление требованиями и коммуникация", "Написание кода", "Дизайн интерфейсов", "Тестирование продукта"],
        "Управление требованиями и коммуникация", "module-1-Q13"))
    acts.append(single_choice("ba_hr_q14_single", mod, "middle", "ba_hr_q14_title", "ba_hr_q14_explanation", next_order(mod),
        ["Сбор и анализ требований", "Непосредственная разработка", "Техническая поддержка", "Маркетинг продукта"],
        "Сбор и анализ требований", "module-1-Q14"))

    # Multiple choice for HR
    acts.append(multiple_choice("ba_hr_q15_multi", mod, "junior", "ba_hr_q15_title", "ba_hr_q15_explanation", next_order(mod),
        ["Внимательность к деталям", "Коммуникабельность", "Владение языками программирования", "Аналитическое мышление"],
        ["Внимательность к деталям", "Коммуникабельность", "Аналитическое мышление"], "module-1-Q15"))
    acts.append(multiple_choice("ba_hr_q16_multi", mod, "junior", "ba_hr_q16_title", "ba_hr_q16_explanation", next_order(mod),
        ["Скрининг резюме", "Телефонное интервью", "Личное собеседование", "Подписание оффера"],
        ["Скрининг резюме", "Телефонное интервью", "Личное собеседование"], "module-1-Q16"))
    acts.append(multiple_choice("ba_hr_q17_multi", mod, "junior", "ba_hr_q17_title", "ba_hr_q17_explanation", next_order(mod),
        ["Умение слушать", "Ясная и структурированная речь", "Умение задавать уточняющие вопросы", "Знание архитектуры микросервисов"],
        ["Умение слушать", "Ясная и структурированная речь", "Умение задавать уточняющие вопросы"], "module-1-Q17"))
    acts.append(multiple_choice("ba_hr_q18_multi", mod, "middle", "ba_hr_q18_title", "ba_hr_q18_explanation", next_order(mod),
        ["Работа с разнородными стейкхолдерами", "Анализ бизнес-процессов", "Управление командой разработки", "Формализация требований"],
        ["Работа с разнородными стейкхолдерами", "Анализ бизнес-процессов", "Формализация требований"], "module-1-Q18"))
    acts.append(multiple_choice("ba_hr_q19_multi", mod, "middle", "ba_hr_q19_title", "ba_hr_q19_explanation", next_order(mod),
        ["Понимание предметной области", "Навыки ведения переговоров", "Знание методологий разработки", "Умение писать код на Python"],
        ["Понимание предметной области", "Навыки ведения переговоров", "Знание методологий разработки"], "module-1-Q19"))
    acts.append(multiple_choice("ba_hr_q20_multi", mod, "junior", "ba_hr_q20_title", "ba_hr_q20_explanation", next_order(mod),
        ["Пунктуальность", "Ответственность за результат", "Ориентация на качество", "Владение Photoshop"],
        ["Пунктуальность", "Ответственность за результат", "Ориентация на качество"], "module-1-Q20"))

    # ============================
    # MODULE 2: ba_basics_stakeholders (19 activities: 9 single + 4 multi + 2 fill + 4 matching)
    # ============================
    mod = "ba_basics_stakeholders"
    acts.append(single_choice("ba_basics_q1_single", mod, "junior", "ba_basics_q1_title", "ba_basics_q1_explanation", next_order(mod),
        ["Сбор и документирование требований", "Написание кода", "Тестирование продукта", "Управление командой"],
        "Сбор и документирование требований", "module-2-Q1"))
    acts.append(single_choice("ba_basics_q2_single", mod, "junior", "ba_basics_q2_title", "ba_basics_q2_explanation", next_order(mod),
        ["BABOK (Business Analysis Body of Knowledge)", "PMBOK (Project Management Body of Knowledge)", "TOGAF", "ITIL"],
        "BABOK (Business Analysis Body of Knowledge)", "module-2-Q2"))
    acts.append(single_choice("ba_basics_q3_single", mod, "junior", "ba_basics_q3_title", "ba_basics_q3_explanation", next_order(mod),
        ["Лицо, принимающее решение (ЛПР)", "Разработчик", "Тестировщик", "Project Manager"],
        "Лицо, принимающее решение (ЛПР)", "module-2-Q3"))
    acts.append(single_choice("ba_basics_q4_single", mod, "junior", "ba_basics_q4_title", "ba_basics_q4_explanation", next_order(mod),
        ["Влияние и интерес к проекту", "Должность и зарплата", "Возраст и опыт", "Технические навыки"],
        "Влияние и интерес к проекту", "module-2-Q4"))
    acts.append(single_choice("ba_basics_q5_single", mod, "junior", "ba_basics_q5_title", "ba_basics_q5_explanation", next_order(mod),
        ["RACI (Responsible, Accountable, Consulted, Informed)", "SWOT (Strengths, Weaknesses, Opportunities, Threats)", "SMART (Specific, Measurable, Achievable, Relevant, Time-bound)", "MoSCoW (Must, Should, Could, Won't)"],
        "RACI (Responsible, Accountable, Consulted, Informed)", "module-2-Q5"))
    acts.append(single_choice("ba_basics_q6_single", mod, "junior", "ba_basics_q6_title", "ba_basics_q6_explanation", next_order(mod),
        ["Responsible (Исполнитель)", "Accountable (Ответственный)", "Consulted (Консультируемый)", "Informed (Информируемый)"],
        "Accountable (Ответственный)", "module-2-Q6"))
    acts.append(single_choice("ba_basics_q7_single", mod, "middle", "ba_basics_q7_title", "ba_basics_q7_explanation", next_order(mod),
        ["IIBA (International Institute of Business Analysis)", "PMI (Project Management Institute)", "IEEE", "ISO"],
        "IIBA (International Institute of Business Analysis)", "module-2-Q7"))
    acts.append(single_choice("ba_basics_q8_single", mod, "middle", "ba_basics_q8_title", "ba_basics_q8_explanation", next_order(mod),
        ["6 областей знаний (Knowledge Areas)", "5 областей знаний", "10 областей знаний", "3 области знаний"],
        "6 областей знаний (Knowledge Areas)", "module-2-Q8"))
    acts.append(single_choice("ba_basics_q9_single", mod, "middle", "ba_basics_q9_title", "ba_basics_q9_explanation", next_order(mod),
        ["Business Analysis Planning and Monitoring", "Elicitation and Collaboration", "Requirements Life Cycle Management", "Strategy Analysis"],
        "Business Analysis Planning and Monitoring", "module-2-Q9"))

    # Multiple choice for Basics
    acts.append(multiple_choice("ba_basics_q10_multi", mod, "junior", "ba_basics_q10_title", "ba_basics_q10_explanation", next_order(mod),
        ["Сбор требований (Elicitation)", "Анализ требований (Analysis)", "Спецификация (Specification)", "Написание кода (Coding)"],
        ["Сбор требований (Elicitation)", "Анализ требований (Analysis)", "Спецификация (Specification)"], "module-2-Q10"))
    acts.append(multiple_choice("ba_basics_q11_multi", mod, "junior", "ba_basics_q11_title", "ba_basics_q11_explanation", next_order(mod),
        ["Sponsor (Спонсор)", "End User (Конечный пользователь)", "Domain Subject Matter Expert (Эксперт)", "Разработчик баз данных"],
        ["Sponsor (Спонсор)", "End User (Конечный пользователь)", "Domain Subject Matter Expert (Эксперт)"], "module-2-Q11"))
    acts.append(multiple_choice("ba_basics_q12_multi", mod, "middle", "ba_basics_q12_title", "ba_basics_q12_explanation", next_order(mod),
        ["Управление конфликтами", "Фасилитация встреч", "Написание технической документации", "Управление командой разработки"],
        ["Управление конфликтами", "Фасилитация встреч", "Написание технической документации"], "module-2-Q12"))
    acts.append(multiple_choice("ba_basics_q13_multi", mod, "middle", "ba_basics_q13_title", "ba_basics_q13_explanation", next_order(mod),
        ["Business Need (Бизнес-потребность)", "Solution Scope (Границы решения)", "Business Case (Бизнес-кейс)", "Код приложения"],
        ["Business Need (Бизнес-потребность)", "Solution Scope (Границы решения)", "Business Case (Бизнес-кейс)"], "module-2-Q13"))

    # Fill blanks for Basics
    acts.append(fill_blanks("ba_basics_q14_fill", mod, "junior", "ba_basics_q14_title", "ba_basics_q14_explanation", next_order(mod),
        "Методика определения уровня вовлечённости и влияния стейкхолдеров называется ___ анализ.",
        [{"id": "blank_0", "options": ["SWOT", "RACI", "Stakeholder", "PESTLE"]}],
        ["Stakeholder"], "module-2-Q14"))
    acts.append(fill_blanks("ba_basics_q15_fill", mod, "junior", "ba_basics_q15_title", "ba_basics_q15_explanation", next_order(mod),
        "Правильно сформулированная цель должна соответствовать критериям ___.",
        [{"id": "blank_0", "options": ["SMART", "RACI", "SWOT", "MoSCoW"]}],
        ["SMART"], "module-2-Q15"))

    # Matching for Basics (4 activities)
    acts.append(matching("ba_basics_q16_match", mod, "middle", "ba_basics_q16_title", "ba_basics_q16_explanation", next_order(mod),
        ["R - Responsible", "A - Accountable", "C - Consulted", "I - Informed"],
        ["Исполнитель работы", "Несёт ответственность за результат", "Консультирует до принятия решения", "Информируется после решения"],
        [
            {"left": "R - Responsible", "right": "Исполнитель работы"},
            {"left": "A - Accountable", "right": "Несёт ответственность за результат"},
            {"left": "C - Consulted", "right": "Консультирует до принятия решения"},
            {"left": "I - Informed", "right": "Информируется после решения"},
        ], "module-2-Q16"))
    acts.append(matching("ba_basics_q17_match", mod, "middle", "ba_basics_q17_title", "ba_basics_q17_explanation", next_order(mod),
        ["Sponsor", "Subject Matter Expert", "End User", "Project Manager"],
        ["Финансирует проект", "Предоставляет экспертные знания", "Использует результат", "Управляет реализацией"],
        [
            {"left": "Sponsor", "right": "Финансирует проект"},
            {"left": "Subject Matter Expert", "right": "Предоставляет экспертные знания"},
            {"left": "End User", "right": "Использует результат"},
            {"left": "Project Manager", "right": "Управляет реализацией"},
        ], "module-2-Q17"))
    acts.append(matching("ba_basics_q18_match", mod, "junior", "ba_basics_q18_title", "ba_basics_q18_explanation", next_order(mod),
        ["Elicitation", "Analysis", "Specification", "Validation"],
        ["Сбор требований от стейкхолдеров", "Анализ и моделирование требований", "Документирование требований", "Проверка требований"],
        [
            {"left": "Elicitation", "right": "Сбор требований от стейкхолдеров"},
            {"left": "Analysis", "right": "Анализ и моделирование требований"},
            {"left": "Specification", "right": "Документирование требований"},
            {"left": "Validation", "right": "Проверка требований"},
        ], "module-2-Q18"))
    acts.append(matching("ba_basics_q19_match", mod, "middle", "ba_basics_q19_title", "ba_basics_q19_explanation", next_order(mod),
        ["Must have", "Should have", "Could have", "Won't have"],
        ["Критически важно", "Важно, но не критично", "Желательно, но не обязательно", "Не будет реализовано"],
        [
            {"left": "Must have", "right": "Критически важно"},
            {"left": "Should have", "right": "Важно, но не критично"},
            {"left": "Could have", "right": "Желательно, но не обязательно"},
            {"left": "Won't have", "right": "Не будет реализовано"},
        ], "module-2-Q19"))

    # ============================
    # MODULE 3: ba_requirements_elicitation (20 activities: 12 single + 6 multi + 2 fill)
    # ============================
    mod = "ba_requirements_elicitation"
    acts.append(single_choice("ba_req_q1_single", mod, "junior", "ba_req_q1_title", "ba_req_q1_explanation", next_order(mod),
        ["Интервью", "Анкетирование", "Мозговой штурм", "Наблюдение"],
        "Интервью", "module-3-Q1"))
    acts.append(single_choice("ba_req_q2_single", mod, "junior", "ba_req_q2_title", "ba_req_q2_explanation", next_order(mod),
        ["Сбор требований напрямую от стейкхолдеров через беседу", "Написание технического задания", "Тестирование продукта", "Создание прототипа"],
        "Сбор требований напрямую от стейкхолдеров через беседу", "module-3-Q2"))
    acts.append(single_choice("ba_req_q3_single", mod, "junior", "ba_req_q3_title", "ba_req_q3_explanation", next_order(mod),
        ["Структурированное (с подготовленными вопросами)", "Свободное (без плана)", "Групповое", "Анонимное"],
        "Структурированное (с подготовленными вопросами)", "module-3-Q3"))
    acts.append(single_choice("ba_req_q4_single", mod, "junior", "ba_req_q4_title", "ba_req_q4_explanation", next_order(mod),
        ["Мозговой штурм (Brainstorming)", "Прототипирование (Prototyping)", "Анкетирование (Survey)", "Наблюдение (Observation)"],
        "Мозговой штурм (Brainstorming)", "module-3-Q4"))
    acts.append(single_choice("ba_req_q5_single", mod, "middle", "ba_req_q5_title", "ba_req_q5_explanation", next_order(mod),
        ["Анализ документов (Document Analysis)", "Фокус-группа (Focus Group)", "Интервью (Interview)", "Наблюдение (Observation)"],
        "Анализ документов (Document Analysis)", "module-3-Q5"))
    acts.append(single_choice("ba_req_q6_single", mod, "junior", "ba_req_q6_title", "ba_req_q6_explanation", next_order(mod),
        ["Требования должны быть проверяемыми (testable)", "Требования могут быть любыми", "Требования пишутся на языке пользователя", "Каждое требование должно быть уникальным"],
        "Требования должны быть проверяемыми (testable)", "module-3-Q6"))
    acts.append(single_choice("ba_req_q7_single", mod, "junior", "ba_req_q7_title", "ba_req_q7_explanation", next_order(mod),
        ["Функциональные (что система должна делать)", "Нефункциональные (как система должна работать)", "Бизнес-требования", "Пользовательские истории"],
        "Функциональные (что система должна делать)", "module-3-Q7"))
    acts.append(single_choice("ba_req_q8_single", mod, "middle", "ba_req_q8_title", "ba_req_q8_explanation", next_order(mod),
        ["Производительность, безопасность, масштабируемость", "Бизнес-правила и процессы", "Интерфейс пользователя", "Сценарии использования"],
        "Производительность, безопасность, масштабируемость", "module-3-Q8"))
    acts.append(single_choice("ba_req_q9_single", mod, "junior", "ba_req_q9_title", "ba_req_q9_explanation", next_order(mod),
        ["Участники совместно создают решение", "Модератор задаёт вопросы группе", "Каждый участник предлагает свои идеи", "Эксперт рассказывает о лучших практиках"],
        "Участники совместно создают решение", "module-3-Q9"))
    acts.append(single_choice("ba_req_q10_single", mod, "middle", "ba_req_q10_title", "ba_req_q10_explanation", next_order(mod),
        ["Требования полны, непротиворечивы, однозначны", "Требования нравятся заказчику", "Требования написаны на английском", "Требования согласованы с командой разработки"],
        "Требования полны, непротиворечивы, однозначны", "module-3-Q10"))
    acts.append(single_choice("ba_req_q11_single", mod, "senior", "ba_req_q11_title", "ba_req_q11_explanation", next_order(mod),
        ["Модель CMMI (Capability Maturity Model Integration)", "Бенчмаркинг конкурентов", "MVP (Minimum Viable Product)", "User Story Mapping"],
        "Модель CMMI (Capability Maturity Model Integration)", "module-3-Q11"))
    acts.append(single_choice("ba_req_q12_single", mod, "senior", "ba_req_q12_title", "ba_req_q12_explanation", next_order(mod),
        ["Event Storming", "Daily Standup", "Ретроспектива", "Code Review"],
        "Event Storming", "module-3-Q12"))

    # Multiple choice for Requirements
    acts.append(multiple_choice("ba_req_q13_multi", mod, "junior", "ba_req_q13_title", "ba_req_q13_explanation", next_order(mod),
        ["Интервью (Interview)", "Анкетирование (Survey)", "Анализ кода (Code Analysis)", "Наблюдение (Observation)"],
        ["Интервью (Interview)", "Анкетирование (Survey)", "Наблюдение (Observation)"], "module-3-Q13"))
    acts.append(multiple_choice("ba_req_q14_multi", mod, "junior", "ba_req_q14_title", "ba_req_q14_explanation", next_order(mod),
        ["Валидность (Validity)", "Полнота (Completeness)", "Непротиворечивость (Consistency)", "Скорость реализации"],
        ["Валидность (Validity)", "Полнота (Completeness)", "Непротиворечивость (Consistency)"], "module-3-Q14"))
    acts.append(multiple_choice("ba_req_q15_multi", mod, "middle", "ba_req_q15_title", "ba_req_q15_explanation", next_order(mod),
        ["Заинтересованные стороны Stakeholder Analysis", "Цели бизнеса Business Goals", "Текущие бизнес-процессы (AS-IS)", "Кодовую базу приложения"],
        ["Заинтересованные стороны Stakeholder Analysis", "Цели бизнеса Business Goals", "Текущие бизнес-процессы (AS-IS)"], "module-3-Q15"))
    acts.append(multiple_choice("ba_req_q16_multi", mod, "middle", "ba_req_q16_title", "ba_req_q16_explanation", next_order(mod),
        ["Требования понятны всем стейкхолдерам", "Каждое требование имеет уникальный ID", "Требования написаны на Python", "Требования прослеживаются от бизнес-целей"],
        ["Требования понятны всем стейкхолдерам", "Каждое требование имеет уникальный ID", "Требования прослеживаются от бизнес-целей"], "module-3-Q16"))
    acts.append(multiple_choice("ba_req_q17_multi", mod, "senior", "ba_req_q17_title", "ba_req_q17_explanation", next_order(mod),
        ["Прототип (Mockup/Wireframe)", "Use Case (вариант использования)", "User Story (пользовательская история)", "Бизнес-план"],
        ["Прототип (Mockup/Wireframe)", "Use Case (вариант использования)", "User Story (пользовательская история)"], "module-3-Q17"))
    acts.append(multiple_choice("ba_req_q18_multi", mod, "senior", "ba_req_q18_title", "ba_req_q18_explanation", next_order(mod),
        ["Изменение требований неизбежно", "Изменения нужно контролировать через Change Control",
         "Изменения запрещены после утверждения", "Каждое изменение требует переоценки приоритетов"],
        ["Изменение требований неизбежно", "Изменения нужно контролировать через Change Control",
         "Каждое изменение требует переоценки приоритетов"], "module-3-Q18"))

    # Fill blanks for Requirements
    acts.append(fill_blanks("ba_req_q19_fill", mod, "junior", "ba_req_q19_title", "ba_req_q19_explanation", next_order(mod),
        "Техника сбора требований, при которой BA наблюдает за работой пользователя без активного вмешательства, называется ___.",
        [{"id": "blank_0", "options": ["интервью", "анкетирование", "наблюдение", "прототипирование"]}],
        ["наблюдение"], "module-3-Q19"))
    acts.append(fill_blanks("ba_req_q20_fill", mod, "junior", "ba_req_q20_title", "ba_req_q20_explanation", next_order(mod),
        "Свойство требования, означающее что оно может быть проверено с помощью теста или инспекции, называется ___.",
        [{"id": "blank_0", "options": ["полнота", "непротиворечивость", "верифицируемость", "однозначность"]}],
        ["верифицируемость"], "module-3-Q20"))

    # ============================
    # MODULE 4: ba_documentation_artifacts (19 activities: 12 single + 5 multi + 2 fill)
    # ============================
    mod = "ba_documentation_artifacts"
    acts.append(single_choice("ba_docs_q1_single", mod, "junior", "ba_docs_q1_title", "ba_docs_q1_explanation", next_order(mod),
        ["User Story", "Use Case", "BRD", "SRS"], "BRD", "module-4-Q1"))
    acts.append(single_choice("ba_docs_q2_single", mod, "junior", "ba_docs_q2_title", "ba_docs_q2_explanation", next_order(mod),
        ["User Story (пользовательская история)", "Use Case (вариант использования)", "BRD (Business Requirements Document)", "SRS (Software Requirements Specification)"],
        "User Story (пользовательская история)", "module-4-Q2"))
    acts.append(single_choice("ba_docs_q3_single", mod, "junior", "ba_docs_q3_title", "ba_docs_q3_explanation", next_order(mod),
        ["As a [пользователь], I want [действие], so that [ценность]", "Given [контекст], When [действие], Then [результат]", "Если [условие], то [результат]", "Пользователь нажимает кнопку"],
        "As a [пользователь], I want [действие], so that [ценность]", "module-4-Q3"))
    acts.append(single_choice("ba_docs_q4_single", mod, "junior", "ba_docs_q4_title", "ba_docs_q4_explanation", next_order(mod),
        ["Acceptance Criteria (критерии приёмки)", "Бизнес-правила", "Макет интерфейса", "Оценка трудозатрат"],
        "Acceptance Criteria (критерии приёмки)", "module-4-Q4"))
    acts.append(single_choice("ba_docs_q5_single", mod, "junior", "ba_docs_q5_title", "ba_docs_q5_explanation", next_order(mod),
        ["Given — When — Then (Gherkin)", "As a — I want — So that", "IF — THEN — ELSE", "Do — Check — Adjust"],
        "Given — When — Then (Gherkin)", "module-4-Q5"))
    acts.append(single_choice("ba_docs_q6_single", mod, "junior", "ba_docs_q6_title", "ba_docs_q6_explanation", next_order(mod),
        ["BRD описывает бизнес-потребности, SRS — технические требования", "BRD и SRS — это одно и то же", "SRS пишется до BRD", "BRD — технический документ, SRS — бизнес-документ"],
        "BRD описывает бизнес-потребности, SRS — технические требования", "module-4-Q6"))
    acts.append(single_choice("ba_docs_q7_single", mod, "junior", "ba_docs_q7_title", "ba_docs_q7_explanation", next_order(mod),
        ["Use Case — описание взаимодействия пользователя с системой", "Use Case — список всех требований к системе", "Use Case — диаграмма базы данных", "Use Case — прототип интерфейса"],
        "Use Case — описание взаимодействия пользователя с системой", "module-4-Q7"))
    acts.append(single_choice("ba_docs_q8_single", mod, "middle", "ba_docs_q8_title", "ba_docs_q8_explanation", next_order(mod),
        ["Трассировка требований (Requirements Traceability)", "Матрица компетенций", "Сетевой график проекта", "Бюджет проекта"],
        "Трассировка требований (Requirements Traceability)", "module-4-Q8"))
    acts.append(single_choice("ba_docs_q9_single", mod, "junior", "ba_docs_q9_title", "ba_docs_q9_explanation", next_order(mod),
        ["Глоссарий (Glossary)", "Техническое задание", "Устав проекта", "План коммуникаций"],
        "Глоссарий (Glossary)", "module-4-Q9"))
    acts.append(single_choice("ba_docs_q10_single", mod, "middle", "ba_docs_q10_title", "ba_docs_q10_explanation", next_order(mod),
        ["Прототип (Prototype/Mockup)", "SRS (Software Requirements Specification)", "RTM (Requirements Traceability Matrix)", "User Story Mapping"],
        "RTM (Requirements Traceability Matrix)", "module-4-Q10"))
    acts.append(single_choice("ba_docs_q11_single", mod, "senior", "ba_docs_q11_title", "ba_docs_q11_explanation", next_order(mod),
        ["Epic (большая пользовательская история)", "Task (задача)", "Bug (дефект)", "Sub-task (подзадача)"],
        "Epic (большая пользовательская история)", "module-4-Q11"))
    acts.append(single_choice("ba_docs_q12_single", mod, "senior", "ba_docs_q12_title", "ba_docs_q12_explanation", next_order(mod),
        ["User Story Mapping", "Диаграмма Ганта", "PERT-диаграмма", "WBS (Work Breakdown Structure)"],
        "User Story Mapping", "module-4-Q12"))

    # Multiple choice for Documentation
    acts.append(multiple_choice("ba_docs_q13_multi", mod, "junior", "ba_docs_q13_title", "ba_docs_q13_explanation", next_order(mod),
        ["User Story", "Acceptance Criteria", "Use Case", "Исходный код"],
        ["User Story", "Acceptance Criteria", "Use Case"], "module-4-Q13"))
    acts.append(multiple_choice("ba_docs_q14_multi", mod, "junior", "ba_docs_q14_title", "ba_docs_q14_explanation", next_order(mod),
        ["Структура BRD", "Формат описания Use Case", "Правила написания User Story (INVEST)", "Синтаксис SQL"],
        ["Структура BRD", "Формат описания Use Case", "Правила написания User Story (INVEST)"], "module-4-Q14"))
    acts.append(multiple_choice("ba_docs_q15_multi", mod, "middle", "ba_docs_q15_title", "ba_docs_q15_explanation", next_order(mod),
        ["Основной сценарий (Main Flow)", "Альтернативный сценарий (Alternative Flow)", "Исключительный сценарий (Exception Flow)", "График разработки"],
        ["Основной сценарий (Main Flow)", "Альтернативный сценарий (Alternative Flow)", "Исключительный сценарий (Exception Flow)"], "module-4-Q15"))
    acts.append(multiple_choice("ba_docs_q16_multi", mod, "middle", "ba_docs_q16_title", "ba_docs_q16_explanation", next_order(mod),
        ["Independent (независимая)", "Negotiable (обсуждаемая)", "Valuable (ценная)", "Executable (исполняемая)"],
        ["Independent (независимая)", "Negotiable (обсуждаемая)", "Valuable (ценная)"], "module-4-Q16"))
    acts.append(multiple_choice("ba_docs_q17_multi", mod, "senior", "ba_docs_q17_title", "ba_docs_q17_explanation", next_order(mod),
        ["Каждое требование связано с бизнес-целью", "Каждое требование ведёт к конкретной реализации",
         "Изменения требований отслеживаются", "Требования автоматически проверяются"],
        ["Каждое требование связано с бизнес-целью", "Каждое требование ведёт к конкретной реализации",
         "Изменения требований отслеживаются"], "module-4-Q17"))

    # Fill blanks for Documentation
    acts.append(fill_blanks("ba_docs_q18_fill", mod, "junior", "ba_docs_q18_title", "ba_docs_q18_explanation", next_order(mod),
        "Шаблон для описания критериев приёмки в BDD: ___ контекст, ___ действие, ___ результат.",
        [{"id": "blank_0", "options": ["When", "Given", "Then", "And"]},
         {"id": "blank_1", "options": ["When", "Given", "Then", "And"]},
         {"id": "blank_2", "options": ["When", "Given", "Then", "And"]}],
        ["Given", "When", "Then"], "module-4-Q18"))
    acts.append(fill_blanks("ba_docs_q19_fill", mod, "junior", "ba_docs_q19_title", "ba_docs_q19_explanation", next_order(mod),
        "User Story должна следовать шаблону: As a ___, I want ___, So that ___.",
        [{"id": "blank_0"}, {"id": "blank_1"}, {"id": "blank_2"}],
        ["пользователь", "действие", "ценность"], "module-4-Q19"))

    # ============================
    # MODULE 5: ba_process_data_modeling (15 activities: 7 single + 4 multi + 2 fill + 1 numeric + 1 matching)
    # ============================
    mod = "ba_process_data_modeling"
    acts.append(single_choice("ba_model_q1_single", mod, "junior", "ba_model_q1_title", "ba_model_q1_explanation", next_order(mod),
        ["BPMN", "UML", "ERD", "DFD"], "BPMN", "module-5-Q1"))
    acts.append(single_choice("ba_model_q2_single", mod, "junior", "ba_model_q2_title", "ba_model_q2_explanation", next_order(mod),
        ["Start Event (Стартовое событие)", "Task (Задача)", "Gateway (Шлюз)", "End Event (Конечное событие)"],
        "Gateway (Шлюз)", "module-5-Q2"))
    acts.append(single_choice("ba_model_q3_single", mod, "junior", "ba_model_q3_title", "ba_model_q3_explanation", next_order(mod),
        ["ERD (Entity-Relationship Diagram)", "BPMN (Business Process Model and Notation)", "UML (Unified Modeling Language)", "DFD (Data Flow Diagram)"],
        "ERD (Entity-Relationship Diagram)", "module-5-Q3"))
    acts.append(single_choice("ba_model_q4_single", mod, "middle", "ba_model_q4_title", "ba_model_q4_explanation", next_order(mod),
        ["Use Case Diagram", "Class Diagram", "Sequence Diagram", "Activity Diagram"],
        "Use Case Diagram", "module-5-Q4"))
    acts.append(single_choice("ba_model_q5_single", mod, "middle", "ba_model_q5_title", "ba_model_q5_explanation", next_order(mod),
        ["Пул (Pool) — организация, Дорожка (Lane) — отдел/роль", "Пул — это задача, Дорожка — это шлюз", "Пул — это событие, Дорожка — это поток", "Пул — это диаграмма, Дорожка — это процесс"],
        "Пул (Pool) — организация, Дорожка (Lane) — отдел/роль", "module-5-Q5"))
    acts.append(single_choice("ba_model_q6_single", mod, "senior", "ba_model_q6_title", "ba_model_q6_explanation", next_order(mod),
        ["Entity (Сущность)", "Attribute (Атрибут)", "Relationship (Связь)", "Primary Key (Первичный ключ)"],
        "Entity (Сущность)", "module-5-Q6"))
    acts.append(single_choice("ba_model_q7_single", mod, "junior", "ba_model_q7_title", "ba_model_q7_explanation", next_order(mod),
        ["Data Flow Diagram (DFD)", "BPMN Diagram", "ERD Diagram", "Use Case Diagram"],
        "Data Flow Diagram (DFD)", "module-5-Q7"))

    # Multiple choice for Modeling
    acts.append(multiple_choice("ba_model_q8_multi", mod, "junior", "ba_model_q8_title", "ba_model_q8_explanation", next_order(mod),
        ["BPMN", "UML", "ERD", "SQL"],
        ["BPMN", "UML", "ERD"], "module-5-Q8"))
    acts.append(multiple_choice("ba_model_q9_multi", mod, "middle", "ba_model_q9_title", "ba_model_q9_explanation", next_order(mod),
        ["Events (События)", "Activities (Действия)", "Gateways (Шлюзы)", "Tables (Таблицы)"],
        ["Events (События)", "Activities (Действия)", "Gateways (Шлюзы)"], "module-5-Q9"))
    acts.append(multiple_choice("ba_model_q10_multi", mod, "middle", "ba_model_q10_title", "ba_model_q10_explanation", next_order(mod),
        ["Structural (структурные)", "Behavioral (поведенческие)", "Interaction (взаимодействия)", "Database (базы данных)"],
        ["Structural (структурные)", "Behavioral (поведенческие)", "Interaction (взаимодействия)"], "module-5-Q10"))
    acts.append(multiple_choice("ba_model_q11_multi", mod, "senior", "ba_model_q11_title", "ba_model_q11_explanation", next_order(mod),
        ["One-to-One", "One-to-Many", "Many-to-Many", "Null-to-Null"],
        ["One-to-One", "One-to-Many", "Many-to-Many"], "module-5-Q11"))

    # Fill blanks for Modeling
    acts.append(fill_blanks("ba_model_q12_fill", mod, "junior", "ba_model_q12_title", "ba_model_q12_explanation", next_order(mod),
        "В BPMN ромбовидный элемент используется для ветвления процесса и называется ___.",
        [{"id": "blank_0", "options": ["Task", "Gateway", "Event", "Pool"]}],
        ["Gateway"], "module-5-Q12"))
    acts.append(fill_blanks("ba_model_q13_fill", mod, "junior", "ba_model_q13_title", "ba_model_q13_explanation", next_order(mod),
        "Связь между таблицами в ERD, где одной записи в таблице A соответствует много записей в таблице B, называется ___-to-___.",
        [{"id": "blank_0", "options": ["One", "Many", "Zero", "Null"]},
         {"id": "blank_1", "options": ["One", "Many", "Zero", "Null"]}],
        ["One", "Many"], "module-5-Q13"))

    # Numeric for Modeling
    acts.append(numeric("ba_model_q14_number", mod, "junior", "ba_model_q14_title", "ba_model_q14_explanation", next_order(mod),
        4, 0, "module-5-Q14"))

    # Matching for Modeling
    acts.append(matching("ba_model_q15_match", mod, "senior", "ba_model_q15_title", "ba_model_q15_explanation", next_order(mod),
        ["BPMN", "UML", "ERD", "DFD"],
        ["Моделирование бизнес-процессов", "Объектно-ориентированное моделирование", "Моделирование данных и связей", "Моделирование потоков данных"],
        [
            {"left": "BPMN", "right": "Моделирование бизнес-процессов"},
            {"left": "UML", "right": "Объектно-ориентированное моделирование"},
            {"left": "ERD", "right": "Моделирование данных и связей"},
            {"left": "DFD", "right": "Моделирование потоков данных"},
        ], "module-5-Q15"))

    # ============================
    # MODULE 6: ba_methodologies (16 activities: 9 single + 4 multi + 3 fill)
    # ============================
    mod = "ba_methodologies"
    acts.append(single_choice("ba_method_q1_single", mod, "junior", "ba_method_q1_title", "ba_method_q1_explanation", next_order(mod),
        ["Scrum", "Waterfall", "Kanban", "SAFe"], "Scrum", "module-6-Q1"))
    acts.append(single_choice("ba_method_q2_single", mod, "junior", "ba_method_q2_title", "ba_method_q2_explanation", next_order(mod),
        ["Sprint Planning", "Daily Stand-up", "Sprint Review", "Retrospective"],
        "Sprint Planning", "module-6-Q2"))
    acts.append(single_choice("ba_method_q3_single", mod, "junior", "ba_method_q3_title", "ba_method_q3_explanation", next_order(mod),
        ["2-4 недели", "1 день", "6 месяцев", "1 год"],
        "2-4 недели", "module-6-Q3"))
    acts.append(single_choice("ba_method_q4_single", mod, "junior", "ba_method_q4_title", "ba_method_q4_explanation", next_order(mod),
        ["Kanban", "Waterfall", "Scrum", "XP (Extreme Programming)"],
        "Kanban", "module-6-Q4"))
    acts.append(single_choice("ba_method_q5_single", mod, "junior", "ba_method_q5_title", "ba_method_q5_explanation", next_order(mod),
        ["Lean (Бережливое производство)", "Waterfall (Каскадная модель)", "Scrum", "RUP (Rational Unified Process)"],
        "Lean (Бережливое производство)", "module-6-Q5"))
    acts.append(single_choice("ba_method_q6_single", mod, "middle", "ba_method_q6_title", "ba_method_q6_explanation", next_order(mod),
        ["SAFe (Scaled Agile Framework)", "LeSS (Large Scale Scrum)", "Scrum of Scrums", "Nexus"],
        "SAFe (Scaled Agile Framework)", "module-6-Q6"))
    acts.append(single_choice("ba_method_q7_single", mod, "middle", "ba_method_q7_title", "ba_method_q7_explanation", next_order(mod),
        ["Product Owner", "Scrum Master", "Development Team", "Project Manager"],
        "Product Owner", "module-6-Q7"))
    acts.append(single_choice("ba_method_q8_single", mod, "middle", "ba_method_q8_title", "ba_method_q8_explanation", next_order(mod),
        ["Sprint Backlog (бэклог спринта)", "Product Backlog (бэклог продукта)", "Increment (инкремент)", "Definition of Done (DoD)"],
        "Definition of Done (DoD)", "module-6-Q8"))
    acts.append(single_choice("ba_method_q9_single", mod, "senior", "ba_method_q9_title", "ba_method_q9_explanation", next_order(mod),
        ["Гибридная методология (Waterfall + Agile)", "Scrum", "Kanban", "XP (Extreme Programming)"],
        "Гибридная методология (Waterfall + Agile)", "module-6-Q9"))

    # Multiple choice for Methodologies
    acts.append(multiple_choice("ba_method_q10_multi", mod, "junior", "ba_method_q10_title", "ba_method_q10_explanation", next_order(mod),
        ["Sprint Planning", "Daily Scrum", "Sprint Review", "Annual Meeting"],
        ["Sprint Planning", "Daily Scrum", "Sprint Review"], "module-6-Q10"))
    acts.append(multiple_choice("ba_method_q11_multi", mod, "junior", "ba_method_q11_title", "ba_method_q11_explanation", next_order(mod),
        ["Люди и взаимодействие важнее процессов и инструментов", "Работающий продукт важнее исчерпывающей документации",
         "Сотрудничество с заказчиком важнее согласования контракта",
         "Готовность к изменениям важнее следования первоначальному плану"],
        ["Люди и взаимодействие важнее процессов и инструментов", "Работающий продукт важнее исчерпывающей документации",
         "Сотрудничество с заказчиком важнее согласования контракта",
         "Готовность к изменениям важнее следования первоначальному плану"], "module-6-Q11"))
    acts.append(multiple_choice("ba_method_q12_multi", mod, "middle", "ba_method_q12_title", "ba_method_q12_explanation", next_order(mod),
        ["Прозрачность (Transparency)", "Инспекция (Inspection)", "Адаптация (Adaptation)", "Документирование (Documentation)"],
        ["Прозрачность (Transparency)", "Инспекция (Inspection)", "Адаптация (Adaptation)"], "module-6-Q12"))
    acts.append(multiple_choice("ba_method_q13_multi", mod, "senior", "ba_method_q13_title", "ba_method_q13_explanation", next_order(mod),
        ["Частая поставка работающего продукта", "Приветствуется изменение требований", "Тесное сотрудничество бизнеса и разработки", "Полная спецификация в начале"],
        ["Частая поставка работающего продукта", "Приветствуется изменение требований", "Тесное сотрудничество бизнеса и разработки"], "module-6-Q13"))

    # Fill blanks for Methodologies
    acts.append(fill_blanks("ba_method_q14_fill", mod, "junior", "ba_method_q14_title", "ba_method_q14_explanation", next_order(mod),
        "Временной цикл в Scrum, длительностью обычно 2-4 недели, называется ___.",
        [{"id": "blank_0", "options": ["релиз", "спринт", "итерация", "фаза"]}],
        ["спринт"], "module-6-Q14"))
    acts.append(fill_blanks("ba_method_q15_fill", mod, "junior", "ba_method_q15_title", "ba_method_q15_explanation", next_order(mod),
        "Методология, основанная на последовательных фазах (анализ, проектирование, реализация, тестирование, сопровождение), называется ___.",
        [{"id": "blank_0", "options": ["Agile", "Waterfall", "Scrum", "Kanban"]}],
        ["Waterfall"], "module-6-Q15"))
    acts.append(fill_blanks("ba_method_q16_fill", mod, "middle", "ba_method_q16_title", "ba_method_q16_explanation", next_order(mod),
        "В Kanban максимальное количество задач на каждом этапе процесса ограничивается с помощью ___.",
        [{"id": "blank_0", "options": ["WIP limit", "Timebox", "Sprint goal", "Buffer"]}],
        ["WIP limit"], "module-6-Q16"))

    # ============================
    # MODULE 7: ba_metrics_prioritization (16 activities: 10 single + 4 multi + 2 numeric)
    # ============================
    mod = "ba_metrics_prioritization"
    acts.append(single_choice("ba_metric_q1_single", mod, "junior", "ba_metric_q1_title", "ba_metric_q1_explanation", next_order(mod),
        ["MoSCoW (Must, Should, Could, Won't)", "Kano Model", "WSJF (Weighted Shortest Job First)", "RICE (Reach, Impact, Confidence, Effort)"],
        "MoSCoW (Must, Should, Could, Won't)", "module-7-Q1"))
    acts.append(single_choice("ba_metric_q2_single", mod, "junior", "ba_metric_q2_title", "ba_metric_q2_explanation", next_order(mod),
        ["Must have (критически важно)", "Should have (важно, но не критично)", "Could have (желательно)", "Won't have (не будет реализовано)"],
        "Must have (критически важно)", "module-7-Q2"))
    acts.append(single_choice("ba_metric_q3_single", mod, "junior", "ba_metric_q3_title", "ba_metric_q3_explanation", next_order(mod),
        ["Kano Model", "MoSCoW", "WSJF", "RICE"],
        "Kano Model", "module-7-Q3"))
    acts.append(single_choice("ba_metric_q4_single", mod, "junior", "ba_metric_q4_title", "ba_metric_q4_explanation", next_order(mod),
        ["Story Points", "Hours (часы)", "Days (дни)", "Function Points"],
        "Story Points", "module-7-Q4"))
    acts.append(single_choice("ba_metric_q5_single", mod, "middle", "ba_metric_q5_title", "ba_metric_q5_explanation", next_order(mod),
        ["WSJF (Weighted Shortest Job First)", "MoSCoW", "Kano Model", "Value vs Effort Matrix"],
        "WSJF (Weighted Shortest Job First)", "module-7-Q5"))
    acts.append(single_choice("ba_metric_q6_single", mod, "junior", "ba_metric_q6_title", "ba_metric_q6_explanation", next_order(mod),
        ["ROI = (Прибыль - Инвестиции) / Инвестиции × 100%", "ROI = Прибыль / Затраты", "ROI = Доходы - Расходы", "ROI = Прибыль × 100"],
        "ROI = (Прибыль - Инвестиции) / Инвестиции × 100%", "module-7-Q6"))
    acts.append(single_choice("ba_metric_q7_single", mod, "middle", "ba_metric_q7_title", "ba_metric_q7_explanation", next_order(mod),
        ["NPV (Net Present Value) — чистая приведённая стоимость", "IRR (Internal Rate of Return)", "TCO (Total Cost of Ownership)", "Payback Period"],
        "NPV (Net Present Value) — чистая приведённая стоимость", "module-7-Q7"))
    acts.append(single_choice("ba_metric_q8_single", mod, "middle", "ba_metric_q8_title", "ba_metric_q8_explanation", next_order(mod),
        ["Velocity (скорость команды)", "Cycle Time (время цикла)", "Lead Time (время выполнения)", "Throughput (пропускная способность)"],
        "Velocity (скорость команды)", "module-7-Q8"))
    acts.append(single_choice("ba_metric_q9_single", mod, "senior", "ba_metric_q9_title", "ba_metric_q9_explanation", next_order(mod),
        ["One-dimensional (линейное качество)", "Must-be (ожидаемое качество)", "Attractive (привлекательное качество)", "Indifferent (безразличное качество)"],
        "One-dimensional (линейное качество)", "module-7-Q9"))
    acts.append(single_choice("ba_metric_q10_single", mod, "senior", "ba_metric_q10_title", "ba_metric_q10_explanation", next_order(mod),
        ["Value (ценность)", "Time Criticality (срочность)", "Risk Reduction (снижение рисков)", "Opportunity Enablement (открытие возможностей)"],
        "Value (ценность)", "module-7-Q10"))

    # Multiple choice for Metrics
    acts.append(multiple_choice("ba_metric_q11_multi", mod, "junior", "ba_metric_q11_title", "ba_metric_q11_explanation", next_order(mod),
        ["Бизнес-ценность (Business Value)", "Сложность реализации (Complexity)", "Прибыль компании", "Количество строк кода"],
        ["Бизнес-ценность (Business Value)", "Сложность реализации (Complexity)"], "module-7-Q11"))
    acts.append(multiple_choice("ba_metric_q12_multi", mod, "junior", "ba_metric_q12_title", "ba_metric_q12_explanation", next_order(mod),
        ["Определение приоритетов функций", "Планирование релизов", "Управление ожиданиями стейкхолдеров", "Написание кода"],
        ["Определение приоритетов функций", "Планирование релизов", "Управление ожиданиями стейкхолдеров"], "module-7-Q12"))
    acts.append(multiple_choice("ba_metric_q13_multi", mod, "middle", "ba_metric_q13_title", "ba_metric_q13_explanation", next_order(mod),
        ["Baseline (базовая оценка)", "Relative estimation (относительная оценка)", "Planning Poker (покер планирования)", "Random guess (случайное предположение)"],
        ["Baseline (базовая оценка)", "Relative estimation (относительная оценка)", "Planning Poker (покер планирования)"], "module-7-Q13"))
    acts.append(multiple_choice("ba_metric_q14_multi", mod, "senior", "ba_metric_q14_title", "ba_metric_q14_explanation", next_order(mod),
        ["WSJF = Value / Time",
         "Value = Business Value + Time Criticality + Risk Reduction + Opportunity Enablement",
         "WSJF = Cost of Delay / Job Size",
         "Cost of Delay = Value + Time Criticality + Risk Reduction + Opportunity Enablement"],
        ["Value = Business Value + Time Criticality + Risk Reduction + Opportunity Enablement",
         "WSJF = Cost of Delay / Job Size",
         "Cost of Delay = Value + Time Criticality + Risk Reduction + Opportunity Enablement"], "module-7-Q14"))

    # Numeric for Metrics
    acts.append(numeric("ba_metric_q15_number", mod, "middle", "ba_metric_q15_title", "ba_metric_q15_explanation", next_order(mod),
        70, 0, "module-7-Q15"))
    acts.append(numeric("ba_metric_q16_number", mod, "middle", "ba_metric_q16_title", "ba_metric_q16_explanation", next_order(mod),
        48, 0, "module-7-Q16"))

    # ============================
    # MODULE 8: ba_communication_conflict (17 activities: 9 single + 7 multi + 1 fill)
    # ============================
    mod = "ba_communication_conflict"
    acts.append(single_choice("ba_comm_q1_single", mod, "junior", "ba_comm_q1_title", "ba_comm_q1_explanation", next_order(mod),
        ["Умение слушать и задавать вопросы", "Умение программировать", "Знание SQL", "Навыки дизайна"],
        "Умение слушать и задавать вопросы", "module-8-Q1"))
    acts.append(single_choice("ba_comm_q2_single", mod, "junior", "ba_comm_q2_title", "ba_comm_q2_explanation", next_order(mod),
        ["Фасилитация (Facilitation)", "Модерация", "Презентация", "Написание отчётов"],
        "Фасилитация (Facilitation)", "module-8-Q2"))
    acts.append(single_choice("ba_comm_q3_single", mod, "junior", "ba_comm_q3_title", "ba_comm_q3_explanation", next_order(mod),
        ["Подготовить повестку, цели и ожидаемые результаты", "Прийти без подготовки для объективности", "Пригласить только технических специалистов", "Провести встречу без ограничения времени"],
        "Подготовить повестку, цели и ожидаемые результаты", "module-8-Q3"))
    acts.append(single_choice("ba_comm_q4_single", mod, "junior", "ba_comm_q4_title", "ba_comm_q4_explanation", next_order(mod),
        ["Ненасильственное общение (NVC)", "Активное слушание", "Парафраз", "Я-сообщения"],
        "Ненасильственное общение (NVC)", "module-8-Q4"))
    acts.append(single_choice("ba_comm_q5_single", mod, "middle", "ba_comm_q5_title", "ba_comm_q5_explanation", next_order(mod),
        ["Компромисс (Compromise)", "Сотрудничество (Collaboration)", "Избегание (Avoidance)", "Конкуренция (Competition)"],
        "Сотрудничество (Collaboration)", "module-8-Q5"))
    acts.append(single_choice("ba_comm_q6_single", mod, "junior", "ba_comm_q6_title", "ba_comm_q6_explanation", next_order(mod),
        ["RACI Matrix", "Communication Plan", "Stakeholder Register", "Project Charter"],
        "Communication Plan", "module-8-Q6"))
    acts.append(single_choice("ba_comm_q7_single", mod, "middle", "ba_comm_q7_title", "ba_comm_q7_explanation", next_order(mod),
        ["Переговоры (Negotiation)", "Арбитраж (Arbitration)", "Фасилитация (Facilitation)", "Медиация (Mediation)"],
        "Переговоры (Negotiation)", "module-8-Q7"))
    acts.append(single_choice("ba_comm_q8_single", mod, "senior", "ba_comm_q8_title", "ba_comm_q8_explanation", next_order(mod),
        ["Собрать факты, понять интересы сторон, найти взаимовыгодное решение", "Принять сторону заказчика", "Передать вопрос выше", "Прекратить обсуждение"],
        "Собрать факты, понять интересы сторон, найти взаимовыгодное решение", "module-8-Q8"))
    acts.append(single_choice("ba_comm_q9_single", mod, "senior", "ba_comm_q9_title", "ba_comm_q9_explanation", next_order(mod),
        ["Ожидания нужно документировать, согласовывать и регулярно обновлять", "Ожидания достаточно обсудить устно", "Ожидания определяются один раз в начале проекта", "Ожидания не требуют управления"],
        "Ожидания нужно документировать, согласовывать и регулярно обновлять", "module-8-Q9"))

    # Multiple choice for Communication
    acts.append(multiple_choice("ba_comm_q10_multi", mod, "junior", "ba_comm_q10_title", "ba_comm_q10_explanation", next_order(mod),
        ["Вербальная коммуникация", "Письменная коммуникация", "Невербальная коммуникация", "Телепатия"],
        ["Вербальная коммуникация", "Письменная коммуникация", "Невербальная коммуникация"], "module-8-Q10"))
    acts.append(multiple_choice("ba_comm_q11_multi", mod, "junior", "ba_comm_q11_title", "ba_comm_q11_explanation", next_order(mod),
        ["Встречи (Meetings)", "Электронная почта (Email)", "Мессенджеры (Chat)", "Гадание на кофейной гуще"],
        ["Встречи (Meetings)", "Электронная почта (Email)", "Мессенджеры (Chat)"], "module-8-Q11"))
    acts.append(multiple_choice("ba_comm_q12_multi", mod, "junior", "ba_comm_q12_title", "ba_comm_q12_explanation", next_order(mod),
        ["Активное слушание", "Уточнение и парафраз", "Суммирование", "Игнорирование собеседника"],
        ["Активное слушание", "Уточнение и парафраз", "Суммирование"], "module-8-Q12"))
    acts.append(multiple_choice("ba_comm_q13_multi", mod, "middle", "ba_comm_q13_title", "ba_comm_q13_explanation", next_order(mod),
        ["Установление доверия", "Прозрачная и честная коммуникация", "Понимание мотивов стейкхолдеров", "Сокрытие проблем"],
        ["Установление доверия", "Прозрачная и честная коммуникация", "Понимание мотивов стейкхолдеров"], "module-8-Q13"))
    acts.append(multiple_choice("ba_comm_q14_multi", mod, "middle", "ba_comm_q14_title", "ba_comm_q14_explanation", next_order(mod),
        ["Определение (Definition)", "Измерение (Measurement)", "Анализ (Analysis)", "Улучшение (Improvement)"],
        ["Определение (Definition)", "Измерение (Measurement)", "Анализ (Analysis)", "Улучшение (Improvement)"], "module-8-Q14"))
    acts.append(multiple_choice("ba_comm_q15_multi", mod, "senior", "ba_comm_q15_title", "ba_comm_q15_explanation", next_order(mod),
        ["Регулярная обратная связь (Feedback)", "Прозрачность статуса задач", "Участие в принятии решений", "Микроменеджмент"],
        ["Регулярная обратная связь (Feedback)", "Прозрачность статуса задач", "Участие в принятии решений"], "module-8-Q15"))
    acts.append(multiple_choice("ba_comm_q16_multi", mod, "senior", "ba_comm_q16_title", "ba_comm_q16_explanation", next_order(mod),
        ["Собрать все факты и данные", "Выслушать все стороны", "Сосредоточиться на интересах, а не на позициях", "Принять сторону сильнейшего"],
        ["Собрать все факты и данные", "Выслушать все стороны", "Сосредоточиться на интересах, а не на позициях"], "module-8-Q16"))

    # Fill blank for Communication
    acts.append(fill_blanks("ba_comm_q17_fill", mod, "junior", "ba_comm_q17_title", "ba_comm_q17_explanation", next_order(mod),
        "Документ, определяющий каналы, частоту и формат коммуникации между участниками проекта, называется ___.",
        [{"id": "blank_0", "options": ["Communication Plan", "Project Charter", "RACI Matrix", "Risk Register"]}],
        ["Communication Plan"], "module-8-Q17"))

    # ============================
    # MODULE 9: ba_technical_aspects (19 activities: 14 single + 4 multi + 1 numeric)
    # ============================
    mod = "ba_technical_aspects"
    acts.append(single_choice("ba_tech_q1_single", mod, "junior", "ba_tech_q1_title", "ba_tech_q1_explanation", next_order(mod),
        ["SELECT — для чтения данных", "INSERT — для вставки", "UPDATE — для обновления", "DELETE — для удаления"],
        "SELECT — для чтения данных", "module-9-Q1"))
    acts.append(single_choice("ba_tech_q2_single", mod, "junior", "ba_tech_q2_title", "ba_tech_q2_explanation", next_order(mod),
        ["FROM", "WHERE", "JOIN", "GROUP BY"],
        "FROM", "module-9-Q2"))
    acts.append(single_choice("ba_tech_q3_single", mod, "junior", "ba_tech_q3_title", "ba_tech_q3_explanation", next_order(mod),
        ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"],
        "INNER JOIN", "module-9-Q3"))
    acts.append(single_choice("ba_tech_q4_single", mod, "junior", "ba_tech_q4_title", "ba_tech_q4_explanation", next_order(mod),
        ["GET — получение данных", "POST — создание ресурса", "PUT — полное обновление", "DELETE — удаление"],
        "GET — получение данных", "module-9-Q4"))
    acts.append(single_choice("ba_tech_q5_single", mod, "junior", "ba_tech_q5_title", "ba_tech_q5_explanation", next_order(mod),
        ["JSON (JavaScript Object Notation)", "XML (eXtensible Markup Language)", "CSV (Comma-Separated Values)", "YAML"],
        "JSON (JavaScript Object Notation)", "module-9-Q5"))
    acts.append(single_choice("ba_tech_q6_single", mod, "junior", "ba_tech_q6_title", "ba_tech_q6_explanation", next_order(mod),
        ["200 OK", "201 Created", "400 Bad Request", "404 Not Found"],
        "404 Not Found", "module-9-Q6"))
    acts.append(single_choice("ba_tech_q7_single", mod, "junior", "ba_tech_q7_title", "ba_tech_q7_explanation", next_order(mod),
        ["200 OK", "201 Created", "400 Bad Request", "500 Internal Server Error"],
        "500 Internal Server Error", "module-9-Q7"))
    acts.append(single_choice("ba_tech_q8_single", mod, "middle", "ba_tech_q8_title", "ba_tech_q8_explanation", next_order(mod),
        ["REST API — архитектурный стиль на основе HTTP методов", "REST — это база данных", "REST — это язык программирования", "REST — это протокол безопасности"],
        "REST API — архитектурный стиль на основе HTTP методов", "module-9-Q8"))
    acts.append(single_choice("ba_tech_q9_single", mod, "junior", "ba_tech_q9_title", "ba_tech_q9_explanation", next_order(mod),
        ["Пара ключ-значение (Key-Value pair)", "Массив значений", "XML-элемент", "SQL-запрос"],
        "Пара ключ-значение (Key-Value pair)", "module-9-Q9"))
    acts.append(single_choice("ba_tech_q10_single", mod, "middle", "ba_tech_q10_title", "ba_tech_q10_explanation", next_order(mod),
        ["Figma", "Balsamiq Mockups", "Axure RP", "Draw.io"],
        "Balsamiq Mockups", "module-9-Q10"))
    acts.append(single_choice("ba_tech_q11_single", mod, "middle", "ba_tech_q11_title", "ba_tech_q11_explanation", next_order(mod),
        ["Swagger / OpenAPI", "Postman", "cURL", "GitHub"],
        "Swagger / OpenAPI", "module-9-Q11"))
    acts.append(single_choice("ba_tech_q12_single", mod, "junior", "ba_tech_q12_title", "ba_tech_q12_explanation", next_order(mod),
        ["Git", "SVN", "Mercurial", "CVS"],
        "Git", "module-9-Q12"))
    acts.append(single_choice("ba_tech_q13_single", mod, "middle", "ba_tech_q13_title", "ba_tech_q13_explanation", next_order(mod),
        ["MVP (Minimum Viable Product)", "PoC (Proof of Concept)", "Prototype (Прототип)", "Beta (Бета-версия)"],
        "MVP (Minimum Viable Product)", "module-9-Q13"))
    acts.append(single_choice("ba_tech_q14_single", mod, "senior", "ba_tech_q14_title", "ba_tech_q14_explanation", next_order(mod),
        ["CI/CD — автоматизация сборки, тестирования и поставки", "CI/CD — это база данных", "CI/CD — это язык программирования", "CI/CD — это методология управления проектами"],
        "CI/CD — автоматизация сборки, тестирования и поставки", "module-9-Q14"))

    # Multiple choice for Technical
    acts.append(multiple_choice("ba_tech_q15_multi", mod, "middle", "ba_tech_q15_title", "ba_tech_q15_explanation", next_order(mod),
        ["Document stores (MongoDB)", "Key-Value stores (Redis)", "Graph databases (Neo4j)", "Реляционные БД"],
        ["Document stores (MongoDB)", "Key-Value stores (Redis)", "Graph databases (Neo4j)"], "module-9-Q15"))
    acts.append(multiple_choice("ba_tech_q16_multi", mod, "middle", "ba_tech_q16_title", "ba_tech_q16_explanation", next_order(mod),
        ["Acceptance Testing", "Integration Testing", "UAT (User Acceptance Testing)", "Unit Testing разработчиков"],
        ["Acceptance Testing", "Integration Testing", "UAT (User Acceptance Testing)"], "module-9-Q16"))
    acts.append(multiple_choice("ba_tech_q17_multi", mod, "senior", "ba_tech_q17_title", "ba_tech_q17_explanation", next_order(mod),
        ["Monolithic (Монолит)", "Microservices (Микросервисы)", "Event-Driven (Событийно-ориентированная)", "Blockchain (Блокчейн)"],
        ["Monolithic (Монолит)", "Microservices (Микросервисы)", "Event-Driven (Событийно-ориентированная)"], "module-9-Q17"))
    acts.append(multiple_choice("ba_tech_q18_multi", mod, "senior", "ba_tech_q18_title", "ba_tech_q18_explanation", next_order(mod),
        ["Независимый деплой сервисов", "Слабая связанность (loose coupling)", "Технологическое разнообразие", "Единая база данных"],
        ["Независимый деплой сервисов", "Слабая связанность (loose coupling)", "Технологическое разнообразие"], "module-9-Q18"))

    # Numeric for Technical
    acts.append(numeric("ba_tech_q19_number", mod, "junior", "ba_tech_q19_title", "ba_tech_q19_explanation", next_order(mod),
        5, 0, "module-9-Q19"))

    # ============================
    # MODULE 10: ba_real_cases (3 activities: 2 single + 1 fill)
    # ============================
    mod = "ba_real_cases"
    acts.append(single_choice("ba_cases_q1_single", mod, "senior", "ba_cases_q1_title", "ba_cases_q1_explanation", next_order(mod),
        ["Изучить контекст, идентифицировать стейкхолдеров, собрать требования, смоделировать процессы", "Сразу начать писать код", "Нанять новую команду", "Купить готовое решение"],
        "Изучить контекст, идентифицировать стейкхолдеров, собрать требования, смоделировать процессы", "module-10-Q1"))
    acts.append(single_choice("ba_cases_q2_single", mod, "senior", "ba_cases_q2_title", "ba_cases_q2_explanation", next_order(mod),
        ["Собрать данные, провести анализ причин, исследовать пользователей, предложить решения", "Сразу изменить дизайн", "Снизить цены", "Уволить команду"],
        "Собрать данные, провести анализ причин, исследовать пользователей, предложить решения", "module-10-Q2"))
    acts.append(fill_blanks("ba_cases_q3_fill", mod, "middle", "ba_cases_q3_title", "ba_cases_q3_explanation", next_order(mod),
        "Для описания сценария тестирования в BDD используется язык ___.",
        [{"id": "blank_0", "options": ["Python", "Gherkin", "Java", "SQL"]}],
        ["Gherkin"], "module-10-Q3"))

    # ============================
    # Write output
    # ============================
    output_path = PACKAGE_DIR / "activities.json"

    # Sort by module then order
    acts.sort(key=lambda a: (a["module_id"], a["order"]))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(acts, f, ensure_ascii=False, indent=2)

    # Count by type
    type_counts = {}
    for a in acts:
        t = a["activity_type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    total = len(acts)
    print(f"Generated {total} activities:")
    for t, c in sorted(type_counts.items()):
        print(f"  {t}: {c}")
    print(f"  Total: {total}")
    print(f"  Written to: {output_path}")

    # Verify totals
    assert total == 164, f"Expected 164 activities, got {total}"
    assert type_counts.get("single_choice", 0) == 98, f"Expected 98 single_choice, got {type_counts.get('single_choice', 0)}"
    assert type_counts.get("multiple_choice", 0) == 44, f"Expected 44 multiple_choice, got {type_counts.get('multiple_choice', 0)}"
    assert type_counts.get("numeric", 0) == 4, f"Expected 4 numeric, got {type_counts.get('numeric', 0)}"
    assert type_counts.get("fill_blanks", 0) == 13, f"Expected 13 fill_blanks, got {type_counts.get('fill_blanks', 0)}"
    assert type_counts.get("matching", 0) == 5, f"Expected 5 matching, got {type_counts.get('matching', 0)}"

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
