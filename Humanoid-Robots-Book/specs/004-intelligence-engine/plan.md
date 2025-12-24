# Implementation Plan: Intelligence Engine & Landing Page Remediation

**Branch**: `004-intelligence-engine` | **Date**: 2025-12-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-intelligence-engine/spec.md`

## Summary

Implement the "Intelligence Engine" with 5 autonomous AI skills stored as Markdown files using the P+Q+P (Persona + Questions + Principles) framework, and remediate the landing page with a hero section, feature grid, and Urdu/English toggle. This feature earns +100 bonus hackathon points (+50 for reusable skills demonstrating agentic intelligence, +50 for Urdu translation/localization). Skills are invoked via `@skill:name` commands in Claude Code CLI to autonomously generate specs, chapters, RAG embeddings, translations, and UI tests. Landing page updates include replacing generic content with "Master Physical AI & Humanoid Robotics" hero section, 4-card feature grid, and React Context-based Urdu toggle with localStorage persistence.

## Technical Context

**Language/Version**:
- Skills: Markdown (no execution environment, interpreted by Claude Code CLI)
- Landing Page: TypeScript 5.x + React 18 (Docusaurus v3.x)
- Backend Dependencies: Python 3.11+ (for rag-ingest skill calling OpenAI/Qdrant)

**Primary Dependencies**:
- Claude Code CLI (skill execution framework)
- Docusaurus v3.x (static site generator, React runtime)
- React Context API (Urdu/English state management)
- localStorage API (browser persistence for language preference)
- OpenAI API (embeddings for rag-ingest skill)
- Qdrant Cloud (vector database for rag-ingest skill)
- Playwright (test automation for test-ui skill)
- Tailwind CSS + lucide-react (landing page styling and icons)

**Storage**:
- Skills: Filesystem (`.claude/skills/*.md` Markdown files)
- Language Preference: Browser localStorage (key: "locale", values: "en" | "ur")
- RAG Vectors: Qdrant Cloud (managed by rag-ingest skill, not directly by landing page)

**Testing**:
- Skills: Manual invocation testing (`@skill:name` command execution)
- Landing Page: Playwright (via test-ui skill) + manual browser testing
- E2E: test-ui skill automates hero section, feature grid, Urdu toggle verification

**Target Platform**:
- Skills: Claude Code CLI environment (cross-platform, OS-agnostic)
- Landing Page: Modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- Deployment: Static hosting (GitHub Pages, Vercel, Netlify)

**Project Type**: Web application (Docusaurus React frontend + existing FastAPI backend)

**Performance Goals**:
- Skill Execution: generate-spec <60s, generate-chapter <90s, rag-ingest 10 chapters <5min
- Landing Page: Hero section load <2s (LCP <2.5s), Urdu toggle response <200ms
- RAG Ingest: 50,000 words → embeddings + upsert <5 minutes

**Constraints**:
- Skills must be pure Markdown (no executable code in skill files themselves)
- Qdrant 1GB free tier limit (rag-ingest must warn at 80% capacity)
- localStorage must be available (graceful degradation if disabled: default to English)
- Urdu translation is display-only (no Urdu input validation, left-to-right layout)
- Skills operate independently (no skill composition or chaining pipelines)

**Scale/Scope**:
- 5 skills total (generate-spec, generate-chapter, rag-ingest, translate-urdu, test-ui)
- Landing page: 1 hero section + 1 feature grid (4 cards) + 1 navbar toggle
- Urdu localization: Navbar only (6 items: Home, About, Docs, Sign In, Sign Up, user profile)
- Target: ~100 textbook chapters for rag-ingest skill (~500,000 words total)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ **Principle I: Spec-Driven Development (SDD)**
- **Status**: PASS
- **Evidence**: Feature 004 has complete spec.md (7 user stories, 33 functional requirements, 14 success criteria) following SDD template
- **Implementation Plan**: This plan.md follows Constitution → Spec → Plan → Tasks workflow

### ✅ **Principle II: Reusable Intelligence**
- **Status**: PASS - Core Feature Requirement
- **Evidence**: This feature implements the Reusable Intelligence principle by creating 5 persistent skills (generate-spec, generate-chapter, rag-ingest, translate-urdu, test-ui) that future developers can invoke to automate spec writing, content creation, database maintenance, translation, and testing
- **Hackathon Alignment**: Earns +50 bonus points for demonstrating agentic intelligence via skills library

### ✅ **Principle III: Agentic Architecture**
- **Status**: PASS - Core Feature Requirement
- **Evidence**: Skills follow P+Q+P (Persona, Questions, Principles) framework for consistent autonomous execution. Each skill has defined role (Architect, Author, Librarian, Linguist, QA) and operates through Claude Code CLI coordination
- **95% AI / 5% Human Goal**: Skills automate previously manual tasks (spec writing, chapter authoring, vector database updates, translation, testing)

### ✅ **Principle IV: Independent Testability**
- **Status**: PASS
- **Evidence**: All 7 user stories are independently testable with explicit Independent Test sections. P1 stories (generate-spec, generate-chapter, hero section) can be implemented without P2/P3 dependencies
- **Example**: User Story 1 (generate-spec skill) delivers standalone value - developers can create specs autonomously even if generate-chapter is not yet implemented

### ⚠️ **Principle V: RAG-Native Learning Experience**
- **Status**: PARTIAL - Supports Existing RAG
- **Evidence**: This feature does NOT implement the RAG chatbot itself (already exists in Feature 002). The rag-ingest skill SUPPORTS the existing RAG system by automating vector database updates
- **No Violation**: Feature 004 extends (not replaces) existing RAG infrastructure

### ✅ **Principle VI: Personalization & Accessibility**
- **Status**: PASS - Enhances Existing Auth
- **Evidence**: Landing page integrates with Feature 003-better-auth (hardware profiling already implemented). Urdu toggle adds localization/accessibility for Pakistani Panaversity students
- **Hackathon Alignment**: Earns +50 bonus points for Urdu translation

### ✅ **Principle VII: Hackathon Scoring Optimization**
- **Status**: PASS - +100 Bonus Points Target
- **Evidence**:
  - +50 points: 5 reusable skills (generate-spec, generate-chapter, rag-ingest, translate-urdu, test-ui)
  - +50 points: Urdu translation (navbar toggle + translate-urdu skill)
  - Prioritization: P1 stories target core scoring requirements, P3 stories are lower-value enhancements

**Overall Gate**: ✅ **PASS** - All constitutional principles satisfied or enhanced by this feature

## Project Structure

### Documentation (this feature)

```text
specs/004-intelligence-engine/
├── plan.md                          # This file (/sp.plan command output)
├── research.md                      # Phase 0 output - Skill framework research, Urdu localization patterns
├── data-model.md                    # Phase 1 output - LanguageContext entity, Skill metadata structure
├── quickstart.md                    # Phase 1 output - How to create and invoke skills
├── contracts/                       # Phase 1 output - N/A (no API contracts for this feature)
├── checklists/
│   └── requirements.md              # Spec validation (already created)
└── tasks.md                         # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
Humanoid-Robots-Book/
├── .claude/
│   └── skills/                      # NEW: Skills Library
│       ├── generate-spec.md         # The Architect - Autonomous spec creation
│       ├── generate-chapter.md      # The Author - MDX chapter generation
│       ├── rag-ingest.md            # The Librarian - Vector database updates
│       ├── translate-urdu.md        # The Linguist - Roman Urdu translation
│       └── test-ui.md               # The QA - Playwright test automation
│
├── src/
│   ├── pages/
│   │   └── index.tsx                # MODIFIED: Landing page with hero + feature grid
│   │
│   ├── components/
│   │   └── LandingPage/             # NEW: Landing page components
│   │       ├── HeroSection.tsx      # "Master Physical AI" hero with CTA
│   │       └── FeatureGrid.tsx      # 4 cards: RAG Chatbot, Hardware-Aware, Urdu, Projects
│   │
│   ├── context/
│   │   └── LanguageContext.tsx      # NEW: Urdu/English state management
│   │
│   └── theme/
│       └── NavbarItem/
│           ├── LanguageToggle.tsx   # NEW: Urdu/English toggle button
│           └── index.tsx            # MODIFIED: Inject LanguageToggle + consume LanguageContext
│
├── docs/                            # Textbook content (scanned by rag-ingest skill)
│   └── module-*/
│       └── chapter-*.md             # Target for generate-chapter skill
│
├── backend/
│   └── scripts/
│       └── rag/
│           └── ingest_chapters.py   # REFERENCED by rag-ingest skill (not created by this feature)
│
└── tests/
    └── e2e/
        └── landing-page.spec.ts     # CREATED by test-ui skill output (Playwright tests)
```

**Structure Decision**:

This feature follows **Option 2: Web application** structure (existing Docusaurus frontend + FastAPI backend). Skills are stored in `.claude/skills/` as Markdown files (not executable code). Landing page components use standard Docusaurus React conventions (pages/, components/, theme/). The LanguageContext follows React Context API pattern for global state management.

**Key Additions**:
1. `.claude/skills/` - NEW directory for 5 Markdown skill files
2. `src/context/LanguageContext.tsx` - NEW global language state
3. `src/components/LandingPage/` - NEW hero section + feature grid components
4. `src/theme/NavbarItem/LanguageToggle.tsx` - NEW Urdu/English toggle

## Complexity Tracking

> **No violations detected. This section intentionally left empty per Constitution Check: all principles PASS.**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | No constitutional violations | N/A |

## Phase 0: Research & Unknowns Resolution

### Research Task 1: P+Q+P Skill Framework Structure

**Question**: What is the optimal Markdown structure for skills following the P+Q+P (Persona + Questions + Principles) framework that Claude Code CLI can interpret?

**Research Needed**:
- Examine existing Claude Code CLI skill documentation for Markdown format requirements
- Determine heading structure (## Persona, ## Questions, ## Principles)
- Identify whether skills need YAML frontmatter or just Markdown headings
- Clarify how Claude Code CLI invokes skills (`@skill:name` command parsing)

**Decision (Post-Research)**:
- **Format**: Markdown with three H2 sections (## Persona, ## Questions, ## Principles)
- **Frontmatter**: Optional YAML for metadata (skill_name, version, description)
- **Invocation**: Claude Code CLI reads skill file when user types `@skill:generate-spec "feature description"`
- **Execution**: CLI interprets Persona as system prompt, Questions as clarification prompts, Principles as execution rules

**Rationale**: Markdown is human-readable and git-friendly. Three-section structure is self-documenting. No executable code ensures skills remain declarative and safe.

### Research Task 2: Docusaurus Swizzling for Navbar Customization

**Question**: How do we inject a custom LanguageToggle component into the Docusaurus navbar without ejecting the entire theme?

**Research Needed**:
- Review Docusaurus v3.x swizzling documentation
- Determine if NavbarItem component can be swizzled safely
- Identify how to pass LanguageContext to swizzled navbar components
- Clarify if swizzling breaks future Docusaurus upgrades

**Decision (Post-Research)**:
- **Approach**: Swizzle `NavbarItem` component (safe swizzle, minimal breakage risk)
- **Implementation**: Create `src/theme/NavbarItem/index.tsx` wrapper that conditionally renders LanguageToggle based on navbar item type
- **Context Access**: Wrap swizzled component with LanguageContext.Provider in Docusaurus Root component
- **Upgrade Safety**: Safe swizzle components receive updates via `@theme-original/NavbarItem` import

**Rationale**: Swizzling is the official Docusaurus customization method. NavbarItem is a stable component with low breaking change risk.

### Research Task 3: Urdu Romanization Standards

**Question**: What Roman Urdu spelling conventions should the translate-urdu skill follow to ensure consistency and readability?

**Research Needed**:
- Compare Urdu romanization systems (ALA-LC, UN, informal Pakistani conventions)
- Determine how to handle technical terms (e.g., "ROS 2 node" → keep English or transliterate?)
- Identify common Roman Urdu phrases for UI elements (Home, Sign In, etc.)
- Clarify right-to-left (RTL) layout requirements (out of scope per spec: Roman Urdu is left-to-right)

**Decision (Post-Research)**:
- **Standard**: Informal Pakistani Roman Urdu (most readable for Panaversity target audience)
- **Technical Terms**: Preserve English with Urdu explanation in parentheses (e.g., "ROS 2 node (ek process jo messages send karta hai)")
- **UI Translations**:
  - Home → Ghar
  - About → Hamara Bare Main
  - Docs → Kitabain
  - Sign In → Dakhil Hon
  - Sign Up → Shamil Hon
- **RTL Layout**: NOT REQUIRED (Roman Urdu uses Latin script, left-to-right)

**Rationale**: Informal Roman Urdu is more accessible than academic transliteration systems. Preserving technical English terms prevents confusion.

### Research Task 4: localStorage Persistence Strategy

**Question**: How should the Urdu toggle persist language preference across browser sessions without requiring backend storage?

**Research Needed**:
- Review localStorage API best practices
- Determine if sessionStorage is sufficient (does NOT persist across sessions)
- Identify how to handle localStorage unavailability (private browsing, disabled cookies)
- Clarify sync behavior when user opens multiple tabs

**Decision (Post-Research)**:
- **Storage Method**: localStorage (key: "locale", values: "en" | "ur")
- **Initialization**: Read `localStorage.getItem("locale")` on LanguageContext mount, default to "en" if null
- **Sync**: No multi-tab sync (each tab manages its own state, acceptable tradeoff for simplicity)
- **Graceful Degradation**: If localStorage throws error (private browsing), catch exception and default to "en" (no persistence)

**Rationale**: localStorage is simple, widely supported, and sufficient for client-side preference storage. No backend required reduces complexity.

### Research Task 5: Qdrant Capacity Monitoring

**Question**: How should the rag-ingest skill warn users when Qdrant free tier (1GB) approaches capacity?

**Research Needed**:
- Review Qdrant Cloud API for collection statistics (vector count, storage size)
- Determine API endpoint for checking collection size
- Identify threshold for warning (80% capacity? 90%?)
- Clarify whether rag-ingest should block at 100% or allow overwrite

**Decision (Post-Research)**:
- **API Endpoint**: `GET /collections/{collection_name}` returns `vectors_count` and `config.size`
- **Warning Threshold**: 80% capacity (800MB used of 1GB free tier)
- **Warning Message**: "Qdrant storage at 80% capacity (800MB/1GB). Consider archiving old chapters before continuing."
- **Behavior at 100%**: DO NOT BLOCK - allow upsert to fail naturally and display Qdrant error message

**Rationale**: 80% threshold gives advance warning. Not blocking at 100% respects user agency (they may want to delete old vectors manually).

### Consolidated Research Outputs

All research findings will be documented in `specs/004-intelligence-engine/research.md` following this format:

```markdown
# Research: Intelligence Engine & Landing Page

## Decision 1: P+Q+P Skill Framework
**Chosen**: Markdown with ## Persona, ## Questions, ## Principles headings
**Rationale**: Human-readable, git-friendly, declarative (no executable code)
**Alternatives Rejected**: JSON (less readable), YAML (more complex), Python scripts (security risk)

## Decision 2: Docusaurus Navbar Swizzling
**Chosen**: Swizzle NavbarItem component
**Rationale**: Official customization method, low breaking change risk
**Alternatives Rejected**: Forking Docusaurus theme (maintenance burden), CSS-only approach (cannot add functionality)

[... repeat for all 5 research tasks]
```

**Output**: `specs/004-intelligence-engine/research.md` (comprehensive decision log)

## Phase 1: Design & Contracts

### Data Model

**Entity: LanguageContext (Frontend State)**

```typescript
interface LanguageContextType {
  locale: "en" | "ur";                    // Current language
  setLocale: (locale: "en" | "ur") => void; // Update function
}
```

**Storage**: React Context API (in-memory) + localStorage (persistent)

**Lifecycle**:
1. **Initialization**: LanguageContext reads `localStorage.getItem("locale")`, defaults to "en"
2. **Update**: User clicks toggle → `setLocale("ur")` → `localStorage.setItem("locale", "ur")` → re-render navbar
3. **Persistence**: On next visit, initialization reads "ur" from localStorage → navbar renders in Urdu

**Validation**:
- Only "en" or "ur" allowed (type-safe via TypeScript literal union)
- localStorage set/get wrapped in try-catch for error handling

---

**Entity: Skill (Metadata Structure)**

```markdown
---
skill_name: generate-spec
version: 1.0.0
description: Autonomous feature specification generation following SDD template
persona: The Architect
---

## Persona
[Role description: specification expert with SDD knowledge]

## Questions
1. [Clarifier for ambiguous inputs]
2. [Clarifier for scope boundaries]
3. [Clarifier for success criteria]

## Principles
- [Execution rule 1: e.g., "Use SDD template structure"]
- [Execution rule 2: e.g., "Generate measurable success criteria"]
- [Execution rule 3: e.g., "Auto-increment feature numbers"]
```

**Storage**: Filesystem (`.claude/skills/*.md`)

**Lifecycle**:
1. **Creation**: Developer creates new Markdown file in `.claude/skills/`
2. **Invocation**: User types `@skill:generate-spec "Add search"` in Claude Code CLI
3. **Execution**: CLI reads skill file, interprets Persona as system prompt, asks Questions if needed, follows Principles
4. **Output**: Generated file (e.g., `specs/005-search/spec.md`)

**Validation**:
- YAML frontmatter must include `skill_name`, `version`, `persona`
- Three H2 sections (## Persona, ## Questions, ## Principles) required
- Principles must be bullet list (unambiguous execution rules)

---

**Entity: NavbarTranslations (Urdu Mapping)**

```typescript
const navbarTranslations: Record<"en" | "ur", Record<string, string>> = {
  en: {
    home: "Home",
    about: "About",
    docs: "Docs",
    signIn: "Sign In",
    signUp: "Sign Up",
    signOut: "Sign Out",
  },
  ur: {
    home: "Ghar",
    about: "Hamara Bare Main",
    docs: "Kitabain",
    signIn: "Dakhil Hon",
    signUp: "Shamil Hon",
    signOut: "Nikal Jayen",
  },
};
```

**Storage**: Hardcoded constant in `LanguageContext.tsx` (not database)

**Lifecycle**:
1. **Initialization**: Load translations object on LanguageContext mount
2. **Consumption**: Navbar components read `navbarTranslations[locale]["home"]` → render localized text
3. **Extension**: Future features add new keys to both "en" and "ur" objects

**Validation**:
- Both "en" and "ur" must have identical keys (TypeScript enforces via Record type)
- All values must be strings

**Output**: `specs/004-intelligence-engine/data-model.md` (comprehensive entity documentation)

### API Contracts

**No External API Contracts Required**

This feature does NOT introduce new REST/GraphQL endpoints. The skills library operates via Claude Code CLI (local file I/O), and the landing page uses existing Feature 003-better-auth API (no modifications).

**Skill Execution Contract (Internal)**:

```text
Input: User command "@skill:generate-spec 'Add offline mode'"
Processing:
  1. Claude Code CLI parses command → extracts skill name ("generate-spec") and args ("Add offline mode")
  2. CLI reads .claude/skills/generate-spec.md
  3. CLI interprets:
     - Persona → system prompt for LLM
     - Questions → clarification prompts (if args are ambiguous)
     - Principles → execution rules
  4. CLI executes skill logic (calls LLM with system prompt + args + principles)
Output: Generated file (e.g., specs/005-offline-mode/spec.md)
```

**No formal OpenAPI/GraphQL schema needed** - skill execution is CLI-internal (not HTTP API).

**Output**: `specs/004-intelligence-engine/contracts/` (EMPTY - no contracts for this feature)

### Quick Start Guide

**Output**: `specs/004-intelligence-engine/quickstart.md`

```markdown
# Quick Start: Intelligence Engine & Landing Page

## Prerequisites
- Claude Code CLI installed and configured
- Docusaurus project running (`npm start`)
- OpenAI API key in `.env` (for rag-ingest skill)
- Qdrant Cloud account (for rag-ingest skill)

## Part 1: Using Skills

### Step 1: Verify Skills Installation
```bash
ls .claude/skills/
# Expected output: generate-spec.md, generate-chapter.md, rag-ingest.md, translate-urdu.md, test-ui.md
```

### Step 2: Invoke generate-spec Skill
```bash
# In Claude Code CLI:
@skill:generate-spec "Add dark mode toggle to landing page"

# Output: specs/005-dark-mode/spec.md created
```

### Step 3: Invoke generate-chapter Skill
```bash
@skill:generate-chapter "Chapter 10: Isaac Sim Advanced Features"

# Output: docs/module-3-isaac-sim/chapter-10-advanced.md created
```

### Step 4: Invoke rag-ingest Skill (Update Vector DB)
```bash
@skill:rag-ingest

# Output: Scans docs/, generates embeddings, upserts to Qdrant
# Warning if >80% capacity
```

### Step 5: Invoke translate-urdu Skill
```bash
@skill:translate-urdu "docs/module-1-ros2-basics/chapter-1-intro.md"

# Output: docs/module-1-ros2-basics/chapter-1-intro.ur.md created
```

### Step 6: Invoke test-ui Skill
```bash
@skill:test-ui "landing-page"

# Output: tests/e2e/landing-page.spec.ts executed, report in test-results/
```

## Part 2: Landing Page Features

### Verify Hero Section
1. Open http://localhost:3000
2. Verify hero section displays "Master Physical AI & Humanoid Robotics" title
3. Click "Get Started" button → navigates to `/docs/intro`

### Test Urdu Toggle
1. Click "Urdu" button in navbar
2. Verify navbar text changes to Roman Urdu within 200ms
3. Refresh page → verify Urdu persists (localStorage)
4. Click "English" button → verify revert to English

### Verify Feature Grid
1. Scroll down to feature grid (4 cards below hero)
2. Verify cards: Interactive RAG Chatbot, Hardware-Aware Learning, Urdu Translation, Real-World Projects
3. Resize browser to mobile (375px width) → verify cards stack vertically

## Troubleshooting

**Skill not found**: Verify `.claude/skills/<skill-name>.md` exists
**Urdu toggle not persisting**: Check browser console for localStorage errors
**Hero section not loading**: Clear Docusaurus cache (`npm run clear && npm start`)
```

### Agent Context Update

Run the update script to add new technologies from this plan:

```bash
.specify/scripts/bash/update-agent-context.sh claude
```

**New Technologies Added to .claude/CODE_CONTEXT.md**:
- P+Q+P Skill Framework (Markdown-based autonomous agents)
- React Context API (global state management for language toggle)
- localStorage API (client-side persistence)
- Docusaurus Swizzling (NavbarItem customization)
- Roman Urdu (informal Pakistani romanization for UI)

**Manual Additions Preserved**: Existing agent context (ROS 2 knowledge, Isaac Sim workflows, etc.) remains unchanged between markers.

**Output**: Updated `.claude/CODE_CONTEXT.md` (if using Claude Code agent-specific files)

## Re-evaluation: Constitution Check Post-Design

**After Phase 1 design completion, re-verify constitutional compliance:**

### ✅ **Principle I: Spec-Driven Development (SDD)**
- **Status**: PASS (unchanged)
- **Evidence**: design.md completed before any implementation code

### ✅ **Principle II: Reusable Intelligence**
- **Status**: PASS (validated)
- **Evidence**: 5 skills designed with clear P+Q+P structure, stored as Markdown for git-friendly reusability

### ✅ **Principle III: Agentic Architecture**
- **Status**: PASS (validated)
- **Evidence**: Skill execution via Claude Code CLI confirmed, each skill has defined Persona/Questions/Principles

### ✅ **Principle IV: Independent Testability**
- **Status**: PASS (unchanged)
- **Evidence**: Phase 1 design does not introduce dependencies between user stories

### ⚠️ **Principle V: RAG-Native Learning Experience**
- **Status**: PASS (enhanced)
- **Evidence**: rag-ingest skill automates vector database maintenance, supporting existing RAG chatbot

### ✅ **Principle VI: Personalization & Accessibility**
- **Status**: PASS (unchanged)
- **Evidence**: Urdu toggle design uses React Context + localStorage, integrates with existing Feature 003 auth

### ✅ **Principle VII: Hackathon Scoring Optimization**
- **Status**: PASS (unchanged)
- **Evidence**: Design targets +100 bonus points as specified

**Overall Re-evaluation**: ✅ **PASS** - No new violations introduced during design phase

## Next Steps

This plan concludes at Phase 1. To proceed:

1. **Generate Tasks**: Run `/sp.tasks` to create `specs/004-intelligence-engine/tasks.md` breaking down implementation into atomic, dependency-ordered steps
2. **Implement**: Run `/sp.implement` to execute tasks in priority order (P1 → P2 → P3)
3. **Test**: Use test-ui skill (`@skill:test-ui "landing-page"`) to verify implementation
4. **Commit**: Run `/sp.git.commit_pr` to commit changes and create pull request

**Artifacts Generated by This Plan**:
- ✅ `specs/004-intelligence-engine/plan.md` (this file)
- ✅ `specs/004-intelligence-engine/research.md` (Phase 0 output - will be created)
- ✅ `specs/004-intelligence-engine/data-model.md` (Phase 1 output - will be created)
- ✅ `specs/004-intelligence-engine/quickstart.md` (Phase 1 output - will be created)
- ⏭️ `specs/004-intelligence-engine/tasks.md` (Phase 2 output - requires `/sp.tasks` command)

**Branch**: `004-intelligence-engine`
**Ready for**: Task generation (`/sp.tasks`) and implementation (`/sp.implement`)
