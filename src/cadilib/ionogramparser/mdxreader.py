from pathlib import Path
import struct
from datetime import timezone, datetime, date, time
from time import strptime
from io import BufferedReader

from cadilib.errorhandlers.errorhandling import FolderNotContainingData
from cadilib.ionogramparser.baserawreader import DataReader
from cadilib.ionogramparser.cadioutput import CADIdata, CADIfreqbin, CADIdopbin, CADIheader
from cadilib.utils.siteinfo import SiteInfo
import numpy as np

#MDn format reader, extended from DataReader baseclass
class MDreader(DataReader):
    """
    MDx binary format ionogram parser. Contains the static method `read_raw_data` to read ionogram data from mdx file.
    """    
    @staticmethod
    def _safe_reader(file: BufferedReader, bytes):
        data = file.read(bytes)
        if data is None or len(data) < bytes:
            raise EOFError
        return data
    
    @staticmethod
    def _convert_bins_to_vals(dopbin_x_freqx, dopbin_x_hflag, dopbin_x_dop_flag, dopbin_iq, 
            noofreceivers, dopbinx, freqs, ndops, npulses_avgd, pps, freqbins_x):
        if dopbinx <= 0:
            return np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
        
        # Vectorize coordinate transformation
        dopbin_iq = np.array(dopbin_iq)
        dopbin_iq[dopbin_iq > 127] -= 256
        
        frequency_dopbins = freqs[dopbin_x_freqx]
        frequency_freqbins = freqs[freqbins_x]
        height = (np.asarray(dopbin_x_hflag) * 3).astype(np.float32)
        
        # Vectorized signal assembly (reshape to flatten receivers and components)
        # Reshaping (N, noofreceivers, 2) to (N, 2 * noofreceivers) effectively interleaves Re and Im
        complex_signal = dopbin_iq.reshape(len(frequency_dopbins), 2 * noofreceivers).astype(np.int16)

        dopbin_x_dop_flag = np.asarray(dopbin_x_dop_flag)
        dopsn2 = 1/(ndops * npulses_avgd/pps)
        dop_shifts = ((dopbin_x_dop_flag - ndops/2) * dopsn2).astype(np.float32)
        
        return height, frequency_dopbins, dop_shifts, complex_signal, frequency_freqbins

    @staticmethod
    def read_raw_data(filename: Path) -> CADIdata:
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
        max_ntimes = 256
        max_ndopbins = 300000
        dheight = 3.0  # not defined in data file
        if isinstance(filename, Path):
            extension = filename.suffix.replace('.', '')
        else:
            extension='unknown'
        
        file_list = []
        time_partitions_dopbins = dict()
        time_partitions_freqbins = dict()
        nfreqs = 0
        noofreceivers = 0
        times = []
        frebins = []
        frebins_x = []
        frebins_gain_flag = []
        frebins_noise_flag = []
        frebins_noise_power10 = []
        time_min = 0
        time_sec = 0
        timex = -1
        freqx = nfreqs - 1
        dopbinx = -1
        frebinx = -1
        freqs = []
        iq_bytes = np.zeros((noofreceivers, 2))
        dopbin_x_timex = []
        dopbin_x_freqx = []
        dopbin_x_hflag = []
        dopbin_x_dop_flag = []
        dopbin_iq = []
        hflag = 0
        file_list = []
        ndops = 0
        npulses_avgd = 0
        pps = 0

        metadata = dict({
                    "site": '',
                    "datetime": datetime(year=1970,month=1,day=1, tzinfo=timezone.utc),
                    "source": filename.name if isinstance(filename, Path) else filename,
                    "filetype": '',
                    "ndops": 0,
                    "nfreqs": nfreqs,
                    "nheights": 0,
                    "minheight": 0,
                    "maxheight": 0,
                    "dheight": 0.0,
                    "pps": 0,
                    "npulses_avgd": 0,
                    "dtime": 0,
                    "base_thr100": 0,
                    "noise_thr100": 0,
                    "min_dop_forsave": 0,
                    "gain_control": "",
                    "sig_process": "",
                    "spares": b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                    "extension": extension,
                    "noofreceivers": noofreceivers,
                    "incompletedata": False,
                    "incompleteheader": False,
        })
        header_read = False
        try:
            with open(filename, "rb") as f:
                f.seek(-1,2)     # go to the file end.
                eof = f.tell()   # get the end of file location
                f.seek(0,0)      # go back to file beginning
                # 1) read header information as described in the documentation p. 26-27
                metadata['dheight'] = dheight
                site = MDreader._safe_reader(f, 3).decode("utf-8")
                metadata['site'] = site
                ascii_datetime = MDreader._safe_reader(f, 22).decode("utf-8")

                datetime_init_observation = datetime.strptime(ascii_datetime, " %b %d %H:%M:%S %Y\n")
                datetime_init_observation = datetime_init_observation.replace(tzinfo=SiteInfo.from_file(site).get_tzinfo(datetime_init_observation))
                metadata['datetime'] = datetime_init_observation
                
                filetype = MDreader._safe_reader(f, 1).decode("utf-8")
                metadata['filetype'] = filetype

                nfreqs = struct.unpack("<H", MDreader._safe_reader(f, 2))[0]
                metadata['nfreqs'] = nfreqs

                ndops = struct.unpack("<B", MDreader._safe_reader(f, 1))[0]
                metadata['ndops'] = ndops

                minheight = struct.unpack("<H", MDreader._safe_reader(f, 2))[0]
                metadata['minheight'] = minheight

                maxheight = struct.unpack("<H", MDreader._safe_reader(f, 2))[0]
                metadata['maxheight'] = maxheight
                nheights = int(maxheight / dheight + 1)
                metadata['nheights'] = nheights

                pps = struct.unpack("<B", MDreader._safe_reader(f, 1))[0]
                metadata['pps'] = pps

                npulses_avgd = struct.unpack("<B", MDreader._safe_reader(f, 1))[0]
                metadata['npulses_avgd'] = npulses_avgd
                
                base_thr100 = struct.unpack("<H", MDreader._safe_reader(f, 2))[0]
                metadata['base_thr100'] = base_thr100
                
                noise_thr100 = struct.unpack("<H", MDreader._safe_reader(f, 2))[0]
                metadata['noise_thr100'] = noise_thr100
                
                min_dop_forsave = struct.unpack("<B", MDreader._safe_reader(f, 1))[0]
                metadata['min_dop_forsave'] = min_dop_forsave
                
                dtime = struct.unpack("<H", MDreader._safe_reader(f, 2))[0]
                metadata['dtime'] = dtime
                
                gain_control = MDreader._safe_reader(f, 1).decode("utf-8")
                metadata['gain_control'] = gain_control
                
                sig_process = MDreader._safe_reader(f, 1).decode("utf-8")
                metadata['sig_process'] = sig_process
                
                noofreceivers = struct.unpack("<B", MDreader._safe_reader(f, 1))[0]
                metadata['noofreceivers'] = noofreceivers
                
                spares = MDreader._safe_reader(f, 11)
                metadata['spares'] = spares

                metadata["extension"] = filename.suffix.replace('.','') if isinstance(filename, Path) else "unknown"

                
                jd = datetime_init_observation.date().toordinal() + 1721424.5
                jd0jd = date(1986, 1, 1)
                jd0 = jd0jd.toordinal() + 1721424.5

                time_header = (jd - jd0) * 86400 + datetime_init_observation.hour * 3600 + datetime_init_observation.minute * 60 + datetime_init_observation.second
                time_hour = time_header

                # 2) read all frequencies used
                for _ in range(nfreqs):
                    freqs.append(struct.unpack("<f", MDreader._safe_reader(f, 4))[0])

                if filetype == 'I':
                    max_nfrebins = nfreqs
                else:
                    max_nfrebins = min(max_ntimes * nfreqs, max_ndopbins)

                
                header_read = True
                freqs = np.asarray(freqs)
                #datetime object representing time of first observation in UTC or local time
                iq_bytes = np.zeros((noofreceivers, 2))
                time_min = struct.unpack("<B", MDreader._safe_reader(f, 1))[0]
                
                # Read complex sensor data from all receivers of all observations till eof.
                while f.tell() < eof and time_min != 255 and  time_min < 60:
                    #Iterate through each time of observation
                    first_obs = struct.unpack("<B", MDreader._safe_reader(f, 1))[0]
                    if first_obs > 60:
                        continue
                    else:
                        time_sec = first_obs

                    flag = struct.unpack("<B", MDreader._safe_reader(f, 1))[0]  # gainflag
                    timex += 1
                    time_partition = time(hour=datetime_init_observation.hour, minute=time_min, second=time_sec)
                    for freqx in range(nfreqs):
                        #Iterate through each frequency at a given time of observation
                        noise_flag = struct.unpack("<B", MDreader._safe_reader(f, 1))[0]  # noiseflag
                        noise_power10 = struct.unpack("<H", MDreader._safe_reader(f, 2))[0]
                        frebinx += 1
                        frebins_x.append(freqx)
                        frebins_gain_flag.append(flag)
                        frebins_noise_flag.append(noise_flag)
                        frebins_noise_power10.append(noise_power10)
                        flag = struct.unpack("<B", MDreader._safe_reader(f, 1))[0]
                        while flag < 224:
                            #Iterate through all sensor values at a given time and at a given frequency
                            ndops_oneh = struct.unpack("<B", MDreader._safe_reader(f, 1))[0]
                            hflag = flag
                            if ndops_oneh >= 128:
                                ndops_oneh = ndops_oneh - 128
                                hflag = hflag + 200
                            for dopx in range(ndops_oneh):
                                dop_flag = struct.unpack("<B", MDreader._safe_reader(f, 1))[0]
                                for rec in range(noofreceivers):
                                    re_part = MDreader._safe_reader(f, 1)
                                    im_part = MDreader._safe_reader(f, 1)
                                    iq_bytes[rec, 0] = struct.unpack("<B", re_part)[0]
                                    iq_bytes[rec, 1] = struct.unpack("<B", im_part)[0]
                                dopbinx += 1
                                dopbin_iq.append(iq_bytes.copy())
                                dopbin_x_timex.append(timex)
                                dopbin_x_freqx.append(freqx)
                                dopbin_x_hflag.append(hflag)
                                if dop_flag < int(ndops / 2):
                                    dop_flag = dop_flag + int(ndops / 2)
                                else:
                                    dop_flag = dop_flag - int(ndops / 2)
                                dopbin_x_dop_flag.append(dop_flag)
                            flag = struct.unpack("<B", MDreader._safe_reader(f, 1))[0]  # next hflag/gainflag/FF
                    time_partitions_dopbins[f"{time_partition.hour:02d}:{time_partition.minute:02d}:{time_partition.second:02d}"] = len(dopbin_iq)
                    time_partitions_freqbins[f"{time_partition.hour:02d}:{time_partition.minute:02d}:{time_partition.second:02d}"] = len(frebins_gain_flag)
                    file_list.append(filename.name if isinstance(filename, Path) else filename)
                    time_min = flag
                    if ((f.tell() - 1) != eof):
                        time_min = struct.unpack("<B", MDreader._safe_reader(f, 1))[0]  # next record
        except EOFError:
            if header_read:
                metadata['incompletedata'] = True
                header = CADIheader.from_raw_header(metadata)
                if len(list(time_partitions_dopbins.keys())) > 0:
                    final_time = list(time_partitions_dopbins.keys())[-1]
                    final_idx = time_partitions_dopbins[final_time]
                    dopbin_x_freqx = np.array(dopbin_x_freqx)[:final_idx]
                    dopbin_iq = np.array(dopbin_iq[:final_idx])
                    dopbin_x_hflag = np.array(dopbin_x_hflag)[:final_idx]
                    dopbin_x_dop_flag = np.array(dopbin_x_dop_flag)[:final_idx]
                    frebins_gain_flag = np.array(frebins_gain_flag)[:time_partitions_freqbins[final_time]]
                    frebins_noise_flag = np.array(frebins_noise_flag)[:time_partitions_freqbins[final_time]]
                    frebins_noise_power10 = np.array(frebins_noise_power10)[:time_partitions_freqbins[final_time]]
                    frebins_x = np.array(frebins_x)[:time_partitions_freqbins[final_time]]
                    height, frequency_dopbins, dop_shifts, complex_signal, frequency_freqbins = MDreader._convert_bins_to_vals(dopbin_x_freqx, dopbin_x_hflag, dopbin_x_dop_flag, dopbin_iq, 
                                       noofreceivers, dopbinx, freqs, ndops, npulses_avgd, pps, frebins_x)
                    freqbins = CADIfreqbin(time_partitions_freqbins, frequency_freqbins, frebins_gain_flag, frebins_noise_flag, frebins_noise_power10)
                    dopbins = CADIdopbin(time_partitions_dopbins, height, frequency_dopbins, 
                                                dop_shifts=dop_shifts, signals=complex_signal)
                    return CADIdata(file=file_list, metadata=header, freq_list=np.asarray(freqs), freqbins=freqbins, dopbins=dopbins)
                else:
                    dopbins = CADIdopbin(time_partitions_dopbins, np.array([]),frequency=np.array([]), 
                                                dop_shifts=np.array([]), signals=np.empty(shape=(0,2 * noofreceivers), dtype=np.int16) )
                    freqbins = CADIfreqbin(time_partitions_freqbins, np.array([]), np.array([]), np.array([]), np.array([]))
                    return CADIdata(file=file_list, metadata=header, freq_list=np.asarray(freqs), freqbins=freqbins, dopbins=dopbins)
            else:
                metadata['incompleteheader'] = True
                metadata['incompletedata'] = True
                header = CADIheader.from_raw_header(metadata)
                dopbins = CADIdopbin(time_partitions_dopbins, np.array([]),frequency=np.array([]),
                                                dop_shifts=np.array([]), signals=np.empty(shape=(0,2 * noofreceivers), dtype=np.int16) )
                freqbins = CADIfreqbin(time_partitions_freqbins, np.array([]), np.array([]), np.array([]), np.array([]))
                return CADIdata(file=file_list, metadata=header,  freq_list=np.asarray(freqs), freqbins=freqbins, dopbins=dopbins)

        height, frequency_dopbins, dop_shifts, complex_signal,frequency_freqbins = MDreader._convert_bins_to_vals(dopbin_x_freqx, dopbin_x_hflag, dopbin_x_dop_flag, dopbin_iq, 
                                       noofreceivers, dopbinx, freqs, ndops, npulses_avgd, pps, frebins_x)

        freqbins = CADIfreqbin(time_partitions_freqbins, np.asarray(frequency_freqbins, dtype=np.float32), np.asarray(frebins_gain_flag, dtype=np.uint8), 
                        np.asarray(frebins_noise_flag, dtype=np.uint8), np.asarray(frebins_noise_power10, dtype=np.float32))
        dopbins = CADIdopbin(time_partitions_dopbins, height, frequency_dopbins,
                                                dop_shifts=dop_shifts, signals=complex_signal)
        header = CADIheader.from_raw_header(metadata)
        return CADIdata(file=file_list, metadata=header, freq_list=np.asarray(freqs), freqbins=freqbins, dopbins=dopbins)