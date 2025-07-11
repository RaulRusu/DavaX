from base_extractor import BaseExtractor
import pandas as pd

class ExcelExtractor(BaseExtractor):
    def extract(self, file_path, *args, **kwargs):
        return pd.read_excel(file_path, *args, **kwargs)
