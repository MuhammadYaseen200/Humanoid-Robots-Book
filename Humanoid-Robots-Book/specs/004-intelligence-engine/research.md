# Research: Intelligence Engine & Landing Page Remediation

**Feature**: 004-intelligence-engine
**Date**: 2025-12-24
**Purpose**: Resolve unknowns from Technical Context before Phase 1 design

## Decision 1: P+Q+P Skill Framework Structure

**Question**: What is the optimal Markdown structure for skills following the P+Q+P (Persona + Questions + Principles) framework that Claude Code CLI can interpret?

**Chosen**: Markdown with YAML frontmatter + three H2 sections (## Persona, ## Questions, ## Principles)

**Rationale**:
- **Human-Readable**: Markdown is git-friendly and easy to review/edit
- **Declarative**: No executable code reduces security risks
- **Self-Documenting**: Three-section structure clearly separates role, clarifiers, and execution rules
- **CLI-Compatible**: Claude Code CLI can parse YAML frontmatter for metadata and interpret H2 headings as skill components

**Alternatives Considered**:
1. **JSON Format** - Rejected: Less human-readable, harder to edit in git diffs
2. **YAML Only** - Rejected: More complex for prose content (Persona descriptions, Principle lists)
3. **Python Scripts** - Rejected: Security risk (arbitrary code execution), violates declarative principle

**Implementation Details**:
```markdown
---
skill_name: generate-spec
version: 1.0.0
description: Autonomous feature specification generation
persona: The Architect
---

## Persona
You are The Architect, a specification expert...

## Questions
1. What is the feature scope?
2. Who are the primary users?
3. What are the success criteria?

## Principles
- Use SDD template structure
- Generate measurable success criteria
- Auto-increment feature numbers
```

**Verification**: Create sample skill file and test invocation via `@skill:test` command

---

## Decision 2: Docusaurus Navbar Swizzling

**Question**: How do we inject a custom LanguageToggle component into the Docusaurus navbar without ejecting the entire theme?

**Chosen**: Swizzle NavbarItem component using safe swizzling approach

**Rationale**:
- **Official Method**: Docusaurus v3.x officially supports component swizzling
- **Minimal Breakage**: NavbarItem is a stable component with low risk of breaking changes
- **Upgrade Safety**: Safe swizzles receive updates via `@theme-original/NavbarItem` import pattern
- **Granular Control**: Can conditionally render custom components without affecting other navbar items

**Alternatives Considered**:
1. **Fork Docusaurus Theme** - Rejected: High maintenance burden, difficult to merge upstream updates
2. **CSS-Only Approach** - Rejected: Cannot add functionality (language toggle requires JavaScript state management)
3. **Plugin API** - Rejected: More complex setup, overkill for single component injection

**Implementation Details**:
```typescript
// src/theme/NavbarItem/index.tsx
import React from 'react';
import OriginalNavbarItem from '@theme-original/NavbarItem';
import LanguageToggle from './LanguageToggle';

export default function NavbarItem(props) {
  if (props.type === 'custom-language-toggle') {
    return <LanguageToggle />;
  }
  return <OriginalNavbarItem {...props} />;
}
```

**Docusaurus Config**:
```javascript
// docusaurus.config.js
navbar: {
  items: [
    // ... existing items
    {
      type: 'custom-language-toggle',
      position: 'right',
    },
  ],
}
```

**Verification**: Swizzle NavbarItem, add custom type, verify toggle appears in navbar

---

## Decision 3: Urdu Romanization Standards

**Question**: What Roman Urdu spelling conventions should the translate-urdu skill follow?

**Chosen**: Informal Pakistani Roman Urdu with preserved English technical terms

**Rationale**:
- **Target Audience**: Panaversity students in Pakistan use informal Roman Urdu in daily digital communication
- **Readability**: Informal conventions are more accessible than academic transliteration systems (ALA-LC, UN)
- **Technical Accuracy**: Preserving English terms ("ROS 2 node", "API") prevents confusion while adding Urdu explanations in parentheses

**Alternatives Considered**:
1. **ALA-LC Transliteration** - Rejected: Too academic, unfamiliar to general audience
2. **UN Romanization** - Rejected: Government/diplomatic standard, not colloquial
3. **Pure Urdu Script (Arabic)** - Rejected: Out of scope (requires RTL layout), most Pakistani students read Roman Urdu online

**UI Translations**:
| English | Roman Urdu | Notes |
|---------|------------|-------|
| Home | Ghar | Common colloquial term |
| About | Hamara Bare Main | Informal "about us" |
| Docs | Kitabain | Plural of "book" (more natural than "dastavezat") |
| Sign In | Dakhil Hon | Formal entry phrase |
| Sign Up | Shamil Hon | Join/participate phrase |
| Sign Out | Nikal Jayen | Polite exit phrase |

**Technical Terms**:
- "ROS 2 node" → "ROS 2 node (ek process jo messages send karta hai)"
- "API" → "API (application programming interface)"
- "Gazebo" → "Gazebo (simulation environment)"

**Verification**: Test translations with Pakistani Panaversity students for comprehension

---

## Decision 4: localStorage Persistence Strategy

**Question**: How should the Urdu toggle persist language preference across browser sessions?

**Chosen**: localStorage with graceful degradation for unavailability

**Rationale**:
- **Simple API**: `localStorage.setItem/getItem` is straightforward
- **Persistence**: Survives browser restarts (unlike sessionStorage)
- **No Backend**: Client-side only reduces complexity, no database schema needed
- **Wide Support**: Available in all modern browsers (Chrome 4+, Firefox 3.5+, Safari 4+)

**Alternatives Considered**:
1. **sessionStorage** - Rejected: Does NOT persist across browser sessions (resets on tab close)
2. **Cookies** - Rejected: More complex API, size limits (4KB), requires expiration management
3. **IndexedDB** - Rejected: Overkill for single key-value pair, complex async API
4. **Backend Storage** - Rejected: Requires authentication, database schema, API endpoints (out of scope)

**Implementation Details**:
```typescript
// LanguageContext initialization
const [locale, setLocaleState] = useState<"en" | "ur">(() => {
  try {
    return (localStorage.getItem("locale") as "en" | "ur") || "en";
  } catch (error) {
    console.warn("localStorage unavailable, defaulting to English");
    return "en";
  }
});

// Update function
const setLocale = (newLocale: "en" | "ur") => {
  setLocaleState(newLocale);
  try {
    localStorage.setItem("locale", newLocale);
  } catch (error) {
    console.warn("Failed to persist language preference");
  }
};
```

**Graceful Degradation**:
- **Private Browsing**: localStorage throws exceptions → catch and default to "en"
- **Disabled Cookies**: Some browsers link localStorage to cookie settings → handle errors
- **Multi-Tab Sync**: NOT IMPLEMENTED (each tab manages own state, acceptable tradeoff)

**Verification**: Test in Chrome/Firefox/Safari normal + private browsing modes

---

## Decision 5: Qdrant Capacity Monitoring

**Question**: How should the rag-ingest skill warn users when Qdrant free tier (1GB) approaches capacity?

**Chosen**: Query collection stats via Qdrant API, warn at 80% capacity, do NOT block at 100%

**Rationale**:
- **Advance Warning**: 80% threshold (800MB of 1GB) gives users time to archive old content
- **API Availability**: Qdrant Cloud provides collection statistics endpoint
- **User Agency**: Not blocking at 100% respects user choice (they may want to manually delete vectors)
- **Failure Transparency**: Letting Qdrant return natural error at 100% is more informative than generic block message

**Alternatives Considered**:
1. **Block at 90%** - Rejected: Too restrictive, users may have legitimate need to approach limit
2. **No Warning** - Rejected: Poor UX, users surprised by sudden failures
3. **Auto-Delete Old Vectors** - Rejected: Too aggressive, users should decide what to archive

**Implementation Details**:
```python
# rag-ingest skill pseudocode
import qdrant_client

client = qdrant_client.QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)
collection_info = client.get_collection("textbook_chapters")

vectors_count = collection_info.vectors_count
max_capacity = 1_000_000  # 1GB free tier ≈ 1M vectors (assuming 1KB/vector)

usage_percent = (vectors_count / max_capacity) * 100

if usage_percent >= 80:
    print(f"⚠️ Qdrant storage at {usage_percent:.1f}% capacity ({vectors_count}/{max_capacity} vectors).")
    print("Consider archiving old chapters before continuing.")
    user_input = input("Continue anyway? (y/n): ")
    if user_input.lower() != 'y':
        exit(0)

# Proceed with upsert...
```

**Warning Thresholds**:
- **80-89%**: Yellow warning, ask for confirmation
- **90-99%**: Red warning, strongly recommend archiving
- **100%**: Let Qdrant return capacity error naturally (don't hide failure)

**Verification**: Test rag-ingest skill with mock collection approaching 80% capacity

---

## Summary of Resolved Unknowns

| Unknown from Technical Context | Resolution | Documented In |
|-------------------------------|------------|---------------|
| P+Q+P Skill Markdown Structure | YAML frontmatter + 3 H2 sections | Decision 1 |
| Docusaurus Navbar Customization | Safe swizzle NavbarItem component | Decision 2 |
| Urdu Romanization Conventions | Informal Pakistani Roman Urdu | Decision 3 |
| localStorage Persistence | localStorage API with graceful degradation | Decision 4 |
| Qdrant Capacity Monitoring | Query API, warn at 80%, no block | Decision 5 |

**All NEEDS CLARIFICATION markers resolved**. Proceed to Phase 1: Design & Contracts.
