# Data Analyst Report — EDA `fake_job_postings` (cleaned)

## Бизнес-контекст
- **Задача:** бинарная классификация мошеннических вакансий (`fraudulent`) на HR-площадке.
- **Зачем:** снизить нагрузку на ручную модерацию и защитить соискателей от скам-постингов.
- **Метрика:** F1 / recall класса 1 при контроле precision (класс 1 — ~5% выборки).
- **Вход EDA:** `data/processed/cleaned.csv` (после очистки Data Engineer).

## Структура ноутбука

### 1. Setup и обзор датасета
- Загрузка `cleaned.csv`, `print(shape/dtypes/head/memory)`.
- Разделение колонок на числовые / категориальные (низкая кардинальность) / текстовые (длинные строки, avg_len > 40).
- `describe()` для числовых + NaN-rate top-15 как санчек, что DE всё действительно импутировал.

### 2. Анализ target `fraudulent` (2 графика)
- `value_counts`, positive rate, imbalance ratio.
- **Fig 1:** bar chart counts классов.
- **Fig 2:** pie chart долей.
- Ожидается: ~95/5, сильный дисбаланс → DS выбирает class_weight / threshold / resampling.

### 3. Числовые признаки vs target (3 графика)
- Корреляционная матрица Пирсона, top-10 признаков по |corr| с таргетом.
- **Fig 3:** heatmap корреляций (num + target).
- **Fig 4:** горизонтальный bar chart |corr| с target для всех числовых — быстрый ранжир.
- **Fig 5 + Fig 5b:** overlapping histogram (density) для top-2 признаков по |corr| — видно, «расходятся» ли распределения между классами.

### 4. Категориальные признаки (3 графика)
- Cardinality всех cat-колонок, выбор top-3 с уникальных в диапазоне 2..500.
- Для каждой — mean(target) и count по топ-10 самым частым категориям + lift vs baseline.
- **Fig 6-8:** horizontal bar chart mean fraud rate по топ-10 категориям для каждой из top-3 cat колонок, линия baseline.

### 5. Текстовые признаки (3 графика)
- Word count и empty-rate по text-колонкам.
- Mean word_count по классам target, empty-rate по классам target.
- **Fig 9:** overlapping histogram word_count главного текстового поля (обычно `description`) по классам (clip p99).
- **Fig 10:** grouped bar chart empty-rate по text-колонкам × target.
- **Fig 11:** grouped bar chart mean word_count по text-колонкам × target.

### 6. Сводка и рекомендации DS
- Сигналы в числовых, категориальных и текстовых фичах.
- Практические советы: baseline = LogReg+TF-IDF, strong model = LGBM на num + freq + text-length/empty флагах, осторожно с target encoding (только OOF), threshold tuning под PR.

## Качество EDA
- **11 plotly-графиков** в `FIGS` (без matplotlib/seaborn).
- Каждая code-ячейка печатает конкретные числа: shape, dtype counts, NaN-rates, value_counts, imbalance, top-10 |corr|, mean-target по категориям с lift, word_count/empty-rate по классам → analyze-нода извлечёт бизнес-инсайты из реальных чисел.
- `DF` не модифицируется (никаких fillna/drop/encode сверх того, что уже сделал DE).
- Код устойчив: если эвристика не задетектировала текстовые колонки, есть fallback на известные поля job-posting датасета.
