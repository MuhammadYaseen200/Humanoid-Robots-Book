# Repository Structure & Working Directory Policy

**Established**: 2025-12-23
**Enforced By**: Lead Architect

## Git Repository Layout

This is a **monorepo structure**:

```
/mnt/e/M.Y/GIAIC-Hackathons/final-project-v2/     [GIT REPOSITORY ROOT]
└── Humanoid-Robots-Book/                         [PROJECT ROOT - ALL WORK HERE]
```

## Critical Rule: Single Source of Truth

**ALL configuration, specifications, and project files MUST reside inside:**

```
Humanoid-Robots-Book/
```

**NEVER create files at the parent directory level** (`../`) except:
- Git metadata (`.git/`, `.gitattributes`)
- Repository-level files (`LICENSE`, top-level `README.md`)

## Directory Ownership

| Directory | Location | Purpose | Status |
|-----------|----------|---------|--------|
| `.specify/` | `Humanoid-Robots-Book/.specify/` | Spec-Kit Plus templates & scripts | ✅ MASTER COPY |
| `history/` | `Humanoid-Robots-Book/history/` | Prompt History Records & ADRs | ✅ MASTER COPY |
| `specs/` | `Humanoid-Robots-Book/specs/` | Feature specifications | ✅ MASTER COPY |
| `backend/` | `Humanoid-Robots-Book/backend/` | FastAPI service | ✅ MASTER COPY |
| `src/` | `Humanoid-Robots-Book/src/` | React components | ✅ MASTER COPY |
| `docs/` | `Humanoid-Robots-Book/docs/` | Docusaurus content | ✅ MASTER COPY |

## Cleanup History

**Date**: 2025-12-23
**Action**: Removed duplicate directories outside project root
**Deleted**:
- `../specs/` (contained empty placeholder files)
- `../history/` (contained empty directories)

**Result**: All configuration now follows single source of truth principle.

## Working Directory Verification

Before executing any file operations, verify you are inside the project root:

```bash
pwd
# Expected output: /mnt/e/M.Y/GIAIC-Hackathons/final-project-v2/Humanoid-Robots-Book
```

Git commands work from anywhere in the repository:

```bash
git rev-parse --show-toplevel
# Output: /mnt/e/M.Y/GIAIC-Hackathons/final-project-v2
```

## Enforcement

All agents and commands MUST:
1. Execute file operations inside `Humanoid-Robots-Book/`
2. Reference paths relative to project root
3. Refuse to create config files in parent directory
4. Verify working directory before creating new specs/history/templates

**Violation Protocol**: If duplicate directories are detected outside `Humanoid-Robots-Book/`, immediately alert and request cleanup approval.
