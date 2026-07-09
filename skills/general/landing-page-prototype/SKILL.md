---
name: landing-page-prototype
description: Build high-quality HTML landing page prototypes by forensically studying a reference website's design system and adapting it for a brand brief. Use when the user provides a reference URL and wants a landing page prototype, or says things like "build a prototype based on [URL]", "create a landing page inspired by [site]", "prototype this for [product]", "make a landing page like [reference]". Also use when the user mentions brand exploration, brand expression prototypes, or landing page variations.
---

# Landing Page Prototype Builder

Build landing page prototypes by forensically studying a reference website and adapting its design system to a brand brief. The reference's actual CSS is the source of truth, not descriptions or screenshots. The output should feel like it belongs in the same design universe as the reference, applied to the user's product.

## Why depth matters

AI-generated landing pages converge on the same generic patterns because the reference study is shallow. A screenshot tells you "the heading is big and bold." The CSS tells you "the heading is Rubik at 83px, weight 400, letter-spacing -2.5px, line-height 1.1, color rgb(26, 36, 96), and everything on the page uses a single font weight with hierarchy achieved through size alone." The second produces a prototype that actually feels like the reference. The first produces another template.

The difference between a good prototype and a generic one is almost always in the details that get skipped: the hover easing curve, the font terminal shape, the card scale direction (up vs. down), the shadow depth on hover, the specific way background colors are applied to sections vs. cards vs. body. These details compound into something that feels designed rather than generated.

## Required tools

- **Playwright MCP** (browser_navigate, browser_evaluate, browser_take_screenshot, browser_hover) for studying reference sites
- **Write** for creating the HTML file
- **Read** for viewing screenshots

## Workflow

### Step 1: Gather inputs

**Reference URL** (required): The website to study.

**Brand brief** (optional): Could be a file path, inline instructions, or conversation context. Extract: product name, what it does, primary color, target audience, key copy, content sections, constraints. If not provided, ask for at minimum: product name, what it does, primary color.

### Step 2: Study the reference

This is the most important step. Treat the reference site as source material to be forensically analyzed, not inspiration to glance at. Run **each investigation separately** since they look at different aspects. Do not combine them into a single pass.

Load the extraction scripts from `references/extraction-scripts.md` and run them in this order:

**2a. Screenshots first** - Take a viewport screenshot (hero feel), then scroll through the page **viewport by viewport** (scroll 600-800px, screenshot, repeat) to see every section transition. Do NOT rely on a single full-page screenshot — full-page screenshots freeze all scroll-driven animations at their initial state and hide transitions between sections (element-to-section expansions, section-to-card shrinks, parallax reveals). You need to see the page the way a user sees it: one viewport at a time, watching what changes between scroll positions.

**2b. Typography system** (Script 1) - Extract every font, size, weight, line-height, letter-spacing, and color. After running, answer:
- How many font families? How many weights?
- Are terminals rounded or flat? Is the font geometric or humanist?
- Is hierarchy achieved through weight, size, or both?
- What color is the body text? (pure black? tinted? deep purple? dark blue?)
- **Optical weight** (check the screenshot, not just CSS): How thick do the strokes actually look at display size? A font at CSS weight 400 can look thin (Cormorant) or thick (GT Alpina, Fraunces) depending on the typeface's design. When substituting, match the visual thickness you see in the screenshot, not the CSS font-weight number.

**2c. Color system** (Script 2) - Extract backgrounds, gradients, borders, CTA colors. After running, answer:
- Monochromatic or multicolor palette?
- How are background colors applied? (alternating sections? cards? accent blocks?)
- What's the CTA button color, border-radius, and padding?

**2d. Layout structure** (Script 3) - Extract section order, content widths, grid/flex patterns. This reveals the page skeleton.

**2e. Hover states** (Script 4) - Extract all :hover CSS rules and transition properties. This is commonly skipped and makes a huge difference. After running, answer:
- Do elements scale UP on hover (lift effect) or DOWN (press effect)?
- What easing function? (cubic-bezier values matter)
- Do inner elements react differently from their containers?
- What shadow changes on hover?

**2f. Scroll animations** (Script 5) - Extract sticky elements, scroll-driven animations, animation libraries. Identify the scroll behavior pattern (parallax? sticky swap? fade-in-on-scroll? card reveal with stagger?).

**2g. Visual elements** (Script 6) - Extract images, SVGs, videos, decorative elements. Identify the illustration style: product screenshots, flat illustrations, collage/sticker style, abstract shapes, photography, or video.

**2h. Card deep dive** (Script 7, if card-based layout) - Extract exact card dimensions, border-radius, padding, shadows, composition.

**2i. Structural patterns** (Script 8) - This is the highest-level analysis and catches architectural decisions that individual CSS properties don't reveal. After running, answer:
- **Nav shape**: Full-width sticky bar? Floating pill/oval centered on the page? Transparent overlay? Does it have a visible inner container with its own border-radius?
- **Section containment**: Are sections full-bleed (edge-to-edge background) or wrapped in rounded cards floating on a visible page background? This is one of the most distinctive architectural choices a page can make. "Content on a canvas" (Phantom) vs. "stacked full-width sections" (most sites) feel completely different.
- **Hero**: Full-viewport section or a card sitting on the page?
- **Footer**: Full-width or card-wrapped to match the sections?
- **Page background**: Is the body background visible between card-wrapped sections? What color is it?
- **Edge-bleed elements**: Are any background shapes or panels positioned to extend beyond the viewport edge? (e.g., a gray panel that starts mid-page and extends past the right edge, with only left corners rounded). These "flush-to-edge" panels are a distinctive spatial pattern that's invisible in individual element CSS but defines the page's feel. Check for elements with very large widths, asymmetric border-radius (like `64px 0 0 64px`), or negative margins/absolute positioning that pushes past the viewport.

These structural patterns define the page's spatial character. A floating pill nav on a page of card-wrapped sections feels like objects on a desk. Full-width sections with a sticky bar feel like scrolling through rooms. Both are valid but they produce very different experiences. If you miss this, the prototype will default to "stacked full-width sections" regardless of what the reference actually does.

**2j. Scroll-driven transitions** (Script 9) - Static CSS extraction can't detect properties that change based on scroll position (GSAP ScrollTrigger, Framer Motion, CSS scroll-timeline). This step detects **shape-shifting containers**: sections that change border-radius, width, or transform as you scroll. Run the scroll transition script, which scrolls the page in increments and compares element properties at each position. After running, answer:
- Do any sections **expand from a smaller element**? (e.g., a button that scales up to become a full section background)
- Do any sections **shrink into cards** as you scroll past them? (full-bleed section gains border-radius and inset margins)
- Is the **entire page content wrapped in a card** that's only revealed at the bottom? (content container has border-radius, sits on a colored page background visible at the very end)
- Do sections **slide over each other**? (sticky section stays while next section scrolls on top of it)

These scroll-driven spatial transformations are some of the most distinctive design patterns a page can have. They're invisible to static CSS extraction and invisible in full-page screenshots. You can only see them by scrolling through viewport by viewport.

### Step 3: Write the Reference Design Spec

Before writing any code, produce a structured spec and share it with the user. This is not optional. It's the bridge between raw CSS data and the prototype. Format it like this:

```
## Reference Design Spec: [Reference Site Name]

### Typography
- Display font: [name], [size range], weight [X], letter-spacing [X], line-height [X]
- Body font: [name], [size], weight [X]
- Text color: [exact rgb value and what it feels like - "deep navy, not black"]
- Hierarchy method: [size only / weight + size / weight only]
- Font substitute (if commercial): [Google Font name] because [specific reason it matches]

### Color System
- Body background: [rgb]
- Section backgrounds: [list with where each is used]
- CTA: [color], border-radius [X], padding [X]
- Accent colors: [list]
- Color application pattern: [how colors are distributed across the page]

### Layout
- Content max-width: [X]px
- Section flow: [ordered list of sections with their background colors]
- Grid/card pattern: [columns, gaps, card dimensions]

### Structural Architecture
- Nav: [full-width sticky bar / floating pill / transparent overlay] with [border-radius, background, backdrop-filter]
- Sections: [full-bleed / card-wrapped on visible page background]
- Hero: [full-viewport section / card floating on page]
- Footer: [full-width / card-wrapped]
- Page background: [color visible between sections, if card-wrapped]
- Heading containment: [grouped (headings inside card wrappers with content) / scattered (headings naked on page bg, content cards separate)]
- Overall spatial feel: ["objects on a canvas" / "stacked rooms" / "scrolling document"]

### Interactions
- Card hover: [scale direction, amount, easing, shadow change]
- Inner element hover: [what happens to children on container hover]
- Scroll entrance: [how elements enter - fade, scale, slide, stagger delay]
- Sticky behavior: [what sticks, at what scroll position]
- Special animations: [any distinctive interactions]

### Visual Language
- Illustration style: [screenshots / collage / flat / abstract / hand-drawn / none]
- Decorative elements: [blobs, dots, patterns, gradients - with colors and placement]
- Card visual composition: [what's inside the cards]

### What Makes It Distinctive
- [The 1-2 design decisions that make this site THIS site]

### Brand Expression Thesis
- "[One sentence: what this expression of the brand brief means]"
```

The brand expression thesis connects the reference's design language to the user's brand. Every decision in the build should trace back to it.

### Step 4: Build the prototype

Write a single self-contained HTML file with embedded CSS and JS.

**Use the Reference Design Spec as your blueprint.** Every CSS value in the prototype should trace back to something you measured in Step 2, adapted for the brand brief. If the reference uses `scale(0.985)` on hover with `cubic-bezier(0.22, 1, 0.36, 1)`, use those exact values. If the reference's heading is 96px with letter-spacing -2.4px, use those proportions.

**Match the reference's design system, not its content.** Use the reference's typography scale, spacing rhythm, color application patterns, layout structure, and interactions, but fill them with the brand brief's content.

**Replicate the interactions.** If the reference has a press-down hover, a staggered card reveal, a sticky scroll section, or a collage-style illustration, build it. These interactions are what makes a site feel designed rather than generated. Use vanilla JS, no libraries.

**Build product mockups in HTML/CSS.** These should look like real product UI. Use form fields, routing flows, email previews, security badges built from actual HTML elements, not placeholder rectangles.

**Font substitution**: When the reference uses a commercial font, choose a Google Fonts alternative that matches the **specific characteristics** you identified (terminal shape, weight range, geometric vs. humanist, character width). Don't just pick a font from the same category.

### Step 5: Self-review

After writing the file, navigate to it in the browser. Take a screenshot of the hero, then the full page. Place them next to your reference screenshots and answer these questions. Do not skip any.

**Subtraction check** (catches filler):
- List every element in your prototype that does NOT appear in the reference. For each one, state why you added it. If your reason is "it felt empty" or "it needed something," delete it. Decoration without a reason traceable to the brand expression thesis is filler.

**Visual weight check** (catches font mismatches):
- Screenshot your hero headline next to the reference hero headline. Do the strokes look equally thick? Is the visual presence the same? If your version looks thinner or lighter, your font weight is wrong regardless of what the CSS number says.

**Section-by-section diff** (catches structural drift):
- For each major section (hero, features, CTA, footer), name one specific difference between your prototype and the reference. Decide if each difference is an intentional adaptation (for the brand brief) or an accidental deviation. Fix the accidental ones.

**Interaction check**:
- Test every hover state and scroll animation. Do they match the reference's behavior?

Fix issues before presenting to the user.

### Step 6: Present and review

Show the user a screenshot and the live URL. Tell them:
- Your brand expression thesis
- What you replicated from the reference (be specific: "96px headings with inline emoji, press-down hover at scale(0.985), staggered card reveal")
- What you adapted for the brand brief
- Any trade-offs or limitations

## Font Substitution Guide

Common fonts like Inter or Roboto can be used if they genuinely match the reference's typographic intent. The test: "Am I choosing this font because it matches the reference, or because it's the first thing that comes to mind?"

When substituting, match the **specific characteristics**:
- Terminal shape (rounded vs. flat vs. tapered)
- Weight range (does the reference use one weight or many?)
- Geometric vs. humanist
- Character width (condensed, normal, wide)
- x-height (tall vs. short)

Some distinctive Google Fonts alternatives:
- Rounded terminals: Lexend, Nunito, Quicksand, Varela Round
- Flat terminals, geometric: Rubik, Sora, Manrope
- Thick serif: Fraunces, Libre Bodoni
- Clean sans: Outfit, Karla, Work Sans
- Editorial serif: Newsreader, Source Serif 4

## Common mistakes

1. **One-pass CSS extraction.** Running a single browser_evaluate and moving on. The reference study needs 5-7 separate investigations (typography, colors, layout, hover, scroll, visuals, cards). Each reveals different details.

2. **Ignoring hover behavior.** Hover states are invisible in screenshots. If you don't extract the CSS rules, you'll default to the generic "lift on hover" when the reference might use a press-down, a color shift, or a shadow change. Always run the hover script.

3. **Wrong font characteristics.** Picking a font from the right category but with wrong terminal shape, weight, or character width. If the reference uses a geometric sans with flat terminals and you pick a rounded sans, the whole page feels different.

4. **Skipping the self-review.** Building the prototype and presenting it without viewing it in the browser first. Always screenshot your own output before showing the user.

5. **Decoration without purpose.** Every visual element must serve the brand expression thesis. If you can't explain why a decorative element is there in terms of the thesis, remove it.

6. **Optimizing for speed.** Every prototype deserves the same forensic depth. Do not cut corners on subsequent prototypes. Do not delegate reference study to agents without visual context.
