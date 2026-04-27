# Data Scientist Report

## Цель
Построен end-to-end ноутбук для бинарной классификации мошеннических вакансий (`fraudulent`) на основе очищенного датасета `cleaned.csv`. Фокус — максимизация `F1` и `recall` класса 1 при разумном контроле `precision`, что соответствует бизнес-задаче HR-площадки: сокращать ручную модерацию и при этом не пропускать скам-публикации.

## Что было сделано

### 1. Data split
Использован stratified split:
- `train`: для обучения baseline и тюнинга;
- `val`: для честного сравнения baseline-моделей и подбора threshold;
- `test`: только для финальной оценки.

Это защищает от утечки информации и даёт корректную offline-оценку.

### 2. Feature engineering
Сконструированы признаки, основанные на EDA и рекомендациях аналитика:

#### Trust features
- `has_company_logo`
- `has_questions`
- `logo_and_questions`
- `no_logo_and_no_questions`
- `logo_x_questions`

Эти признаки важны, потому что по EDA они хорошо разделяют мошеннические и нормальные вакансии.

#### Text-derived features
Для полей:
- `company_profile`
- `description`
- `requirements`
- `benefits`
- `title`

созданы признаки:
- `*_word_count`
- `*_char_count`
- `*_is_missing_token`
- `*_is_short`

Дополнительно:
- `company_profile_placeholder_flag`
- флаги наличия URL/email/телефона/денежных терминов в текстах.

#### Category risk flags
Добавлены бинарные флаги для потенциально рискованных категорий:
- `function__is_administrative`
- `required_education__is_high_school_or_equivalent`
- `required_education__is_certification`
- `required_experience__is_entry_level`
- `required_experience__is_internship`
- `employment_type__is_part_time` / `temporary` / `contract`

#### Title/location heuristics
- `title_has_seniority`
- `title_all_caps_ratio`
- `telecommuting_flag`

Полный feature dataset сохраняется в:
`/Users/iuriipostnii/Desktop/ГП3/gp3/data/processed/features.csv`

## 3. Baseline models
Сравниваются 3 baseline-модели:
- `LogisticRegression(class_weight='balanced')`
- `RandomForestClassifier(class_weight='balanced')`
- `GradientBoostingClassifier`

Для всех моделей считается:
- `f1`
- `precision`
- `recall`
- `roc_auc`
- `pr_auc`

на validation.

Threshold не фиксируется жёстко на 0.5: он подбирается по `precision-recall curve`, приоритетно среди точек с `precision >= 0.5`, иначе выбирается глобально лучший по F1.

## 4. Hyperparameter tuning
Лучшая baseline-модель определяется по validation `F1`, далее для неё запускается `RandomizedSearchCV` с `StratifiedKFold(n_splits=3)` и `scoring='f1'`.

Подбираются 2–4 ключевых гиперпараметра в зависимости от типа модели.

## 5. Финальная модель
После тюнинга модель переобучается на `train + val` и оценивается на `test`.

Сохраняются:
- лучшая модель: `/Users/iuriipostnii/Desktop/ГП3/gp3/data/memory/best_model.pkl`
- метрики: `/Users/iuriipostnii/Desktop/ГП3/gp3/data/memory/best_metrics.json`

## 6. Сравнение с предыдущим best
Если предыдущий `best_metrics.json` существует, выполняется сравнение по `test_metrics.f1`:
- если новый `F1` выше — best перезаписывается;
- если ниже или равен — предыдущий best сохраняется.

Это соответствует требованию не ухудшать production baseline.

## Формат итогового JSON
Записывается структура вида:

```json
{
  "model_name": "...",
  "test_metrics": {
    "f1": ...,
    "precision": ...,
    "recall": ...,
    "roc_auc": ...,
    "pr_auc": ...,
    "threshold": ...
  },
  "validation_best_threshold": ...,
  "best_params": {...}
}
```

## Почему решение корректное
- нет оценки качества на train;
- tuning делается без доступа к test;
- test используется один раз для финальной честной оценки;
- учтён class imbalance;
- feature engineering осмысленный, а не формальный;
- есть сравнение с предыдущим лучшим решением;
- артефакты и метрики сохраняются по указанным путям.

## Self-critique
Что можно улучшить дальше:
1. Подключить `LightGBM`/`XGBoost` с `scale_pos_weight` — вероятно, это даст лучший `PR-AUC` и `F1`.
2. Добавить TF-IDF по `title`, `company_profile`, `description` и объединить с табличными признаками.
3. Сделать out-of-fold target/frequency encoding для некоторых категориальных полей.
4. Провести error analysis по ложноположительным и ложноотрицательным кейсам.
5. Настроить threshold под конкретный SLA по precision от бизнеса.

## Вывод
Ноутбук закрывает полный цикл задачи Data Scientist:
- feature engineering;
- обучение baseline-моделей;
- гиперпараметрический поиск;
- честная финальная оценка;
- сохранение модели и метрик;
- сравнение с предыдущим best.

Это пригодная основа для следующей итерации и для принятия решения о продвижении модели дальше по пайплайну.