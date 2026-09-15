from cadilib.ionogramparser.baseoutput import BaseOutput
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime
import numpy as np
import numpy.typing as npt

@dataclass
class CADIdata(BaseOutput):
    file: List[str]
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
    def from_raw_header(self, metadata: Dict) -> CADIheader:
        return CADIheader(
            **metadata
        )

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

    timepartitions: Dict[str, int]
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

    timepartitions: Dict[str, int]
    frequency: npt.NDArray[np.float32]
    frebins_gain_flag: npt.NDArray[np.uint8]
    frebins_noise_flag: npt.NDArray[np.uint8]
    frebins_noise_power10: npt.NDArray[np.uint16]