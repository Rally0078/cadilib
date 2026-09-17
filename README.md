# cadilib

`cadilib` is a high-performance Python and Rust library designed for parsing, processing, and analyzing **Canadian Advanced Digital Ionosonde (CADI)** binary data (`.md1`, `.md2`, `.md3`, `.md4`) and **SAMEER** ionogram ASCII data (`.iono`) in India.

Originally a part of [CADI Ionogram Tools](https://github.com/Rally0078/cadiionogram), the CADI parsing library is now separate from the GUI.

---

## Features

- **High-Performance Rust Reader (`MDreader_rs`)**: Accelerated binary parser compiled as a native PyO3 extension module for maximum throughput.
- **Pure-Python Fallback Reader (`MDreader`)**: Complete pure-Python reader for CADI MDx binary formats without requiring native compilation.
- **SAMEER ASCII Reader (`SameerReader`)**: Robust parser for SAMEER `.iono` ASCII format ionograms.
- **DataFrame Interoperability**: First-class conversion to both **Pandas** and **Polars** DataFrames with structured time partitioning.
- **Ionogram Signal Processing & Filtering**: Built-in noise reduction, Doppler filtering, O/X mode separation, and k-vector estimation.
- **Site Metadata & Timezone Support**: Configurable site parameters and local/universal time (UT/LT) coordinate calculations via `sites.json`.

---

## Todo

- MacOS builds in PyPI

---

## Installation

### From PyPI

```bash
pip install cadilib
```

Or using [uv](https://github.com/astral-sh/uv):

```bash
uv add cadilib
```

### From Source

```bash
git clone https://github.com/Rally0078/cadilib.git
cd cadilib
uv sync
```

### Manually generate stubs (warning: overwrites the handwritten Rust module stub)

```bash
uv run stubgen --include-docstrings -p cadilib -o stubs
```

---

## Quick Start

### 1. Parsing CADI Binary Files (`.mdX`)

You can read CADI binary files using either the Rust-accelerated parser or the pure-Python reader:

```python
from pathlib import Path
from cadilib import MDreader, MDreader_rs

file_path = Path("data/sample.md4")

# Fast Rust reader (recommended)
if MDreader_rs is not None:
    cadi_data = MDreader_rs.read_raw_data(file_path)
else:
    # Fallback to pure Python reader
    cadi_data = MDreader.read_raw_data(file_path)

# Access metadata and data structures
print(f"Site: {cadi_data.metadata.station_name}")
print(f"Number of frequencies: {cadi_data.metadata.nfreqs}")
print(f"Height array shape: {cadi_data.dopbins.height.shape}")
```

### 2. Exporting to Pandas or Polars DataFrames

Convert raw CADI or SAMEER ionogram data into structured DataFrames:

```python
from cadilib import MDreader, PandasUtils, PolarsUtils
from pathlib import Path

raw_data = MDreader.read_raw_data(Path("data/sample.md4"))

# Convert to Pandas DataFrames
df_pandas_dop, df_pandas_freq = PandasUtils.create_pandas_from_arrays(
    raw_data, radar_type="cadi"
)

# Convert to Polars DataFrames
df_polars_dop, df_polars_freq = PolarsUtils.create_polars_from_arrays(
    raw_data, radar_type="cadi"
)
```

### 3. Parsing SAMEER ASCII Files (`.iono`)

```python
from pathlib import Path
from cadilib.ionogramparser import SameerReader

sameer_data = SameerReader.read_raw_data(Path("data/sample.iono"))
print(f"Frequencies scanned: {len(sameer_data.freq_list)}")
```

---

## Development & Building

### Prerequisites

- Python `>= 3.12`
- [uv](https://github.com/astral-sh/uv)
- [Rust toolchain](https://rustup.rs/) (Cargo)

### Build Wheel

```bash
uv build --wheel
```

### Run Tests

```bash
uv run pytest
```