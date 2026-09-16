from abc import ABC
from cadilib.ionogramparser.baseoutput import BaseOutput as BaseOutput
from pathlib import Path

class DataReader(ABC):
    """
    Base raw reader for all ionogram file types. 

    API specification
    ---
    All reader classes must subclass the abstract class `DataReader`, providing overrides to the abstract methods as follows:

    Methods
    ---------
    read_raw_data : Reads ionogram data from a file.
    """
    @staticmethod
    def read_raw_data(filename: Path) -> BaseOutput: ...
