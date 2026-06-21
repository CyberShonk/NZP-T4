# Project process

This file is authoritative for repository work.

## Session start

Record:

- **Project:** NZ:P T4
- **Goal:** one measurable result
- **Work type:** research, source, test, build, documentation, or release
- **Risk:** low, medium, or high
- **Before touching files:** current branch, HEAD, status, relevant source, tests, and content-policy impact
- **Likely affected files:** exact paths where known
- **Validation:** exact commands and expected evidence
- **Docs/changelog:** whether verified public state changes
- **Commit message:** proposed only after validation
- **Next action:** one concrete continuation step

Read, in order:

1. `README.md`
2. `CURRENT_STATUS.md`
3. relevant public documentation
4. local private `CURRENT_STATUS.md` and `SESSION_HANDOFF.md`, when present
5. relevant source and tests

## Before modifying files

```bash
git status --short
git branch --show-current
git log -1 --oneline --decorate
```

Then:

1. Confirm the task against current repository state and reproducible evidence, not external recollection.
2. Check `docs/CONTENT_POLICY.md` before adding fixtures, archives, scripts, or binary data.
3. Keep imported user content outside the repository.
4. Do not execute imported installers, scripts, DLLs, or binaries.
5. Prefer a small vertical change with a deterministic test.
6. Do not claim compatibility from file recognition alone.

## Required validation

For inspector changes:

```bash
./tools/check-project.sh
```

For future Android/runtime changes, record the exact build command, device, ABI, Android version, renderer, map, logs, and result. A build without a runtime test is not a verified Android capability.

## Documentation rule

Update public status only when behavior is verified. Keep unreleased strategy, private corpus findings, legal-risk analysis, map-specific research, and speculative implementation plans in the local private context.

## Commit rule

Before committing:

```bash
git diff --check
git diff --cached --name-only
git status --short
```

Never bypass the local pre-commit guard to add imported or private content.

## Session end

Record only:

- verified current state;
- work completed;
- validation commands and results;
- durable decision or risk;
- exact next measurable action.

Do not store full transcripts or proprietary package contents.
