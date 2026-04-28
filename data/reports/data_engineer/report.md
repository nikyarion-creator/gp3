# Data Engineer Report — fake_job_postings

## Контекст
- **Задача:** бинарная классификация мошеннических вакансий (`fraudulent`).
- **Бизнес-ценность:** снижение ручной модерации, защита пользователей от скам-постингов.
- **Приоритетная метрика:** F1 / recall класса 1 при контроле precision (класс 1 сильно миноритарный, ~5%).
- **Вход:** `data/raw/fake_job_postings.csv` (~17880 строк).
- **Выход:** `/Users/iuriipostnii/Desktop/ГП3/gp3/data/processed/cleaned.csv`.

## Что было сломано в прошлой итерации (QC-1)
1. Детект категориальных был сделан через строковое сравнение dtype (`== 'str'` / `== 'object'` по имени), из-за чего `CAT_COLS` оказывался пустым, и `location/department/employment_type/required_experience/required_education/industry/function` уходили в `NUM_COLS` как сырые строки с ~41k суммарных NaN.
2. `salary_range` дропалась как колонка с >70% NaN **до** парсинга, хотя в стратегии было заявлено извлечение `salary_min/salary_max`. Отчёт и код расходились.

## Что починено в этой итерации
1. Детект категориальных через `pd.api.types.is_object_dtype(col) or pd.api.types.is_string_dtype(col)`. Теперь:
   - `CAT_LOW` (<20 уникальных, one-hot): `employment_type`, `required_experience`, `required_education`, `telecommuting` (если object), `has_company_logo`, `has_questions` — из них one-hot получают именно object-поля с <20 значениями.
   - `CAT_HIGH` (>50 уникальных, frequency encoding): `location`, `department`, `industry`, `function`.
2. `salary_range` парсится в два новых числовых поля `salary_min`/`salary_max` **до** правила drop>70% NaN. Исходная колонка дропается после извлечения сигнала.

## Профиль данных (коротко)
- Target `fraudulent`: сильный дисбаланс (~95/5). DS сам выберет стратегию взвешивания/threshold'а.
- Длинные тексты (`description`, `requirements`, `benefits`, `company_profile`, `title`) — **as_is** (NaN → `""`), фичеризация — зона DS.
- Числовые флаги и счётчики — clip [1, 99] перцентили, impute median.
- Категориальные — mode impute, затем one-hot (<20) либо frequency (>=20).

## Стратегия очистки

| Группа | Правило | Обоснование |
|---|---|---|
| target `fraudulent` | не трогаем | иначе утечка/ломаем задачу |
| `salary_range` | parse → `salary_min`, `salary_max`, затем drop исходной | сохраняем сигнал ДО drop по >70% NaN |
| колонки с >70% NaN | drop_column | шум, нет смысла импутить |
| числовые | clip [p01, p99] + impute median | распределения скошены, есть выбросы |
| cat <20 уникальных | mode impute + one-hot | компактно, без утечки |
| cat 20..50 / >50 | mode impute + frequency encoding | one-hot взорвал бы размерность (тысячи уникальных locations/industries) |
| текстовые поля | NaN → `""`, as_is | фичеризация (TF-IDF/embeddings) — решение DS |

## Что НЕ делалось (осознанно)
- **Не** делаем target encoding — это задача DS под CV, иначе утечка таргета.
- **Не** заполняем 0 в `salary_min`/`salary_max` — 0 там имеет смысл, используем median.
- **Не** балансируем классы — это решение DS (class_weight / SMOTE / threshold tuning).
- **Не** one-hot на `location`/`industry`/`function` — тысячи уникальных.

## Проверки после запуска
- `df.shape` отличается от raw (добавлены `salary_min/max` + one-hot колонки, убраны колонки с >70% NaN).
- `df.isna().sum().sum() == 0`.
- `fraudulent` сохранён.
- Файл записан в `/Users/iuriipostnii/Desktop/ГП3/gp3/data/processed/cleaned.csv`.

## Что дальше делает DS
- Фичеризация текстов (TF-IDF char+word / embeddings / длина, доля заглавных, наличие URL/email).
- Cross-validated target encoding для `location`/`industry`/`function` поверх frequency, если модель попросит.
- Взвешивание классов или калибровка порога под целевой precision.
