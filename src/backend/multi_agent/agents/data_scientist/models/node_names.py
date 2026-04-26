from enum import StrEnum


class DSNodeNames(StrEnum):
    CREATE_NOTEBOOK = "create_notebook"
    TOOLS = "tools"
    FIX = "fix"
    EVALUATE = "evaluate"
    TUNE = "tune"
    SUPERVISOR = "supervisor"
    SUBMIT = "submit"
