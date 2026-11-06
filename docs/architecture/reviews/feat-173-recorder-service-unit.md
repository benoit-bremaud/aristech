# Local review — aristech (#173, recorder service unit)

- Date: 2026-11-06
- Scope: branch diff `origin/dev...feat/173-recorder-service-unit` (systemd unit, env example, unit
  test, INSTALL steps, capture-rig deployment diagram, bench-acceptance BA6–BA13 wording)
- Checks run: adversarial review (3 rounds: findings, verify, verify) · `mise x -- just check` ·
  `systemd-analyze verify` and `systemd-analyze security --offline=yes` on the unit
- Verdict: push gate open · Must 4 (4 fixed) · Should 9 (9 fixed) · Nice 10 (7 fixed, 3 declined)

## Pre-push checks

| Step | Result |
|---|---|
| Tests | ✅ `just check`: 368 passed, 2 skipped (cv2 absent); coverage ≈ 97 % (floor 80) |
| Unit file | ✅ `systemd-analyze verify`: only the binary path missing off the Pi; security score 9.0 → 8.3 |
| Secrets | ✅ gitleaks clean; the env example holds placeholder values only, the real file lives in `/etc/aristech/` |

## 🔴 Must Have

- `deploy/systemd/aristech-record.service` · `RequiresMountsFor` is a no-op without an fstab entry,
  so a missing SSD let the recorder write to the SD card · **Fixed**: fstab step (`nofail`) in
  INSTALL, `ExecStartPre` mount check.
- `docs/INSTALL.md` · `/opt/aristech` layout never created · **Fixed**: clone, venv and ownership
  steps; only `/mnt/ssd/segments` belongs to the service user.
- `docs/architecture/traceability/matrix.md` · UC7 row missing the deployment diagram, the unit and
  its test · **Fixed**.
- `deploy/systemd/aristech-record.service` (round 2) · the mount check ran inside the sandbox, where
  `ReadWritePaths=/mnt/ssd` bind-mounts the folder onto itself, so it always passed · **Fixed**:
  `ExecStartPre=+…` (outside the sandbox) and the test asserts it.

## 🟡 Should Have

- Test split ExecStart after substitution, unlike systemd · **Fixed**: per-word substitution, an
  example value with a space.
- `network-online.target` delayed boot for nothing · **Fixed**: removed; `time-sync` kept as best effort.
- Static software version goes stale after a pull · **Fixed**: sed-and-restart step in INSTALL.
- Bench preconditions and BA13 said "stop `aristech-record`" (a kill is restarted) · **Fixed**:
  `sudo systemctl stop aristech-record`.
- BA6 and BA8 still referred to BA7 as blocked · **Fixed**.
- No hardening · **Fixed**: `NoNewPrivileges`, `ProtectSystem=strict`, `ProtectHome`, `PrivateTmp`,
  `ReadWritePaths=/mnt/ssd`.
- Conception gate UML row missing 05 · **Fixed**.
- (round 2) `RequiresMountsFor` failed the start for good when the SSD was absent at boot · **Fixed**:
  `Wants=`/`After=mnt-ssd.mount`, the mount check retries.
- (round 2) fstab step failed as written · **Fixed**: partition, mkfs, mkdir, daemon-reload.

## 🔵 Nice to Have

- **Fixed**: nologin service user, ExecStart split over lines, `Type=exec`, restart-loop hint in
  INSTALL, deployment diagram (LR, stereotypes, devices to the node, `+` and `Wants` note), retry
  period stated as about 40 s, test asserts `Wants` and no `Requires`.
- **Declined**: `--audio-device` from the env file (the I²S card is the default input; YAGNI until
  the bench says otherwise), README tree and CHANGELOG (pre-existing gaps, out of scope).
- **To verify on the bench**: the hardening with libcamera / Picamera2 (BA7 journal) and the 40 s
  retry period with the SSD unplugged (BA10).
