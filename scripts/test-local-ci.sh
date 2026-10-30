#!/bin/sh
# Wiring test of the local CI (ADR-0027): the recipes exist and compose, the hooks are valid, the
# commit-msg check works, and the pre-commit gitleaks job refuses a staged secret.
# Usage: mise x -- sh scripts/test-local-ci.sh
set -eu

root=$(git rev-parse --show-toplevel)
cd "$root"
fail() { echo "test-local-ci: FAIL $*" >&2; exit 1; }

for r in fast lint test test-312 security secrets check gate; do
  just --summary | tr ' ' '\n' | grep -qx "$r" || fail "recipe '$r' missing"
done
just --show check | grep -q '^check: lint test security secrets' || fail "check does not compose lint test security secrets"
just --show gate | grep -q ': check' || fail "gate does not depend on check"

lefthook validate > /dev/null || fail "lefthook validate"

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
printf 'feat(ci): add local tiers\n' > "$tmp/ok"
printf 'Add local tiers.\n' > "$tmp/bad"
sh scripts/check-commit-msg.sh "$tmp/ok" || fail "valid commit subject refused"
if sh scripts/check-commit-msg.sh "$tmp/bad" 2> /dev/null; then fail "invalid commit subject accepted"; fi

# Inside a git hook GIT_DIR and friends point at this repository: clear them for the throwaway one.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
git init -q "$tmp/repo"
key="AKIA""QYLPMN5HHHFPZAM2"
printf 'aws_access_key_id = %s\naws_secret_access_key = %s\n' "$key" "wJalrXUtnFEMI/K7MDENG/bPxRfiCYzEXAMPLEKEYx" > "$tmp/repo/creds.ini"
git -C "$tmp/repo" add creds.ini
rc=0
(cd "$tmp/repo" && gitleaks git --staged --redact --no-banner . > /dev/null 2>&1) || rc=$?
[ "$rc" -eq 1 ] || fail "gitleaks did not report the staged secret (exit $rc)"

echo "test-local-ci: OK"
