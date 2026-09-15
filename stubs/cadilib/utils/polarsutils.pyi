from cadilib.ionogramparser.cadioutput import CADIdata as CADIdata
from cadilib.ionogramparser.sameeroutput import SameerData as SameerData
from cadilib.utils.siteinfo import SiteInfo as SiteInfo

__test__: dict

class PolarsUtils:
    def __init__(self, *args, **kwargs) -> None: ...
    @staticmethod
    def create_polars_from_arrays(*args, **kwargs):
        """
            Creates a polars dataframe from the given input.

            Parameters
            ----------
            data: `CADIdata` or `SameerData`
                Contains the raw data from either of the two radars
            radar_type: `str`
                Contains the radar type. This is either `cadi` or `sameer`. In the case of SAMEER data, the output is in amplitude-phase format instead of I/Q.

            Returns
            -------
            df : `polars.DataFrame` (for `SameerData`) or `Tuple[pl.DataFrame, pl.DataFrame]` (for `CADIdata`)
                DataFrame containing all the IQ, frequency, and height data indexed by the timestamp from metadata.
                If `CADIdata` is used, the optional 2nd dataframe contains frequency bin data.

        """
