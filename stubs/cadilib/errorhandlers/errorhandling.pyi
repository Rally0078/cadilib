__test__: dict

class BadIndicesInData(ValueError):
    def __init__(self, *args, **kwargs) -> None: ...

class FolderNotContainingData(Exception):
    def __init__(self, *args, **kwargs) -> None: ...
