from pathlib import Path

from configs.config import Config


_config = Config()
_root = Path(__file__).resolve().parents[4]


def processed_dir():
    p = _root / _config.PROCESSED_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def memory_dir():
    p = _root / _config.MEMORY_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def reports_dir():
    p = _root / _config.REPORTS_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def agent_reports_dir(agent):
    p = reports_dir() / agent
    p.mkdir(parents=True, exist_ok=True)
    return p


def dataset_path():
    return _root / _config.DATASET_PATH
