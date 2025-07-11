import pandas as pd
from pipeline.transformer.base_transformer import BaseTransformer

class MultiOutputTransformer(BaseTransformer):
    def transform(self, data : pd.DataFrame):
        raise NotImplementedError("Subclasses should implement this method.")