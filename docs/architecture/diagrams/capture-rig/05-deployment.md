# Deployment diagram — capture-rig — recorder service on the Pi 5

> **Feature**: capture-rig (brick C1) · **Spec**: [capture-rig](../../specs/capture-rig.md) ·
> **Related ADRs**: ADR-0017

## Context

The recorder runs unattended for days (bench BA7) and must come back by itself after a power
loss (spec A5, bench BA10). systemd owns its lifecycle: it starts it at boot once the SSD is
mounted and restarts it after any exit; per-rig settings come from an env file outside git.

## Diagram

```mermaid
flowchart TB
    subgraph pi["«device» Raspberry Pi 5 — Raspberry Pi OS"]
        subgraph systemd["«execution environment» systemd"]
            unit["«artifact» aristech-record.service<br/>Restart=always, KillSignal=SIGINT"]
        end
        env["«artifact» /etc/aristech/record.env<br/>rig, hive, site, lat, lon, output"]
        app["«artifact» /opt/aristech/.venv/bin/aristech-record"]
        ssd[("«device» SSD /mnt/ssd/segments")]
    end
    cam["«device» Camera Module 3"]
    mics["«device» 2 × ICS-43434 (I²S)"]

    unit -- reads --> env
    unit -- starts / restarts --> app
    app -- writes segments and sidecars --> ssd
    cam -- CSI --> app
    mics -- I²S --> app
```

## Notes

- `RequiresMountsFor=/mnt/ssd`: the recorder never writes to the SD card if the SSD is missing.
- `StartLimitIntervalSec=0`: systemd never stops restarting it.
- The unit and the env example are checked by `tests/unit/interface/test_record_service_unit.py`.
