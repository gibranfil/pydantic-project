from pathlib import Path
import pandas as pd
import shutil

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
    ".parquet"
}

class DatasetManager:
    def __init__(self):
        self.datasets = {}
    
    def save_dataset(self, name: str, dataframe: pd.DataFrame):
        self.datasets[name] = dataframe
    
    def get_dataset(self, name: str):
        return self.datasets.get(name)
    
    def validate_file(self, filename: str):
        suffix = Path(filename).suffix.lower()

        if suffix not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {suffix}"
            )
        
    def save_uploaded_file(self, upload_file):

        destination = UPLOAD_FOLDER / upload_file.filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

        return destination
    
    def load_dataset(self, path: Path):

        suffix = path.suffix.lower()

        if suffix == ".csv":
            return pd.read_csv(path)

        elif suffix in [".xlsx", ".xls"]:
            return pd.read_excel(path)

        elif suffix == ".parquet":
            return pd.read_parquet(path)

        raise ValueError("Unsupported format")
    
    def save_dataset(self, name: str, dataframe: pd.DataFrame):
        self.datasets[name] = dataframe


    def get_dataset(self, name: str):
        return self.datasets.get(name)
    
    def dataset_summary(self, dataframe):

        return {
            "rows": len(dataframe),
            "columns": list(dataframe.columns),
            "shape": dataframe.shape
        }


dataset_manager = DatasetManager()


