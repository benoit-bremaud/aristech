# tests/e2e/

End-to-end tests: the full loop, ideally on real hardware (camera, deterrent in a safe mock mode).

pytest marker: `@pytest.mark.e2e`, deselected by default; run with `pytest -m e2e`.

No test ships yet: an end-to-end run needs the hardware prototype, which is gated on the D0 field
test. Integration tests of the real adapters live in `tests/integration/`.
