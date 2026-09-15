import _abc
import cadilib.ionogramparser.baserawreader
from cadilib.ionogramparser.baserawreader import DataReader as DataReader
from cadilib.ionogramparser.sameeroutput import SameerData as SameerData
from cadilib.utils.siteinfo import SiteInfo as SiteInfo
from typing import ClassVar

__test__: dict

class SameerReader(cadilib.ionogramparser.baserawreader.DataReader):
    """
    SAMEER iono ASCII format ionogram parser. Contains the static method `read_raw_data` to read ionogram data from iono file.
    """
    _abc_impl: ClassVar[_abc._abc_data] = ...
    __abstractmethods__: ClassVar[frozenset] = ...
    @staticmethod
    def read_raw_data(*args, **kwargs):
        """Read SAMEER ionogram ASCII data from .iono ASCII format.

                Parameters
                ----------
                filename : `Path`
                    Location of the .iono file to parse.

                Returns
                ----------
                Returns multiple values in a `SameerData` object as follows, where the arrays can be partitioned by the timepartitions provided in `metadata`.

                file_list : `List[str]`
                    List containing the name of the file.

                metadata : `Dict`
                    Dictionary containing metadata of the observations. Contains header info stored in the .iono file and         time partitions in key-value pairs to partition the observations by time.

                height : `numpy.ndarray`
                    Heights in km from all the observations in the file. Use the time_partitions to         partition the heights by observation time.

                frequency : `numpy.ndarray` 
                    Frequencies in Hz from all the observations in the file. Use the time_partitions to         partition the heights by observation time.

                freq_list : `numpy.ndarray`
                    List of all frequencies used by the Ionosonde.

                dop_shifts : `numpy.ndarray`
                    Contains the scaled doppler shift values of all the observations.

                signals : `numpy.ndarray`
                    Contains the complex signal value from each receiver in amplitude-phase form. Use the time_partitions         to partition the signals by observation time.

                Examples
                --------
                Read one iono file from current directory

                >>> files, metadata, heights, frequencies, freq_list, dop_shifts, signals = SameerReader.read_raw_data(Path('./input.iono'))

        """
