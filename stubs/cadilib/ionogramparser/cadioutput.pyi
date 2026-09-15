import _abc
import cadilib.ionogramparser.baseoutput
import dataclasses
from cadilib.ionogramparser.baseoutput import BaseOutput as BaseOutput
from typing import Callable, ClassVar

__test__: dict

class CADIdata(cadilib.ionogramparser.baseoutput.BaseOutput):
    """
    Contains the CADI output data from a given `mdX(X=1,2,3,4)` file.

    file: `List[str]`
        List containing the name of the file.

    metadata: `CADIheader`
        An object containing metadata of the observations. Contains header info stored in the mdx file.

    freq_list: `npt.NDArray[np.float32]`
        A 1D array of frequencies in Hz, the unique values of the frequencies in the `freqbins` and `dopbins`.
    
    freqbins: `CADIfreqbin`
        An object containing the CADI frequency bin data.

    dopbins: `CADIdopbin`
        An object containing the CADI doppler bin data.
    """
    __init__: ClassVar[Callable] = ...
    _abc_impl: ClassVar[_abc._abc_data] = ...
    __abstractmethods__: ClassVar[frozenset] = ...
    __dataclass_fields__: ClassVar[dict] = ...
    __dataclass_params__: ClassVar[dataclasses._DataclassParams] = ...
    __eq__: ClassVar[Callable] = ...
    __match_args__: ClassVar[tuple] = ...
    __replace__: ClassVar[Callable] = ...

class CADIdopbin:
    """
    Contains the CADI doppler bin data from a given `mdX(X=1,2,3,4)` file. 

    timepartitions : `dict`
        The timestamps and the cumulative length of each timestamp's observation data is given in `timepartitions`. 
    
    height : `numpy.ndarray`
        Heights in km from all the observations in the file.

    frequency : `numpy.ndarray` 
        Frequencies in Hz from all the observations in the file.

    dop_shifts : `numpy.ndarray`
        Contains the scaled doppler shift values of all the observations.

    complex_signal : `numpy.ndarray`
        Contains the complex signal value from each receiver.
    """
    __init__: ClassVar[Callable] = ...
    __dataclass_fields__: ClassVar[dict] = ...
    __dataclass_params__: ClassVar[dataclasses._DataclassParams] = ...
    __eq__: ClassVar[Callable] = ...
    __match_args__: ClassVar[tuple] = ...
    __replace__: ClassVar[Callable] = ...

class CADIfreqbin:
    """
    Contains the CADI frequency bin data from a given `mdX(X=1,2,3,4)` file. 

    timepartitions : `dict`
        The timestamps and the cumulative length of each timestamp's observation data is given in `timepartitions`. 
    
    frequency : `numpy.ndarray` 
        Frequencies in Hz from all the observations in the file.

    frebins_gain_flag : `numpy.ndarray`
        Contains the gain flag values of all the observations.

    frebins_noise_flag : `numpy.ndarray` 
        Contains the noise flag values of all the observations.

    frebins_noise_power10 : `numpy.ndarray`
        Contains the scaled noise power10 values of all the observations.
    """
    __init__: ClassVar[Callable] = ...
    __dataclass_fields__: ClassVar[dict] = ...
    __dataclass_params__: ClassVar[dataclasses._DataclassParams] = ...
    __eq__: ClassVar[Callable] = ...
    __match_args__: ClassVar[tuple] = ...
    __replace__: ClassVar[Callable] = ...

class CADIheader:
    """
    Contains the CADI header data from a given `mdX(X=1,2,3,4)` file.
    """
    __init__: ClassVar[Callable] = ...
    from_raw_header: ClassVar[method] = ...
    __dataclass_fields__: ClassVar[dict] = ...
    __dataclass_params__: ClassVar[dataclasses._DataclassParams] = ...
    __eq__: ClassVar[Callable] = ...
    __match_args__: ClassVar[tuple] = ...
    __replace__: ClassVar[Callable] = ...
