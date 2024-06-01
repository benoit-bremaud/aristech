# tests/test_data_structures.py

def test_data_structure():
    # Exemple de test pour une structure de données
    data = {
        "key1": "value1",
        "key2": "value2",
        "key3": {
            "subkey1": "subvalue1"
        }
    }
    assert "key1" in data, "key1 should be in data"
    assert isinstance(data["key3"], dict), "key3 should be a dictionary"