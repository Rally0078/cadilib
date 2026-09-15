from typing import Tuple
from cadilib.ionogramparser.cadioutput import CADIdata
from cadilib.ionogramparser.sameeroutput import SameerData
import numpy as np
import pandas as pd
from cadilib.utils.siteinfo import SiteInfo

class PandasUtils:
    def __init__(self):
        pass
    
    @staticmethod
    def create_pandas_from_arrays(data: CADIdata | SameerData, radar_type='cadi') -> pd.DataFrame | Tuple[pd.DataFrame, pd.DataFrame]:
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
        return PandasUtils._get_single_dataframe(data, radar_type)

    @staticmethod
    def _get_timestamps(metadata, timepartitions):
        date_of_obs = metadata['datetime'] if isinstance(metadata, dict) else metadata.datetime
        site = metadata['site'] if isinstance(metadata, dict) else metadata.site
        counts = np.diff(list(timepartitions.values()), prepend=0)
        base_date_str = f"{date_of_obs.year:04d}-{date_of_obs.month:02d}-{date_of_obs.day:02d} "
        datetime_strs = [base_date_str + t for t in timepartitions.keys()]
        time_index = pd.to_datetime(datetime_strs, format='%Y-%m-%d %H:%M:%S')
        time_index = time_index.tz_localize(SiteInfo.from_file(site).get_tzinfo(date_of_obs))
        return time_index.repeat(counts)
    
    @staticmethod
    def _get_single_dataframe(data: CADIdata | SameerData, radar_type='cadi') -> pd.DataFrame | Tuple[pd.DataFrame, pd.DataFrame]:
        column_names = ['freq (Hz)', 'height (km)', 'dopplershift']

        if radar_type.lower() == 'cadi' and isinstance(data, CADIdata):
            freqs = data.dopbins.frequency
            heights = data.dopbins.height
            dop_shifts = data.dopbins.dop_shifts
            signals = data.dopbins.signals
            timepartitions = data.dopbins.timepartitions
            for i in range(signals.shape[1]):
                signals_idx = i//2
                if i%2 == 0:
                    column_names.append(f"sensor{signals_idx+1} real")
                else:
                    column_names.append(f"sensor{signals_idx+1} imag")
        elif radar_type.lower() == 'sameer' and isinstance(data, SameerData):
            column_names.extend(['receiver_id', 'amplitude', 'phase'])
            freqs = data.frequency
            heights = data.height
            dop_shifts = data.dop_shifts
            signals = data.signals
            timepartitions = data.metadata.timepartitions
        else:
            raise ValueError('radar_type must be "cadi" or "sameer"')        
        receiver_signals = [signals[:, i] for i in range(signals.shape[1])]
        table_data = [freqs, heights, dop_shifts, *receiver_signals]
        time_index = PandasUtils._get_timestamps(data.metadata, timepartitions)
        df_signals = pd.DataFrame.from_dict(dict(zip(column_names, table_data)))
        df_signals = df_signals.set_index(time_index)

        if radar_type.lower() == 'cadi' and isinstance(data, CADIdata):
            column_names = ['freq (Hz)', 'gain_flag', 'noise_flag', 'noise_power10']
            table_data = [data.freqbins.frequency, data.freqbins.frebins_gain_flag, 
                        data.freqbins.frebins_noise_flag, data.freqbins.frebins_noise_power10]
            freqbin_timepartitions = data.freqbins.timepartitions
            time_index = PandasUtils._get_timestamps(data.metadata, freqbin_timepartitions)
            df_frebins = pd.DataFrame.from_dict(dict(zip(column_names, table_data)))
            df_frebins = df_frebins.set_index(time_index)
            return df_signals, df_frebins
        else:
            return df_signals