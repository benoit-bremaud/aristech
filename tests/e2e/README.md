# tests/e2e/

Tests end-to-end : la boucle complète, idéalement avec du matériel
(caméra réelle, micro, GPIO en mode mock-sûr).

Marqueur pytest : `@pytest.mark.e2e`. Lancés explicitement via
`pytest -m e2e` ou `make test-e2e` (à venir).

Aucun test n'est encore livré : l'infrastructure (adaptateurs concrets)
n'est pas implémentée. Ce dossier existe pour aligner le code sur la
documentation d'architecture.
