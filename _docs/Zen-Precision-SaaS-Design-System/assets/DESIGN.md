---
name: Zen Precision SaaS
colors:
  surface: '#faf9f5'
  surface-dim: '#dbdad6'
  surface-bright: '#faf9f5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f4f0'
  surface-container: '#efeeea'
  surface-container-high: '#e9e8e4'
  surface-container-highest: '#e3e2df'
  on-surface: '#1b1c1a'
  on-surface-variant: '#45474a'
  inverse-surface: '#2f312e'
  inverse-on-surface: '#f2f1ed'
  outline: '#76777b'
  outline-variant: '#c6c6ca'
  surface-tint: '#5e5e60'
  primary: '#07080a'
  on-primary: '#ffffff'
  primary-container: '#1f2022'
  on-primary-container: '#87878a'
  inverse-primary: '#c7c6c8'
  secondary: '#5b5e64'
  on-secondary: '#ffffff'
  secondary-container: '#e0e2e9'
  on-secondary-container: '#61646a'
  tertiary: '#100600'
  on-tertiary: '#ffffff'
  tertiary-container: '#2c1d0c'
  on-tertiary-container: '#9b836c'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e3e2e4'
  primary-fixed-dim: '#c7c6c8'
  on-primary-fixed: '#1b1c1e'
  on-primary-fixed-variant: '#464749'
  secondary-fixed: '#e0e2e9'
  secondary-fixed-dim: '#c4c6cd'
  on-secondary-fixed: '#181c21'
  on-secondary-fixed-variant: '#44474c'
  tertiary-fixed: '#fadec2'
  tertiary-fixed-dim: '#ddc2a7'
  on-tertiary-fixed: '#271908'
  on-tertiary-fixed-variant: '#56432f'
  background: '#faf9f5'
  on-background: '#1b1c1a'
  surface-variant: '#e3e2df'
typography:
  display:
    fontFamily: Inter
    fontSize: 1.75rem
    fontWeight: '500'
    lineHeight: 2.25rem
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Inter
    fontSize: 1.375rem
    fontWeight: '500'
    lineHeight: 1.875rem
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 1.125rem
    fontWeight: '500'
    lineHeight: 1.625rem
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Inter
    fontSize: 0.9375rem
    fontWeight: '600'
    lineHeight: 1.375rem
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 0.9375rem
    fontWeight: '400'
    lineHeight: 1.5rem
    letterSpacing: -0.005em
  body-md:
    fontFamily: Inter
    fontSize: 0.8125rem
    fontWeight: '400'
    lineHeight: 1.25rem
    letterSpacing: -0.002em
  body-sm:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: '400'
    lineHeight: 1.125rem
    letterSpacing: 0em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 0.75rem
    fontWeight: '500'
    lineHeight: 1rem
    letterSpacing: -0.01em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 0.6875rem
    fontWeight: '400'
    lineHeight: 0.875rem
    letterSpacing: 0.02em
  code:
    fontFamily: JetBrains Mono
    fontSize: 0.75rem
    fontWeight: '400'
    lineHeight: 1.2rem
    letterSpacing: '0'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 0.75rem
  gutter-desktop: 1rem
  margin: 1rem
  margin-desktop: 1.5rem
  space-xs: 0.25rem
  space-sm: 0.375rem
  space-md: 0.625rem
  space-lg: 1rem
  space-xl: 1.5rem
---

## Brand & Style

This design system synthesizes traditional Japanese wabi-sabi reduction with the hyper-dense, keyboard-driven utility of modern high-performance engineering suites (Linear, Raycast). The brand personality is disciplined, quiet, and profoundly intentional. It rejects decorative noise, loud saturated accents, and heavy containerization in favor of spatial clarity, restrained line-work, and natural paper-like warmth.

The interface is engineered for knowledge workers, developers, and product orchestrators who spend 8+ hours a day inside dense data environments. The emotional response is one of visual deceleration and structural mastery: serene, unhurried, yet uncompromisingly rapid and exact.

Visually, the style merges **Warm Minimalism** with **Structural Monasticism**:
- Organic neutral surfaces referencing washi (rice paper), raw unbleached linen, and pale river stones.
- Deep calligraphic sumi ink contrasts for effortless legibility.
- Hairline structural framing, flat surfaces, and subtle, dry, low-diffusion contact edges rather than artificial atmospheric glows.

## Colors

The palette avoids stark sterile blue-whites, opting for an unbleached organic spectrum balanced against ink-dense charcoals.

### Surface Tones
- **Washi Base (Canvas / Ground):** `#FAF9F5` — Primary application background; warm bone with low fatigue.
- **Sand (Sub-surface / Neutral Light):** `#F3F2EC` — Sidebars, command panels, secondary group wells.
- **Matte Pure (Surface Container / Elevate):** `#FFFFFF` — Focused cards, active rows, dialog sheets.

### Ink Spectrum (Content & Typography)
- **Sumi Dark (Primary Text):** `#1F2022` — Intense calligraphic charcoal for high priority headers and data points.
- **Ground Ink (Secondary Text):** `#4B4D52` — Body text, interface labels, interactive inactive states.
- **Dilute Charcoal (Muted Text / Metadata):** `#8C8E95` — Timestamps, hotkey hints, inactive icons, subtle metadata.
- **Hairline Ink (Dividers & Ghost Borders):** `#E7E5DC` — 1px hairline delimiters; quiet boundary separation.
- **Border Focus / Hover:** `#D5D3C8` — Interactive border confirmation.

### Quiet Accents & Semantic Signals
Accents follow a dry, muted, mineral quality rather than vivid neon luminescence:
- **Lichen Green (Success / Complete):** `#5E7A63` (Surface: `#F0F4F1`)
- **Raw Amber (Warning / In Progress):** `#B38038` (Surface: `#FAF4EB`)
- **Cinnabar Red (Danger / Urgent):** `#A34A42` (Surface: `#F8EFEB`)
- **Stone Indigo (Information / Linked):** `#53677A` (Surface: `#EFF3F6`)

## Typography

Typography prioritizes micro-legibility and typographic cadence under dense informational load.

- **Primary Interface (Inter):** Leveraged for its neutral structure, compact horizontal footprint, and extensive optical adaptations. Headings adopt a restrained medium weight (`500` or `600`), avoiding heavy black styles to preserve the visual weight of parchment and sumi ink.
- **Monospaced Utility (JetBrains Mono):** Applied strictly to identifiers (`ENG-1049`), keyboard triggers (`⌘K`), tabular metrics, status tags, and commit hashes. The technical mono balances the organic warmth of the canvas with mechanical discipline.
- **Tracking Discipline:** Headings use negative letter spacing (`-0.025em` to `-0.01em`) to tighten character flow, while micro-labels and technical counters incorporate neutral to slight positive tracking (`0` to `0.02em`) to guarantee glyph disambiguation at small scales.

## Layout & Spacing

Layout adheres to a rigorous, high-density modular system where white space is treated not as vacant void (*ma*), but as active spatial tension.

- **Layout Grid Model:** Fluid-flexible viewports divided into strict functional columns (Navigation Rail: 220px fixed; Main Workbench: fluid; Context Inspector: 320px fixed). Content arrays utilize a fluid 12-column grid or single-axis CSS flex ribbons with hairline dividers.
- **Density Rhythms:** Compact 4px base increments. Standard table rows, command palette line-items, and tree lists operate at 28px to 32px height boundaries to allow high data visibility without crowding text baselines.
- **Breakpoints:**
  - `Mobile` (< 640px): Sidebar compresses to a bottom sheet or off-canvas drawer. Gutter collapses to `0.5rem`, outer margin `0.75rem`.
  - `Tablet` (640px – 1024px): Context inspector moves behind an expandable overlay panel. Gutter set to `0.75rem`.
  - `Desktop` (> 1024px): Multi-pane three-column workflow exposed simultaneously. Gutters fixed at `1rem`, outer margins at `1.5rem`.

## Elevation & Depth

This system avoids layered dropshadows, blurred ambient haloes, and multi-colored luminous blurs. Depth is achieved via pure planar contrast and tactile hairline boundaries.

1. **Planar Tonal Contrast:** Depth relies on the difference between the `#FAF9F5` canvas and the `#FFFFFF` matte surface.
2. **Hairline Seams:** Elevating elements (popovers, flyout menus, focused cards) sit within a precise `1px solid #E7E5DC` perimeter.
3. **Micro Contact Shadows:** When true elevation is required (such as modal command palettes or detached floating popovers), utilize a dry, compressed physical stamp shadow:
   - `box-shadow: 0 1px 2px rgba(31, 32, 34, 0.04), 0 4px 12px rgba(31, 32, 34, 0.03);`
4. **Active Selection Layering:** Hovered or active table rows and list items do not elevate; they tint into the surface with `#F3F2EC` or receive a hairline border frame with an internal inset edge.

## Shapes

Shapes emulate hand-cut, refined paper edges: precise, sharp, but slightly softened to prevent aggressive pixel corners.

- **Default Border Radius:** `4px` (`0.25rem`) for interactive buttons, text inputs, list selections, and inline tags.
- **Containers & Overlays (`rounded-lg`):** `6px` or `8px` (`0.5rem`) strictly reserved for floating panels, dialog cards, and command palettes.
- **Micro Tokens:** Status dots and keyboard hotkey keys (`kbd`) maintain `3px` or full circular `9999px` radii for strict circular dots.

## Components

### Buttons
- **Primary:** Background `#1F2022`, text `#FAF9F5`, border `1px solid #1F2022`, radius `4px`, height `28px` (compact) or `32px` (standard). Hover: `#333538`.
- **Secondary / Ghost:** Background `transparent` or `#FFFFFF`, text `#1F2022`, border `1px solid #E7E5DC`. Hover: background `#F3F2EC`, border `#D5D3C8`.
- **Keyboard Shortcut Affordance:** Append inline `<kbd>` inside buttons styled with JetBrains Mono, border `1px solid #E7E5DC`, background `#FAF9F5`, text `#8C8E95`, padding `0 3px`.

### Command Palette & Menus
- Background `#FFFFFF`, border `1px solid #E7E5DC`, micro shadow applied.
- Search input uses zero border, relying on bottom hairline separator `#E7E5DC`.
- Items have `28px` height, full width, padded `6px 10px`. Hover/Active: `#F3F2EC` with text `#1F2022`.

### Chips & Badges
- Issue tokens and tag chips have a maximum height of `20px`.
- Typography: JetBrains Mono `11px`, letter-spacing `0.02em`.
- Background `#F3F2EC`, border `1px solid #E7E5DC`, text `#4B4D52`. No pill capsules—keep subtle `3px` roundedness.

### Status Indicators (Quiet Status Dots)
- Diameter: `6px` geometric solid circles.
- Unset / Backlog: Outline circle `#8C8E95`.
- Todo: Solid `#8C8E95`.
- In Progress: Half-filled or solid Raw Amber (`#B38038`).
- Done: Solid Lichen Green (`#5E7A63`).
- Canceled: Hairline stroke with sumi line diagonal.

### Text Inputs & Form Controls
- Background `#FFFFFF`, text `#1F2022`, placeholder `#8C8E95`.
- Border: `1px solid #E7E5DC`.
- Focus State: Border color switches directly to `#1F2022` with a `1px` outline or shadow ring at `rgba(31, 32, 34, 0.08)`. No default browser blue outlines.

### Lists & Dense Tables
- Rows delimited exclusively by `1px solid #E7E5DC` bottom borders; no vertical grid lines.
- Row padding: `6px 12px`. Hover state: background `#F3F2EC` across the entire row transition-free (`0ms`) for immediate tactile feedback.

### Cards & Group Panels
- Flat structure: Background `#FFFFFF`, outline `1px solid #E7E5DC`.
- Header separator: subtle hairline border with metadata aligned using `label-sm` monospaced labels.