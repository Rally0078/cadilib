import pandas as pd
from cadilib.ionogramparser.cadioutput import CADIdata as CADIdata
from cadilib.ionogramparser.sameeroutput import SameerData as SameerData
from cadilib.utils.siteinfo import SiteInfo as SiteInfo

class PandasUtils:
    def __init__(self) -> None: ...
    @staticmethod
    def create_pandas_from_arrays(data: CADIdata | SameerData, radar_type: str = 'cadi') -> pd.DataFrame | tuple[pd.DataFrame, pd.DataFrame]:
        """
            Creates a pandas dataframe from the given input.

            Parameters
            ----------
            data: `CADIdata` or `SameerData`
                Contains the raw data from either of the two radars
            radar_type: `str`
                Contains the radar type. This is either `cadi` or `sameer`. In the case of SAMEER data, the output is in amplitude-phase format instead of I/Q.

            Returns
            -------
            df : `pandas.DataFrame` (for `SameerData`) or `Tuple[pd.DataFrame, pd.DataFrame]` (for `CADIdata`)
                DataFrame containing all the IQ, frequency, and height data indexed by the timestamp from metadata.
                If `CADIdata` is used, the optional 2nd dataframe contains frequency bin data.

        """
