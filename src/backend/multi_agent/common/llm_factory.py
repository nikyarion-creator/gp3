from langchain_openai import ChatOpenAI

from configs.config import Config


_config = Config()


def _make(model, temperature, top_p, max_tokens):
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        api_key=_config.OPENROUTER_API_KEY,
        base_url=_config.OPENROUTER_BASE_URL,
        timeout=120,
        model_kwargs={"parallel_tool_calls": True},
    )


def make_supervisor_llm():
    return _make(
        _config.SUPERVISOR_MODEL,
        _config.SUPERVISOR_TEMPERATURE,
        _config.SUPERVISOR_TOP_P,
        _config.SUPERVISOR_MAX_TOKENS,
    )


def make_data_engineer_llm():
    return _make(
        _config.DATA_ENGINEER_MODEL,
        _config.DATA_ENGINEER_TEMPERATURE,
        _config.DATA_ENGINEER_TOP_P,
        _config.DATA_ENGINEER_MAX_TOKENS,
    )


def make_data_analyst_llm():
    return _make(
        _config.DATA_ANALYST_MODEL,
        _config.DATA_ANALYST_TEMPERATURE,
        _config.DATA_ANALYST_TOP_P,
        _config.DATA_ANALYST_MAX_TOKENS,
    )


def make_data_scientist_llm():
    return _make(
        _config.DATA_SCIENTIST_MODEL,
        _config.DATA_SCIENTIST_TEMPERATURE,
        _config.DATA_SCIENTIST_TOP_P,
        _config.DATA_SCIENTIST_MAX_TOKENS,
    )


