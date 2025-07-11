class BaseJob:
    def __init__(self, extractor, transformer, loader):
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

    def run(self, source, target, *args, **kwargs):
        data = self.extractor.extract(source, *args, **kwargs)
        transformed_data = self.transformer.transform(data, *args, **kwargs)
        self.loader.load(transformed_data, target, *args, **kwargs)