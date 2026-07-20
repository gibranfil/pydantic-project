from dataclasses import dataclass
from pathlib import Path
import shutil

import pandas as pd
from fastapi import UploadFile

from app.profiler.profiler import DatasetProfiler
from app.models import DatasetProfile

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
    ".parquet",
}


@dataclass
class DatasetRecord:
    dataframe: pd.DataFrame
    profile: DatasetProfile
    filepath: Path


class DatasetManager:

    def __init__(self):
        self.datasets: dict[str, DatasetRecord] = {}

    ##########################################################
    # Upload
    ##########################################################

    def upload_dataset(self, upload_file: UploadFile):

        self.validate_file(upload_file.filename)

        filepath = self.save_uploaded_file(upload_file)

        dataframe = self.load_dataset(filepath)

        profiler = DatasetProfiler(
            dataframe=dataframe,
            filename=upload_file.filename,
        )

        profile = profiler.build_profile()

        self.datasets[upload_file.filename] = DatasetRecord(
            dataframe=dataframe,
            profile=profile,
            filepath=filepath,
        )

        return profile

    ##########################################################
    # Validation
    ##########################################################

    def validate_file(self, filename: str):

        suffix = Path(filename).suffix.lower()

        if suffix not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {suffix}"
            )

    ##########################################################
    # Save uploaded file
    ##########################################################

    def save_uploaded_file(self, upload_file: UploadFile):

        destination = UPLOAD_FOLDER / upload_file.filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

        return destination

    ##########################################################
    # Read dataset
    ##########################################################

    def load_dataset(self, filepath: Path):

        suffix = filepath.suffix.lower()

        if suffix == ".csv":
            return pd.read_csv(filepath)

        elif suffix in [".xlsx", ".xls"]:
            return pd.read_excel(filepath)

        elif suffix == ".parquet":
            return pd.read_parquet(filepath)

        raise ValueError("Unsupported file format.")

    ##########################################################
    # Get dataframe
    ##########################################################

    def get_dataframe(self, filename: str):

        dataset = self.datasets.get(filename)

        if dataset is None:
            raise ValueError("Dataset not found.")

        return dataset.dataframe

    ##########################################################
    # Get profile
    ##########################################################

    def get_profile(self, filename: str):

        dataset = self.datasets.get(filename)

        if dataset is None:
            raise ValueError("Dataset not found.")

        return dataset.profile

    ##########################################################
    # List datasets
    ##########################################################

    def list_datasets(self):

        return list(self.datasets.keys())

    ##########################################################
    # Delete dataset
    ##########################################################

    def delete_dataset(self, filename: str):

        dataset = self.datasets.get(filename)

        if dataset is None:
            raise ValueError("Dataset not found.")

        if dataset.filepath.exists():
            dataset.filepath.unlink()

        del self.datasets[filename]


dataset_manager = DatasetManager()