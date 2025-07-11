class BaseTransformer:
    def transform(self, data):
        """
        Transform the extracted data.

        :param data: The data to transform.
        :param args: Additional positional arguments for transformation.
        :param kwargs: Additional keyword arguments for transformation.
        :return: Transformed data.
        """
        raise NotImplementedError("Subclasses should implement this method.")
