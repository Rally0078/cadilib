# cadilib

`cadilib` is a Python library for parsing, processing, and analyzing Canadian Advanced Digital Ionosonde(CADI) MDx format data, and SAMEER ionogram ASCII data.

## Features

- **Binary MDx Parser**: Parse CADI binary `.mdX(X=1,2,3,4)` files into numpy arrays, pandas DataFrames, or polars DataFrames.
- **SAMEER ASCII Parser**: Parse SAMEER `.iono` ASCII format ionograms.
- **Fast Rust Reader**: Optional high-performance Rust reader extension (`mdxreader_rs`).
- **Data Filtering & Processing**: Optional Ionogram noise reduction, O/X mode separation, and k-vector estimation.
- **Site Metadata Support**: Configurable site parameters and timezone handling (UT/LT) through sites.json.

## Todo:

- Automatic PyPI upload through GitHub Actions


## Quick Start

```python
from cadilib import MDreader, MDreader_rs, SameerReader, SiteInfo, PandasUtils, PolarsUtils
from pathlib import Path

# Parse a CADI MDx file
raw_data = MDreader.read_raw_data(
    Path("data/sample.md4")
)

# Convert to Pandas DataFrame
df_pandas_dopbins, df_pandas_freqbins = PandasUtils.create_pandas_from_arrays(
    raw_data, radar_type='cadi'
)

# Or convert to Polars DataFrame
df_polars_dopbins, df_polars_freqbins = PolarsUtils.create_polars_from_arrays(
    raw_data, radar_type='cadi'
)
```

## Development & Building

This project is managed with [uv](https://github.com/astral-sh/uv).

To build the wheel:
```bash
uv build --wheel
```

To run tests:
```bash
uv run pytest
```

The built-wheels are available in dist/cadilib-*.whl. 

To install the wheel, choose the appropriate wheel for the platform, since the Rust binaries are platform-dependent:

```python
uv pip install dist/cadilib-*.whl
```
