from pathlib import Path
import numpy as np
import numpy.typing as npt
from cadilib.ionogramparser.baseoutput import BaseOutput as BaseOutput
from dataclasses import dataclass
from datetime import datetime

def read_raw_data(filename: Path) -> CADIdata:
    """
    Read CADI ionogram data from mdx binary formats(x=1,2,3,4).

    Parameters
    ----------
    filename : `Path`
        Location of the mdx file to parse.

    Returns
    ----------
    Returns multiple values in a `CADIdata` object as follows, where the arrays can be partitioned by the timepartitions provided in the corresponding data bins.

    file_list : `List[str]`
        List containing the name of the file.

    metadata : `CADIheader`
        An object containing metadata of the observations. Contains header info stored in the mdx file.

    freqbins : `CADIfreqbin`
        An object containing the CADI frequency bin data.

    dopbins: `CADIdopbin`
        An object containing the CADI doppler bin data.

    Examples
    --------
    Read one md4 file from current directory

    >>> output = MDreader.read_raw_data(Path('./input.md4'))
    >>> files_list = output.file_list
    >>> metadata = output.metadata
    >>> heights = output.dopbins.height
    >>> frequencies = output.dopbins.frequency
    >>> freq_list = output.dopbins.freq_list
    >>> dop_shifts = output.dopbins.dop_shifts
    >>> complex_signal = output.dopbins.complex_signal
    >>> frebins_noise_power10 = output.freqbins.frebins_noise_power10
    """

@dataclass
class CADIdata(BaseOutput):
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
    file: list[str]
    metadata: CADIheader
    freq_list: npt.NDArray[np.float32]
    freqbins: CADIfreqbin
    dopbins: CADIdopbin

@dataclass
class CADIheader:
    """
    Contains the CADI header data from a given `mdX(X=1,2,3,4)` file.
    """
    site: str
    datetime: datetime
    source: str
    filetype: str
    nfreqs: int
    nheights: int
    minheight: int
    maxheight: int
    dheight: float
    pps: float
    ndops: int
    npulses_avgd: float
    dtime: int
    base_thr100: int
    noise_thr100: int
    min_dop_forsave: int
    gain_control: str
    sig_process: str
    extension: str
    spares: str
    noofreceivers: int
    incompletedata: bool
    incompleteheader: bool
    @classmethod
    def from_raw_header(self, metadata: dict) -> CADIheader: ...

@dataclass
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
    timepartitions: dict[str, int]
    height: npt.NDArray[np.float32]
    frequency: npt.NDArray[np.float32]
    dop_shifts: npt.NDArray[np.float32]
    signals: npt.NDArray[np.int16]

@dataclass
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
    timepartitions: dict[str, int]
    frequency: npt.NDArray[np.float32]
    frebins_gain_flag: npt.NDArray[np.uint8]
    frebins_noise_flag: npt.NDArray[np.uint8]
    frebins_noise_power10: npt.NDArray[np.uint16]