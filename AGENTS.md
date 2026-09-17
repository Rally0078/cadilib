# AGENTS.md — Development and Operational Guide for `cadilib`

This document provides context, architectural guidelines, build instructions, and development standards for AI agents and human contributors working within the `cadilib` codebase.

---

## 1. Project Overview

`cadilib` is a Python and Rust library designed for parsing, processing, and analyzing:
- **Canadian Advanced Digital Ionosonde (CADI)** binary data (`.md1`, `.md2`, `.md3`, `.md4`).
- **SAMEER** ionogram ASCII data (`.iono`).

The library provides dual implementations for parsing CADI binary data:
1. **Rust Reader (`mdxreader_rs`)**: Accelerated native extension built with PyO3 for maximum parsing speed.
2. **Pure-Python Reader (`MDreader`)**: Complete fallback reader requiring no native compilation.

---

## 2. Codebase Architecture

```text
cadilib/
├── .github/
│   └── workflows/
│       └── publish.yml            # CI/CD: Automated PyPI publishing on push to `release`
├── rust/                          # Rust workspace containing PyO3 binary parser
│   ├── Cargo.toml                 # Rust dependencies (pyo3, numpy, chrono, serde)
│   └── src/                       # Rust reader implementation & Python module binding
├── src/
│   └── cadilib/
│       ├── __init__.py            # Root package exports
│       ├── errorhandlers/         # Custom exception definitions
│       ├── ionogramfiltering/     # Noise reduction, filtering, O/X separation
│       ├── ionogramparser/        # Python MDx/SAMEER parsers & compiled Rust library (.pyd/.so)
│       │   ├── baserawreader.py   # Abstract base parser
│       │   ├── cadioutput.py      # CADI data structures (CADIdata, CADIheader, etc.)
│       │   ├── mdxreader.py       # Pure-Python CADI parser
│       │   ├── sameerreader.py    # SAMEER parser
│       │   └── sameeroutput.py    # SAMEER data structures
│       └── utils/                 # Data utilities (Pandas, Polars, SiteInfo, K-vector)
├── tests/
│   ├── unit/                      # Unit tests for raw parsers, SiteInfo, and utilities
│   └── integration/               # Integration tests & Python vs Rust parity tests
├── hatch_build.py                 # Custom Hatchling build hook to compile Rust crate
├── pyproject.toml                 # PEP 621 metadata, dependencies, and build config
├── sites.json                     # Site metadata configuration (coordinates, timezones)
├── README.md                      # PyPI and user-facing documentation
├── AGENTS.md                      # Guide for AI agents and developers
└── LICENSE                        # MIT License
```

---

## 3. Technology Stack & Key Dependencies

- **Language & Runtime**: Python >= 3.12, Rust Edition 2024 (PyO3 >= 0.29).
- **Package & Environment Management**: [uv](https://github.com/astral-sh/uv).
- **Build System**: Hatchling (`hatchling.build`) with custom hook plugin (`hatch_build.py`).
- **Core Dependencies**:
  - `numpy`, `scipy`, `scikit-image` (signal processing & numerical arrays)
  - `pandas`, `polars`, `pyarrow` (DataFrame conversions)
  - `joblib` (parallel processing)
- **Rust Dependencies**:
  - `pyo3` (Python extension bindings)
  - `numpy` (Rust <-> NumPy array sharing)
  - `chrono`, `chrono-tz`, `serde`, `serde_json`

---

## 4. Build & Compilation Workflow

### Custom Hatch Build Hook (`hatch_build.py`)

When building wheels or installing the package:
1. `hatch_build.py` runs `cargo build --release --lib` inside `./rust`.
2. Locates the compiled binary:
   - Windows: `rust/target/release/mdxreader_rs.dll` -> `src/cadilib/ionogramparser/mdxreader_rs.pyd`
   - Linux: `rust/target/release/libmdxreader_rs.so` -> `src/cadilib/ionogramparser/mdxreader_rs.so`
   - macOS: `rust/target/release/libmdxreader_rs.dylib` -> `src/cadilib/ionogramparser/mdxreader_rs.so`
3. Copies the artifact to `src/cadilib/ionogramparser/`.
4. Sets `build_data["pure_python"] = False` and `build_data["infer_tag"] = True` to generate platform-tagged wheels.

### Useful Build Commands

- **Build Wheel**: `uv build --wheel`
- **Build Source Distribution**: `uv build --sdist`
- **Compile Rust Extension Manually**: `cargo build --release --lib` (inside `rust/` directory)

---

## 5. Development & Testing Conventions

### Testing

Tests are organized under `tests/`:
- `tests/unit/`: Tests individual parser and utility components.
- `tests/integration/`: Validates end-to-end reading, Pandas vs Polars consistency, and Python vs Rust reader parity.

**Run test suite:**
```bash
uv run pytest
```

### Critical Invariants & Rules

1. **Parity between Python and Rust Readers**: Any modification to `mdxreader.py` (Python reader) or `rust/src/` (Rust reader) must preserve 100% parity verified by `tests/integration/test_integration_py_rs_equality.py`.
2. **Graceful Fallback**: If the compiled `mdxreader_rs` module is unavailable, `cadilib` must continue to import without crashing and fall back to `MDreader`.
3. **Data Structure Consistency**: All parsers must return typed output objects (`CADIdata`, `SAMEERdata`) matching the contracts defined in `cadioutput.py` and `sameeroutput.py`.
4. **Timezone Awareness**: Time operations must respect the site configuration specified in `sites.json` and support both Universal Time (UT) and Local Time (LT).

---

## 6. CI/CD & PyPI Publishing

Automated publishing to PyPI is configured via GitHub Actions (`.github/workflows/publish.yml`):
- **Trigger**: Pushes to the `release` branch.
- **Workflow**:
  1. Matrix builds binary wheels across platforms (`ubuntu-latest`, `windows-latest`, macos currently unavailable) across Python 3.12, 3.13, and 3.14 using `uv build --wheel`.
  2. Closed-source distribution: only binary wheels (`.whl`) are published (source distributions `sdist` are not generated or released).
  3. Publishes wheels to PyPI via Trusted Publishing (OIDC).
