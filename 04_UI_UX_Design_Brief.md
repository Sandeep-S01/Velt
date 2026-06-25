# UI & UX Design Brief
## SmartSearch API — Semantic Search for E-commerce

**Version:** 1.0  
**Date:** 2026-06-22  
**Status:** Draft  
**Author:** Design Team

---

## 1. Design Philosophy

### Core Principle: "Invisible Intelligence"
The AI should feel magical but never intrusive. Users shouldn't think "this is AI" — they should think "this search just works."

### Three Design Pillars
1. **Clarity over Cleverness** — Every element has one clear purpose
2. **Speed over Decoration** — Load in <100ms, no heavy animations
3. **Trust through Transparency** — Show WHY results matched (when helpful)

---

## 2. Color Palette

### Primary Colors
| Color Name | Hex | Usage | Psychology |
|------------|-----|-------|------------|
| **Deep Indigo** | `#4F46E5` | Primary buttons, active states, links, brand identity | Trust, intelligence, tech-forward |
| **Indigo Light** | `#818CF8` | Hover states, secondary accents, icons | Approachable, friendly |
| **Indigo Dark** | `#3730A3` | Pressed states, deep backgrounds | Authority, premium |

### Neutral Colors
| Color Name | Hex | Usage |
|------------|-----|-------|
| **Pure White** | `#FFFFFF` | Primary backgrounds, cards |
| **Off-White** | `#F9FAFB` | Page backgrounds, subtle separation |
| **Light Gray** | `#F3F4F6` | Input backgrounds, hover states |
| **Medium Gray** | `#9CA3AF` | Placeholder text, disabled states, borders |
| **Dark Gray** | `#374151` | Secondary text, labels |
| **Charcoal** | `#111827` | Primary text, headings |

### Semantic Colors
| Color Name | Hex | Usage |
|------------|-----|-------|
| **Success Green** | `#10B981` | Success states, positive metrics, "live" indicators |
| **Warning Amber** | `#F59E0B` | Warnings, approaching limits, attention needed |
| **Error Red** | `#EF4444` | Errors, failures, critical alerts |
| **Info Blue** | `#3B82F6` | Informational tips, help text, neutral alerts |

### Gradient Accents
```
Primary Gradient: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)
Usage: Hero sections, feature highlights, premium badges

Success Gradient: linear-gradient(135deg, #10B981 0%, #34D399 100%)
Usage: Conversion metrics, positive trends, achievement badges
```

---

## 3. Typography

### Font Family
| Role | Font | Weight | Fallback |
|------|------|--------|----------|
| **Headings** | Inter | 600, 700 | system-ui, -apple-system, sans-serif |
| **Body** | Inter | 400, 500 | system-ui, -apple-system, sans-serif |
| **Monospace** | JetBrains Mono | 400, 500 | Menlo, Monaco, Consolas, monospace |

### Type Scale
| Level | Size | Weight | Line Height | Letter Spacing | Usage |
|-------|------|--------|-------------|----------------|-------|
| **H1** | 36px | 700 | 1.2 | -0.02em | Page titles, hero headlines |
| **H2** | 30px | 600 | 1.3 | -0.01em | Section headers |
| **H3** | 24px | 600 | 1.4 | 0 | Card titles, modal headers |
| **H4** | 20px | 600 | 1.4 | 0 | Subsection headers |
| **H5** | 18px | 600 | 1.5 | 0 | Feature titles |
| **Body Large** | 18px | 400 | 1.6 | 0 | Hero descriptions, important text |
| **Body** | 16px | 400 | 1.6 | 0 | Primary body text |
| **Body Small** | 14px | 400 | 1.5 | 0 | Secondary text, descriptions |
| **Caption** | 12px | 500 | 1.4 | 0.01em | Labels, timestamps, metadata |
| **Overline** | 12px | 600 | 1.4 | 0.08em | Uppercase labels, badges |

---

## 4. Spacing System

### Base Unit: 4px
| Token | Value | Usage |
|-------|-------|-------|
| **xs** | 4px | Tight gaps, icon padding |
| **sm** | 8px | Inline spacing, small gaps |
| **md** | 16px | Standard padding, card gaps |
| **lg** | 24px | Section padding, modal gaps |
| **xl** | 32px | Large section spacing |
| **2xl** | 48px | Page sections, hero spacing |
| **3xl** | 64px | Major section breaks |
| **4xl** | 96px | Page-level spacing |

### Border Radius
| Token | Value | Usage |
|-------|-------|-------|
| **none** | 0px | Tables, data grids |
| **sm** | 4px | Small buttons, tags, badges |
| **md** | 8px | Inputs, cards, modals |
| **lg** | 12px | Large cards, feature blocks |
| **xl** | 16px | Hero sections, containers |
| **full** | 9999px | Pills, avatars, circular elements |

---

## 5. Component Specifications

### 5.1 Search Bar (Primary Component)

```
┌────────────────────────────────────────────────────────────────┐
│  SEARCH BAR — Default State                                    │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  🔍  Search for products...                        [⌘K] │  │
│  │  Border: 1px solid #E5E7EB                             │  │
│  │  Background: #FFFFFF                                     │  │
│  │  Height: 48px                                            │  │
│  │  Border Radius: 12px (lg)                              │  │
│  │  Padding: 0 16px                                       │  │
│  │  Font: Body (16px, 400)                                │  │
│  │  Shadow: 0 1px 3px rgba(0,0,0,0.08)                    │  │
│  │  Focus: Border → #4F46E5, Shadow → 0 0 0 3px rgba(79,70,229,0.15)│  │
│  │  Placeholder: #9CA3AF                                    │  │
│  │  Icon: #9CA3AF (left), #D1D5DB (right shortcut)        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  SEARCH BAR — Active State                                     │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  🔍  comfortable chair for long hours at desk...     ✕   │  │
│  │  Border: 2px solid #4F46E5                               │  │
│  │  Background: #FFFFFF                                     │  │
│  │  Shadow: 0 0 0 3px rgba(79,70,229,0.15), 0 4px 12px rgba(0,0,0,0.1)│  │
│  │  Clear button: #9CA3AF → hover #EF4444                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  SEARCH BAR — Loading State                                    │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  🔍  comfortable chair for long hours at desk...   ⏳   │  │
│  │  Spinner: 16px, #4F46E5, 1s linear infinite rotation   │  │
│  │  Input: opacity 0.7, cursor: not-allowed               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### 5.2 Autocomplete Dropdown

```
┌────────────────────────────────────────────────────────────────┐
│  AUTOCOMPLETE DROPDOWN                                         │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  🔍  comfortable chair for long hours at desk            │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  💡 Suggestions (Semantic — not just prefix match)   │  │  │
│  │  │                                                      │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  comfortable office chair for back pain      │  │  │  │
│  │  │  │  Font: 14px, #374151  │  Match: #4F46E5     │  │  │  │
│  │  │  │  Hover: bg #F3F4F6, cursor pointer           │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  ergonomic desk chair lumbar support         │  │  │  │
│  │  │  │  Font: 14px, #374151  │  Match: #4F46E5     │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  chair for long hours at computer            │  │  │  │
│  │  │  │  Font: 14px, #374151  │  Match: #4F46E5     │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  │                                                      │  │  │
│  │  │  ─────────────────────────────────────────────────   │  │  │
│  │  │  📊 Popular Searches                                 │  │  │
│  │  │  • ergonomic chair (342 searches this week)        │  │  │
│  │  │  • standing desk (287 searches)                    │  │  │
│  │  │  • foot rest (156 searches)                        │  │  │
│  │  │  Font: 12px, #9CA3AF                                │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  Border: 1px solid #E5E7EB                               │  │
│  │  Shadow: 0 10px 40px rgba(0,0,0,0.12)                   │  │
│  │  Border Radius: 12px (lg)                                │  │
│  │  Background: #FFFFFF                                     │  │
│  │  Max Height: 400px, Overflow: auto                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### 5.3 Search Result Card

```
┌────────────────────────────────────────────────────────────────┐
│  SEARCH RESULT CARD — Product                                  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ┌────────────┐                                          │  │
│  │  │            │  Title: 18px, 600, #111827                │  │
│  │  │  🖼️ IMAGE   │  "Ergonomic Office Chair Pro"            │  │
│  │  │  120x120px  │                                          │  │
│  │  │  Border:    │  Rating: ⭐ 4.8 (14px, #F59E0B)         │  │
│  │  │  1px solid  │  "1,247 reviews" (12px, #9CA3AF)         │  │
│  │  │  #E5E7EB    │                                          │  │
│  │  │  Radius: 8px│  Price: $199.99 (20px, 700, #111827)     │  │
│  │  │             │  Compare: $249.99 (14px, #9CA3AF, strikethru)│  │
│  │  │             │                                          │  │
│  │  │             │  Description: 14px, 400, #6B7280            │  │
│  │  │             │  "Lumbar support and breathable mesh back   │  │
│  │  │             │   perfect for long work sessions..."        │  │
│  │  │             │  Max 2 lines, ellipsis                      │  │
│  │  │             │                                          │  │
│  │  │             │  Match Badge:                              │  │
│  │  │             │  ┌────────────────────────────────────┐  │  │
│  │  │             │  │  💡 Matched: "lumbar", "long hours"│  │  │
│  │  │             │  │  12px, 500, #4F46E5, bg rgba(79,70,229,0.08)│  │  │
│  │  │             │  │  Border: 1px solid rgba(79,70,229,0.2)    │  │  │
│  │  │             │  │  Border Radius: 4px (sm)                │  │  │
│  │  │             │  └────────────────────────────────────┘  │  │
│  │  │             │                                          │  │
│  │  │             │  [🛒 Add to Cart]  [❤️ Save]  [🔗 Share]  │  │
│  │  │             │  Primary Button: 14px, 600, #FFFFFF      │  │
│  │  │             │  Background: #4F46E5, Radius: 8px          │  │
│  │  │             │  Hover: #3730A3, transition 150ms ease    │  │
│  │  │             │  Secondary: ghost, border 1px #E5E7EB     │  │
│  │  └────────────┘                                          │  │
│  │  Padding: 16px, Gap: 16px                                │  │
│  │  Border Bottom: 1px solid #F3F4F6                        │  │
│  │  Hover: bg #F9FAFB, transition 150ms ease                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### 5.4 Dashboard Cards

```
┌────────────────────────────────────────────────────────────────┐
│  METRIC CARD — Dashboard                                       │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  ICON CONTAINER                                      │  │  │
│  │  │  ┌────┐                                             │  │  │
│  │  │  │ 🔍 │  48x48px, bg rgba(79,70,229,0.1)            │  │  │
│  │  │  └────┘  Border Radius: 12px (lg)                   │  │  │
│  │  │  Icon Color: #4F46E5                                │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                                │  │
│  │  Label: "Total Searches" (12px, 500, #9CA3AF, uppercase)      │  │
│  │                                                                │  │
│  │  Value: "1,247" (30px, 700, #111827)                          │  │
│  │                                                                │  │
│  │  Trend: "↑ 23% vs last week" (14px, 500)                       │  │
│  │  Positive: #10B981  │  Negative: #EF4444  │  Neutral: #9CA3AF  │  │
│  │  Arrow: ▲ or ▼                                                 │  │
│  │                                                                │  │
│  │  Sparkline: 60px wide, 20px tall, #4F46E5 stroke              │  │
│  │  2px stroke, no fill, 5 data points                            │  │
│  │                                                                │  │
│  │  Padding: 20px, Border Radius: 12px (lg)                       │  │
│  │  Background: #FFFFFF, Border: 1px solid #E5E7EB               │  │
│  │  Shadow: 0 1px 3px rgba(0,0,0,0.04)                          │  │
│  │  Hover: Shadow 0 4px 12px rgba(0,0,0,0.08), transition 200ms  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### 5.5 Buttons

```
┌────────────────────────────────────────────────────────────────┐
│  BUTTON VARIANTS                                               │
│                                                                │
│  PRIMARY BUTTON                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  [Get Started]                                             │  │
│  │  Background: #4F46E5                                       │  │
│  │  Text: #FFFFFF, 14px, 600, Inter                           │  │
│  │  Padding: 10px 20px                                        │  │
│  │  Border Radius: 8px (md)                                   │  │
│  │  Shadow: 0 1px 2px rgba(79,70,229,0.3)                     │  │
│  │  Hover: Background #3730A3, translateY(-1px)               │  │
│  │  Active: Background #312E81, translateY(0)                 │  │
│  │  Disabled: Background #C7D2FE, Text #818CF8, cursor: not-allowed│  │
│  │  Transition: all 150ms ease                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  SECONDARY BUTTON                                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  [Learn More]                                              │  │
│  │  Background: #FFFFFF                                       │  │
│  │  Border: 1px solid #E5E7EB                               │  │
│  │  Text: #374151, 14px, 600                                 │  │
│  │  Hover: Background #F9FAFB, Border #D1D5DB                 │  │
│  │  Active: Background #F3F4F6                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  GHOST BUTTON                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  [Cancel]                                                  │  │
│  │  Background: transparent                                   │  │
│  │  Text: #6B7280, 14px, 500                                  │  │
│  │  Hover: Background #F3F4F6, Text #374151                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  DANGER BUTTON                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  [Delete Store]                                            │  │
│  │  Background: #FFFFFF                                       │  │
│  │  Border: 1px solid #EF4444                                 │  │
│  │  Text: #EF4444, 14px, 600                                  │  │
│  │  Hover: Background #FEF2F2, Border #DC2626                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### 5.6 Form Inputs

```
┌────────────────────────────────────────────────────────────────┐
│  FORM INPUT — Default                                          │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Store Name                                                │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │ Sarah's Jewelry                                      │  │  │
│  │  │ Background: #FFFFFF                                  │  │  │
│  │  │ Border: 1px solid #E5E7EB                            │  │  │
│  │  │ Border Radius: 8px (md)                              │  │  │
│  │  │ Padding: 10px 14px                                   │  │  │
│  │  │ Font: 16px, 400, Inter                               │  │  │
│  │  │ Color: #111827                                       │  │  │
│  │  │ Placeholder: #9CA3AF                                 │  │  │
│  │  │ Focus: Border #4F46E5, Shadow 0 0 0 3px rgba(79,70,229,0.15)│  │  │
│  │  │ Error: Border #EF4444, Shadow 0 0 0 3px rgba(239,68,68,0.15)│  │  │
│  │  │ Error Message: 12px, #EF4444, margin-top 4px         │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │  Label: 14px, 500, #374151, margin-bottom 6px             │  │
│  │  Helper: 12px, #9CA3AF, margin-top 4px                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### 5.7 Toast Notifications

```
┌────────────────────────────────────────────────────────────────┐
│  TOAST NOTIFICATIONS                                           │
│                                                                │
│  SUCCESS                                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ✅ Store connected successfully!                          │  │
│  │  Background: #FFFFFF, Border-left: 4px solid #10B981     │  │
│  │  Shadow: 0 4px 12px rgba(0,0,0,0.08)                     │  │
│  │  Border Radius: 8px, Padding: 12px 16px                  │  │
│  │  Position: Top-right, 16px from edges                    │  │
│  │  Animation: Slide in from right, 300ms ease-out          │  │
│  │  Auto-dismiss: 5 seconds, fade out 300ms                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ERROR                                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ❌ Failed to connect store. Please check your URL.      │  │
│  │  Background: #FFFFFF, Border-left: 4px solid #EF4444     │  │
│  │  [Retry] [Dismiss]                                       │  │
│  │  Action buttons: 14px, 500, #4F46E5                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  INFO                                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ℹ️ Indexing 487 products. This may take 2 minutes.      │  │
│  │  Background: #FFFFFF, Border-left: 4px solid #3B82F6     │  │
│  │  Progress bar: 4px height, #4F46E5 fill, animated        │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## 6. Layout Patterns

### 6.1 Dashboard Layout
```
┌────────────────────────────────────────────────────────────────┐
│  [Logo]  Dashboard  Stores  Analytics  Docs  [🔔] [👤 Profile ▾]│
│  Height: 64px, Background: #FFFFFF, Border-bottom: 1px #E5E7EB │
│  Shadow: 0 1px 3px rgba(0,0,0,0.04)                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Sarah's Jewelry                              [⚙️ Settings]│  │
│  │  Breadcrumb: Home / Stores / Sarah's Jewelry             │  │
│  │  H1: 30px, 600, #111827                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────┐│
│  │ Metric Card  │ │ Metric Card  │ │ Metric Card  │ │ Metric ││
│  │  Searches    │ │ Conversion   │ │ No-Result    │ │ Revenue││
│  │  1,247       │ │ 12.4%        │ │ 8.2%         │ │ $3,420 ││
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────┘│
│  Grid: 4 columns, gap 24px, responsive: 2 cols tablet, 1 mobile│
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ┌────────────────────┐  ┌────────────────────────────┐  │  │
│  │  │  TOP QUERIES       │  │  SEARCH TRENDS            │  │  │
│  │  │  List view         │  │  Line chart               │  │  │
│  │  │  Table: 100% width │  │  Height: 300px            │  │  │
│  │  │  Row height: 48px  │  │  Stroke: #4F46E5, 2px     │  │  │
│  │  │  Hover: #F9FAFB    │  │  Grid: #F3F4F6, dashed    │  │  │
│  │  └────────────────────┘  └────────────────────────────┘  │  │
│  │  Grid: 2 columns, gap 24px                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  NO-RESULTS INSIGHTS                                      │  │
│  │  Alert banner: bg #FEF3C7, border #F59E0B, rounded 8px   │  │
│  │  Icon: ⚠️ #F59E0B, Text: #92400E                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  Footer: 48px height, #F9FAFB, text 12px #9CA3AF, centered   │
│  "© 2026 SmartSearch API — [Privacy] [Terms] [Support]"       │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 6.2 Widget Layout (Embedded on Merchant Store)
```
┌────────────────────────────────────────────────────────────────┐
│  WIDGET — Overlay Mode (Default)                               │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  [Search... 🔍]  ← Trigger button, fixed position        │  │
│  │  Bottom-right: 24px from edges, 48px diameter             │  │
│  │  Background: #4F46E5, Icon: #FFFFFF, 20px               │  │
│  │  Shadow: 0 4px 12px rgba(79,70,229,0.3)                 │  │
│  │  Hover: scale(1.05), transition 200ms ease               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  WIDGET — Expanded                                         │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  🔍 [Search for anything...              ]  [✕]   │  │  │
│  │  │  Height: 56px, Radius: 16px (xl), Shadow: 0 4px 20px│  │  │
│  │  │  Background: #FFFFFF, Border: 1px #E5E7EB           │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                                │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  RESULTS CONTAINER                                   │  │  │
│  │  │  Max Height: 500px, Overflow: auto                  │  │  │
│  │  │  Background: #FFFFFF, Radius: 16px                  │  │  │
│  │  │  Shadow: 0 10px 40px rgba(0,0,0,0.12)               │  │  │
│  │  │  Padding: 16px                                       │  │  │
│  │  │  Scrollbar: 6px width, #E5E7EB track, #9CA3AF thumb │  │  │
│  │  │                                                      │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  🖼️  │ Title + Price + Description        │  │  │  │
│  │  │  │      │ Match badge + CTA buttons          │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  │  ... (more results) ...                            │  │  │
│  │  │                                                      │  │  │
│  │  │  [Load More Results]  [Powered by SmartSearch]       │  │  │
│  │  │  Footer: 12px, #9CA3AF, center-aligned            │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  Width: 100% (mobile), 480px (tablet), 560px (desktop) │  │
│  │  Position: Fixed, bottom-right, 24px margin             │  │
│  │  Animation: Slide up + fade in, 300ms ease-out           │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## 7. Animation & Motion Guidelines

### 7.1 Principles
- **Purposeful:** Every animation guides attention or confirms action
- **Fast:** Most transitions < 300ms, micro-interactions < 150ms
- **Subtle:** Never distract from content or task completion
- **Respectful:** Honor `prefers-reduced-motion`

### 7.2 Standard Animations
| Animation | Duration | Easing | Usage |
|-----------|----------|--------|-------|
| **Fade In** | 200ms | ease-out | Modal appearance, toast |
| **Slide Up** | 300ms | cubic-bezier(0.16, 1, 0.3, 1) | Dropdown, widget expand |
| **Scale Press** | 100ms | ease-in-out | Button active state |
| **Skeleton Pulse** | 1.5s | ease-in-out infinite | Loading placeholders |
| **Spinner Rotate** | 1s | linear infinite | Loading states |
| **Number Count** | 800ms | ease-out | Metric value changes |
| **Progress Fill** | 300ms | ease-out | Progress bars |

### 7.3 Loading States
```
┌────────────────────────────────────────────────────────────────┐
│  SKELETON LOADING — Search Results                             │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ┌────────┐                                              │  │
│  │  │ ██████ │  120x120px, bg #F3F4F6, radius 8px          │  │
│  │  │ ██████ │  Pulse animation: opacity 0.5 → 1 → 0.5      │  │
│  │  │ ██████ │  Duration: 1.5s, infinite                    │  │
│  │  └────────┘                                              │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │ ████████████████████████████  (Title, 18px)        │    │  │
│  │  │ ██████████████████            (Subtitle, 14px)     │    │  │
│  │  │ ████████████████              (Description, 14px)  │    │  │
│  │  │ All: bg #F3F4F6, radius 4px, height matches text │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │  Repeat 3x for multiple skeleton items                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## 8. Responsive Breakpoints

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| **Mobile** | < 640px | Single column, stacked cards, hamburger menu, full-screen widget |
| **Tablet** | 640px - 1024px | 2-column grid, sidebar collapses, widget 480px wide |
| **Desktop** | 1024px - 1280px | 3-4 column grid, full sidebar, widget 560px wide |
| **Wide** | > 1280px | Max-width container 1280px, centered, generous whitespace |

### Mobile-Specific Adaptations
- Search bar: Full width, 56px height (thumb-friendly)
- Cards: Full width, stacked vertically
- Filters: Horizontal scroll or bottom sheet
- Widget: Full-screen overlay, bottom sheet style
- Touch targets: Minimum 44x44px

---

## 9. Accessibility Standards

### WCAG 2.1 AA Compliance
| Requirement | Implementation |
|-------------|----------------|
| **Color Contrast** | All text ≥ 4.5:1 ratio, large text ≥ 3:1 |
| **Focus Indicators** | 2px solid #4F46E5 outline, offset 2px |
| **Keyboard Navigation** | Tab order logical, Enter/Space activation |
| **Screen Readers** | Semantic HTML, ARIA labels, alt text for images |
| **Reduced Motion** | `prefers-reduced-motion: reduce` disables animations |
| **Text Scaling** | Layout supports 200% zoom without breakage |

### ARIA Patterns
```html
<!-- Search Bar -->
<div role="search" aria-label="Product search">
  <input 
    type="search" 
    aria-autocomplete="list" 
    aria-controls="search-suggestions"
    aria-expanded="false"
    placeholder="Search for products..."
  />
  <ul id="search-suggestions" role="listbox" aria-label="Search suggestions">
    <li role="option" aria-selected="false">Suggestion 1</li>
  </ul>
</div>

<!-- Result Card -->
<article aria-label="Product: Ergonomic Office Chair Pro">
  <img alt="Ergonomic office chair with lumbar support, black mesh back" />
  <h3>Ergonomic Office Chair Pro</h3>
  <p aria-label="Price: $199.99">$199.99</p>
  <button aria-label="Add Ergonomic Office Chair Pro to cart">
    Add to Cart
  </button>
</article>
```

---

## 10. Iconography

### Icon Style
- **Style:** Outlined (2px stroke), rounded corners, consistent 24x24px viewbox
- **Library:** Lucide React (open-source, consistent, lightweight)
- **Color:** Inherit from parent text color, or #4F46E5 for emphasis
- **Size:** 16px (inline), 20px (buttons), 24px (navigation), 48px (feature icons)

### Key Icons
| Icon | Name | Usage |
|------|------|-------|
| 🔍 | `Search` | Search bar, search action |
| ✕ | `X` | Close, clear, dismiss |
| ⏳ | `Loader` | Loading spinner |
| ✅ | `Check` | Success, completion |
| ⚠️ | `AlertTriangle` | Warning, attention |
| ❌ | `XCircle` | Error, failure |
| 📊 | `BarChart3` | Analytics, metrics |
| ⚙️ | `Settings` | Configuration, settings |
| 🛒 | `ShoppingCart` | Add to cart, purchase |
| ❤️ | `Heart` | Save, favorite, wishlist |
| 🔗 | `Link` | Share, external link |
| 📋 | `Copy` | Copy to clipboard |
| 📁 | `Upload` | File upload |
| 📖 | `BookOpen` | Documentation |
| 💬 | `MessageCircle` | Support, chat |
| 🔔 | `Bell` | Notifications |
| 👤 | `User` | Profile, account |
| ▾ | `ChevronDown` | Dropdown, expand |
| ▲ | `ChevronUp` | Collapse, scroll up |
| → | `ArrowRight` | Navigation, next |
| ← | `ArrowLeft` | Back, previous |

---

## 11. Empty States & Illustrations

### Empty State — No Search Results
```
┌────────────────────────────────────────────────────────────────┐
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  🖼️ Illustration: 160x160px                        │  │  │
│  │  │  Style: Flat, minimal, single accent color (#4F46E5)│  │  │
│  │  │  Scene: Person looking at empty box with magnifying glass│  │  │
│  │  │  Stroke: 2px, rounded corners, no fill             │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  Title: "No results found" (H3, 24px, 600, #111827)      │  │
│  │  Description: "Try different keywords or browse categories"│  │
│  │  (Body, 16px, 400, #6B7280, max-width 400px, centered) │  │
│  │                                                          │  │
│  │  [🔍 Browse All Products]  [💬 Contact Support]          │  │
│  │  Primary + Secondary buttons, centered                   │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### Empty State — Dashboard (First Visit)
```
┌────────────────────────────────────────────────────────────────┐
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  🖼️ Illustration: Store + Search icon + Sparkles          │  │
│  │  Title: "Welcome to SmartSearch!"                        │  │
│  │  Description: "Connect your store to start seeing search analytics"│  │
│  │  [🔗 Connect Store]  [📖 Read Setup Guide]               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## 12. Dark Mode (Future Phase)

### Color Inversion Strategy
| Light Mode | Dark Mode |
|------------|-----------|
| `#FFFFFF` background | `#0F172A` background |
| `#F9FAFB` off-white | `#1E293B` card background |
| `#111827` text | `#F8FAFC` text |
| `#374151` secondary text | `#94A3B8` secondary text |
| `#E5E7EB` borders | `#334155` borders |
| `#4F46E5` primary | `#818CF8` primary (lighter for contrast) |
| Shadows | Remove or reduce (dark mode needs less depth) |

---

*End of UI & UX Design Brief*
