from cadilib.ionogramparser.baseoutput import BaseOutput
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime
import numpy as np
import numpy.typing as npt

@dataclass
class SameerData(BaseOutput):
    file: List[str]
    metadata: SameerHeader
    height: npt.NDArray[np.float32]
    frequency: npt.NDArray[np.float32]
    freq_list: npt.NDArray[np.float32]
    dop_shifts: npt.NDArray[np.float32]
    signals: npt.NDArray[np.float32]
    
    @classmethod
    def from_raw_reader(self, file: List[str], metadata: dict, 
                        height: npt.NDArray[np.float32], 
                        frequency: npt.NDArray[np.float32], 
                        freq_list: npt.NDArray[np.float32], 
                        dop_shifts: npt.NDArray[np.float32], 
                        signals: npt.NDArray[np.float32]) -> SameerData:
        return SameerData(
            file=file,
            metadata=SameerHeader.from_raw_header(metadata),
            height=height,
            frequency=frequency,
            freq_list=freq_list,
            dop_shifts=dop_shifts,
            signals=signals,
        )

@dataclass
class SameerHeader:
    site: str
    lat: float
    long: float
    filetype: str
    extension: str
    datetime: datetime
    timepartitions: Dict[str, int]
    nfreqs: int
    start_freq: float
    end_freq: float
    freq_step: float
    ipp: float
    nrgb: int
    nfft: int
    nci: int
    cbl: int

    @classmethod
    def from_raw_header(self, header: dict) -> SameerHeader:
        return SameerHeader(
            **header
        )