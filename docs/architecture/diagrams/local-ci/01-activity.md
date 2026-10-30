# Activity diagram — local CI — from a commit to a merge into `dev`

> **Feature**: local CI tiers (ADR-0027, issue #109)
> **Related ADRs**: ADR-0027, ADR-0025 (promotion model), ADR-0026 (frozen environment records)

## Context

Which checks run on the developer machine, when, and what stops the flow. It details the "Developer
machine (local CI)" partition of [`promotion/01-activity.md`](../promotion/01-activity.md). The
partitions are the git hooks and the manual pre-merge step, not components.

## Diagram

```mermaid
flowchart TD
    A([Developer commits]) --> B

    subgraph PreCommit["pre-commit hook — just fast (L0)"]
        B["gitleaks on staged changes ·<br/>ruff on staged Python ·<br/>typos · actionlint on staged workflows"]
        B --> C{"all green?"}
        C -- yes --> D["commit-msg: Conventional Commits subject"]
        D --> E{"subject valid?"}
    end

    subgraph PrePush["pre-push hook — just check (L1)"]
        F["lint: ruff, mypy, typos, actionlint,<br/>zizmor, wiring test"]
        F --> G["test: unit tests, coverage ≥ 80 %"]
        G --> H["security: Semgrep p/python ·<br/>osv-scanner on requirements.txt"]
        H --> I["secrets: gitleaks full history"]
        I --> J{"all green?"}
    end

    subgraph PreMerge["before merge — just gate (L2)"]
        K["check + SonarQube quality gate"]
        K --> L{"gate green, owner OK?"}
    end

    C -- no --> X["Fix and retry"]
    E -- no --> X
    X --> A
    E -- yes --> M([Commit recorded]) --> N([Developer pushes]) --> F
    J -- no --> X
    J -- yes --> O["Pull request to dev"] --> K
    L -- no --> X
    L -- yes --> P([Squash-merge into dev])
    H -. "rule registry unreachable" .-> W["WARNING semgrep not run<br/>(reported as not green)"]
    W -.-> I
```

## Notes

- Semgrep offline is the only skip: it prints a warning and the pre-merge review reports the step
  as not green (ADR-0027 D2).
- The frozen environment records under `docs/research/` are outside the osv-scanner scan.
