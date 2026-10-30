"""Species the detector can report."""

from enum import StrEnum


class Species(StrEnum):
    """Insects told apart at the hive entrance; `UNKNOWN` for any other class."""

    VESPA_VELUTINA = "vespa_velutina"
    VESPA_CRABRO = "vespa_crabro"
    APIS_MELLIFERA = "apis_mellifera"
    UNKNOWN = "unknown"
