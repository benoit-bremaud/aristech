from enum import Enum


class Species(str, Enum):
    VESPA_VELUTINA = "vespa_velutina"
    VESPA_CRABRO = "vespa_crabro"
    APIS_MELLIFERA = "apis_mellifera"
    UNKNOWN = "unknown"
