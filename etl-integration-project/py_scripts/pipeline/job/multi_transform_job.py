from db.db_context import DBContext

class MultiTransformJob:
    def __init__(self, extractor, transformers, loader):
        self.extractor = extractor
        self.transformers = transformers
        self.loader = loader

    def run(self, source, target, *args, **kwargs):
        raw_data = self.extractor.extract(source, *args, **kwargs)
        working_stack = [raw_data]

        for transformer in self.transformers:
            new_stack = []
            for data in working_stack:
                transformed_data = transformer.transform(data, *args, **kwargs)
                if isinstance(transformed_data, list):
                    new_stack.extend(transformed_data)
                else:
                    new_stack.append(transformed_data)
            working_stack = new_stack

        for transformed_data in working_stack:
            self.loader.load(transformed_data, target, *args, **kwargs)
