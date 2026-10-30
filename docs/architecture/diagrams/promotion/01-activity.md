# Activity diagram — promotion — from a branch to the field

> **Feature**: branching and promotion model (ADR-0025, issue #112)
> **Related ADRs**: ADR-0025, ADR-0008 (method), ADR-0017 (bench device)

## Context

How a change travels from a developer's branch to a device at the apiary: which checks run where,
and which steps are local (`just`) versus GitHub (one workflow, on the signed tag). The partitions
(Mermaid subgraphs, standing in for UML activity partitions) are the places where the work happens,
not components.

## Diagram

```mermaid
flowchart TD
    subgraph Local["Developer machine (local CI)"]
        A([Issue opened]) --> B["Branch from dev<br/>feat/N-slug"]
        B --> C["Commit · just fast (pre-commit)"]
        C --> D["Push · just check (pre-push)"]
        D --> E{"check green?"}
        E -- no --> C
        E -- yes --> F["PR → dev"]
        F --> G["just gate on the head SHA<br/>(tests, coverage, Sonar, secrets, QA local)"]
        G --> H{"gate green,<br/>comments handled,<br/>owner OK?"}
        H -- no --> C
    end

    subgraph Integration["GitHub — dev (squash)"]
        I["Squash-merge into dev"]
    end

    subgraph Staging["Staging environment (bench device)"]
        J["just deploy staging<br/>from the dev commit"]
        J --> K["QA pass (qa-browser-check)"]
        K --> L{"QA passed?"}
        L -- no --> M["Issue per defect"]
        L -- yes --> N["just attest staging<br/>(signed note deploy/staging)"]
    end

    subgraph Main["GitHub — main (merge commit)"]
        O["PR dev → main<br/>merge commit of the attested SHA"]
        O --> P["Owner cuts signed tag vX.Y.Z"]
    end

    subgraph Prod["GitHub Actions — production (tag only)"]
        Q["Workflow: verify tag signature,<br/>gate status and staging note"]
        Q --> R(["Device install · model publication"])
    end

    subgraph Hotfix["Hotfix (from main)"]
        X([Field bug]) --> Y["Branch from main · same gate and QA"]
        Y --> Z["PR → main (merge commit)"]
    end

    H -- yes --> I
    I --> J
    M --> B
    N --> O
    P --> Q
    Z --> P
    Z -- "back-merge via PR" --> I
```

## Notes

- Until the bench device exists (ADR-0017), the "Staging" partition is replaced by `just gate` run
  locally; `just deploy staging` and `just attest staging` arrive with the device.
- The production workflow is a sketch: aristech has no device install nor model publication job
  yet. The tag already marks the field-ready version.
- The attestations (`gate` commit status, `deploy/staging` signed note) are the cross-project
  tooling of agents-skills#210, bricks 3 and 5; until then the PR review and the owner's approval
  stand in for them.
- A hotfix follows the same tag path as a release; its back-merge into `dev` is a merge-commit
  pull request, since `dev` refuses direct pushes.
