import pandas as pd
from pipeline.transformer.base_transformer import BaseTransformer


class AbsenceTransformer(BaseTransformer):
    def transform(self, data : pd.DataFrame):
        def sql_value(val):
            if pd.isna(val):
                return "NULL"
            return f"""'{str(val).replace("'", "''")}'"""

        data.where(pd.notnull(data), None, inplace=True)
        data = data.apply(lambda col: col.map(sql_value))
        return data
