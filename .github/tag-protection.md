# Tag protection

Release tags `v*` are protected by the repository ruleset `protect-release-tags` (ADR-0025).

## Policy

- Target: `refs/tags/v*`, enforcement `active`.
- Rules: `creation`, `update`, `deletion` blocked; `required_signatures`.
- Bypass: repository role Admin (`actor_id: 5`), mode `always`. Only the owner creates a tag.
- Tags are created from `main` only, signed (`git tag -s`), pushed by name; a published tag is
  never moved or deleted (supersede it with a higher version).

## Verify

```bash
gh api repos/benoit-bremaud/aristech/rulesets --jq '.[] | select(.target == "tag")'
```

## Apply

```bash
gh api -X POST repos/benoit-bremaud/aristech/rulesets --input - <<'EOF'
{
  "name": "protect-release-tags",
  "target": "tag",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["refs/tags/v*"], "exclude": [] } },
  "rules": [
    { "type": "creation" }, { "type": "update" }, { "type": "deletion" },
    { "type": "required_signatures" }
  ],
  "bypass_actors": [{ "actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always" }]
}
EOF
```

## Remove

```bash
gh api -X DELETE repos/benoit-bremaud/aristech/rulesets/<ruleset-id>
```
