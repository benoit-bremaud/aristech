from aristech.domain import Species


def test_species_is_str_enum():
    assert isinstance(Species.VESPA_VELUTINA, str)
    assert Species.VESPA_VELUTINA == "vespa_velutina"


def test_species_members_and_values():
    assert {s.value for s in Species} == {
        "vespa_velutina",
        "vespa_crabro",
        "apis_mellifera",
        "unknown",
    }


def test_species_lookup_by_value():
    assert Species("apis_mellifera") is Species.APIS_MELLIFERA
    assert Species("unknown") is Species.UNKNOWN


def test_velutina_distinct_from_protected_pollinator():
    # Legal-floor guard: the only threat species must never equal the bee.
    assert Species.VESPA_VELUTINA is not Species.APIS_MELLIFERA
