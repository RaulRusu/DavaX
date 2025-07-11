import pandas as pd
from .base_extractor import BaseExtractor

class CSVExtractor(BaseExtractor):
    def extract(self, file_path, *args, **kwargs):
        return pd.read_csv(file_path, *args, **kwargs)
