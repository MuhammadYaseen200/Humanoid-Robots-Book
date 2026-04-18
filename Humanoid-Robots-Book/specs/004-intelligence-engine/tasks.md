# Tasks: Intelligence Engine & Landing Page Remediation

**Input**: Design documents from `/specs/004-intelligence-engine/`
**Prerequisites**: plan.md (✅ complete), spec.md (✅ complete), research.md (✅ complete), data-model.md (✅ complete)

**Tests**: Not explicitly requested in spec.md - test tasks are omitted per /sp.tasks guidelines. Manual testing and test-ui skill (US6) will validate implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US7)
- Include exact file paths in descriptions

## Path Conventions

Per plan.md Project Structure:
- Skills: `.claude/skills/*.md`
- Landing Page Components: `src/components/LandingPage/*.tsx`
- Context: `src/context/*.tsx`
- Theme Customization: `src/theme/NavbarItem/*.tsx`
- Landing Page: `src/pages/index.tsx`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure and verify dependencies

- [X] T001 Create skills directory at `.claude/skills/` (mkdir -p)
- [X] T002 [P] Verify Docusaurus project structure exists (src/pages/, src/components/)
- [X] T003 [P] Verify package.json includes React 18, Docusaurus v3.x, Tailwind CSS
- [X] T004 [P] Create landing page components directory at `src/components/LandingPage/`
- [X] T005 [P] Create context directory at `src/context/` (if not exists)
- [X] T006 [P] Create navbar theme directory at `src/theme/NavbarItem/` (for swizzling)

**Checkpoint**: Directory structure ready for skill and component implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Install lucide-react icon library (npm install lucide-react)
- [X] T008 [P] Verify OpenAI API key exists in .env as OPENAI_API_KEY (created .env.example template)
- [X] T009 [P] Verify Qdrant connection details in .env (QDRANT_URL, QDRANT_API_KEY) (created .env.example template)
- [X] T010 [P] Verify Playwright installed (npx playwright install chromium)
- [X] T011 Create LanguageContext at `src/context/LanguageContext.tsx` (React Context + localStorage for "en" | "ur")
- [X] T012 Create NavbarTranslations constant in LanguageContext.tsx (English↔Urdu mappings per data-model.md)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - generate-spec Skill (Priority: P1) 🎯 MVP

**Goal**: Enable autonomous feature specification generation via `@skill:generate-spec` command

**Independent Test**: Run `@skill:generate-spec "Add dark mode toggle"` in Claude Code CLI, verify it creates `specs/005-dark-mode/spec.md` with User Scenarios, Functional Requirements, Success Criteria sections

### Implementation for User Story 1

- [X] T013 [US1] Create generate-spec skill at `.claude/skills/generate-spec.md`
- [X] T014 [US1] Add YAML frontmatter to generate-spec.md (skill_name: generate-spec, version: 1.0.0, persona: The Architect)
- [X] T015 [US1] Write ## Persona section defining The Architect role (specification expert with SDD knowledge)
- [X] T016 [US1] Write ## Questions section with 3 clarifiers (feature scope, primary users, success criteria)
- [X] T017 [US1] Write ## Principles section with execution rules (use SDD template, auto-increment feature numbers, generate measurable success criteria, create requirements checklist)
- [X] T018 [US1] Add example invocation in skill Principles: `@skill:generate-spec 'Add search functionality'`
- [X] T019 [US1] Document output path pattern in Principles: `specs/NNN-feature-name/spec.md`

**Checkpoint**: generate-spec skill complete and ready for testing per Independent Test criteria

---

## Phase 4: User Story 2 - generate-chapter Skill (Priority: P1) 🎯 MVP

**Goal**: Enable autonomous textbook chapter generation via `@skill:generate-chapter` command

**Independent Test**: Run `@skill:generate-chapter "Chapter 10: Isaac Sim Advanced Features"`, verify it creates `docs/module-3-isaac-sim/chapter-10-advanced.md` with YAML frontmatter, code examples, Docusaurus admonitions

### Implementation for User Story 2

- [X] T020 [US2] Create generate-chapter skill at `.claude/skills/generate-chapter.md`
- [X] T021 [US2] Add YAML frontmatter to generate-chapter.md (skill_name: generate-chapter, version: 1.0.0, persona: The Author)
- [X] T022 [US2] Write ## Persona section defining The Author role (educational content writer for robotics, ROS 2, Isaac Sim)
- [X] T023 [US2] Write ## Questions section with clarifiers (target audience level: beginner/intermediate/advanced, prerequisites: which chapters must be completed first)
- [X] T024 [US2] Write ## Principles section with execution rules (use Docusaurus MDX syntax, include YAML frontmatter with title/sidebar_position, add 3+ Python/C++ code blocks with syntax highlighting, use Docusaurus components: :::tip, :::warning, :::note, create beginner-friendly explanations, add cross-references to related chapters, minimum 1500 words)
- [X] T025 [US2] Add example invocation in Principles: `@skill:generate-chapter 'Chapter 5: ROS 2 Services and Clients'`
- [X] T026 [US2] Document output path pattern: `docs/module-N/chapter-M-<slug>.md`

**Checkpoint**: generate-chapter skill complete and ready for testing per Independent Test criteria

---

## Phase 5: User Story 7 - Landing Page Hero Section (Priority: P1) 🎯 MVP

**Goal**: Replace generic homepage content with "Master Physical AI & Humanoid Robotics" hero section and feature grid

**Independent Test**: Open http://localhost:3000, verify hero section displays title, subtitle, "Get Started" CTA button, and 4-card feature grid below

### Implementation for User Story 7

- [X] T027 [P] [US7] Create HeroSection component at `src/components/LandingPage/HeroSection.tsx`
- [X] T028 [P] [US7] Create FeatureGrid component at `src/components/LandingPage/FeatureGrid.tsx`
- [X] T029 [US7] Implement HeroSection: title "Master Physical AI & Humanoid Robotics", subtitle explaining project value (free interactive textbook with RAG chatbot for ROS 2, Isaac Sim, humanoid robotics)
- [X] T030 [US7] Add CTA button to HeroSection with conditional text: "Get Started" (if unauthenticated) or "Continue Learning" (if authenticated) - check AuthContext from Feature 003
- [X] T031 [US7] Link CTA button to `/docs/module-1-ros2-basics/chapter-1-intro`
- [X] T032 [US7] Implement responsive layout for HeroSection: single column mobile (<768px), two-column desktop (≥768px)
- [X] T033 [US7] Define 4 FeatureCard props in FeatureGrid.tsx: {icon: ReactNode, title: string, description: string}
- [X] T034 [US7] Add FeatureCard data for "Interactive RAG Chatbot" with MessageSquare icon from lucide-react
- [X] T035 [US7] Add FeatureCard data for "Hardware-Aware Learning" with Cpu icon from lucide-react
- [X] T036 [US7] Add FeatureCard data for "Urdu Translation" with Languages icon from lucide-react
- [X] T037 [US7] Add FeatureCard data for "Real-World Projects" with Rocket icon from lucide-react
- [X] T038 [US7] Implement responsive grid layout for FeatureGrid: 1 card/row mobile, 2 cards/row tablet, 4 cards/row desktop
- [X] T039 [US7] Update `src/pages/index.tsx` to import HeroSection and FeatureGrid components
- [X] T040 [US7] Replace existing homepage content with HeroSection and FeatureGrid (remove generic Docusaurus starter content)

**Checkpoint**: Landing page complete with hero section above the fold, feature grid visible on scroll, responsive layout working on mobile/tablet/desktop

---

## Phase 6: User Story 3 - rag-ingest Skill (Priority: P2)

**Goal**: Automate Qdrant vector database updates with textbook content via `@skill:rag-ingest` command

**Independent Test**: Add new file `docs/test-chapter.md`, run `@skill:rag-ingest`, query Qdrant API to verify vectors exist with correct metadata (chapter_id, file_path, module_name)

### Implementation for User Story 3

- [ ] T041 [US3] Create rag-ingest skill at `.claude/skills/rag-ingest.md`
- [ ] T042 [US3] Add YAML frontmatter to rag-ingest.md (skill_name: rag-ingest, version: 1.0.0, persona: The Librarian)
- [ ] T043 [US3] Write ## Persona section defining The Librarian role (vector database manager, embeddings expert)
- [ ] T044 [US3] Write ## Questions section (no clarifiers needed - skill is fully automated)
- [ ] T045 [US3] Write ## Principles section with execution rules (scan docs/ recursively for .md files, chunk content into 512 tokens with 50-token overlap, generate embeddings via OpenAI text-embedding-3-small, upsert to Qdrant collection "textbook_chapters", attach metadata: {chapter_id, file_path, module_name, chunk_index, title}, warn at 80% Qdrant capacity per research.md Decision 5, display progress: "Processed 15/20 chapters...")
- [ ] T046 [US3] Add API endpoint references in Principles: OpenAI https://api.openai.com/v1/embeddings, Qdrant https://<cluster>.qdrant.io/collections/textbook_chapters/points
- [ ] T047 [US3] Document environment variables required: OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY
- [ ] T048 [US3] Add capacity monitoring logic in Principles: Query Qdrant collection stats, calculate usage_percent = (vectors_count / max_capacity) * 100, warn if ≥80%
- [ ] T049 [US3] Add example invocation: `@skill:rag-ingest` (no arguments, scans entire docs/ directory)

**Checkpoint**: rag-ingest skill complete, ready to update vector database with textbook chapters

---

## Phase 7: User Story 4 - Urdu Toggle Navbar (Priority: P2)

**Goal**: Enable language switching between English and Roman Urdu with localStorage persistence

**Independent Test**: Open landing page, click "Urdu" toggle in navbar, verify text changes to Roman Urdu within 200ms, refresh page and verify Urdu persists

### Implementation for User Story 4

- [ ] T050 [P] [US4] Create LanguageToggle component at `src/theme/NavbarItem/LanguageToggle.tsx`
- [ ] T051 [P] [US4] Swizzle NavbarItem at `src/theme/NavbarItem/index.tsx` (wrap original with custom logic)
- [ ] T052 [US4] Import LanguageContext into LanguageToggle.tsx, consume {locale, setLocale}
- [ ] T053 [US4] Implement toggle button UI in LanguageToggle: two-state button showing "Urdu" when locale="en", "English" when locale="ur"
- [ ] T054 [US4] Add onClick handler in LanguageToggle: setLocale("ur") if currently "en", setLocale("en") if currently "ur"
- [ ] T055 [US4] Verify localStorage.setItem("locale", newLocale) is called in LanguageContext.setLocale (already implemented in T011)
- [ ] T056 [US4] Update swizzled NavbarItem index.tsx to conditionally render LanguageToggle when navbar item type is "custom-language-toggle"
- [ ] T057 [US4] Update docusaurus.config.js navbar.items array to add {type: 'custom-language-toggle', position: 'right'}
- [ ] T058 [US4] Consume navbarTranslations[locale] in existing navbar components to display localized text (Home→Ghar, Sign In→Dakhil Hon, etc. per data-model.md Entity 3)
- [ ] T059 [US4] Wrap Docusaurus Root component with LanguageContext.Provider (ensure context available globally)

**Checkpoint**: Urdu toggle functional, navbar text switches languages instantly, preference persists across page reloads via localStorage

---

## Phase 8: User Story 5 - translate-urdu Skill (Priority: P3)

**Goal**: Enable chapter translation to Roman Urdu while preserving code blocks via `@skill:translate-urdu` command

**Independent Test**: Run `@skill:translate-urdu "docs/module-1-ros2-basics/chapter-1-intro.md"`, verify `.ur.md` file exists with Roman Urdu prose and identical Python code blocks

### Implementation for User Story 5

- [ ] T060 [US5] Create translate-urdu skill at `.claude/skills/translate-urdu.md`
- [ ] T061 [US5] Add YAML frontmatter to translate-urdu.md (skill_name: translate-urdu, version: 1.0.0, persona: The Linguist)
- [ ] T062 [US5] Write ## Persona section defining The Linguist role (technical translator for Roman Urdu, understands Pakistani colloquial Urdu)
- [ ] T063 [US5] Write ## Questions section with clarifier: "Which Urdu dialect? (Standard/Punjabi-influenced/Sindhi-influenced)" - default to Standard Pakistani Roman Urdu per research.md Decision 3
- [ ] T064 [US5] Write ## Principles section with execution rules (translate prose to informal Pakistani Roman Urdu, preserve ALL code blocks unchanged, keep English technical terms with Urdu explanations in parentheses: "ROS 2 node (ek process jo messages send karta hai)", create parallel .ur.md file - do NOT overwrite original, add `locale: ur` to frontmatter, translate title in frontmatter, use Roman Urdu UI translations from data-model.md Entity 3)
- [ ] T065 [US5] Add example invocation: `@skill:translate-urdu "docs/module-1-ros2-basics/chapter-2-pub-sub.md"`
- [ ] T066 [US5] Document output path pattern: `docs/module-N/chapter-M-<slug>.ur.md`
- [ ] T067 [US5] Add validation rule in Principles: Verify code blocks unchanged via diff comparison after translation

**Checkpoint**: translate-urdu skill complete, ready to create localized chapter versions

---

## Phase 9: User Story 6 - test-ui Skill (Priority: P3)

**Goal**: Enable automated Playwright testing for landing page features via `@skill:test-ui` command

**Independent Test**: Run `@skill:test-ui "landing-page"`, verify it executes Playwright tests and generates `test-results/landing-page-report.html`

### Implementation for User Story 6

- [ ] T068 [US6] Create test-ui skill at `.claude/skills/test-ui.md`
- [ ] T069 [US6] Add YAML frontmatter to test-ui.md (skill_name: test-ui, version: 1.0.0, persona: The QA)
- [ ] T070 [US6] Write ## Persona section defining The QA role (automated testing expert, Playwright specialist)
- [ ] T071 [US6] Write ## Questions section with clarifier: "Test scope: landing-page | auth-flow | chatbot | full-suite?"
- [ ] T072 [US6] Write ## Principles section with execution rules (launch Playwright headless Chromium, execute tests in tests/e2e/<scope>.spec.ts, validate hero section renders, validate feature grid has 4 cards, validate Urdu toggle changes navbar text, validate "Get Started" button navigates to /docs/intro, measure performance: LCP <2.5s, generate HTML report in test-results/, take screenshots on failure)
- [ ] T073 [US6] Add example invocation: `@skill:test-ui "landing-page"`
- [ ] T074 [US6] Document test file creation in Principles: If tests/e2e/<scope>.spec.ts doesn't exist, skill should generate it based on quickstart.md test scenarios
- [ ] T075 [US6] Add prerequisite check: Verify Playwright installed (`npx playwright --version`), if not found display: "Install Playwright: npx playwright install chromium"
- [ ] T076 [US6] Document output path: `test-results/<scope>-report.html` and `test-results/screenshots/` for failures

**Checkpoint**: test-ui skill complete, ready to automate landing page validation

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T077 [P] Verify all 5 skills exist in `.claude/skills/` (generate-spec.md, generate-chapter.md, rag-ingest.md, translate-urdu.md, test-ui.md)
- [ ] T078 [P] Validate all skills follow P+Q+P structure (YAML frontmatter + ## Persona + ## Questions + ## Principles)
- [ ] T079 [P] Run quickstart.md Part 1 validation: Test all 5 skills with sample invocations
- [ ] T080 [P] Run quickstart.md Part 2 validation: Verify hero section, Urdu toggle, feature grid on http://localhost:3000
- [ ] T081 Verify hero section Largest Contentful Paint <2.5s using Lighthouse (per success criterion SC-012)
- [ ] T082 [P] Verify feature grid responsive layout on mobile (375px), tablet (768px), desktop (1200px)
- [ ] T083 [P] Test Urdu toggle response time <200ms (use browser DevTools Performance tab)
- [ ] T084 [P] Verify localStorage persistence: Toggle to Urdu, refresh page, confirm navbar stays in Urdu
- [ ] T085 [P] Verify auth integration: Sign in with Feature 003 account, confirm hero CTA changes to "Continue Learning"
- [ ] T086 [P] Verify Urdu toggle independent of auth state: Change language while signed in, sign out, confirm language persists
- [ ] T087 Code cleanup: Remove any commented-out Docusaurus starter code from src/pages/index.tsx
- [ ] T088 Documentation: Update README.md with "Intelligence Engine" section explaining skills library
- [ ] T089 [P] Verify constitution compliance: All 7 principles PASS (from plan.md Constitution Check)
- [ ] T090 Final validation: Confirm +100 hackathon bonus points earned (5 skills + Urdu translation)

**Checkpoint**: Feature 004 implementation complete, all user stories independently testable, hackathon requirements met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phases 3-9)**: All depend on Foundational (Phase 2) completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order: P1 stories (US1, US2, US7) → P2 stories (US3, US4) → P3 stories (US5, US6)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 generate-spec (P1)**: Can start after Foundational - No dependencies on other stories
- **US2 generate-chapter (P1)**: Can start after Foundational - No dependencies on other stories
- **US7 Landing Page Hero (P1)**: Can start after Foundational - Integrates with Feature 003 AuthContext but independently testable
- **US3 rag-ingest (P2)**: Can start after Foundational - No dependencies (works on docs/ files independently)
- **US4 Urdu Toggle (P2)**: Can start after Foundational - Uses LanguageContext from Phase 2
- **US5 translate-urdu (P3)**: Can start after Foundational - No dependencies (translates existing chapters)
- **US6 test-ui (P3)**: Should start after US7 complete (tests landing page features), but skill file itself can be created anytime

### Within Each User Story

- Skills (US1-US6): Single-file Markdown creation - tasks are sequential within each skill
- Landing Page (US7): T027-T028 can run in parallel (different components), T029-T040 are sequential (building HeroSection, FeatureGrid, integrating)
- Urdu Toggle (US4): T050-T051 can run in parallel (different files), remaining tasks sequential

### Parallel Opportunities

**Within Setup (Phase 1)**:
- Tasks T002, T003, T004, T005, T006 can all run in parallel (different directories)

**Within Foundational (Phase 2)**:
- Tasks T008, T009, T010 can run in parallel (independent verifications)

**Across User Stories** (after Phase 2 complete):
- All P1 stories (US1, US2, US7) can start in parallel
- All P2 stories (US3, US4) can start in parallel after P1 complete
- All P3 stories (US5, US6) can start in parallel after P2 complete

**Within User Stories**:
- US7: Tasks T027-T028, T034-T037 marked [P] can run in parallel
- US4: Tasks T050-T051 marked [P] can run in parallel

**Within Polish (Phase 10)**:
- Tasks T077, T078, T079, T080, T082, T083, T084, T085, T086, T089 marked [P] can run in parallel

---

## Parallel Example: MVP (P1 Stories)

```bash
# After Phase 2 completes, launch all P1 user stories together:

# Developer A or Parallel Session 1:
Task: "Create generate-spec skill at .claude/skills/generate-spec.md" (US1)

# Developer B or Parallel Session 2:
Task: "Create generate-chapter skill at .claude/skills/generate-chapter.md" (US2)

# Developer C or Parallel Session 3:
Task: "Create HeroSection component at src/components/LandingPage/HeroSection.tsx" (US7)
Task: "Create FeatureGrid component at src/components/LandingPage/FeatureGrid.tsx" (US7)
```

---

## Parallel Example: Landing Page Components (US7)

```bash
# Within User Story 7, these tasks can run in parallel:

Task: "Create HeroSection component at src/components/LandingPage/HeroSection.tsx"
Task: "Create FeatureGrid component at src/components/LandingPage/FeatureGrid.tsx"

# Later in US7, these feature card data tasks can run in parallel:
Task: "Add FeatureCard data for 'Interactive RAG Chatbot' with MessageSquare icon"
Task: "Add FeatureCard data for 'Hardware-Aware Learning' with Cpu icon"
Task: "Add FeatureCard data for 'Urdu Translation' with Languages icon"
Task: "Add FeatureCard data for 'Real-World Projects' with Rocket icon"
```

---

## Implementation Strategy

### MVP First (P1 Stories: US1 + US2 + US7)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T012) - CRITICAL
3. Complete Phase 3: US1 generate-spec skill (T013-T019)
4. **STOP and TEST**: Run `@skill:generate-spec "test feature"`, verify spec created
5. Complete Phase 4: US2 generate-chapter skill (T020-T026)
6. **STOP and TEST**: Run `@skill:generate-chapter "test chapter"`, verify MDX created
7. Complete Phase 5: US7 Landing Page (T027-T040)
8. **STOP and TEST**: Open http://localhost:3000, verify hero + feature grid
9. **MVP COMPLETE**: Demo shows 2 working skills + remediated landing page

### Incremental Delivery (Add P2 Stories: US3 + US4)

10. Complete Phase 6: US3 rag-ingest skill (T041-T049)
11. **STOP and TEST**: Run `@skill:rag-ingest`, verify Qdrant vectors created
12. Complete Phase 7: US4 Urdu Toggle (T050-T059)
13. **STOP and TEST**: Toggle language, verify navbar changes + persists
14. **P2 COMPLETE**: Demo shows 3 skills + localized UI

### Full Feature (Add P3 Stories: US5 + US6)

15. Complete Phase 8: US5 translate-urdu skill (T060-T067)
16. **STOP and TEST**: Run `@skill:translate-urdu "<chapter>"`, verify .ur.md created
17. Complete Phase 9: US6 test-ui skill (T068-T076)
18. **STOP and TEST**: Run `@skill:test-ui "landing-page"`, verify tests pass
19. **ALL STORIES COMPLETE**: All 5 skills + landing page remediation working

### Polish & Validate

20. Complete Phase 10: Polish (T077-T090)
21. **FINAL VALIDATION**: Run full quickstart.md, verify all success criteria met
22. **HACKATHON READY**: +100 bonus points confirmed (5 skills + Urdu translation)

### Parallel Team Strategy

With 3 developers (optimal for P1 MVP):

1. All complete Setup + Foundational together (T001-T012)
2. Once Foundational done:
   - **Developer A**: US1 generate-spec skill (T013-T019)
   - **Developer B**: US2 generate-chapter skill (T020-T026)
   - **Developer C**: US7 Landing Page (T027-T040)
3. Test MVP independently, merge when all pass
4. Proceed to P2 stories (2 developers) then P3 stories (2 developers)

---

## Notes

- **[P] tasks**: Different files, no dependencies - safe to parallelize
- **[Story] labels**: Map tasks to user stories for traceability and independent testing
- **Tests omitted**: Spec does not explicitly request TDD. Manual testing via quickstart.md + test-ui skill (US6) provides validation
- **Skill files**: Markdown only (no executable code) - safe, declarative, git-friendly
- **Constitution compliance**: All tasks align with 7 principles (validated in plan.md)
- **Hackathon alignment**: Tasks prioritized to earn +100 bonus points (5 skills + Urdu = +50 + +50)
- **Independent user stories**: Each story (US1-US7) delivers standalone value and can be tested independently per spec.md requirements
- **Commit strategy**: Commit after each phase checkpoint to enable incremental rollback
- **Stop points**: Each checkpoint is a natural demo/validation point - stop to verify before continuing

---

## Task Count Summary

- **Phase 1 (Setup)**: 6 tasks
- **Phase 2 (Foundational)**: 6 tasks (BLOCKS all user stories)
- **Phase 3 (US1 generate-spec)**: 7 tasks
- **Phase 4 (US2 generate-chapter)**: 7 tasks
- **Phase 5 (US7 Landing Page)**: 14 tasks
- **Phase 6 (US3 rag-ingest)**: 9 tasks
- **Phase 7 (US4 Urdu Toggle)**: 10 tasks
- **Phase 8 (US5 translate-urdu)**: 8 tasks
- **Phase 9 (US6 test-ui)**: 9 tasks
- **Phase 10 (Polish)**: 14 tasks

**Total**: 90 tasks

**MVP Scope** (P1 stories): 40 tasks (Setup + Foundational + US1 + US2 + US7)

**Parallel Opportunities Identified**: 18 tasks marked [P] across all phases

**Independent Test Criteria**: All 7 user stories have explicit "Independent Test" sections in spec.md and corresponding checkpoint validation in tasks.md
