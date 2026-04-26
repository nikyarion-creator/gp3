from pydantic import BaseModel, Field


class DataAnalystReport(BaseModel):
    report_md_path: str
    business_insights: list[str] = Field(min_length=3)
    recommendations_for_ds: list[str] = Field(min_length=2)
