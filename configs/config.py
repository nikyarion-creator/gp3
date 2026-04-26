from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    OPENAI_API_KEY: str = ""

    MODEL_GPT_MINI: str = "gpt-4o-mini"
    MODEL_GPT: str = "gpt-4o"
    MODEL_GPT_41_MINI: str = "gpt-4.1-mini"
    MODEL_GPT_41: str = "gpt-4.1"

    SUPERVISOR_MODEL: str = MODEL_GPT_41_MINI
    SUPERVISOR_TEMPERATURE: float = 0.0
    SUPERVISOR_TOP_P: float = 0.9
    SUPERVISOR_MAX_TOKENS: int = 10000

    DATA_ENGINEER_MODEL: str = MODEL_GPT_41_MINI
    DATA_ENGINEER_TEMPERATURE: float = 0.0
    DATA_ENGINEER_TOP_P: float = 0.9
    DATA_ENGINEER_MAX_TOKENS: int = 10000

    DATA_ANALYST_MODEL: str = MODEL_GPT_41_MINI
    DATA_ANALYST_TEMPERATURE: float = 0.1
    DATA_ANALYST_TOP_P: float = 0.95
    DATA_ANALYST_MAX_TOKENS: int = 10000

    DATA_SCIENTIST_MODEL: str = MODEL_GPT_41_MINI
    DATA_SCIENTIST_TEMPERATURE: float = 0.0
    DATA_SCIENTIST_TOP_P: float = 0.9
    DATA_SCIENTIST_MAX_TOKENS: int = 10000

    DATASET_PATH: str = "data/raw/fake_job_postings.csv"
    TARGET_COLUMN: str = "fraudulent"
    BUSINESS_TASK: str = (
        "Бинарная классификация мошеннических вакансий для HR-площадки. "
        "Цель: снизить ручную модерацию и защитить пользователей от скам-постингов. "
        "Метрика-приоритет: F1 / recall класса 1 при контроле precision."
    )

    PROCESSED_DIR: str = "data/processed"
    MEMORY_DIR: str = "data/memory"
    REPORTS_DIR: str = "data/reports"

    MAX_SUPERVISOR_ITERATIONS: int = 11
    MAIN_RECURSION_LIMIT: int = 25
    AGENT_RECURSION_LIMIT: int = 20
