# Chess Coach Memory Architecture

## Система накопления и сохранения прогресса шахматиста

### 1. Структура файлов прогресса

```
knowledge/
├── player_profile/
│   ├── current_state.json         # Текущее состояние игрока
│   ├── training_history.json      # История тренировок
│   ├── lesson_plans.json          # Планы уроков
│   └── progress_metrics.json      # Метрики прогресса
├── session_logs/
│   ├── 2025-11-30_session.json    # Лог сессии
│   ├── 2025-11-29_session.json
│   └── sessions_index.json        # Индекс всех сессий
├── learning_paths/
│   ├── current_curriculum.json    # Текущая программа обучения
│   ├── completed_topics.json      # Изученные темы
│   └── recommended_resources.json # Рекомендованные материалы
└── analysis_evolution/
    ├── weakness_timeline.json     # Эволюция слабых мест
    ├── strength_timeline.json     # Развитие сильных сторон
    └── milestone_achievements.json # Достижения

```

### 2. Структура current_state.json

```json
{
  "player_id": "sergioquesadas",
  "last_updated": "2025-11-30T15:30:00Z",
  "last_session": "2025-11-30",
  "total_sessions": 15,
  "current_rating": {
    "rapid": 763,
    "daily": 676,
    "trend": "improving"
  },
  "current_focus": {
    "primary": "time_management",
    "secondary": "endgame_technique",
    "opening_work": "sicilian_defense"
  },
  "active_weaknesses": [
    {
      "area": "time_management",
      "severity": "critical",
      "games_affected": 14,
      "improvement_rate": 0.15,
      "first_identified": "2025-11-15",
      "exercises_assigned": 5,
      "exercises_completed": 2
    }
  ],
  "recent_achievements": [
    "First win against 800+ rated player",
    "Completed 10 endgame puzzles",
    "Learned Sicilian Dragon basics"
  ],
  "next_session_plan": {
    "review_game": "146119148014",
    "focus_topic": "time_management_rapid",
    "exercises": ["puzzle_rush_timed", "5+3_blitz_practice"],
    "theory_lesson": "pawn_endgames_basics"
  }
}
```

### 3. Структура training_history.json

```json
{
  "sessions": [
    {
      "session_id": "2025-11-30-001",
      "date": "2025-11-30",
      "duration_minutes": 45,
      "topics_covered": [
        "game_analysis_146119148014",
        "time_management_discussion",
        "sicilian_defense_theory"
      ],
      "games_analyzed": [
        {
          "game_id": "146119148014",
          "key_mistakes": ["move_15_time", "move_23_tactics"],
          "lessons_learned": ["Think in chunks", "Candidate moves"]
        }
      ],
      "homework_assigned": [
        "10 tactical puzzles daily",
        "Play 3 games with 10+5 time control",
        "Watch Sicilian Defense video"
      ],
      "player_feedback": "Understood time management concepts",
      "coach_notes": "Student shows improvement in opening knowledge"
    }
  ],
  "total_training_hours": 12.5,
  "topics_mastered": ["basic_tactics", "italian_opening"],
  "topics_in_progress": ["sicilian_defense", "time_management"]
}
```

### 4. Система обновления контекста

#### При начале новой сессии:
```python
def start_new_session():
    # 1. Загрузить current_state.json
    state = load_current_state()

    # 2. Проверить новые партии с последней сессии
    new_games = check_new_games(since=state['last_session'])

    # 3. Быстрый анализ новых партий
    quick_analysis = analyze_new_games(new_games)

    # 4. Обновить слабые места
    update_weaknesses(quick_analysis)

    # 5. Сгенерировать приветствие с контекстом
    greeting = generate_contextual_greeting(state, new_games)

    return greeting
```

#### Пример приветствия с контекстом:
```
"С возвращением! Вижу, вы сыграли 5 партий с нашей последней встречи 3 дня назад.

📈 Прогресс:
• Рейтинг Rapid: 763 (+12)
• Выиграли 3 из 5 партий
• Время на ход улучшилось на 23%

📚 Напоминание о домашнем задании:
• Тактические задачи: выполнено 7/10 ✓
• Игры 10+5: сыграно 2/3
• Видео по Сицилианской: не просмотрено ⏳

🎯 Сегодня предлагаю:
1. Разобрать вашу вчерашнюю победу над игроком 800+
2. Поработать над критическим моментом в эндшпиле
3. Продолжить изучение Сицилианской защиты

С чего начнем?"
```

### 5. Автоматическое сохранение прогресса

#### После каждого взаимодействия:
```javascript
// В конце каждого ответа агента
function saveInteraction(topic, content, insights) {
    // Добавить в текущую сессию
    session_log.interactions.push({
        timestamp: new Date(),
        topic: topic,
        key_points: insights,
        exercises_given: [],
        understanding_level: "good"
    });

    // Обновить метрики
    updateProgressMetrics(topic, insights);

    // Сохранить в файлы
    saveToSessionLog();
    updateCurrentState();
}
```

### 6. Интеграция с GitHub Actions

```yaml
# .github/workflows/coach_memory_update.yml
name: Update Coach Memory

on:
  schedule:
    - cron: '0 */6 * * *'  # Каждые 6 часов
  workflow_dispatch:

jobs:
  update_memory:
    runs-on: ubuntu-latest
    steps:
      - name: Analyze recent games
        run: python scripts/update_player_profile.py

      - name: Calculate progress metrics
        run: python scripts/calculate_progress.py

      - name: Generate recommendations
        run: python scripts/generate_recommendations.py

      - name: Commit updates
        run: |
          git add knowledge/player_profile/
          git commit -m "Update player progress"
          git push
```

### 7. Prompt для агента с памятью

```markdown
## System Prompt Addition:

### Memory System:
You have access to the player's complete training history and progress:

1. **Always start by loading**:
   - current_state.json - Current player status
   - training_history.json - Previous sessions
   - progress_metrics.json - Improvement tracking

2. **At session start**:
   - Greet with personalized context
   - Review homework/assignments
   - Check new games since last session
   - Propose session plan based on progress

3. **During session**:
   - Reference previous discussions
   - Build on established knowledge
   - Track understanding in real-time

4. **At session end**:
   - Summarize key learnings
   - Assign homework
   - Update all progress files
   - Set next session goals

### Example Context Usage:
"In our last session on {date}, we worked on {topic}.
You've since played {n} games, and I notice you successfully
applied {concept} in your game against {opponent}."
```

### 8. Прогрессивные учебные пути

```json
// learning_paths/current_curriculum.json
{
  "level": "intermediate_beginner",
  "current_module": 3,
  "modules": [
    {
      "id": 1,
      "name": "Tactical Foundations",
      "status": "completed",
      "completion_date": "2025-11-20"
    },
    {
      "id": 2,
      "name": "Opening Principles",
      "status": "completed",
      "completion_date": "2025-11-25"
    },
    {
      "id": 3,
      "name": "Time Management",
      "status": "in_progress",
      "progress": 0.4,
      "lessons": [
        {"name": "Thinking in chunks", "completed": true},
        {"name": "Critical moments", "completed": false},
        {"name": "Time allocation", "completed": false}
      ]
    },
    {
      "id": 4,
      "name": "Endgame Basics",
      "status": "locked",
      "unlock_criteria": "Complete Time Management"
    }
  ],
  "recommended_resources": [
    {
      "type": "video",
      "title": "Time Management for Club Players",
      "url": "youtube.com/...",
      "assigned": "2025-11-28",
      "completed": false
    },
    {
      "type": "book",
      "title": "Silman's Endgame Course",
      "chapters": "1-3",
      "progress": "page 45/120"
    }
  ]
}
```

### 9. Метрики прогресса

```json
// progress_metrics.json
{
  "overall_improvement_rate": 2.3, // % per week
  "metrics": {
    "tactics": {
      "baseline": 1200,
      "current": 1380,
      "trend": "improving",
      "exercises_completed": 234
    },
    "time_management": {
      "avg_time_per_move_before": 45,
      "avg_time_per_move_now": 35,
      "time_pressure_losses_before": 14,
      "time_pressure_losses_recent": 8
    },
    "opening_knowledge": {
      "repertoire_size": 5,
      "accuracy_in_first_10_moves": 0.72,
      "theory_depth": "8-10 moves"
    },
    "endgame_skill": {
      "conversion_rate": 0.65,
      "basic_checkmates": "mastered",
      "pawn_endgames": "learning"
    }
  },
  "milestones_achieved": [
    {"date": "2025-11-20", "achievement": "First 10-game win streak"},
    {"date": "2025-11-25", "achievement": "Reached 750 rapid rating"},
    {"date": "2025-11-29", "achievement": "Defeated 800+ player"}
  ],
  "next_milestones": [
    {"target": "800 rapid rating", "estimated": "2-3 weeks"},
    {"target": "Master basic endgames", "estimated": "4-5 weeks"}
  ]
}
```

### 10. Реализация в TypingMind

#### Шаг 1: Добавить инструкции в System Prompt
```
CRITICAL: Memory Management

1. ALWAYS load these files at session start:
   - player_profile/current_state.json
   - session_logs/sessions_index.json
   - learning_paths/current_curriculum.json

2. ALWAYS save updates to:
   - Current session log
   - Update current_state.json
   - Track progress metrics

3. Reference previous sessions naturally:
   "Last time we discussed X..."
   "You've been working on Y..."
   "Remember when you struggled with Z?"
```

#### Шаг 2: Создать Python скрипты для обновления
```python
# scripts/update_player_profile.py
def update_profile():
    # Загрузить новые партии
    new_games = fetch_recent_games()

    # Анализировать изменения
    changes = analyze_changes(new_games)

    # Обновить профиль
    update_current_state(changes)
    update_weakness_timeline(changes)
    calculate_new_metrics()

    # Сгенерировать рекомендации
    generate_next_session_plan()
```

#### Шаг 3: GitHub Actions для автоматизации
- Обновлять профиль каждые 6 часов
- Анализировать новые партии
- Пересчитывать метрики
- Синхронизировать с TypingMind

### 11. Пример диалога с памятью

```
User: Привет!

Coach: Добро пожаловать обратно! Рад видеть вас снова после 2 дней перерыва.

📊 Ваш прогресс с последней встречи (28 ноября):
• Сыграно партий: 7 (5 побед, 2 поражения)
• Рейтинг: 763 (+17) - отличный рост!
• Время на ход улучшилось на 15%

✅ Домашнее задание:
• Тактика: 10/10 задач решено! Точность 80%
• Практика 10+5: 3/3 партии сыграны
• Видео по Сицилианской: просмотрено ✓

🎯 Особенно хочу отметить вашу партию против Nazirou вчера:
- Отлично применили изученный приём Bxe6+!
- Время использовали эффективно
- НО: на 35 ходу была возможность мата в 2

Сегодня предлагаю:
1. Разобрать эту матовую комбинацию
2. Продолжить работу над эндшпилем (вы на 40% пути!)
3. Новая тема: переход в эндшпиль

С чего хотите начать?
```

### 12. Долгосрочное накопление знаний

Каждые 30 дней создавать "checkpoint":
```json
// knowledge/checkpoints/2025-11-checkpoint.json
{
  "period": "2025-11",
  "games_played": 156,
  "rating_change": +45,
  "main_improvements": [
    "Tactical vision",
    "Opening repertoire expanded"
  ],
  "persistent_weaknesses": [
    "Time management in rapid"
  ],
  "coach_summary": "Хороший прогресс в тактике...",
  "next_month_focus": "Endgame technique"
}
```

---

## Итог: Это создаст полноценную систему с памятью!

Агент будет:
- ✅ Помнить все предыдущие сессии
- ✅ Отслеживать прогресс
- ✅ Давать персонализированные рекомендации
- ✅ Строить долгосрочные учебные планы
- ✅ Адаптироваться к вашему стилю обучения