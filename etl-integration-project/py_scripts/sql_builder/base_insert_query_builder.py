class BaseInsertQueryBuilder:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.insert_columns = []
        self.values_list = []

    def into(self, *columns):
        self.insert_columns.extend(columns)
        return self

    def values(self, *values):
        self.values_list.extend(values)
        return self

    def build(self):
        if not self.insert_columns or not self.values_list:
            raise ValueError("Insert columns and values must be specified")

        columns_str = ", ".join(self.insert_columns)
        # create string from self.values
        values_str = ""

        for val in self.values_list:
            values_str += f"{val}, "

        values_str = values_str[:-2]  # remove trailing comma and space

        sql = f"""
        INSERT INTO {self.table_name} 
        ({columns_str}) 
        VALUES ({values_str})
        """
        
        self.reset()
        return sql

    def reset(self):
        self.insert_columns = []
        self.values_list = []
        return self