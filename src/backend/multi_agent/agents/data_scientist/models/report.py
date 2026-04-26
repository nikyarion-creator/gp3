from pydantic import BaseModel, Field


class BestModel(BaseModel):
    model_name: str
    test_metrics: dict[str, float] = Field(default_factory=dict)


class DataScientistReport(BaseModel):
    report_md_path: str
    feature_dataset_path: str
    best_model: BestModel
    best_model_path: str
