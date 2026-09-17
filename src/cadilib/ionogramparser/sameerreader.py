from pathlib import Path
from datetime import datetime
from cadilib.ionogramparser.baserawreader import DataReader
from cadilib.ionogramparser.sameeroutput import SameerData
import numpy as np
from cadilib.utils.siteinfo import SiteInfo

time_partition_dict = dict[str, int]

#Sameer .iono ASCII format reader, extended from DataReader baseclass
class SameerReader(DataReader):
    """
    SAMEER iono ASCII format ionogram parser. Contains the static method `read_raw_data` to read ionogram data from iono file.
    """
    @staticmethod
    def read_raw_data(filename: Path) -> SameerData:
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
            Dictionary containing metadata of the observations. Contains header info stored in the .iono file and \
        time partitions in key-value pairs to partition the observations by time.

        height : `numpy.ndarray`
            Heights in km from all the observations in the file. Use the time_partitions to \
        partition the heights by observation time.

        frequency : `numpy.ndarray` 
            Frequencies in Hz from all the observations in the file. Use the time_partitions to \
        partition the heights by observation time.

        freq_list : `numpy.ndarray`
            List of all frequencies used by the Ionosonde.

        dop_shifts : `numpy.ndarray`
            Contains the scaled doppler shift values of all the observations.

        signals : `numpy.ndarray`
            Contains the complex signal value from each receiver in amplitude-phase form. Use the time_partitions \
        to partition the signals by observation time.

        Examples
        --------
        Read one iono file from current directory

        >>> files, metadata, heights, frequencies, freq_list, dop_shifts, signals = SameerReader.read_raw_data(Path('./input.iono'))

        """
        lines = []
        with open(filename, 'r') as f:
            lines = f.readlines()
        lines = [line.strip() for line in lines]
        site, lat, long =  lines[3].split(sep='\t')
        _datetime_formats = [
            "%d-%m-%Y %H:%M",
            "%Y-%m-%d %H:%M:%S",
        ]
        datetime_obj = None
        for _fmt in _datetime_formats:
            try:
                datetime_obj = datetime.strptime(lines[4], _fmt)
                break
            except ValueError:
                continue
        if datetime_obj is None:
            raise ValueError(f"Unable to parse datetime string: {lines[4]!r}")
        nfreqs = int(lines[5])
        start_freq, end_freq, step_freq = lines[6].split(sep='\t')
        ipp, nrgb, nfft, nci, cbl = lines[7].split(sep='\t')
        freq_line_idx_original = 8
        freq_bin_idx = freq_line_idx_original + 1
        antenna_idxs = []
        no_of_peaks = []
        frequencies = []
        range_bins = []
        height_txs = []
        height_rxs = []
        noise_lvls = []
        dop_frequencies = []
        amps = []
        phases = []
        polarizations = []
        antenna_selections = []
        n_antennas = 4 + 1  #4 antennas + 1 average
        sensors = np.empty(shape=(0, 10))
        sensor_bins_all_antennas = []
        while(freq_bin_idx < len(lines)):
            for antenna_idx in range(n_antennas):
                antenna_no, no_peaks_freq = lines[freq_bin_idx].split(sep='\t')
                sensors_bin_antenna_list = []
                no_peaks_freq = int(no_peaks_freq)
                no_of_peaks.append(no_peaks_freq)
                freq_bin_idx += 1
                for peak in range(1,no_peaks_freq+1):
                    range_bin, height_tx, height_rx, noise_level, dop_frequency, amplitude, phase, polarization, antenna_selection = lines[freq_bin_idx].split(sep='\t')
                    frequencies.append(float(lines[freq_line_idx_original]))
                    antenna_idxs.append(int(antenna_no))
                    range_bins.append(int(range_bin))
                    height_txs.append(float(height_tx))
                    height_rxs.append(float(height_rx))
                    noise_lvls.append(float(noise_level))
                    dop_frequencies.append(float(dop_frequency))
                    amps.append(float(amplitude))
                    phases.append(float(phase))
                    polarizations.append(int(polarization))
                    antenna_selections.append(int(antenna_selection))
                    freq_bin_idx += 1

            freq_line_idx_original = freq_bin_idx
            freq_bin_idx += 1
        datetime_obj = datetime_obj.replace(tzinfo=SiteInfo.from_file(site).get_tzinfo(datetime_obj))
        metadata = {'site': site, 'lat': float(lat), 'long': float(long), 
            'filetype': 'iono',
            'extension': 'iono',
            'datetime': datetime_obj, 
            'timepartitions': {
                datetime_obj.strftime("%H:%M:%S"): len(amps)
            },
            'nfreqs': nfreqs, 'start_freq': start_freq, 'end_freq': end_freq, 'freq_step': step_freq,
            'ipp': ipp, 'nrgb': nrgb, 'nfft': nfft, 'nci': nci, 'cbl': cbl}
        output = SameerData.from_raw_reader([filename.name], metadata, np.array(height_txs), 
                                        np.array(frequencies), np.unique(frequencies), np.array(dop_frequencies), 
                                        np.vstack([antenna_idxs, amps, phases]).T)
        return output