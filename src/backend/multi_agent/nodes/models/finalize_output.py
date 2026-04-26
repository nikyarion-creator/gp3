from pydantic import BaseModel, Field


class FinalizeOutput(BaseModel):
    md_report: str
    executive_summary: str
    key_findings: list[str] = Field(min_length=3)
