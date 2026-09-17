from _typeshed import Incomplete
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

DEFAULT_SITES: Incomplete

def get_sites_json_path() -> Path: ...
def load_sites_file() -> dict: ...

@dataclass
class SiteInfo:
    FH: float
    dip: float
    site: str
    short_site: str
    ph_corr: list[float]
    polarity: list[float]
    site_separation: list[float]
    def get_tzinfo(self, dtime: datetime) -> ZoneInfo: ...
    def get_tzstr(self, dtime: datetime) -> str: ...
    @classmethod
    def from_file(cls, site_name: str) -> SiteInfo: ...
    @classmethod
    def get_from_file(cls, site_name: str, default=None) -> SiteInfo | None: ...
