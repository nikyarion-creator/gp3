from pydantic import BaseModel, Field


class FinalReport(BaseModel):
    report_md_path: str
    report_json_path: str
    executive_summary: str
    key_findings: list[str] = Field(min_length=3)
