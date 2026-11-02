# QA passes

Dated proof that the running product was checked before a merge (pre-merge gate step 5).

- [`checklist-template.md`](checklist-template.md) — copy it to `<YYYY-MM-DD>-<topic>.md` at
  every QA pass. It checks that the planned checks cover the use cases and requirements the
  diff touches, and records each check as run with its evidence.
- `<YYYY-MM-DD>-<topic>.md` — one filled checklist (or earlier free-form report) per pass;
  screenshots and data files sit beside it with the same date prefix.
- `tools/` — scripts used during QA passes.

The review report (`../reviews/<branch>.md`) links the filled checklist from step 5.
