"""AIP – AI-powered market intelligence platform."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("aip")
except PackageNotFoundError:
    __version__ = "0.1.0"
