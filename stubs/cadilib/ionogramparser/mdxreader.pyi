import _abc
import cadilib.ionogramparser.baserawreader
from cadilib.errorhandlers.errorhandling import FolderNotContainingData as FolderNotContainingData
from cadilib.ionogramparser.baserawreader import DataReader as DataReader
from cadilib.ionogramparser.cadioutput import CADIdata as CADIdata, CADIdopbin as CADIdopbin, CADIfreqbin as CADIfreqbin, CADIheader as CADIheader
from cadilib.utils.siteinfo import SiteInfo as SiteInfo
from typing import ClassVar

__test__: dict

class MDreader(cadilib.ionogramparser.baserawreader.DataReader):
    """
    MDx binary format ionogram parser. Contains the static method `read_raw_data` to read ionogram data from mdx file.
    """
    _abc_impl: ClassVar[_abc._abc_data] = ...
    __abstractmethods__: ClassVar[frozenset] = ...
    @staticmethod
    def read_raw_data(*args, **kwargs):
        """Read CADI ionogram data from mdx binary formats(x=1,2,3,4).

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
