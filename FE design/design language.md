# Design System Specification

## 1. Overview & Creative North Star: "The Sun-Drenched Courtyard"

The philosophy of this design system is rooted in the concept of **The Sun-Drenched Courtyard**. Unlike standard productivity tools that rely on the cold, clinical efficiency of a laboratory, this system seeks to emulate the steady, warm, and organic rhythm of a Tuscan estate. It moves away from the "urgency-driven" UI of the last decade, favoring a calm, editorial approach that reduces cognitive load for neurodivergent users.

To move beyond the "template" look, we employ **intentional asymmetry**. Layouts should not always be perfectly centered; instead, they should "flow" vertically like a winding stone path. By utilizing overlapping elements and a high-contrast typography scale, we create a sense of place and presence, making time management feel like a ritual rather than a chore.

---

## 2. Colors: Tonal Architecture

Our palette is derived from the natural elements of the Tuscan landscape: deep olive groves, terracotta earth, and sun-bleached stone. These colors are not merely decorative; they define the functional architecture of the interface.

### The "No-Line" Rule
To maintain a high-end, editorial feel, **1px solid borders are strictly prohibited for sectioning.** Boundaries must be defined through background color shifts. For example, a task list section should be distinguished from the background not by a line, but by transitioning from `surface` to `surface_container_low`.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers—stacked sheets of fine, heavy-stock paper. 
- **Base Layer:** `surface` (#fdf9f2)
- **Secondary Sectioning:** `surface_container` (#f1ede7)
- **Interactive Objects (Cards):** `surface_container_low` (#f7f3ed)
- **Floating Elements:** `surface_container_lowest` (#ffffff)

By nesting these tiers, we create depth without visual noise. An inner container should always be a slightly higher or lower tier than its parent to define its importance.

### Glass & Gradient (The Soul)
Flat color can feel stagnant. To provide a "premium" soul:
- **Primary CTAs:** Use a subtle linear gradient from `primary` (#263328) to `primary_container` (#3c4a3e) at a 135-degree angle.
- **Floating Overlays:** Use Glassmorphism. Apply `surface` at 80% opacity with a `backdrop-blur` of 20px. This allows the warm ochre or terracotta tones of the background to bleed through, softening the edges of the experience.

---

## 3. Typography: Editorial Clarity

The typography is designed for "skimmability"—crucial for ADHD-friendly interfaces. We use a combination of **Plus Jakarta Sans** for structure and **Manrope** for utility.

- **Display & Headlines (Plus Jakarta Sans):** These are our "anchors." Use generous letter spacing (-0.02em) and a line height of 1.2 to 1.3 to create a grounded, authoritative feel. 
- **Body & Labels (Manrope):** Chosen for its distinct character shapes (e.g., the clarity of 'l', 'I', and '1'). We mandate a **line height of 1.6 to 1.8** for all body text to prevent "line jumping" during reading.

**Hierarchy as Brand Identity:**
- **Display-lg (3.5rem):** Used for daily affirmations or big-picture goals.
- **Headline-md (1.75rem):** Used for section titles.
- **Body-lg (1rem):** The standard for task descriptions, prioritizing breathability over density.

---

## 4. Elevation & Depth: Atmospheric Perspective

We convey hierarchy through **Tonal Layering** rather than traditional structural shadows.

### The Layering Principle
Depth is achieved by "stacking" the surface-container tiers. For instance, a "Current Task" card should use `surface_container_lowest` and sit atop a `surface_container_low` dashboard. This creates a soft, natural lift that mimics paper on a desk.

### Ambient Shadows
When a "floating" effect is necessary (e.g., a FAB or a Modal), use **Ambient Shadows**:
- **Color:** A tinted version of `on_surface` at 5% opacity.
- **Blur:** Large values (40px to 60px) with 0-4px Y-offset.
Avoid dark grey "drop shadows" which feel dated and heavy.

### The "Ghost Border" Fallback
If a border is required for accessibility (e.g., in high-contrast needs), it must be a **Ghost Border**: use the `outline_variant` token at **15% opacity**. This provides a hint of structure without breaking the flowing, organic aesthetic.

---

## 5. Components: Tactile Objects

### Buttons (The "Smooth Stone" Aesthetic)
- **Primary:** Gradient background (`primary` to `primary_container`), `on_primary` text. Shape: `xl` (3rem) roundedness for a pebble-like feel.
- **Secondary:** `surface_variant` background with `on_surface_variant` text.
- **States:** On hover, increase the gradient intensity. On press, scale down to 0.98 for tactile feedback.

### Cards & Lists (The Flow)
- **No Dividers:** Forbid the use of divider lines. Separate list items using 12px to 16px of vertical whitespace.
- **Interactive States:** Use a subtle shift to `surface_bright` on hover to signal interactivity.

### Chips (Visual Cues)
- **Action Chips:** Use `secondary_fixed` (Terracotta) for active states to provide a warm, motivating signal without the stress of "High-Alert Red."
- **Filter Chips:** Soft `tertiary_fixed_dim` (Ochre) to evoke sunshine and positivity.

### Input Fields
- **Style:** "Bottom-Heavy." Use a `surface_container` background with a slightly thicker (2px) `outline` only on the bottom edge when focused. This creates a grounded, "writing on a line" feel.

---

## 6. Do’s and Don’ts

### Do:
- **Embrace White Space:** If a screen feels "busy," add 24px of padding rather than adding a border or divider.
- **Use "Flowing" Rhythms:** Allow cards to have varying heights. A rigid, uniform grid is often overwhelming; a staggered, editorial layout is more inviting.
- **Prioritize Soft Signals:** Use `secondary` (Terracotta) for warnings. Avoid #FF0000; it triggers a stress response that this system is designed to mitigate.

### Don't:
- **Don't use 100% Black:** Even in dark mode, the "darkest" color should be a deep, cozy charcoal-olive to maintain the "Tuscan Night" feel.
- **Don't use Serif fonts:** While they look editorial, they can be difficult for neurodivergent users to process quickly. Stick to the specified sans-serifs.
- **Don't use Sharp Corners:** Nothing in the natural Tuscan landscape is perfectly sharp. Stick to the `2xl` to `3xl` roundedness scale for all containers.

---

## 7. Token Reference Summary

| Token | Value | Usage |
| :--- | :--- | :--- |
| **Surface** | #fdf9f2 | Main background, airy & stone-like |
| **Primary** | #263328 | Deep olive for focus and grounding |
| **Secondary** | #904b36 | Terracotta accent for motivation |
| **Tertiary** | #452b00 | Ochre for subtle "sunlit" highlights |
| **Radius-xl** | 3rem | Soft, pebble-like corners |
| **Shadow** | 5% on_surface / 40px blur | Ambient, natural depth |