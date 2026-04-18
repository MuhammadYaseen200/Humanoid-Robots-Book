# Data Model: Intelligence Engine & Landing Page Remediation

**Feature**: 004-intelligence-engine
**Date**: 2025-12-24
**Purpose**: Document entities, state structures, and data flows

## Entity 1: LanguageContext (Frontend State)

**Purpose**: Manage global UI language preference (English or Urdu) across all Docusaurus pages

**Type**: React Context (in-memory state) + localStorage (persistent)

**TypeScript Interface**:
```typescript
interface LanguageContextType {
  locale: "en" | "ur";                      // Current language
  setLocale: (locale: "en" | "ur") => void; // Update function
}
```

**Fields**:
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| locale | `"en" \| "ur"` | Current UI language | Must be exactly "en" or "ur" (TypeScript literal union) |
| setLocale | Function | Updates locale + persists to localStorage | Accepts only "en" or "ur" |

**State Transitions**:
```text
Initial State: "en" (default)
User clicks "Urdu" toggle → setLocale("ur") → localStorage.setItem("locale", "ur") → Re-render navbar
Page refresh → Read localStorage.getItem("locale") → Initialize with "ur"
User clicks "English" toggle → setLocale("en") → localStorage.setItem("locale", "en") → Re-render navbar
```

**Storage**:
- **In-Memory**: React Context Provider wrapping Docusaurus Root component
- **Persistent**: Browser localStorage (key: "locale", values: "en" | "ur")

**Lifecycle**:
1. **Mount**: LanguageContext.Provider initializes
   - Attempt `localStorage.getItem("locale")`
   - If successful and value is "en" or "ur", use it
   - If null or error (private browsing), default to "en"
2. **Update**: User clicks toggle
   - Call `setLocale("ur")`
   - Update React state (triggers re-render)
   - Call `localStorage.setItem("locale", "ur")`
3. **Unmount**: No cleanup required (localStorage persists independently)

**Validation Rules**:
- locale MUST be "en" or "ur" (enforced by TypeScript)
- setLocale rejects any value other than "en" or "ur" (runtime check optional, type-safe)

**Error Handling**:
```typescript
// Graceful degradation for localStorage unavailability
try {
  const saved = localStorage.getItem("locale");
  if (saved === "en" || saved === "ur") {
    return saved;
  }
} catch (error) {
  console.warn("localStorage unavailable, defaulting to English");
}
return "en"; // Fallback
```

---

## Entity 2: Skill (Markdown Metadata Structure)

**Purpose**: Define reusable AI agent capabilities following P+Q+P (Persona, Questions, Principles) framework

**Type**: Markdown file stored in `.claude/skills/`

**File Structure**:
```markdown
---
skill_name: generate-spec         # Unique identifier
version: 1.0.0                     # Semantic versioning
description: Brief summary         # Human-readable description
persona: The Architect             # Role name
---

## Persona
[Detailed role description: who the skill acts as, what expertise it has]

## Questions
[Numbered list of clarification questions to ask users when inputs are ambiguous]
1. What is the feature scope?
2. Who are the primary users?
3. What are the success criteria?

## Principles
[Bullet list of execution rules the skill follows]
- Use SDD template structure
- Generate measurable success criteria
- Auto-increment feature numbers
```

**Fields (YAML Frontmatter)**:
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| skill_name | string | Unique skill identifier | "generate-spec" |
| version | string | Semantic version | "1.0.0" |
| description | string | Brief summary | "Autonomous spec generation" |
| persona | string | Role name | "The Architect" |

**Fields (Markdown Sections)**:
| Section | Type | Description | Constraints |
|---------|------|-------------|-------------|
| ## Persona | Prose | Role description, expertise, context | Required, free-form Markdown |
| ## Questions | Numbered list | Clarification prompts | 0-5 questions, numbered list format |
| ## Principles | Bullet list | Execution rules | 3-10 principles, bullet list format |

**Storage**: Filesystem (`.claude/skills/<skill_name>.md`)

**Lifecycle**:
1. **Creation**: Developer writes Markdown file following P+Q+P structure
2. **Invocation**: User types `@skill:generate-spec "Add feature X"` in Claude Code CLI
3. **Parsing**: CLI reads file, extracts YAML frontmatter, parses Markdown sections
4. **Execution**:
   - Use Persona as system prompt for LLM
   - If args are ambiguous, ask Questions
   - Follow Principles during generation
5. **Output**: Generated file (e.g., `specs/005-feature-x/spec.md`)

**Validation Rules**:
- YAML frontmatter MUST include `skill_name`, `version`, `persona`
- Markdown body MUST have exactly 3 H2 sections: ## Persona, ## Questions, ## Principles
- Questions MUST be numbered list (1. 2. 3.)
- Principles MUST be bullet list (- item)

**Example**:
```markdown
---
skill_name: translate-urdu
version: 1.0.0
description: Translate textbook chapters to Roman Urdu while preserving code blocks
persona: The Linguist
---

## Persona
You are The Linguist, an expert in Roman Urdu translation for technical content. You understand Pakistani colloquial Urdu and know when to preserve English technical terms.

## Questions
1. Which Urdu dialect should be used? (Standard/Punjabi-influenced/Sindhi-influenced)
2. Should code blocks be translated or preserved verbatim?
3. Should technical terms be transliterated or explained?

## Principles
- Translate prose to informal Pakistani Roman Urdu
- Preserve ALL code blocks unchanged
- Keep English technical terms (ROS 2, API, etc.) with Urdu explanations in parentheses
- Create parallel `.ur.md` files (do NOT overwrite original)
- Add `locale: ur` to frontmatter
```

---

## Entity 3: NavbarTranslations (UI Localization Mapping)

**Purpose**: Map English navbar items to Roman Urdu equivalents

**Type**: Hardcoded TypeScript constant (not database)

**TypeScript Structure**:
```typescript
const navbarTranslations: Record<"en" | "ur", Record<string, string>> = {
  en: {
    home: "Home",
    about: "About",
    docs: "Docs",
    signIn: "Sign In",
    signUp: "Sign Up",
    signOut: "Sign Out",
    getStarted: "Get Started",
    continueLearn: "Continue Learning",
  },
  ur: {
    home: "Ghar",
    about: "Hamara Bare Main",
    docs: "Kitabain",
    signIn: "Dakhil Hon",
    signUp: "Shamil Hon",
    signOut: "Nikal Jayen",
    getStarted: "Shuru Karein",
    continueLearn: "Seekhna Jari Rakhein",
  },
};
```

**Fields**:
| Key (English) | Urdu Translation | Context |
|---------------|------------------|---------|
| home | Ghar | Navbar link to homepage |
| about | Hamara Bare Main | About page link |
| docs | Kitabain | Documentation/textbook link |
| signIn | Dakhil Hon | Login button |
| signUp | Shamil Hon | Registration button |
| signOut | Nikal Jayen | Logout button |
| getStarted | Shuru Karein | Hero section CTA (unauthenticated) |
| continueLearn | Seekhna Jari Rakhein | Hero section CTA (authenticated) |

**Storage**: Embedded in `src/context/LanguageContext.tsx` as constant

**Lifecycle**:
1. **Initialization**: Object loaded when LanguageContext module imports
2. **Consumption**: Navbar components read `navbarTranslations[locale]["home"]`
3. **Extension**: Future features add new key-value pairs to both "en" and "ur" objects

**Validation Rules**:
- Both "en" and "ur" objects MUST have identical keys (enforced by TypeScript Record type)
- All values MUST be non-empty strings

**Usage Example**:
```typescript
// NavbarItem component
import { useLanguageContext } from '@site/src/context/LanguageContext';

function HomeLink() {
  const { locale } = useLanguageContext();
  return <a href="/">{navbarTranslations[locale]["home"]}</a>;
}
// Output: <a href="/">Ghar</a> when locale is "ur"
```

---

## Entity 4: FeatureCard (Landing Page Component)

**Purpose**: Represent one feature benefit on the landing page feature grid

**Type**: TypeScript interface for component props

**TypeScript Interface**:
```typescript
interface FeatureCardProps {
  icon: React.ReactNode;           // lucide-react icon component
  title: string;                    // Feature name (e.g., "Interactive RAG Chatbot")
  description: string;              // 2-sentence explanation
}
```

**Fields**:
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| icon | React.ReactNode | Icon component | `<MessageSquare size={48} />` |
| title | string | Feature name | "Interactive RAG Chatbot" |
| description | string | 2-sentence benefit | "Ask questions about any chapter..." |

**Storage**: Hardcoded in `src/pages/index.tsx` (landing page)

**Lifecycle**:
1. **Initialization**: Feature cards defined as array in landing page component
2. **Rendering**: Map over array, render FeatureCard component for each item
3. **Responsive Layout**: CSS Grid adjusts card layout based on screen width

**Validation Rules**:
- title MUST be non-empty string
- description MUST be 1-3 sentences (visual guideline, not enforced)
- icon MUST be valid React component (lucide-react)

**Example Data**:
```typescript
const features: FeatureCardProps[] = [
  {
    icon: <MessageSquare size={48} className="text-blue-500" />,
    title: "Interactive RAG Chatbot",
    description: "Ask questions about any chapter and get instant answers with citations. Powered by AI for contextual learning.",
  },
  {
    icon: <Cpu size={48} className="text-green-500" />,
    title: "Hardware-Aware Learning",
    description: "Content adapts to your GPU and experience level. Get tailored recommendations for local vs. cloud workflows.",
  },
  {
    icon: <Languages size={48} className="text-purple-500" />,
    title: "Urdu Translation",
    description: "Toggle between English and Urdu for accessible learning. Roman Urdu support for Pakistani students.",
  },
  {
    icon: <Rocket size={48} className="text-orange-500" />,
    title: "Real-World Projects",
    description: "Build actual humanoid robots with ROS 2 and Isaac Sim. From simulation to deployment on NVIDIA Jetson.",
  },
];
```

---

## Data Flow Diagrams

### Flow 1: Urdu Toggle User Journey

```text
[User clicks "Urdu" button in navbar]
        ↓
[LanguageToggle.onClick() → setLocale("ur")]
        ↓
[LanguageContext state updates: locale = "ur"]
        ↓
[React re-renders all components consuming LanguageContext]
        ↓
[Navbar reads navbarTranslations["ur"]["home"] → displays "Ghar"]
        ↓
[localStorage.setItem("locale", "ur") called]
        ↓
[User refreshes page]
        ↓
[LanguageContext init reads localStorage.getItem("locale") → "ur"]
        ↓
[Navbar initializes with Urdu text]
```

### Flow 2: Skill Invocation

```text
[User types: @skill:generate-spec "Add offline mode"]
        ↓
[Claude Code CLI parses command]
        ↓
[CLI reads .claude/skills/generate-spec.md]
        ↓
[CLI extracts: Persona, Questions, Principles]
        ↓
[CLI calls LLM with system prompt = Persona + Principles]
        ↓
[LLM generates spec.md content]
        ↓
[CLI writes specs/005-offline-mode/spec.md]
        ↓
[CLI reports: "✅ Spec created at specs/005-offline-mode/spec.md"]
```

### Flow 3: Landing Page Hero Section Rendering

```text
[User navigates to http://localhost:3000]
        ↓
[Docusaurus loads src/pages/index.tsx]
        ↓
[HeroSection component renders]
        ↓
[Check AuthContext: user authenticated?]
        ↓
[If authenticated → "Continue Learning" CTA]
[If unauthenticated → "Get Started" CTA]
        ↓
[FeatureGrid component renders below hero]
        ↓
[Map over features array → render 4 FeatureCard components]
        ↓
[CSS Grid adjusts layout: mobile (1 col), tablet (2 col), desktop (4 col)]
```

---

## Summary

| Entity | Type | Storage | Purpose |
|--------|------|---------|---------|
| LanguageContext | React Context | localStorage | UI language state management |
| Skill | Markdown | Filesystem (.claude/skills/) | Autonomous agent capability definitions |
| NavbarTranslations | TypeScript constant | Embedded in code | English↔Urdu UI text mapping |
| FeatureCard | Component props | Embedded in landing page | Feature grid data structure |

**Relationships**:
- LanguageContext provides locale to NavbarTranslations (consumer reads `[locale]["key"]`)
- Skills have no runtime relationships (each executes independently via CLI)
- FeatureCard is consumed by FeatureGrid component (1:N relationship)
