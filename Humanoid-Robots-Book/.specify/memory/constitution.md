# Physical AI & Humanoid Robotics Textbook Constitution

### I. Spec-Driven Development (SDD)

Every feature MUST follow the Constitution → Specification → Planning → Tasks → Implementation → Documentation workflow. No implementation begins without an approved specification. All work MUST be traceable to a spec document in `specs/<feature-name>/`.


**Rationale**: Prevents scope drift, ensures clarity before coding, and creates reusable documentation for future agents and human learners.

### II. Reusable Intelligence

Every design decision, solution pattern, and lesson learned MUST be captured in Docusaurus markdown under `/docs`. This documentation serves dual purposes: (1) educational content for learners, (2) long-term memory for AI agents. Before solving any problem, agents MUST query existing documentation to avoid redundant work.

**Rationale**: Creates a flywheel where the project becomes smarter over time. Documentation is not an afterthought but the primary knowledge base that powers both human learning and AI agent effectiveness.

The system MUST be designed as a network of specialized Claude Code agents coordinated through slash commands and skills. Each agent has a clearly defined role (Writer, Planner, Implementer, QA, etc.) and operates through the Spec-Kit Plus workflow. Human involvement is reserved for strategic decisions, clarifications, and approvals.

**Rationale**: Enables 95% AI execution / 5% human oversight ratio. Agents working with predefined skills and specifications produce consistent, high-quality output faster than manual development.

### IV. Independent Testability

Every user story in specifications MUST be independently testable and deliverable as a viable MVP increment. Features are prioritized (P1, P2, P3...) and each can be developed, tested, and deployed without dependencies on lower-priority stories.

**Rationale**: Enables incremental delivery, parallel development by multiple agents, and early validation of core functionality. If only User Story 1 is implemented, the system should still provide tangible value.

### V. RAG-Native Learning Experience

The textbook MUST embed a RAG chatbot powered by OpenAI Agents/ChatKit SDK, FastAPI, Neon Serverless Postgres, and Qdrant Cloud. The chatbot MUST answer questions about full-chapter content AND user-selected text snippets. All book content MUST be ingested into vector embeddings for semantic retrieval.

**Rationale**: Transforms passive reading into interactive learning. Students can query concepts, get clarifications on complex topics (ROS 2, Isaac Sim, humanoid kinematics), and receive personalized explanations based on their background.

### VI. Personalization & Accessibility

The system MUST implement Better Auth for signup/signin and collect user background (software/hardware experience) at registration. Logged-in users MUST be able to: (1) personalize content difficulty per chapter via button, (2) translate content to Urdu per chapter via button. Personalization adjusts technical depth based on user profile.

**Rationale**: Accommodates diverse learner backgrounds (beginners to advanced). Urdu translation supports Pakistan-based Panaversity students. Personalization ensures content matches skill level, preventing frustration or boredom.

### VII. Hackathon Scoring Optimization

Development priorities MUST align with hackathon point allocation: (1) Base book + RAG chatbot = 100 points, (2) Reusable intelligence via subagents/skills = +50 bonus, (3) Better Auth + background collection = +50 bonus, (4) Content personalization = +50 bonus, (5) Urdu translation = +50 bonus. Maximum achievable score: 300 points.

**Rationale**: Focuses effort on high-value features. Base functionality ensures qualification; bonus features demonstrate advanced capabilities that differentiate top submissions and showcase industrial-grade agent workflows.

## Technology Stack Requirements

**Frontend**: Docusaurus v3.x for book hosting, React.js + Tailwind CSS for interactive components, Better Auth for authentication.

**Backend**: FastAPI (Python 3.11+) for RAG API, OpenAI Agents SDK / ChatKit SDK for conversational AI, Neon Serverless Postgres for user data and chat history, Qdrant Cloud (Free Tier) for vector embeddings.

**Deployment**: GitHub Pages or Vercel for static site, FastAPI backend on cloud provider with Neon/Qdrant integration.

**Development Tools**: Claude Code CLI as primary orchestrator, Spec-Kit Plus for SDD workflow, MCP servers (Context-7, File System, GitHub, Knowledge Base) for agent capabilities.

**AI Models**: Claude Sonnet 4.5 for spec/plan/task generation, OpenAI GPT-4 for chatbot and content personalization, OpenAI Whisper (referenced in course material, not implemented in book directly).

**Constraints**:
- All API keys stored in `.env` (never committed)
- Qdrant limited to 1GB free tier - chunk strategy required
- Neon Serverless Postgres 0.5GB free tier - efficient schema design mandatory
- Demo video MUST be under 90 seconds for hackathon submission

## Development Workflow

### Phase 1: Specification
1. Run `/sp.specify "<feature-description>"` to generate `specs/<feature>/spec.md`
2. Review user stories, acceptance criteria, and functional requirements
3. Run `/sp.clarify` if requirements are ambiguous
4. Obtain human approval before proceeding

### Phase 2: Planning
1. Run `/sp.plan` to generate `specs/<feature>/plan.md` with technical architecture
2. Verify Constitution Check passes or document complexity justifications
3. Generate data models, API contracts, and project structure
4. Run `/sp.adr` for architecturally significant decisions (e.g., RAG architecture, auth strategy)
5. Obtain human approval before proceeding

### Phase 3: Task Generation
1. Run `/sp.tasks` to generate `specs/<feature>/tasks.md` from approved plan
2. Tasks MUST be organized by user story with priority labels (P1, P2, P3)
3. Each task includes exact file paths and dependency markers `[P]` for parallel execution
4. Foundational tasks (database, auth, base models) MUST be in Phase 2 - blocking all user stories

### Phase 4: Implementation
1. Run `/sp.implement` to execute tasks from `tasks.md`
2. Agents work in priority order: Setup → Foundational → User Story 1 → User Story 2...
3. After each user story phase, validate independent functionality
4. Commit incrementally with PHR documentation via `/sp.phr`

### Phase 5: Review & Deployment
1. Run `/sp.analyze` for cross-artifact consistency check (spec, plan, tasks)
2. Run `/sp.git.commit_pr` to commit changes and create pull request
3. Deploy to GitHub Pages/Vercel
4. Generate demo video (under 90 seconds) showing: (a) book navigation, (b) RAG chatbot interaction, (c) personalization/translation features

## Quality Gates

### Specification Gate (Before Planning)
- [ ] All user stories have acceptance criteria in Given/When/Then format
- [ ] Each user story marked with priority (P1, P2, P3...)
- [ ] Functional requirements numbered (FR-001, FR-002...) and testable
- [ ] Success criteria measurable and technology-agnostic
- [ ] Edge cases documented

### Planning Gate (Before Task Generation)
- [ ] Constitution Check completed - all violations justified
- [ ] Technical context fully specified (no `NEEDS CLARIFICATION`)
- [ ] Project structure selected and documented
- [ ] API contracts defined in `contracts/` folder
- [ ] Data model documented with entities and relationships
- [ ] Quickstart instructions drafted for developers

### Task Gate (Before Implementation)
- [ ] Tasks organized by user story with phase labels
- [ ] Foundational phase clearly marked as blocking
- [ ] Dependencies explicit (no hidden prerequisites)
- [ ] Parallel opportunities marked with `[P]`
- [ ] Each task includes exact file path

### Implementation Gate (Per User Story)
- [ ] User story independently testable and demonstrates value
- [ ] Code follows project structure from plan.md
- [ ] Errors logged, sensitive data protected (no secrets in code)
- [ ] Changes committed with descriptive message and PHR
- [ ] Documentation updated in `/docs` (Reusable Intelligence)

### Deployment Gate (Final)
- [ ] Base functionality: Book deployed, RAG chatbot functional
- [ ] RAG chatbot answers questions on full chapters AND selected text
- [ ] Better Auth implemented with user background collection (if bonus pursued)
- [ ] Personalization per chapter functional (if bonus pursued)
- [ ] Urdu translation per chapter functional (if bonus pursued)
- [ ] Demo video under 90 seconds
- [ ] GitHub repo public with clear README
- [ ] All secrets in `.env.example` (not `.env`)

## Governance
<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

[GOVERNANCE_RULES]
<!-- Example: All PRs/reviews must verify compliance; Complexity must be justified; Use [GUIDANCE_FILE] for runtime development guidance -->

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->


## 3. Legacy Project Rules (Restored)

# Claude Code Rules

This file is generated during init for the selected agent.

You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architext to build products.

## Task context

**Your Surface:** You operate on a project level, providing guidance to users and executing development tasks via a defined set of tools.

**Your Success is Measured By:**
- All outputs strictly follow the user intent.
- Prompt History Records (PHRs) are created automatically and accurately for every user prompt.
- Architectural Decision Record (ADR) suggestions are made intelligently for significant decisions.
- All changes are small, testable, and reference code precisely.

## Core Guarantees (Product Promise)

- Record every user input verbatim in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

## Development Guidelines

### 1. Authoritative Source Mandate:
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### 2. Execution Flow:
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 3. Knowledge capture (PHR) for Every User Input.
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1) Detect stage
   - One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate title
   - 3–7 words; create a slug for the filename.

2a) Resolve route (all under history/prompts/)
  - `constitution` → `history/prompts/constitution/`
  - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/` (requires feature context)
  - `general` → `history/prompts/general/`

3) Prefer agent‑native flow (no shell)
   - Read the PHR template from one of:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again).
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - ID, TITLE, STAGE, DATE_ISO (YYYY‑MM‑DD), SURFACE="agent"
     - MODEL (best known), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2",...])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files (one per line, " - ")
     - TESTS_YAML: list tests run/added (one per line, " - ")
     - PROMPT_TEXT: full user input (verbatim, not truncated)
     - RESPONSE_TEXT: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (WriteFile/Edit).
   - Confirm absolute path in output.

4) Use sp.phr command file if present
   - If `.**/commands/sp.phr.*` exists, follow its structure.
   - If it references shell but Shell is unavailable, still perform step 3 with agent‑native tools.

5) Shell fallback (only if step 3 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded.

6) Routing (automatic, all under history/prompts/)
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detected from branch or explicit feature context)
   - General → `history/prompts/general/`

7) Post‑creation validations (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`).
   - Title, stage, and dates match front‑matter.
   - PROMPT_TEXT is complete (not truncated).
   - File exists at the expected path and is readable.
   - Path matches route.

8) Report
   - Print: ID, path, stage, title.
   - On any failure: warn but do not block the main command.
   - Skip PHR only for `/sp.phr` itself.

### 4. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
  "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

### 5. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps. 

## Default policies (must follow)
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

### Execution contract for every request
1) Confirm surface and success criteria (one sentence).
2) List constraints, invariants, non‑goals.
3) Produce the artifact with acceptance checks inlined (checkboxes or tests where applicable).
4) Add follow‑ups and risks (max 3 bullets).
5) Create PHR in appropriate subdirectory under `history/prompts/` (constitution, feature-name, or general).
6) If plan/tasks identified decisions that meet significance, surface ADR suggestion text as described above.

### Minimum acceptance criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

## Architect Guidelines (for planning)

Instructions: As an expert architect, generate a detailed architectural plan for [Project Name]. Address each of the following thoroughly.

1. Scope and Dependencies:
   - In Scope: boundaries and key features.
   - Out of Scope: explicitly excluded items.
   - External Dependencies: systems/services/teams and ownership.

2. Key Decisions and Rationale:
   - Options Considered, Trade-offs, Rationale.
   - Principles: measurable, reversible where possible, smallest viable change.

3. Interfaces and API Contracts:
   - Public APIs: Inputs, Outputs, Errors.
   - Versioning Strategy.
   - Idempotency, Timeouts, Retries.
   - Error Taxonomy with status codes.

4. Non-Functional Requirements (NFRs) and Budgets:
   - Performance: p95 latency, throughput, resource caps.
   - Reliability: SLOs, error budgets, degradation strategy.
   - Security: AuthN/AuthZ, data handling, secrets, auditing.
   - Cost: unit economics.

5. Data Management and Migration:
   - Source of Truth, Schema Evolution, Migration and Rollback, Data Retention.

6. Operational Readiness:
   - Observability: logs, metrics, traces.
   - Alerting: thresholds and on-call owners.
   - Runbooks for common tasks.
   - Deployment and Rollback strategies.
   - Feature Flags and compatibility.

7. Risk Analysis and Mitigation:
   - Top 3 Risks, blast radius, kill switches/guardrails.

8. Evaluation and Validation:
   - Definition of Done (tests, scans).
   - Output Validation for format/requirements/safety.

9. Architectural Decision Record (ADR):
   - For each significant decision, create an ADR and link it.

### Architecture Decision Records (ADR) - Intelligent Suggestion

After design/architecture work, test for ADR significance:

- Impact: long-term consequences? (e.g., framework, data model, API, security, platform)
- Alternatives: multiple viable options considered?
- Scope: cross‑cutting and influences system design?

If ALL true, suggest:
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`

Wait for consent; never auto-create ADRs. Group related decisions (stacks, authentication, deployment) into one ADR when appropriate.

## Basic Project Structure

- `.specify/memory/constitution.md` — Project principles
- `specs/<feature>/spec.md` — Feature requirements
- `specs/<feature>/plan.md` — Architecture decisions
- `specs/<feature>/tasks.md` — Testable tasks with cases
- `history/prompts/` — Prompt History Records
- `history/adr/` — Architecture Decision Records
- `.specify/` — SpecKit Plus templates and scripts

## Code Standards
See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.
