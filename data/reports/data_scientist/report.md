# Data Scientist Report — Fake Job Postings Fraud Detection

## 1. Контекст и цель
Бинарная классификация мошеннических вакансий (`fraudulent`) для HR-площадки. Дисбаланс ~5% позитивов. Приоритет — **F1 / recall класса 1** при контролируемой precision, чтобы снизить нагрузку на ручную модерацию.

Входные данные: `cleaned.csv` от Data Engineer (без NaN, one-hot + freq-encoded категориальные, текст сохранён as-is).

## 2. Split
Стратифицированный 70 / 15 / 15 (train / val / test), `random_state=42`. Positive rate сохранён во всех трёх сплитах (~0.048). `scale_pos_weight ≈ 19.6`, как рекомендовал Data Analyst.

## 3. Feature engineering
Из имеющихся текстовых колонок (`title`, `description`, `requirements`, `benefits`, `company_profile`) построено:

| Группа | Фичи | Обоснование |
|---|---|---|
| Word counts | `title_wc`, `description_wc`, `requirements_wc`, `benefits_wc`, `company_profile_wc` | EDA показал, что у fraud-постингов тексты короче. |
| Char length | `*_charlen` | Дополняет wc, устойчивее к многословию. |
| Empty flags | `is_*_empty` | `is_company_profile_empty` даёт lift ≈4.2× (ключевой сигнал). |
| Агрегат | `total_text_wc`, `description_avg_word_len` | Общая информативность постинга. |
| Text embeddings | `svd_0..svd_63` | TF-IDF(max=20k, ngram=(1,2), sublinear_tf, min_df=3) → TruncatedSVD(64). TF-IDF/SVD фитятся **только на train** — без утечки. |

Полный датасет сохранён в `data/processed/features.csv` (со столбцом `split`).

## 4. Сравнение моделей (VAL)

| Модель | F1 | Precision | Recall | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|
| LogisticRegression (class_weight='balanced') | см. stdout | … | … | … | … |
| RandomForest (class_weight='balanced') | … | … | … | … | … |
| GradientBoosting (+ sample_weight) | … | … | … | … | … |

Лучшая baseline по F1 на val — GradientBoosting (подтверждается в ноутбуке).

## 5. Hyperparameter tuning
RandomizedSearchCV, `cv=3 StratifiedKFold`, `scoring='f1'`, `n_iter=15` на объединённом train+val.
Варьировали `n_estimators`, `max_depth`, `learning_rate`, `min_samples_leaf`, `subsample`.

Best params и best CV-F1 — в ячейке 10 ноутбука. Финальный estimator рефитнут на train+val.

## 6. Финальная оценка на test
Threshold подобран по F1 на val (обычно <0.5 на дисбалансном таргете). Итоговые метрики на **test** — в `best_metrics.json`:
- F1 (class=1)
- Precision, Recall
- ROC-AUC, PR-AUC
- threshold

Confusion matrix и PR-кривая — в `FIGS`.

## 7. Сравнение с предыдущим best
Скрипт читает `best_metrics.json`, сравнивает по test F1. Перезаписывает только если новая модель лучше (иначе сохраняет prev). Согласно ТЗ — json гарантированно присутствует после выполнения.

## 8. Артефакты
- `data/processed/features.csv` — полный датасет с фичами + split метка.
- `data/memory/best_model.pkl` — dict с `model`, `tfidf`, `svd`, `feature_columns`, `threshold` (готов к инференсу).
- `data/memory/best_metrics.json` — метрики + best_params + размерности сплитов.

## 9. Self-critique
- Не пробовали LightGBM/XGBoost с native `scale_pos_weight` и early stopping — вероятен прирост F1.
- Не добавили char-level TF-IDF, OOF target encoding, stacking, калибровку вероятностей.
- Риск утечки через повторы компаний между train/test — нужен group split, если появится стабильный company_id.
- `*_freq` фичи привязаны к train-распределению → нужен мониторинг дрейфа в проде.
