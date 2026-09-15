"""cadilib: CADI MDx and SAMEER ionogram binary/ASCII data parsing and analysis library."""

from .ionogramparser.mdxreader import MDreader
from .utils.siteinfo import SiteInfo
from .utils.pandasutils import PandasUtils
from .utils.polarsutils import PolarsUtils

try:
    from .ionogramparser import mdxreader_rs as MDreader_rs
except ImportError:
    MDreader_rs = None

__version__ = "0.1.0"

__all__ = [
    "MDreader",
    "MDreader_rs",
    "SiteInfo",
    "PandasUtils",
    "PolarsUtils",
    "__version__",
]
