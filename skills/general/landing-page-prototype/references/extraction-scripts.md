# Reference Site Extraction Scripts

Use these browser_evaluate scripts to extract the design system from a reference site. Run each one separately - they investigate different aspects.

## Script 1: Typography System

Extracts font families, sizes, weights, line heights, letter spacing, and colors for all text elements.

```javascript
() => {
  const samples = [];
  document.querySelectorAll('h1, h2, h3, h4, p, a, button, span, li').forEach(el => {
    const s = getComputedStyle(el);
    const text = el.textContent.trim();
    if (samples.length < 30 && text.length > 2 && text.length < 100 && parseFloat(s.fontSize) > 10) {
      samples.push({
        tag: el.tagName,
        text: text.slice(0, 60),
        fontSize: s.fontSize,
        fontWeight: s.fontWeight,
        fontFamily: s.fontFamily.split(',')[0].trim().replace(/"/g, ''),
        lineHeight: s.lineHeight,
        letterSpacing: s.letterSpacing,
        color: s.color,
        fontFeatureSettings: s.fontFeatureSettings,
        fontVariationSettings: s.fontVariationSettings
      });
    }
  });
  const body = getComputedStyle(document.body);
  return {
    bodyFont: body.fontFamily,
    bodyFontSize: body.fontSize,
    bodyColor: body.color,
    typeSamples: samples
  };
}
```

After running this, analyze:
- How many font families are used? (1 = single-font system, 2+ = paired)
- How many font weights? (1 = hierarchy through size only, multiple = weight-based hierarchy)
- What's the size range? (largest heading vs. smallest body text)
- Are the terminals rounded or flat? (compare against known fonts)
- What's the text color? (pure black, near-black, dark grey, or a tinted color like deep purple?)

## Script 2: Color System & Backgrounds

Extracts all background colors, gradients, and accent colors.

```javascript
() => {
  const bgColors = new Set();
  const gradients = [];
  const borderColors = new Set();
  document.querySelectorAll('section, div, main, header, footer, article, aside, nav').forEach(el => {
    const s = getComputedStyle(el);
    const bg = s.backgroundColor;
    if (bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') bgColors.add(bg);
    const bgImg = s.backgroundImage;
    if (bgImg !== 'none' && bgImg.includes('gradient')) gradients.push(bgImg.slice(0, 200));
    const bc = s.borderColor;
    if (bc && bc !== 'rgb(0, 0, 0)' && bc !== 'rgba(0, 0, 0, 0)') borderColors.add(bc);
  });
  // Find CTA/accent colors from buttons and links
  const ctaColors = [];
  document.querySelectorAll('a, button').forEach(el => {
    const s = getComputedStyle(el);
    if (s.backgroundColor !== 'rgba(0, 0, 0, 0)' && s.backgroundColor !== 'transparent' && s.backgroundColor !== 'rgb(255, 255, 255)') {
      ctaColors.push({ bg: s.backgroundColor, color: s.color, text: el.textContent.trim().slice(0, 30), borderRadius: s.borderRadius, padding: s.padding });
    }
  });
  return {
    bgColors: [...bgColors].slice(0, 15),
    gradients: gradients.slice(0, 5),
    borderColors: [...borderColors].slice(0, 10),
    ctaColors: ctaColors.slice(0, 8)
  };
}
```

After running this, analyze:
- Is the page monochromatic (one hue family) or multicolor?
- How are background colors used? (alternating sections, cards vs. body, accent blocks)
- What's the CTA color and shape (border-radius, padding)?
- Are there gradients? Where?

## Script 3: Layout Structure

Extracts section order, content widths, grid/flex patterns, and spacing.

```javascript
() => {
  // Map the page's section flow
  const sections = [];
  const topLevel = document.querySelector('main') || document.body;
  const directChildren = topLevel.children;
  for (let i = 0; i < Math.min(directChildren.length, 20); i++) {
    const el = directChildren[i];
    const s = getComputedStyle(el);
    if (el.offsetHeight > 50) {
      sections.push({
        tag: el.tagName,
        class: el.className.toString().slice(0, 60),
        height: el.offsetHeight,
        bgColor: s.backgroundColor !== 'rgba(0, 0, 0, 0)' ? s.backgroundColor : 'transparent',
        display: s.display,
        maxWidth: s.maxWidth,
        padding: s.padding,
        text: el.textContent.trim().slice(0, 50)
      });
    }
  }
  // Find content containers and their max-width
  const containers = new Set();
  document.querySelectorAll('div, section, main').forEach(el => {
    const mw = getComputedStyle(el).maxWidth;
    if (mw !== 'none' && mw !== '100%' && parseFloat(mw) > 500) {
      containers.add(mw);
    }
  });
  return { sections, contentWidths: [...containers] };
}
```

## Script 4: Hover States & Micro-interactions

Extracts all CSS :hover rules that involve transforms, shadows, or visual changes.

```javascript
() => {
  const hoverRules = [];
  const transitionEls = [];
  const sheets = Array.from(document.styleSheets);
  sheets.forEach(ss => {
    try {
      const rules = Array.from(ss.cssRules || []);
      rules.forEach(rule => {
        const text = rule.cssText || '';
        if (text.includes(':hover') && (
          text.includes('scale') || text.includes('rotate') ||
          text.includes('translate') || text.includes('transform') ||
          text.includes('shadow') || text.includes('opacity') ||
          text.includes('background')
        )) {
          hoverRules.push(text.slice(0, 400));
        }
      });
    } catch(e) {}
  });
  // Find elements with transitions set
  document.querySelectorAll('*').forEach(el => {
    const s = getComputedStyle(el);
    if (s.transition && !s.transition.includes('0s') && s.transition !== 'all' && el.offsetWidth > 50) {
      if (transitionEls.length < 15) {
        transitionEls.push({
          tag: el.tagName,
          class: el.className.toString().slice(0, 50),
          transition: s.transition.slice(0, 150),
          cursor: s.cursor
        });
      }
    }
  });
  return { hoverRules: hoverRules.slice(0, 15), transitionEls };
}
```

After running this, identify the hover pattern:
- Do cards scale UP (common, lifts off page) or DOWN (press effect, like Phantom)?
- What easing function is used? (ease, ease-in-out, cubic-bezier?)
- Do inner elements react differently from outer containers?
- What cursor is used? (pointer, default?)

## Script 5: Scroll Animations & Sticky Elements

Extracts sticky positioning, scroll-driven CSS, and animation infrastructure.

```javascript
() => {
  const stickyEls = [];
  const animatedEls = [];
  document.querySelectorAll('*').forEach(el => {
    const s = getComputedStyle(el);
    if (s.position === 'sticky') {
      stickyEls.push({
        tag: el.tagName,
        class: el.className.toString().slice(0, 60),
        top: s.top,
        height: el.offsetHeight,
        text: el.textContent.trim().slice(0, 40)
      });
    }
    if (s.animationName && s.animationName !== 'none') {
      animatedEls.push({
        tag: el.tagName,
        class: el.className.toString().slice(0, 50),
        animation: s.animationName,
        duration: s.animationDuration,
        timing: s.animationTimingFunction
      });
    }
  });
  // Check for scroll-driven animation APIs
  let hasScrollTimeline = false;
  const sheets = Array.from(document.styleSheets);
  sheets.forEach(ss => {
    try {
      Array.from(ss.cssRules || []).forEach(rule => {
        const text = rule.cssText || '';
        if (text.includes('scroll-timeline') || text.includes('animation-timeline') || text.includes('view-timeline')) {
          hasScrollTimeline = true;
        }
      });
    } catch(e) {}
  });
  // Check for animation libraries in scripts
  const scriptSrcs = Array.from(document.querySelectorAll('script[src]')).map(s => s.src);
  const animLibs = scriptSrcs.filter(s => s.includes('gsap') || s.includes('framer') || s.includes('lenis') || s.includes('locomotive') || s.includes('aos'));
  return { stickyEls, animatedEls: animatedEls.slice(0, 10), hasScrollTimeline, animLibs };
}
```

## Script 6: Visual Elements & Illustration Style

Extracts images, SVGs, videos, and decorative elements to understand the visual language.

```javascript
() => {
  const visuals = [];
  document.querySelectorAll('img, svg, video').forEach(el => {
    if (el.offsetWidth > 40 && el.offsetHeight > 40) {
      visuals.push({
        tag: el.tagName,
        width: el.offsetWidth,
        height: el.offsetHeight,
        src: el.tagName === 'IMG' ? (el.src || '').slice(0, 120) : (el.tagName === 'VIDEO' ? 'video-element' : 'inline-svg'),
        alt: el.alt || '',
        class: el.className.toString().slice(0, 50),
        borderRadius: getComputedStyle(el).borderRadius
      });
    }
  });
  // Check for decorative elements (absolute/fixed positioned, low-content divs)
  const decorative = [];
  document.querySelectorAll('div, span').forEach(el => {
    const s = getComputedStyle(el);
    if ((s.position === 'absolute' || s.position === 'fixed') && el.children.length === 0 && el.offsetWidth > 20) {
      if (decorative.length < 10) {
        decorative.push({
          width: el.offsetWidth,
          height: el.offsetHeight,
          borderRadius: s.borderRadius,
          bgColor: s.backgroundColor,
          opacity: s.opacity,
          filter: s.filter !== 'none' ? s.filter : null
        });
      }
    }
  });
  return { visuals: visuals.slice(0, 15), decorativeElements: decorative };
}
```

After running this, identify:
- Are visuals product screenshots, illustrations, photos, or videos?
- What's the illustration style? (flat, 3D, hand-drawn, collage, abstract shapes)
- Are there decorative blobs, dots, or background shapes?
- What border-radius do images/cards use?

## Script 7: Card Structure Deep Dive

When the reference uses a card-based layout, extract exact card dimensions and composition.

```javascript
() => {
  const cards = [];
  document.querySelectorAll('div, article, section').forEach(el => {
    const s = getComputedStyle(el);
    const br = parseFloat(s.borderRadius);
    const w = el.offsetWidth;
    const h = el.offsetHeight;
    if (br > 12 && w > 200 && h > 200 && w < 800) {
      cards.push({
        width: w,
        height: h,
        borderRadius: s.borderRadius,
        bgColor: s.backgroundColor,
        padding: s.padding,
        boxShadow: s.boxShadow !== 'none' ? s.boxShadow.slice(0, 80) : 'none',
        overflow: s.overflow,
        display: s.display,
        flexDirection: s.flexDirection,
        gap: s.gap,
        childCount: el.children.length,
        text: el.textContent.trim().slice(0, 50)
      });
    }
  });
  return { cards: cards.slice(0, 12) };
}
```

## Script 8: Structural Patterns

Higher-level structural analysis. The previous scripts extract CSS values, but this one identifies **how the page is architecturally composed**. Things like whether the nav floats or spans full-width, whether content sections are full-bleed or wrapped in cards, whether the hero is a card or a section. These structural decisions define the page's character just as much as colors and fonts do.

```javascript
() => {
  // NAV STRUCTURE
  const nav = document.querySelector('nav') || document.querySelector('header');
  let navInfo = null;
  if (nav) {
    const ns = getComputedStyle(nav);
    const navInner = nav.querySelector('div') || nav;
    const nis = getComputedStyle(navInner);
    navInfo = {
      position: ns.position,
      width: nav.offsetWidth,
      viewportWidth: window.innerWidth,
      isFullWidth: nav.offsetWidth >= window.innerWidth - 20,
      borderRadius: ns.borderRadius,
      innerBorderRadius: nis.borderRadius,
      background: ns.backgroundColor,
      backdropFilter: ns.backdropFilter,
      border: ns.border,
      boxShadow: ns.boxShadow !== 'none' ? ns.boxShadow.slice(0, 80) : 'none',
      margin: ns.margin,
      padding: ns.padding,
      maxWidth: ns.maxWidth,
      top: ns.top,
      // Is it a floating pill? (has border-radius, not full-width, or has margin)
      isFloatingPill: parseFloat(ns.borderRadius) > 20 || (parseFloat(ns.margin) > 0 && ns.position === 'fixed')
    };
    // Check if nav has a visible container with its own border-radius
    nav.querySelectorAll('div').forEach(el => {
      const es = getComputedStyle(el);
      if (parseFloat(es.borderRadius) > 20 && el.offsetWidth > 200) {
        navInfo.innerContainerRadius = es.borderRadius;
        navInfo.innerContainerBg = es.backgroundColor;
        navInfo.innerContainerBorder = es.border;
        navInfo.hasFloatingInnerContainer = true;
      }
    });
  }

  // SECTION CONTAINMENT: Are sections full-bleed or card-wrapped?
  const sectionPatterns = [];
  const mainContent = document.querySelector('main') || document.body;
  const topChildren = mainContent.querySelectorAll(':scope > section, :scope > div, :scope > article');
  topChildren.forEach(el => {
    if (el.offsetHeight > 100 && sectionPatterns.length < 12) {
      const s = getComputedStyle(el);
      const isFullWidth = el.offsetWidth >= window.innerWidth - 20;
      const hasRadius = parseFloat(s.borderRadius) > 0;
      const hasBg = s.backgroundColor !== 'rgba(0, 0, 0, 0)' && s.backgroundColor !== 'transparent';
      sectionPatterns.push({
        tag: el.tagName,
        width: el.offsetWidth,
        isFullWidth,
        borderRadius: s.borderRadius,
        isCardWrapped: hasRadius && !isFullWidth,
        bgColor: hasBg ? s.backgroundColor : 'transparent',
        margin: s.margin,
        maxWidth: s.maxWidth,
        boxShadow: s.boxShadow !== 'none' ? 'has-shadow' : 'none',
        overflow: s.overflow,
        text: el.textContent.trim().slice(0, 40)
      });
    }
  });

  // HERO STRUCTURE
  const heroEl = mainContent.querySelector('section:first-of-type') || mainContent.querySelector(':scope > div:first-of-type');
  let heroInfo = null;
  if (heroEl) {
    const hs = getComputedStyle(heroEl);
    heroInfo = {
      isFullViewport: heroEl.offsetHeight >= window.innerHeight * 0.8,
      isFullWidth: heroEl.offsetWidth >= window.innerWidth - 20,
      isCardWrapped: parseFloat(hs.borderRadius) > 0 && heroEl.offsetWidth < window.innerWidth - 20,
      borderRadius: hs.borderRadius,
      minHeight: hs.minHeight,
      height: heroEl.offsetHeight
    };
  }

  // FOOTER STRUCTURE
  const footer = document.querySelector('footer');
  let footerInfo = null;
  if (footer) {
    const fs = getComputedStyle(footer);
    footerInfo = {
      isFullWidth: footer.offsetWidth >= window.innerWidth - 20,
      borderRadius: fs.borderRadius,
      isCardWrapped: parseFloat(fs.borderRadius) > 0 && footer.offsetWidth < window.innerWidth - 20,
      bgColor: fs.backgroundColor
    };
  }

  // PAGE-LEVEL CONTAINMENT
  const bodyBg = getComputedStyle(document.body).backgroundColor;
  const htmlBg = getComputedStyle(document.documentElement).backgroundColor;

  // CONTAINMENT ANALYSIS: Are headings grouped with their content cards,
  // or do headings float independently on the page background?
  // This distinguishes "grouped sections" (heading + cards in a wrapper)
  // from "scattered objects" (heading naked on bg, cards naked on bg).
  const containmentAnalysis = [];
  const bigHeadings = document.querySelectorAll('h2');
  bigHeadings.forEach(h => {
    const fontSize = parseFloat(getComputedStyle(h).fontSize);
    if (fontSize > 50) {
      // Walk up to find the nearest container with background or border-radius
      let el = h.parentElement;
      let nearestCard = null;
      for (let i = 0; i < 8 && el && el !== document.body; i++) {
        const s = getComputedStyle(el);
        if (parseFloat(s.borderRadius) > 12 || (s.backgroundColor !== 'rgba(0, 0, 0, 0)' && s.backgroundColor !== 'transparent' && s.backgroundColor !== htmlBg && s.backgroundColor !== bodyBg)) {
          nearestCard = {
            tag: el.tagName,
            borderRadius: s.borderRadius,
            bgColor: s.backgroundColor,
            width: el.offsetWidth,
            depth: i
          };
          break;
        }
        el = el.parentElement;
      }
      // Check if sibling cards share the same container
      const headingParent = h.closest('[class]');
      const siblingCards = headingParent ? headingParent.querySelectorAll('div').length : 0;

      containmentAnalysis.push({
        headingText: h.textContent.trim().slice(0, 40),
        fontSize: fontSize + 'px',
        isNakedOnPageBg: nearestCard === null,
        nearestCardWrapper: nearestCard,
        note: nearestCard === null ? 'Heading floats directly on page background' : 'Heading is inside a card container at depth ' + nearestCard.depth
      });
    }
  });

  return {
    nav: navInfo,
    sectionPatterns,
    hero: heroInfo,
    footer: footerInfo,
    pageBg: { body: bodyBg, html: htmlBg },
    containmentAnalysis,
    summary: {
      isNavFloating: navInfo ? navInfo.isFloatingPill || (navInfo.hasFloatingInnerContainer === true) : false,
      areSectionsCardWrapped: sectionPatterns.some(s => s.isCardWrapped),
      isHeroCardWrapped: heroInfo ? heroInfo.isCardWrapped : false,
      isFooterCardWrapped: footerInfo ? footerInfo.isCardWrapped : false,
      headingsAreNaked: containmentAnalysis.every(h => h.isNakedOnPageBg)
    }
  };
}
```

After running this, answer these structural questions:
- **Nav**: Is it a full-width sticky bar, a floating pill/oval, or a transparent overlay? Does it have its own background card within the nav?
- **Sections**: Are they full-bleed (edge-to-edge) or wrapped in rounded cards floating on a page background?
- **Hero**: Is it a full-viewport section or a card sitting on the page?
- **Footer**: Full-width or card-wrapped?
- **Page background**: Is the body/html background visible between elements? What color is it?
- **Heading containment** (this is subtle but critical): Do the big section headings live INSIDE card wrappers alongside their content, or do they float NAKED on the page background with their content cards as separate elements below? The difference:
  - "Grouped": heading + cards wrapped together in a parent card = sections feel like contained panels
  - "Scattered": heading naked on bg, cards as individual pieces below = page feels like objects arranged on a desk/canvas
  
  Phantom uses the "scattered" pattern. Most SaaS sites use the "grouped" pattern. Getting this wrong changes the entire spatial character of the page.

These structural patterns define whether the page feels like "content on a canvas" (card-wrapped, like Phantom) vs. "stacked sections" (full-bleed, like most sites). This is one of the most distinctive architectural decisions a landing page makes and is easily overlooked.

## Script 9: Scroll-Driven Transitions

Static CSS extraction can't detect properties that change based on scroll position. This script scrolls the page in increments and compares element properties at each position to detect **shape-shifting containers** — sections that change border-radius, width, or transform as you scroll.

**Important**: This script must be run using `browser_run_code_unsafe` (not `browser_evaluate`) because it needs to programmatically scroll the page and wait between positions.

```javascript
async (page) => {
  const pageHeight = await page.evaluate(() => document.body.scrollHeight);
  const viewportHeight = await page.evaluate(() => window.innerHeight);
  const increment = Math.round(viewportHeight * 0.75);
  const positions = [];
  for (let y = 0; y <= pageHeight; y += increment) {
    positions.push(y);
  }
  // Cap at 25 positions to avoid excessive runtime
  const sampledPositions = positions.length > 25
    ? positions.filter((_, i) => i % Math.ceil(positions.length / 25) === 0)
    : positions;

  const snapshots = [];
  for (const scrollY of sampledPositions) {
    await page.evaluate((y) => window.scrollTo(0, y), scrollY);
    await page.waitForTimeout(200); // let scroll-driven animations settle

    const data = await page.evaluate(() => {
      const containers = [];
      // Broad selector: any div large enough to be a section-level container.
      // Only track elements with interesting visual properties to keep the list manageable.
      document.querySelectorAll('div').forEach(el => {
        if (el.offsetHeight > 300 && el.offsetWidth > 600 && containers.length < 40) {
          const s = getComputedStyle(el);
          const br = s.borderRadius;
          const transform = s.transform;
          const inlineStyle = el.getAttribute('style') || '';
          if (br !== '0px' || transform !== 'none' || inlineStyle.includes('transform') || inlineStyle.includes('border-radius') || inlineStyle.includes('scale')) {
            containers.push({
              id: (el.className.toString().slice(0, 35) || el.tagName) + '_' + el.offsetTop,
              width: el.offsetWidth,
              height: el.offsetHeight,
              borderRadius: br,
              transform: transform !== 'none' ? transform.slice(0, 80) : 'none',
              opacity: s.opacity
            });
          }
        }
      });
      return containers;
    });
    snapshots.push({ scrollY, containers: data });
  }

  // Compare snapshots to find elements whose properties changed
  const changes = [];
  const seen = new Set();
  for (let i = 1; i < snapshots.length; i++) {
    const prev = snapshots[i - 1];
    const curr = snapshots[i];
    for (const cEl of curr.containers) {
      const pEl = prev.containers.find(p => p.id === cEl.id);
      if (pEl && !seen.has(cEl.id)) {
        const diffs = [];
        if (pEl.borderRadius !== cEl.borderRadius) diffs.push(`borderRadius: ${pEl.borderRadius} → ${cEl.borderRadius}`);
        if (Math.abs(pEl.width - cEl.width) > 20) diffs.push(`width: ${pEl.width} → ${cEl.width}`);
        if (pEl.transform !== cEl.transform) diffs.push(`transform changed`);
        if (pEl.opacity !== cEl.opacity) diffs.push(`opacity: ${pEl.opacity} → ${cEl.opacity}`);
        if (diffs.length > 0) {
          changes.push({
            element: cEl.id,
            scrollRange: `${prev.scrollY}px → ${curr.scrollY}px`,
            changes: diffs
          });
          seen.add(cEl.id);
        }
      }
    }
  }
  return { totalPositions: snapshots.length, shapeshifters: changes };
}
```

After running this, look for:
- **border-radius changes**: A section going from `0px` to `40px` means it's shrinking into a card as you scroll past it.
- **width changes**: A container getting narrower means it's pulling away from the viewport edges (section → card).
- **transform changes**: Scale or translate changes mean elements are expanding/shrinking/sliding based on scroll.
- **margin changes**: Margin appearing means the element is gaining inset from the viewport edges.

Common patterns this catches:
- **Button-to-section expansion**: A small pill element scales up to become a full-section background
- **Section-to-card shrink**: A full-bleed section gains border-radius and margin as you scroll past, becoming a card
- **Page-is-a-card reveal**: The outermost content container has border-radius, sitting on a colored body background that's only visible at the very top and bottom of the scroll
- **Sticky overlap**: One section stays fixed while the next slides over it
