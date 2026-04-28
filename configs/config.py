from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    BASE_MODEL: str = "anthropic/claude-opus-4.7"

    SUPERVISOR_MODEL: str = BASE_MODEL
    SUPERVISOR_TEMPERATURE: float = 0.01
    SUPERVISOR_TOP_P: float = 0.85
    SUPERVISOR_MAX_TOKENS: int = 10000

    DATA_ENGINEER_MODEL: str = BASE_MODEL
    DATA_ENGINEER_TEMPERATURE: float = 0.01
    DATA_ENGINEER_TOP_P: float = 0.90
    DATA_ENGINEER_MAX_TOKENS: int = 10000

    DATA_ANALYST_MODEL: str = BASE_MODEL
    DATA_ANALYST_TEMPERATURE: float = 0.2
    DATA_ANALYST_TOP_P: float = 0.95
    DATA_ANALYST_MAX_TOKENS: int = 12000

    DATA_SCIENTIST_MODEL: str = BASE_MODEL
    DATA_SCIENTIST_TEMPERATURE: float = 0.1
    DATA_SCIENTIST_TOP_P: float = 0.90
    DATA_SCIENTIST_MAX_TOKENS: int = 12000

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
