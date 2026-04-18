# API Contracts: Intelligence Engine & Landing Page Remediation

**Feature**: 004-intelligence-engine
**Status**: No External API Contracts Required

## Why This Directory Is Empty

This feature does NOT introduce new REST/GraphQL/gRPC endpoints that require formal API contracts.

### What This Feature Does:

1. **Skills Library**: Creates 5 Markdown files (`.claude/skills/*.md`) that are interpreted by Claude Code CLI locally. Skills operate via file I/O, not HTTP APIs.

2. **Landing Page**: Updates Docusaurus React components (hero section, feature grid, Urdu toggle). These are frontend-only changes consuming existing APIs.

3. **Urdu Toggle**: Uses React Context API + localStorage (browser APIs, not custom HTTP endpoints).

### Existing API Integrations (No Changes)

This feature **consumes but does not modify** these existing APIs:

- **Feature 003-better-auth API**: `/api/auth/signup`, `/api/auth/signin`
  - Landing page integrates with existing AuthContext (no API changes)
  - Contracts: See `specs/003-better-auth/contracts/` (if exists)

- **OpenAI Embeddings API**: Used by `rag-ingest` skill
  - Endpoint: `POST https://api.openai.com/v1/embeddings`
  - External API (OpenAI-managed, no custom contract)

- **Qdrant Vector Database API**: Used by `rag-ingest` skill
  - Endpoint: `POST https://<cluster>.qdrant.io/collections/<name>/points`
  - External API (Qdrant Cloud-managed, no custom contract)

### Internal Skill Execution Contract

Skills are invoked via Claude Code CLI command pattern (not HTTP):

```text
Input:  @skill:generate-spec "feature description"
Output: Generated file at specs/<NNN>-feature-name/spec.md
```

This is a **CLI contract**, not an API contract. No OpenAPI/GraphQL schema required.

---

**Conclusion**: This directory remains empty because no formal API contracts exist for this feature. All interactions are either:
- Local file I/O (skills)
- Frontend-only (React components)
- External managed APIs (OpenAI, Qdrant)
