# Upstream components

NZ:P is split across repositories. The expected source relationships are:

| Component | Repository | Observed default branch | Role |
|---|---|---|---|
| Hub/releases | `nzp-team/nzportable` | `main` | Project hub, issues, and builds |
| Engine | `nzp-team/fteqw` | `master` | NZ:P FTE-derived engine |
| Gameplay | `nzp-team/quakec` | `main` | QuakeC game logic |

The engine and gameplay repositories identify GPL-2.0 licensing. Their exact revisions have not yet been pinned for NZ:P T4.

## Fork policy

Do not copy upstream source into this repository without a deliberate history and license decision. The preferred next step is to create explicit forks, record exact commit SHAs, preserve notices, and document how the umbrella repository coordinates them.
