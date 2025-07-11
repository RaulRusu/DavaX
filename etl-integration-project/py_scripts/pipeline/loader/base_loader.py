class BaseLoader:
    """
    Base class for loaders
    """
    def load(self, data, target):
        """
        Load data into the target using the provided database context.
        
        :param data: Data to be loaded
        :param target: Target where data should be loaded
        :param db_context: Database context for the operation
        """
        raise NotImplementedError("Subclasses must implement this method")