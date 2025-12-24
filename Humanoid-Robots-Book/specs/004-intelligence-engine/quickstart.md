# Quick Start: Intelligence Engine & Landing Page Remediation

**Feature**: 004-intelligence-engine
**Audience**: Developers implementing or testing this feature
**Time to Complete**: 30 minutes (skills setup) + 15 minutes (landing page verification)

## Prerequisites

Before starting, ensure you have:

- ✅ Claude Code CLI installed and configured ([installation guide](https://claude.ai/code))
- ✅ Docusaurus project running (`npm start` on port 3000)
- ✅ OpenAI API key in `.env` (required for rag-ingest skill)
- ✅ Qdrant Cloud account with collection created (required for rag-ingest skill)
- ✅ Playwright installed (`npx playwright install chromium` - required for test-ui skill)
- ✅ Feature 003-better-auth implemented (authentication + hardware profiling)

## Part 1: Skills Library Setup

### Step 1: Verify Skills Directory

Check that the skills directory exists and contains 5 skill files:

```bash
ls .claude/skills/

# Expected output:
# generate-spec.md
# generate-chapter.md
# rag-ingest.md
# translate-urdu.md
# test-ui.md
```

If the directory doesn't exist, create it:

```bash
mkdir -p .claude/skills
```

### Step 2: Test generate-spec Skill

**Purpose**: Autonomous feature specification generation following SDD template

```bash
# In Claude Code CLI terminal:
@skill:generate-spec "Add dark mode toggle to landing page"

# Expected behavior:
# 1. Skill asks 3 clarifying questions (if feature description is ambiguous)
# 2. Generates specs/005-dark-mode/spec.md
# 3. Outputs confirmation: "✅ Spec created at specs/005-dark-mode/spec.md"
```

**Verification**:
```bash
# Check that spec was created
cat specs/005-dark-mode/spec.md | head -50

# Verify it contains:
# - Feature Specification title
# - User Scenarios section
# - Functional Requirements section
# - Success Criteria section
```

**If skill fails**: Check that `.claude/skills/generate-spec.md` exists and has correct P+Q+P structure

---

### Step 3: Test generate-chapter Skill

**Purpose**: Autonomous textbook chapter generation with Docusaurus MDX syntax

```bash
@skill:generate-chapter "Chapter 10: Isaac Sim Advanced Features"

# Expected behavior:
# 1. Skill asks about target audience level (beginner/intermediate/advanced)
# 2. Asks about prerequisites (which chapters should readers complete first?)
# 3. Generates docs/module-3-isaac-sim/chapter-10-advanced.md
# 4. Outputs confirmation with file path
```

**Verification**:
```bash
# Check that chapter was created
cat docs/module-3-isaac-sim/chapter-10-advanced.md | head -80

# Verify it contains:
# - YAML frontmatter (title, sidebar_position)
# - ## Introduction section
# - Python/C++ code blocks with syntax highlighting
# - Docusaurus admonitions (:::tip, :::warning, etc.)
```

**Open in Docusaurus**:
```bash
npm start  # If not already running
# Navigate to http://localhost:3000/docs/module-3-isaac-sim/chapter-10-advanced
# Verify chapter renders without errors
```

---

### Step 4: Test rag-ingest Skill

**Purpose**: Update Qdrant vector database with textbook content for RAG chatbot

**Prerequisites**:
- Ensure `QDRANT_URL` and `QDRANT_API_KEY` are in `.env`
- Ensure `OPENAI_API_KEY` is in `.env`

```bash
@skill:rag-ingest

# Expected behavior:
# 1. Scans docs/ directory recursively for .md files
# 2. Chunks content into 512-token segments with 50-token overlap
# 3. Generates embeddings via OpenAI API (text-embedding-3-small)
# 4. Upserts vectors to Qdrant collection "textbook_chapters"
# 5. Displays progress: "Processed 15/20 chapters..."
# 6. Shows warning if storage >80%: "⚠️ Qdrant at 82% capacity"
```

**Verification**:
```bash
# Query Qdrant to verify vectors exist
curl -X POST "https://YOUR_QDRANT_URL/collections/textbook_chapters/points/search" \
  -H "api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.1, 0.2, ...],  # Sample embedding
    "limit": 5
  }'

# Should return 5 vectors with metadata (chapter_id, file_path, module_name)
```

**If skill fails**:
- Check API keys in `.env`
- Verify Qdrant collection exists (`GET /collections/textbook_chapters`)
- Check OpenAI API quota

---

### Step 5: Test translate-urdu Skill

**Purpose**: Translate chapter prose to Roman Urdu while preserving code blocks

```bash
@skill:translate-urdu "docs/module-1-ros2-basics/chapter-1-intro.md"

# Expected behavior:
# 1. Reads original chapter
# 2. Translates prose to informal Pakistani Roman Urdu
# 3. Preserves ALL code blocks unchanged
# 4. Creates parallel file: docs/module-1-ros2-basics/chapter-1-intro.ur.md
# 5. Adds `locale: ur` to frontmatter
```

**Verification**:
```bash
# Check that .ur.md file exists
ls docs/module-1-ros2-basics/chapter-1-intro.ur.md

# Compare original and translated
diff docs/module-1-ros2-basics/chapter-1-intro.md \
     docs/module-1-ros2-basics/chapter-1-intro.ur.md

# Verify:
# - Code blocks are IDENTICAL (no changes)
# - Prose is in Roman Urdu (e.g., "Is chapter mein..." instead of "In this chapter...")
# - Technical terms preserved (e.g., "ROS 2 node" not transliterated)
```

---

### Step 6: Test test-ui Skill

**Purpose**: Run Playwright tests for landing page features

```bash
@skill:test-ui "landing-page"

# Expected behavior:
# 1. Launches Playwright (headless Chromium)
# 2. Executes tests/e2e/landing-page.spec.ts
# 3. Tests:
#    - Hero section renders
#    - Feature grid has 4 cards
#    - Urdu toggle changes navbar text
#    - "Get Started" button links to /docs/intro
# 4. Generates HTML report: test-results/landing-page-report.html
# 5. Takes screenshots on failure
```

**Verification**:
```bash
# Check test results
open test-results/landing-page-report.html  # macOS
xdg-open test-results/landing-page-report.html  # Linux

# Expected output:
# ✅ Hero section visible
# ✅ Feature grid has 4 cards
# ✅ Urdu toggle works
# ✅ CTA button navigates correctly
# ✅ Performance: LCP < 2.5s
```

**If tests fail**:
- Check that Docusaurus is running on http://localhost:3000
- Verify Playwright browser installed (`npx playwright install chromium`)
- Review screenshots in `test-results/screenshots/`

---

## Part 2: Landing Page Features

### Verify Hero Section

**What to Check**:
1. Navigate to http://localhost:3000
2. Hero section should display above the fold (no scrolling required)
3. Title: "Master Physical AI & Humanoid Robotics"
4. Subtitle: Description of the textbook project
5. CTA button:
   - If unauthenticated: "Get Started"
   - If authenticated: "Continue Learning"

**Manual Test**:
```bash
# 1. Open homepage
open http://localhost:3000

# 2. Sign out if authenticated
# Click "Sign Out" in navbar

# 3. Verify hero section
# - Title visible? ✅
# - Subtitle visible? ✅
# - "Get Started" button visible? ✅

# 4. Click "Get Started"
# Should navigate to /docs/module-1-ros2-basics/chapter-1-intro

# 5. Sign in with test account
# Email: test@example.com
# Password: SecurePass123!

# 6. Return to homepage
# - CTA button now says "Continue Learning"? ✅
```

---

### Test Urdu Toggle

**What to Check**:
1. Urdu/English toggle button in navbar (top-right)
2. Clicking toggle changes navbar text within 200ms
3. Language preference persists across page reloads
4. No page reload during toggle (smooth transition)

**Manual Test**:
```bash
# 1. Open homepage
open http://localhost:3000

# 2. Verify English navbar
# Items: Home | About | Docs | Sign In | Sign Up

# 3. Click "Urdu" toggle button
# Wait <200ms

# 4. Verify Urdu navbar
# Items: Ghar | Hamara Bare Main | Kitabain | Dakhil Hon | Shamil Hon

# 5. Refresh page (Cmd+R / Ctrl+R)
# Navbar should still display Urdu text (localStorage persistence)

# 6. Click "English" toggle
# Navbar reverts to English

# 7. Open browser dev tools → Application → Local Storage
# Key: "locale"
# Value: "en" or "ur" (depending on current selection)
```

**If toggle doesn't work**:
- Check browser console for JavaScript errors
- Verify LanguageContext.tsx is imported in Docusaurus Root
- Test in incognito mode (localStorage may be disabled in regular mode)

---

### Verify Feature Grid

**What to Check**:
1. Feature grid appears below hero section
2. 4 cards: Interactive RAG Chatbot, Hardware-Aware Learning, Urdu Translation, Real-World Projects
3. Each card has icon, title, 2-sentence description
4. Responsive layout:
   - Mobile (<768px): 1 card per row
   - Tablet (768-1024px): 2 cards per row
   - Desktop (>1024px): 4 cards per row

**Manual Test**:
```bash
# 1. Open homepage
open http://localhost:3000

# 2. Scroll down to feature grid
# Verify 4 cards are visible

# 3. Check card content
# Card 1: "Interactive RAG Chatbot" with message icon
# Card 2: "Hardware-Aware Learning" with CPU icon
# Card 3: "Urdu Translation" with language icon
# Card 4: "Real-World Projects" with rocket icon

# 4. Test responsiveness
# - Resize browser to 375px width (mobile)
#   → Cards stack vertically (1 per row)
# - Resize to 800px width (tablet)
#   → Cards display 2 per row
# - Resize to 1200px width (desktop)
#   → Cards display 4 per row (horizontal grid)
```

---

## Part 3: Integration Testing

### Test Skill + Landing Page Workflow

**Scenario**: Generate a new spec using generate-spec skill, then verify it's usable for future work

```bash
# 1. Create new feature spec
@skill:generate-spec "Add search functionality to textbook"

# 2. Verify spec created
cat specs/005-search/spec.md

# 3. Use spec to plan implementation
/sp.plan  # (assuming you're in Feature 005 branch)

# 4. This demonstrates the full SDD workflow:
# Constitution → Spec (via skill) → Plan → Tasks → Implementation
```

---

### Test Urdu Toggle + Authentication Integration

**Scenario**: Verify language preference persists independently of auth state

```bash
# 1. Sign out (if authenticated)
# Click "Sign Out" in navbar

# 2. Toggle to Urdu
# Click "Urdu" button → navbar changes to Roman Urdu

# 3. Sign in
# Click "Dakhil Hon" (Sign In)
# Enter credentials

# 4. Verify Urdu persists after authentication
# Navbar should still show: Ghar | Hamara Bare Main | Nikal Jayen (Sign Out)

# 5. Sign out
# Click "Nikal Jayen" (Sign Out)

# 6. Verify Urdu persists after sign-out
# Navbar should show: Ghar | Hamara Bare Main | Dakhil Hon | Shamil Hon
```

**Expected**: Language preference (Urdu) is INDEPENDENT of authentication state

---

## Troubleshooting

### Issue: Skill not found

**Error**: `@skill:generate-spec: command not found`

**Solution**:
```bash
# 1. Verify skill file exists
ls .claude/skills/generate-spec.md

# 2. Check skill file structure
head -20 .claude/skills/generate-spec.md

# Should have:
# - YAML frontmatter (---)
# - ## Persona section
# - ## Questions section
# - ## Principles section

# 3. Verify Claude Code CLI configuration
claude --version
claude config list
```

---

### Issue: Urdu toggle not persisting

**Error**: Navbar reverts to English after page refresh

**Solution**:
```bash
# 1. Open browser dev tools → Console
# Look for errors like "localStorage.setItem failed"

# 2. Check if localStorage is disabled
# Dev Tools → Application → Local Storage
# If empty or grayed out, localStorage may be disabled

# 3. Test in regular browsing mode (not incognito)
# Incognito/Private browsing often disables localStorage

# 4. Verify LanguageContext initialization
# In src/context/LanguageContext.tsx:
# - Check localStorage.getItem("locale") is called on mount
# - Check setLocale calls localStorage.setItem("locale", newLocale)
```

---

### Issue: Hero section not loading

**Error**: Landing page shows blank white screen

**Solution**:
```bash
# 1. Clear Docusaurus cache
npm run clear
npm start

# 2. Check browser console for React errors
# Dev Tools → Console
# Look for "Error: Cannot read property 'user' of undefined" (AuthContext issue)

# 3. Verify AuthContext.Provider wraps Root
# Check src/theme/Root.tsx (or Docusaurus config)

# 4. Check for conflicting CSS
# Inspect hero section element → Computed styles
# Verify `display: none` is not set by accident
```

---

## Success Criteria Checklist

After completing this quickstart, verify:

- [x] All 5 skills execute successfully (generate-spec, generate-chapter, rag-ingest, translate-urdu, test-ui)
- [x] Hero section displays "Master Physical AI & Humanoid Robotics" title
- [x] "Get Started" button links to `/docs/intro`
- [x] Feature grid shows 4 cards with icons
- [x] Urdu toggle changes navbar text within 200ms
- [x] Language preference persists across page reloads
- [x] Responsive layout works on mobile/tablet/desktop
- [x] Authentication integration works (Urdu persists independent of auth state)

**If all items checked**: Feature 004 implementation is COMPLETE ✅

**If any item unchecked**: Refer to Troubleshooting section or review implementation tasks in `specs/004-intelligence-engine/tasks.md`

---

## Next Steps

1. **Commit Changes**: Run `/sp.git.commit_pr` to create pull request
2. **Demo Video**: Record <90 second demo showing:
   - Skill invocation (`@skill:generate-spec`)
   - Hero section on landing page
   - Urdu toggle functionality
   - Feature grid responsiveness
3. **Hackathon Submission**: Document +100 bonus points earned:
   - +50 for 5 reusable skills
   - +50 for Urdu translation
