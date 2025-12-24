# MVP Validation Guide - Feature 004 Intelligence Engine

**Status**: MVP Implementation Complete (40/40 tasks)
**Date**: 2025-12-25
**Branch**: `004-intelligence-engine`

## Overview

This guide provides step-by-step instructions to validate the MVP implementation of Feature 004-intelligence-engine.

**MVP Scope Completed**:
- ✅ Phase 1: Setup (6 tasks)
- ✅ Phase 2: Foundational (6 tasks)
- ✅ Phase 3: US1 generate-spec Skill (7 tasks)
- ✅ Phase 4: US2 generate-chapter Skill (7 tasks)
- ✅ Phase 5: US7 Landing Page (14 tasks)

---

## Prerequisites

Before testing, ensure you have:
- [x] Node.js and npm installed
- [x] Docusaurus dependencies installed (`npm install`)
- [x] Claude Code CLI installed (for skill testing)
- [x] Feature 003-better-auth implemented (for auth integration testing)

---

## Part 1: Test Skills Library

### Test 1.1: generate-spec Skill

**Purpose**: Verify The Architect skill can create feature specifications

**Steps**:
```bash
# 1. Open Claude Code CLI in project directory
cd /mnt/e/M.Y/GIAIC-Hackathons/final-project-v2/Humanoid-Robots-Book

# 2. Invoke the generate-spec skill
@skill:generate-spec "Add dark mode toggle to landing page"
```

**Expected Behavior**:
1. Skill asks clarifying questions (if feature description is ambiguous):
   - Feature scope boundaries?
   - Primary users and their goals?
   - Success metrics?
2. Generates `specs/005-dark-mode/spec.md`
3. Creates `specs/005-dark-mode/checklists/requirements.md`
4. Output confirms: "✅ Created specs/005-dark-mode/spec.md"

**Verification**:
```bash
# Check spec was created
ls specs/005-dark-mode/spec.md

# Verify spec contains required sections
grep -E "## User Scenarios|## Requirements|## Success Criteria" specs/005-dark-mode/spec.md

# Verify checklist created
ls specs/005-dark-mode/checklists/requirements.md
```

**Pass Criteria**:
- [ ] Spec file created at correct path
- [ ] Spec contains User Scenarios section
- [ ] Spec contains Functional Requirements section
- [ ] Spec contains Success Criteria section
- [ ] Requirements checklist created
- [ ] Feature number auto-incremented (005 after 004)

---

### Test 1.2: generate-chapter Skill

**Purpose**: Verify The Author skill can create Docusaurus MDX chapters

**Steps**:
```bash
# Invoke the generate-chapter skill
@skill:generate-chapter "Chapter 10: Isaac Sim Advanced Features"
```

**Expected Behavior**:
1. Skill asks clarifying questions:
   - Target audience level? (beginner/intermediate/advanced)
   - Prerequisites? (which chapters must be completed first)
2. Generates `docs/module-3-isaac-sim/chapter-10-advanced.md`
3. Output confirms file creation with word count and code example count

**Verification**:
```bash
# Check chapter was created
ls docs/module-3-isaac-sim/chapter-10-advanced.md

# Verify YAML frontmatter exists
head -5 docs/module-3-isaac-sim/chapter-10-advanced.md | grep -E "title:|sidebar_position:"

# Verify code blocks exist
grep -c '```' docs/module-3-isaac-sim/chapter-10-advanced.md
# Should return at least 6 (3 code blocks = 6 backtick lines)

# Verify Docusaurus admonitions exist
grep -E ':::tip|:::warning|:::note' docs/module-3-isaac-sim/chapter-10-advanced.md
```

**Pass Criteria**:
- [ ] Chapter file created at correct path (module-3-isaac-sim)
- [ ] YAML frontmatter includes title and sidebar_position
- [ ] At least 3 code blocks with syntax highlighting
- [ ] Docusaurus components used (:::tip, :::warning, etc.)
- [ ] Chapter length ≥1500 words
- [ ] Cross-references to other chapters present

---

## Part 2: Test Landing Page

### Test 2.1: Start Development Server

**Steps**:
```bash
# Start Docusaurus dev server
npm start
```

**Expected Output**:
```
[INFO] Starting the development server...
[SUCCESS] Docusaurus website is running at: http://localhost:3000/
```

**Pass Criteria**:
- [ ] Server starts without errors
- [ ] No TypeScript compilation errors
- [ ] No React component errors in terminal

---

### Test 2.2: Hero Section Visual Validation

**Steps**:
1. Open browser: `http://localhost:3000`
2. Observe hero section above the fold

**Expected Visual**:
- **Title**: "Master Physical AI & Humanoid Robotics" (large, prominent)
- **Subtitle**: Multi-line description mentioning "free interactive textbook", "RAG chatbot", "ROS 2", "Isaac Sim", "Gazebo", "humanoid robotics"
- **CTA Button**: Blue/secondary button with text

**Pass Criteria**:
- [ ] Hero section visible without scrolling (above the fold)
- [ ] Title displays correctly
- [ ] Subtitle is readable and complete
- [ ] CTA button is visible and styled

---

### Test 2.3: Authentication Integration (Feature 003)

**Purpose**: Verify conditional CTA button text based on auth state

**Steps**:

**Test Case A - Unauthenticated User**:
1. Ensure you are signed out (click "Sign Out" if needed)
2. Refresh homepage: `http://localhost:3000`
3. Observe CTA button text

**Expected**: Button shows **"Get Started"**

**Test Case B - Authenticated User**:
1. Sign in using Feature 003-better-auth
2. Return to homepage: `http://localhost:3000`
3. Observe CTA button text

**Expected**: Button shows **"Continue Learning"**

**Pass Criteria**:
- [ ] Unauthenticated: CTA shows "Get Started"
- [ ] Authenticated: CTA shows "Continue Learning"
- [ ] No JavaScript errors in browser console
- [ ] AuthContext integration works correctly

---

### Test 2.4: CTA Button Navigation

**Steps**:
1. Click the "Get Started" / "Continue Learning" button
2. Observe navigation

**Expected**: Browser navigates to `/docs/module-1-ros2-basics/chapter-1-intro`

**Pass Criteria**:
- [ ] Button is clickable
- [ ] Navigation occurs without page refresh
- [ ] Correct documentation page loads

---

### Test 2.5: Feature Grid Validation

**Purpose**: Verify 4 feature cards display correctly with icons

**Steps**:
1. Scroll down on homepage to see feature grid (below hero section)
2. Count feature cards
3. Verify each card has icon, title, description

**Expected Cards**:
1. **Interactive RAG Chatbot** - MessageSquare icon (blue)
2. **Hardware-Aware Learning** - Cpu icon (green)
3. **Urdu Translation** - Languages icon (purple)
4. **Real-World Projects** - Rocket icon (orange)

**Pass Criteria**:
- [ ] Exactly 4 feature cards visible
- [ ] All 4 icons render correctly (lucide-react)
- [ ] Each card has title and 2-sentence description
- [ ] Icons have color styling

---

### Test 2.6: Responsive Layout Testing

**Purpose**: Verify layout adapts to mobile/tablet/desktop

**Steps**:

**Mobile (375px width)**:
1. Open browser DevTools (F12)
2. Enable device emulation (iPhone SE or similar)
3. Set width to 375px
4. Observe feature grid

**Expected**: Cards stack vertically (1 card per row)

**Tablet (768px width)**:
1. Set device width to 768px
2. Observe feature grid

**Expected**: Cards display 2 per row

**Desktop (1200px width)**:
1. Set device width to 1200px
2. Observe feature grid

**Expected**: Cards display 4 per row (horizontal)

**Pass Criteria**:
- [ ] Mobile: 1 card per row (stacked vertically)
- [ ] Tablet: 2 cards per row
- [ ] Desktop: 4 cards per row (uses col col--3 = 4 columns)
- [ ] No horizontal scrolling on any screen size
- [ ] Icons remain visible at all sizes

---

## Part 3: Code Quality Checks

### Test 3.1: TypeScript Compilation

**Steps**:
```bash
# Run TypeScript type checking
npm run build
```

**Expected**: No TypeScript errors

**Pass Criteria**:
- [ ] Build completes successfully
- [ ] No type errors in HeroSection.tsx
- [ ] No type errors in FeatureGrid.tsx
- [ ] No type errors in LanguageContext.tsx

---

### Test 3.2: Component Import Verification

**Steps**:
```bash
# Verify imports resolve correctly
grep -r "import.*HeroSection" src/
grep -r "import.*FeatureGrid" src/
grep -r "import.*useAuth" src/components/LandingPage/
```

**Expected**:
- HeroSection imported in `src/pages/index.tsx`
- FeatureGrid imported in `src/pages/index.tsx`
- useAuth imported from `@site/src/context/AuthContext`

**Pass Criteria**:
- [ ] All imports resolve without errors
- [ ] No circular dependencies
- [ ] Paths use @site/ alias correctly

---

## Part 4: Foundation Verification

### Test 4.1: LanguageContext Setup

**Purpose**: Verify LanguageContext is ready for Phase 7 (Urdu Toggle)

**Steps**:
```bash
# Check LanguageContext file exists
ls src/context/LanguageContext.tsx

# Verify navbarTranslations constant exists
grep "navbarTranslations" src/context/LanguageContext.tsx

# Verify Urdu translations exist
grep "Ghar\|Dakhil Hon" src/context/LanguageContext.tsx
```

**Pass Criteria**:
- [ ] LanguageContext.tsx exists
- [ ] navbarTranslations constant defined
- [ ] English translations present (Home, Sign In, etc.)
- [ ] Urdu translations present (Ghar, Dakhil Hon, etc.)
- [ ] localStorage integration implemented

---

### Test 4.2: Skills Directory Structure

**Steps**:
```bash
# Verify skills directory exists
ls -la .claude/skills/

# Check skill files exist
ls .claude/skills/generate-spec.md
ls .claude/skills/generate-chapter.md

# Verify P+Q+P structure
grep -E "## Persona|## Questions|## Principles" .claude/skills/generate-spec.md
```

**Pass Criteria**:
- [ ] `.claude/skills/` directory exists
- [ ] generate-spec.md present
- [ ] generate-chapter.md present
- [ ] Both skills have YAML frontmatter
- [ ] Both skills have 3 H2 sections (Persona, Questions, Principles)

---

## Part 5: Performance Validation

### Test 5.1: Landing Page Load Time

**Purpose**: Verify hero section loads quickly (per SC-012: LCP <2.5s)

**Steps**:
1. Open browser DevTools → Lighthouse tab
2. Run Lighthouse audit on `http://localhost:3000`
3. Check Performance score and Largest Contentful Paint (LCP)

**Expected**:
- Performance score: ≥90
- Largest Contentful Paint (LCP): <2.5 seconds

**Pass Criteria**:
- [ ] Performance score ≥90
- [ ] LCP <2.5s
- [ ] No layout shift issues
- [ ] No blocking resources

---

### Test 5.2: Touch Target Size (Mobile Accessibility)

**Purpose**: Verify feature card icons meet minimum touch target size (44x44px)

**Steps**:
1. Open DevTools → Elements tab
2. Inspect feature card icons
3. Check computed dimensions

**Expected**: Icon size ≥44px (lucide-react default is 48px)

**Pass Criteria**:
- [ ] Icon touch targets ≥44x44px
- [ ] CTA button touch target ≥44x44px
- [ ] No accessibility warnings in Lighthouse

---

## Summary Checklist

### MVP Acceptance Criteria

**Skills Library**:
- [ ] generate-spec skill creates valid specs with SDD template
- [ ] generate-chapter skill creates valid Docusaurus MDX chapters
- [ ] Skills follow P+Q+P framework structure
- [ ] Skills are invocable via Claude Code CLI

**Landing Page**:
- [ ] Hero section visible above fold
- [ ] Title: "Master Physical AI & Humanoid Robotics"
- [ ] CTA button conditional on auth state
- [ ] CTA navigates to Chapter 1
- [ ] Feature grid shows 4 cards with icons
- [ ] Responsive layout works (mobile/tablet/desktop)

**Foundation**:
- [ ] LanguageContext ready for Urdu toggle (Phase 7)
- [ ] lucide-react icons render correctly
- [ ] AuthContext integration works
- [ ] No TypeScript errors
- [ ] Build succeeds

---

## Troubleshooting

### Issue: "Cannot find module '@site/src/context/AuthContext'"

**Solution**: Verify Feature 003-better-auth is implemented. If not, create a mock AuthContext:

```typescript
// src/context/AuthContext.tsx (mock)
import { createContext, useContext } from 'react';

const AuthContext = createContext({ user: null });

export function useAuth() {
  return useContext(AuthContext);
}
```

---

### Issue: Landing page shows blank white screen

**Solution**:
```bash
# Clear Docusaurus cache
npm run clear

# Rebuild
npm run build

# Restart dev server
npm start
```

---

### Issue: Icons not displaying

**Solution**:
```bash
# Verify lucide-react installed
npm list lucide-react

# Reinstall if missing
npm install lucide-react

# Restart dev server
npm start
```

---

## Next Steps After Validation

**If All Tests Pass**:
1. Commit MVP checkpoint:
   ```bash
   git add .
   git commit -m "feat(intelligence-engine): Complete MVP implementation"
   ```

2. Choose next phase:
   - **Option B**: Continue with P2 stories (rag-ingest + Urdu Toggle)
   - **Option C**: Create pull request for MVP review

**If Tests Fail**:
1. Review error messages in browser console
2. Check tasks.md for implementation details
3. Consult quickstart.md for troubleshooting steps
4. Fix issues and re-test

---

## Validation Report Template

After completing all tests, fill out this report:

```markdown
# MVP Validation Report - Feature 004

**Date**: YYYY-MM-DD
**Tester**: [Your Name]
**Branch**: 004-intelligence-engine

## Test Results

### Skills Library
- [ ] PASS / [ ] FAIL - generate-spec skill
- [ ] PASS / [ ] FAIL - generate-chapter skill

### Landing Page
- [ ] PASS / [ ] FAIL - Hero section display
- [ ] PASS / [ ] FAIL - Auth integration
- [ ] PASS / [ ] FAIL - Feature grid (4 cards)
- [ ] PASS / [ ] FAIL - Responsive layout

### Performance
- [ ] PASS / [ ] FAIL - LCP <2.5s
- [ ] PASS / [ ] FAIL - No TypeScript errors

## Issues Found
[List any failures or bugs discovered]

## Overall Status
- [ ] MVP READY FOR MERGE
- [ ] MVP NEEDS FIXES

## Recommendation
[Proceed with P2 implementation / Fix issues / Other]
```

---

**End of Validation Guide**
