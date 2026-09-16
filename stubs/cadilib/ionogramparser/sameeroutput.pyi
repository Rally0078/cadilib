import numpy as np
import numpy.typing as npt
from cadilib.ionogramparser.baseoutput import BaseOutput as BaseOutput
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SameerData(BaseOutput):
    file: list[str]
    metadata: SameerHeader
    height: npt.NDArray[np.float32]
    frequency: npt.NDArray[np.float32]
    freq_list: npt.NDArray[np.float32]
    dop_shifts: npt.NDArray[np.float32]
    signals: npt.NDArray[np.float32]
    @classmethod
    def from_raw_reader(self, file: list[str], metadata: dict, height: npt.NDArray[np.float32], frequency: npt.NDArray[np.float32], freq_list: npt.NDArray[np.float32], dop_shifts: npt.NDArray[np.float32], signals: npt.NDArray[np.float32]) -> SameerData: ...

@dataclass
class SameerHeader:
    site: str
    lat: float
    long: float
    filetype: str
    extension: str
    datetime: datetime
    timepartitions: dict[str, int]
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
    def from_raw_header(self, header: dict) -> SameerHeader: ...
