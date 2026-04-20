# UI Design Language Compliance Audit

Date: 2026-04-20
Scope: `apps/web/src/app/globals.css` and `apps/web/src/app/layout.tsx` against `FE design/design language.md`.

## Verdict

The UI now **substantially adheres** to the design language for shared form/input and reusable surface behaviors. Core palette, typography families, tonal layering, CTA gradients, glassmorphism, and key interaction states are implemented.

## What matches the design language

1. **Core color token values align** with the spec for surface/primary/secondary tiers.
2. **Primary CTAs use the required 135° gradient** (`primary` → `primary_container`).
3. **No-line sectioning approach is mostly followed** (containers use background-tier contrast, not 1px divider borders).
4. **Typography family split is implemented** (Manrope base text, Plus Jakarta Sans headings).
5. **Glassmorphism appears in the user menu** with translucent surface + `backdrop-filter: blur(20px)`.

## Original gaps found in this audit

### 1) Input fields do not implement the required “bottom-heavy” focus pattern
- Spec requires a `surface_container` field with **2px bottom-edge outline on focus**.
- Current implementation uses borderless, fully rounded inputs with no bottom-only focus rule.
- Impact: weak focus affordance and mismatch with input interaction language.

### 2) Missing required interaction states for buttons/cards
- Spec requires:
  - Button hover: stronger gradient intensity
  - Button press: scale to `0.98`
  - Card/list hover: shift to `surface_bright`
- Current CSS defines no hover/active states for `.app-button` or `.task-row`/cards.
- Impact: tactile “smooth stone” behavior is not present.

### 3) Container corner scale drifts below the prescribed 2xl–3xl rhythm
- Spec says avoid sharp corners and keep containers on the `2xl` to `3xl` scale.
- Multiple reusable surfaces use `0.7rem`, `0.8rem`, and `1rem` radii.
- Impact: UI feels less organic and less aligned with the “pebble-like” tactile identity.

### 4) Dark theme ambient shadow is too heavy/dark relative to spec guidance
- Spec calls for ambient depth using tinted `on_surface` at ~5% opacity.
- Dark theme uses `rgba(0,0,0,0.36)` for `--ambient-shadow`.
- Impact: depth appears heavier than intended and less “atmospheric.”

### 5) Selected task state uses a strong solid outline outside ghost-border guidance
- Spec fallback border guidance: `outline_variant` at ~15% opacity.
- Current selection styling uses `outline: 2px solid #c9b48f`.
- Impact: selection treatment looks more structural than the “ghost border” fallback style.

## Remediation status (implemented)

1. ✅ Added focus-visible and focus states for `.app-input` with bottom-only 2px line treatment.
2. ✅ Added `.app-button--primary:hover` and `.app-button:active { transform: scale(0.98); }`.
3. ✅ Added card/list hover tonal shifts for `.task-row`, `.section-card`, `.day-card` via `--surface-bright`.
4. ✅ Normalized key reusable container radii toward tokenized `--radius-xl`.
5. ✅ Replaced dark-mode ambient shadow with a tinted, low-opacity variant.
6. ✅ Replaced selected-task outline with ghost-border token treatment.

## Evidence references

- Design spec: `FE design/design language.md`
- Web styling implementation: `apps/web/src/app/globals.css`
- Typography/font loading: `apps/web/src/app/layout.tsx`
