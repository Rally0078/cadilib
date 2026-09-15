"""
    Base raw reader for all ionogram file types. 

    API specification
    ---
    All reader classes must subclass the abstract class `DataReader`, providing overrides to the abstract methods as follows:

    Methods
    ---------
    read_raw_data : Reads ionogram data from a file.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from cadilib.ionogramparser.baseoutput import BaseOutput

class DataReader(ABC):
    @staticmethod
    @abstractmethod
    def read_raw_data(filename: Path) -> BaseOutput:
        pass
