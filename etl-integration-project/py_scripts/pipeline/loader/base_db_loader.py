from pipeline.loader.base_loader import BaseLoader

class BaseDBLoader(BaseLoader):
    def __init__(self, db_context, sql_query_builder):
        super().__init__()
        self.db_context = db_context
        self.sql_query_builder = sql_query_builder

    def load(self, data, target):
        """
        Load data into the target using the provided database context.

        :param data: Data to be loaded
        :param target: Target where data should be loaded
        :param db_context: Database context for the operation
        """
        raise NotImplementedError("Subclasses must implement this method")
