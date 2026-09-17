from _typeshed import Incomplete

class FolderNotContainingData(Exception):
    input_dir: Incomplete
    message: Incomplete
    def __init__(self, input_dir, message: str = 'Folder does not contain the required data files') -> None: ...

class BadIndicesInData(ValueError):
    timepartitions: Incomplete
    len_data: Incomplete
    filename: Incomplete
    def __init__(self, metadata, iq, filename) -> None: ...
