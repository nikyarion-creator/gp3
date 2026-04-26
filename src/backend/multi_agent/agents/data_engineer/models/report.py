from pydantic import BaseModel


class DataEngineerReport(BaseModel):
    cleaned_dataset_path: str
    report_md_path: str
