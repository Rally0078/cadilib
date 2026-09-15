import _abc
import abc
from cadilib.ionogramparser.baseoutput import BaseOutput as BaseOutput
from typing import ClassVar

__test__: dict

class DataReader(abc.ABC):
    """
    Base raw reader for all ionogram file types. 

    API specification
    ---
    All reader classes must subclass the abstract class `DataReader`, providing overrides to the abstract methods as follows:

    Methods
    ---------
    read_raw_data : Reads ionogram data from a file.
    """
    _abc_impl: ClassVar[_abc._abc_data] = ...
    __abstractmethods__: ClassVar[frozenset] = ...
    @staticmethod
    def read_raw_data(*args, **kwargs): ...
