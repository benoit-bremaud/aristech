# Local CI (ADR-0027): `fast` on commit, `check` on push, `gate` before merge.
# Tools come from mise.toml; tests run in the project venv (.venv, see CLAUDE.md).

set shell := ["sh", "-eu", "-c"]

py := ".venv/bin/python"

default: check

# L0 — pre-commit checks on the staged files (< 10 s)
fast:
    lefthook run pre-commit

lint:
    ruff check src tests
    ruff format --check src tests
    mypy
    typos . .github
    actionlint
    zizmor --quiet .github/workflows
    sh scripts/test-local-ci.sh

# Unit tests with the 80 % coverage floor
test:
    {{py}} -m pytest -q --cov=aristech --cov-report=term --cov-report=xml --cov-fail-under=80

# SAST (Semgrep Community Edition, no login, metrics off) and lockfile vulnerabilities
security:
    # EIO_BACKEND=posix: semgrep-core's io_uring backend fails under a low locked-memory limit
    if curl -fsS -o /dev/null --max-time 10 https://semgrep.dev/c/p/python; then \
      EIO_BACKEND=posix semgrep scan --config p/python --error --metrics=off --quiet src scripts; \
    else echo "security: WARNING semgrep rule registry unreachable, semgrep not run"; fi
    osv-scanner scan source -L requirements.txt

secrets:
    gitleaks git --redact --no-banner .

# L1 — pre-push (< 3 min)
check: lint test security secrets

# L2 — pre-merge: L1 + the SonarQube quality gate on the local server
gate base="origin/dev": check
    @echo "gate: base {{base}}"
    if ! command -v sonar-scanner > /dev/null; then echo "gate: sonar-scanner not on PATH" >&2; exit 1; fi
    SONAR_TOKEN="$(cat "$HOME/.config/sonar-tokens/aristech" 2>/dev/null || printf '%s' "${SONAR_TOKEN:-}")" \
      sonar-scanner -Dsonar.qualitygate.wait=true
