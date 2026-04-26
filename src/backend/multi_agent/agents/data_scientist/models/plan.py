from typing import Literal

from pydantic import BaseModel, Field


class Cell(BaseModel):
    type: Literal["markdown", "code"]
    content: str


class Plan(BaseModel):
    cells: list[Cell] = Field(min_length=8)
    md_report: str
