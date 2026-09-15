import pytest
from pathlib import Path
import numpy as np
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from itertools import chain
from cadilib.ionogramparser.mdxreader import MDreader
from cadilib.ionogramparser.cadioutput import CADIdata, CADIheader, CADIdopbin, CADIfreqbin
import struct
import tempfile
from cadilib.utils.siteinfo import SiteInfo

# Make this True to test the Rust binary. Ensure that the binary is actually built and copied to the right place first.
require_rust = True

if require_rust:
    try:
        import cadilib.ionogramparser.mdxreader_rs as cadiionogram
    except ImportError:
        cadiionogram = None
        require_rust = False

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "rust_test: mark test as requiring the Rust binary to be built"
    )

def pytest_collection_modifyitems(items):
    """Modifies test items in place to ensure test classes run in a given order."""
    CLASS_ORDER = ["TestCADIRaw","TestSiteInfo","TestPandasUtils", "TestCADIPyRawIntegration", "TestPandasPolarsEquality", 
    "TestCADIRustRaw", "TestCADIRustRawIntegration", "TestCADIRustPyEquality"]
    if not require_rust:
        skip_rust = pytest.mark.skip(reason="require_rust is False")
        for item in items:
            if "rust_test" in item.keywords:
                item.add_marker(skip_rust)

    # 1. Map items to their class names
    class_mapping = {item: (item.cls.__name__ if item.cls else None) for item in items}

    # 2. Extract items that belong to our ordered list
    ordered_items = []
    for class_name in CLASS_ORDER:
        matching_items = [it for it in items if class_mapping[it] == class_name]
        ordered_items.extend(matching_items)

    # 3. Identify items that are NOT in our CLASS_ORDER
    remaining_items = [it for it in items if class_mapping[it] not in CLASS_ORDER]

    # 4. Rebuild the list: Specified order first, then everything else
    items[:] = ordered_items + remaining_items

@pytest.fixture
def test_raw_dir():
    return Path(__file__).parent / Path("rawfiles")
@pytest.fixture
def test_raw_reader():
    return MDreader
@pytest.fixture
def test_rust_raw_reader():
    return cadiionogram
@pytest.fixture
def test_py_rs_readers():
    if not cadiionogram:
        return [MDreader]
    return [MDreader, cadiionogram]

def _build_mock_raw_header(nfreqs=4, noofreceivers=4, include_spares=True, num_freq_entries=4) -> bytearray:
    mock_bytes = bytearray()
    mock_bytes.extend('MOC'.encode('utf-8'))
    mock_bytes.extend(b" Jan 20 12:34:56 2030\n")
    mock_bytes.extend('H'.encode('utf-8'))
    mock_bytes.extend(struct.pack('<H', nfreqs))
    mock_bytes.extend(struct.pack('<B', 2))
    mock_bytes.extend(struct.pack("<H", 90))
    mock_bytes.extend(struct.pack("<H", 1024))
    mock_bytes.extend(struct.pack('<B', 8))
    mock_bytes.extend(struct.pack("<B", 3))
    mock_bytes.extend(struct.pack("<H", 400))
    mock_bytes.extend(struct.pack("<H", 135))
    mock_bytes.extend(struct.pack("<B", 1))
    mock_bytes.extend(struct.pack("<H", 60))
    mock_bytes.extend('2'.encode('utf-8'))
    mock_bytes.extend('F'.encode('utf-8'))
    mock_bytes.extend(struct.pack('<B', noofreceivers))
    if include_spares:
        mock_bytes.extend('abcxyzdef32'.encode('utf-8'))
        freq_list_mock = [3e6, 6e6, 9e6, 12e6]
        for n_freq in range(num_freq_entries):
            mock_bytes.extend(struct.pack("<f", freq_list_mock[n_freq]))
    return mock_bytes

def _write_mock_file(mock_bytes: bytearray) -> Path:
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(mock_bytes)
        f.flush()
        return Path(f.name)

@pytest.fixture
def mock_raw_file():
    mock_bytes = _build_mock_raw_header()
    nfreqs = 4
    noofreceivers = 4
    minutes = [1, 7, 8, 12, 17, 24, 32, 41, 43, 52, 59]
    dop_flags = [0, 1, 2]
    ndops_oneh = 3
    for minute in minutes:
        mock_bytes.extend(struct.pack('<B', minute))
        mock_bytes.extend(struct.pack('<B', 42))
        mock_bytes.extend(struct.pack("<B", 226))
        for nfreq in range(nfreqs):
            mock_bytes.extend(struct.pack("<B", 32))
            mock_bytes.extend(struct.pack("<H", 384))
            mock_bytes.extend(struct.pack("<B", 101))
            mock_bytes.extend(struct.pack("<B", ndops_oneh))
            for dop_x in range(ndops_oneh):
                mock_bytes.extend(struct.pack("<B", dop_flags[dop_x]))
                for receiver in range(noofreceivers):
                    mock_bytes.extend(struct.pack("<B", 120))
                    mock_bytes.extend(struct.pack("<B", 254))
            mock_bytes.extend(struct.pack("<B", 226))
    mock_bytes.extend(struct.pack("<B", 255))
    return _write_mock_file(mock_bytes)

@pytest.fixture
def mock_raw_file_incomplete_header():
    mock_bytes = _build_mock_raw_header(include_spares=False)
    return _write_mock_file(mock_bytes)

@pytest.fixture
def mock_raw_file_incomplete_header_2():
    mock_bytes = _build_mock_raw_header(include_spares=True, num_freq_entries=2)
    return _write_mock_file(mock_bytes)

@pytest.fixture
def mock_raw_file_incomplete_data():
    mock_bytes = _build_mock_raw_header()
    nfreqs = 4
    minutes = [1, 7, 8, 12, 17, 24, 32, 41, 43, 52, 59]
    for minute in minutes:
        mock_bytes.extend(struct.pack('<B', minute))
        mock_bytes.extend(struct.pack('<B', 42))
        mock_bytes.extend(struct.pack("<B", 226))
        for nfreq in range(nfreqs):
            mock_bytes.extend(struct.pack("<B", 32))
            mock_bytes.extend(struct.pack("<H", 384))
            mock_bytes.extend(struct.pack("<B", 101))
    return _write_mock_file(mock_bytes)

@pytest.fixture
def mock_raw_file_incomplete_data_2():
    mock_bytes = _build_mock_raw_header()
    minutes = [1, 7, 8, 12, 17, 24, 32, 41, 43, 52, 59]
    for minute in minutes:
        mock_bytes.extend(struct.pack('<B', minute))
    return _write_mock_file(mock_bytes)

@pytest.fixture
def mock_raw_file_incomplete_data_3():
    mock_bytes = _build_mock_raw_header()
    nfreqs = 4
    noofreceivers = 4
    minutes = [1, 7, 8, 12, 17, 24, 32, 41, 43, 52, 59]
    dop_flags = [0, 1, 2]
    ndops_oneh = 3
    for minute in minutes:
        mock_bytes.extend(struct.pack('<B', minute))
        mock_bytes.extend(struct.pack('<B', 42))
        mock_bytes.extend(struct.pack("<B", 226))
        for nfreq in range(nfreqs):
            mock_bytes.extend(struct.pack("<B", 32))
            mock_bytes.extend(struct.pack("<H", 384))
            mock_bytes.extend(struct.pack("<B", 101))
            mock_bytes.extend(struct.pack("<B", ndops_oneh))
            for dop_x in range(ndops_oneh):
                mock_bytes.extend(struct.pack("<B", dop_flags[dop_x]))
                for receiver in range(noofreceivers):
                    mock_bytes.extend(struct.pack("<B", 120))
                    mock_bytes.extend(struct.pack("<B", 254))
    return _write_mock_file(mock_bytes)

@pytest.fixture
def mock_raw_file_incomplete_data_4():
    mock_bytes = _build_mock_raw_header()
    nfreqs = 4
    noofreceivers = 4
    minutes = [1, 7, 8, 12, 17, 24, 32, 41, 43, 52, 59]
    dop_flags = [0, 1, 2]
    ndops_oneh = 3
    for i, minute in enumerate(minutes):
        mock_bytes.extend(struct.pack('<B', minute))
        mock_bytes.extend(struct.pack('<B', 42))
        mock_bytes.extend(struct.pack("<B", 226))
        for nfreq in range(nfreqs):
            mock_bytes.extend(struct.pack("<B", 32))
            mock_bytes.extend(struct.pack("<H", 384))
            mock_bytes.extend(struct.pack("<B", 101))
            mock_bytes.extend(struct.pack("<B", ndops_oneh))
            if i > 4:
                break
            for dop_x in range(ndops_oneh):
                mock_bytes.extend(struct.pack("<B", dop_flags[dop_x]))
                for receiver in range(noofreceivers):
                    mock_bytes.extend(struct.pack("<B", 120))
                    mock_bytes.extend(struct.pack("<B", 254))
            mock_bytes.extend(struct.pack("<B", 226))
    mock_bytes.extend(struct.pack("<B", 255))
    return _write_mock_file(mock_bytes)

@pytest.fixture
def mock_raw_files(mock_raw_file, mock_raw_file_incomplete_header, 
    mock_raw_file_incomplete_header_2, mock_raw_file_incomplete_data, 
    mock_raw_file_incomplete_data_2, mock_raw_file_incomplete_data_3, mock_raw_file_incomplete_data_4):
    return [mock_raw_file, mock_raw_file_incomplete_header, 
        mock_raw_file_incomplete_header_2, mock_raw_file_incomplete_data, 
        mock_raw_file_incomplete_data_2, mock_raw_file_incomplete_data_3, mock_raw_file_incomplete_data_4]

def _generate_mock_cadi_data(site="MOC") -> CADIdata:
    file_list = ['mockfile.md4']
    header_dict = {
        "site": site,
        "datetime": datetime(year=2035, month=1, day=15, hour=12, minute=34, second=56),
        "source": 'mockfile.md4',
        "filetype": 'H',
        "ndops": 4,
        "nfreqs": 2,
        "nheights": 10,
        "minheight": 90,
        "maxheight": 1020,
        "dheight": 3.0,
        "pps": 10.0,
        "npulses_avgd": 3.0,
        "dtime": 60,
        "gain_control": '2',
        "sig_process": 'F',
        "extension": 'md4',
        "spares": 'abcxyzdef32',
        "noofreceivers": 4,
        "min_dop_forsave": 1,
        "base_thr100": 400,
        "noise_thr100": 135,
        "incompletedata": False,
        "incompleteheader": False,
    }
    metadata = CADIheader(**header_dict)
    freq_list = np.array([4e6, 6e6], dtype=np.float32)
    timepartitions = {
        '12:00:00': 100,
        '12:10:00': 150,
        '12:20:00': 250,
        '12:30:00': 450,
        '12:40:00': 500,
        '12:50:00': 578
    }
    n_samples = 578
    heights = np.random.uniform(90, 800, n_samples).astype(np.float32)
    frequencies = np.random.choice(freq_list, replace=True, size=n_samples).astype(np.float32)
    dop_shifts = np.random.choice(np.linspace(-5, 5, 4), size=n_samples).astype(np.float32)
    signals = np.random.randint(0, 256, size=(n_samples, 8), dtype=np.int16)
    dopbins = CADIdopbin(
        timepartitions=timepartitions,
        height=heights,
        frequency=frequencies,
        dop_shifts=dop_shifts,
        signals=signals,
    )
    n_freqbin_samples = 12
    freqbin_timepartitions = {'12:00:00': 2, '12:10:00': 4, '12:20:00': 6, '12:30:00': 8, '12:40:00': 10, '12:50:00': 12}
    freqbins = CADIfreqbin(
        timepartitions=freqbin_timepartitions,
        frequency=np.tile(freq_list, 6).astype(np.float32),
        frebins_gain_flag=np.full(n_freqbin_samples, 0xE0, dtype=np.uint8),
        frebins_noise_flag=np.full(n_freqbin_samples, 0xF0, dtype=np.uint8),
        frebins_noise_power10=np.full(n_freqbin_samples, 38.4, dtype=np.uint16),
    )
    return CADIdata(
        file=file_list,
        metadata=metadata,
        freq_list=freq_list,
        freqbins=freqbins,
        dopbins=dopbins,
    )

@pytest.fixture
def mock_data():
    return _generate_mock_cadi_data(site='MOC')

@pytest.fixture
def mock_data_UT():
    return _generate_mock_cadi_data(site='TIR')

@pytest.fixture
def mock_multi_TZ_data(mock_data, mock_data_UT):
    return [mock_data, mock_data_UT]

@pytest.fixture
def expected_column_names():
    return ['freq (Hz)', 'height (km)', 'dopplershift']

@pytest.fixture
def mock_parquet_file(mock_data):
    return mock_data

@pytest.fixture
def test_raw_files_day():
    return [Path("250409TI"), Path("250410TI")]

