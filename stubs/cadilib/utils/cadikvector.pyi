import pandas as pd
from cadilib.utils.pandasutils import PandasUtils as PandasUtils
from copy import deepcopy as deepcopy

def compute_xpha_only(df, freq_list, site: str = 'TIR') -> tuple[pd.DataFrame, pd.DataFrame]: ...
def compute_xpha_full(df: pd.DataFrame, freq_list, site: str = 'TIR'): ...
def compute_kvector(df, freq_list, sort_by_freq: bool = False, points_thres: int = 5, site: str = 'TIR'):
    """
        Computes k vector, given the raw data for one time observation.

        Parameters
        ----------
        freq_list : `List | np.ndarray`
            Frequency bins from the raw data.
        sort_by_freq : `bool`, optional
            Sort data by frequency.
        points_thres : `int`, optional
            Minimum number of samples to consider for the computation of k vector. Works only when sort_by_freq is true.
        
        Returns
        -------
        k_out_with_ts : `pd.DataFrame`
            A DataFrame consisting of `kx`, `ky`, `kz` values, and the corresponding frequency.
        output_freqs : `pd.Series`
            A Series consisting of the frequencies corresponding to each k vector row in the dataframe.
        output_heights : `pd.Series`
            A Series consisting of the heights corresponding to each k vector row in the dataframe.
        output_dops : `pd.Series`
            A Series consisting of the doppler shifts corresponding to each k vector row in the dataframe.
        output_signals : `pd.DataFrame`
            A DataFrame consisting of the signals corresponding to each k vector row in the dataframe.
        output_xpow : `pd.DataFrame`
            A DataFrame consisting of the cross-powers of pairwise sensors corresponding to each k vector row in the dataframe.
    """
def compute_vel(df, freq_list, points_thres: int = 5, site: str = 'TIR'): ...
def compute_xy(df, freq_list, sort_by_freq: bool = False, points_thres: int = 5, site: str = 'TIR'): ...
