# Финальный отчёт — детекция мошеннических вакансий (fake_job_postings)

Задача: бинарная классификация постингов вакансий по признаку `fraudulent` для HR-площадки. Цель бизнеса — снизить нагрузку на ручную модерацию и защитить соискателей от скам-вакансий. Приоритетная метрика — **F1 / recall класса 1 при контролируемой precision**, поскольку класс «мошенник» сильно миноритарный (~5%).

## Executive summary

Команда прошла полный цикл: очистка → EDA → обучение модели → отбор лучшего кандидата и его упаковка под инференс. Исходный датасет ~17 880 строк, доля фрода ~5%. Data Engineer исправил баги прошлой итерации (неправильный детект категориальных, преждевременный drop `salary_range`) и выдал чистый `cleaned.csv` без NaN. Data Analyst подтвердил сильный дисбаланс классов и выделил устойчивые сигналы во фродовых объявлениях: короткие тексты и пустые поля (особенно `company_profile`). Data Scientist собрал числовые, категориальные и текстовые фичи (TF-IDF → SVD-64), сравнил три модели и вывел в прод тюненный **GradientBoosting** с подбором порога по F1. Артефакты готовы к инференсу (`best_model.pkl`, `best_metrics.json`), но конкретные итоговые значения метрик на test в текстовых отчётах явно не прописаны — они лежат только в JSON.

## Ключевые находки

- **Сильный дисбаланс.** Positive rate ~4.8% во всех сплитах, `scale_pos_weight ≈ 19.6`. Без взвешивания классов и подбора порога модель бесполезна.
- **Главный одиночный сигнал — пустой `company_profile`.** Флаг `is_company_profile_empty` даёт lift по fraud rate ≈ **4.2×** относительно baseline.
- **Фрод — это короткие тексты.** Word count и char length по `title`, `description`, `requirements`, `benefits`, `company_profile` систематически ниже у мошеннических постингов. Все эти поля ушли в модель как `*_wc`, `*_charlen` и `is_*_empty`.
- **Категориальные с большой кардинальностью (`location`, `department`, `industry`, `function`)** обработаны через frequency encoding — one-hot дал бы тысячи колонок. Низкокардинальные — через one-hot.
- **Salary-сигнал не потерян.** `salary_range` распарсен в `salary_min`/`salary_max` **до** правила drop>70% NaN — в прошлой итерации этот сигнал терялся.
- **Лучший кандидат — GradientBoosting** (после RandomizedSearchCV, 15 итераций, cv=3, scoring=F1), упакован вместе с TF-IDF и SVD в `data/memory/best_model.pkl`.

## Что сделал Data Engineer

**Вход:** `data/raw/fake_job_postings.csv` (~17 880 строк). **Выход:** `data/processed/cleaned.csv`, NaN = 0.

Что починено по сравнению с прошлой итерацией:
1. Детект категориальных переведён на `pd.api.types.is_object_dtype / is_string_dtype` — раньше из-за строкового сравнения dtype категориальные колонки (`location`, `department`, `employment_type`, `required_experience`, `required_education`, `industry`, `function`) уходили в числовые с ~41k суммарных NaN.
2. `salary_range` теперь парсится в `salary_min` / `salary_max` **перед** drop-правилом по >70% NaN.

Стратегия очистки:
- Числовые: clip [p01, p99] + impute median.
- Категориальные <20 уникальных: mode + one-hot.
- Категориальные ≥50 уникальных (`location`, `department`, `industry`, `function`): mode + frequency encoding.
- Тексты (`title`, `description`, `requirements`, `benefits`, `company_profile`): NaN → `""`, без трансформаций (фичеризация — зона DS).
- Target `fraudulent` не трогается, классы не балансируются на этапе DE.

## Что нашёл Data Analyst

EDA построен в plotly (11 графиков), `DF` не модифицируется. Главные выводы для DS:

- **Таргет.** Распределение ~95/5, классический rare-event. Нужны class_weight / threshold tuning / resampling.
- **Числовые фичи.** Корреляции с таргетом по отдельности слабые; сильных одиночных числовых предикторов нет — работают в композиции.
- **Категориальные.** По топ-3 колонкам с кардинальностью 2..500 посчитан mean(target) с lift к baseline — видны «горячие» категории, но осторожно: нужен OOF target encoding, иначе утечка.
- **Тексты — ключ.** У фрода систематически меньше word count в `description` и чаще пустые `company_profile` / `benefits`. Empty-rate и word_count по классам расходятся визуально в разы.

Рекомендации DS: baseline = LogReg + TF-IDF; strong model = градиентный бустинг на (num + freq + text-length + empty-флаги + TF-IDF); target encoding — только через OOF; обязательно threshold tuning под PR-цель.

## Что обучил Data Scientist

**Split:** стратифицированный 70/15/15, `random_state=42`, positive rate ~0.048 во всех частях.

**Feature engineering:**
- Word count по каждому тексту: `title_wc`, `description_wc`, `requirements_wc`, `benefits_wc`, `company_profile_wc`.
- Char length: `*_charlen`.
- Empty-флаги: `is_*_empty` (лучший — `is_company_profile_empty`, lift ≈ 4.2×).
- Агрегаты: `total_text_wc`, `description_avg_word_len`.
- Текстовые эмбеддинги: TF-IDF (max_features=20 000, ngram=(1,2), sublinear_tf, min_df=3) → TruncatedSVD(64 компоненты). Фит — **только на train**, без утечки.

Полный датасет с фичами и меткой split — в `data/processed/features.csv`.

**Сравнение моделей (на val):** LogisticRegression (class_weight='balanced'), RandomForest (class_weight='balanced'), GradientBoosting (+ sample_weight). По F1 на val лучшей оказалась **GradientBoosting**. Конкретные значения F1 / Precision / Recall / ROC-AUC / PR-AUC в таблице отчёта DS оставлены как «…» — то есть в текстовом отчёте они не зафиксированы, реальные числа лежат в stdout ноутбука и в `best_metrics.json`.

**Tuning:** RandomizedSearchCV, `cv=3 StratifiedKFold`, `scoring='f1'`, `n_iter=15` на train+val. Варьировались `n_estimators`, `max_depth`, `learning_rate`, `min_samples_leaf`, `subsample`. Финальный estimator рефитнут на train+val.

**Финальная оценка на test:** порог подбирается по F1 на val (на дисбалансе обычно <0.5). Итоговые метрики (F1 класса 1, Precision, Recall, ROC-AUC, PR-AUC, threshold) записаны в `data/memory/best_metrics.json` — **явные числовые значения в текстовом отчёте DS не приведены**, поэтому здесь их не цитируем.

**Артефакты в проде:**
- `data/processed/features.csv` — датасет с фичами и split-меткой.
- `data/memory/best_model.pkl` — dict с `model`, `tfidf`, `svd`, `feature_columns`, `threshold`.
- `data/memory/best_metrics.json` — метрики + best_params + размеры сплитов.

**Self-critique DS:**
- Не пробовали LightGBM / XGBoost с native `scale_pos_weight` и early stopping — возможен прирост F1.
- Не добавили char-level TF-IDF, OOF target encoding, stacking, калибровку вероятностей.
- Риск утечки через повторы компаний между train/test — нужен group split при появлении стабильного `company_id`.
- `*_freq` фичи привязаны к train-распределению → нужен мониторинг дрейфа в проде.

## Что дальше

- **Проверить LightGBM/XGBoost** с native `scale_pos_weight` и early stopping — самый вероятный быстрый прирост F1 над текущим GradientBoosting.
- **Group-split по компании.** Если поднять стабильный `company_id`, заменить стратифицированный сплит на GroupKFold — уберёт оптимистичный bias от повторяющихся работодателей.
- **OOF target encoding** для `location` / `industry` / `function` поверх текущего frequency encoding; параллельно добавить char-level TF-IDF и калибровку вероятностей (для осмысленного порога под бизнес-precision).
- **Мониторинг в проде:** дрейф распределений `*_freq` фичей и доли пустых `company_profile`; периодический refit TF-IDF/SVD по свежему train-окну.
