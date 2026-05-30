// =============================================================================
// 05-two-column-comparison.js — TWO-COLUMN COMPARISON
// =============================================================================
// Slide master definition + demo slide for layout 5: TWO-COLUMN COMPARISON.
// Override per-org by writing branding/<org>/masters/05-two-column-comparison.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "05_TWO_COLUMN",
    background: { color: C.offwhite },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 5  ·  TWO-COLUMN COMPARISON"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  const { addTitleSubtitle } = helpers;
  let s = pres.addSlide({ masterName: "05_TWO_COLUMN" });
  addTitleSubtitle(s, "[Two-Column Comparison]",
    "Use this layout for competitor watch, before/after, or option A vs option B framing");
  const cols = [
    { tag: "[COMPETITOR / OPTION A]", sub: "[Sub-line: pillar, employer, or framing]",
      flag: "[Risk / re-pegged flag]",   flagColor: C.red,  flagTint: C.redTint,  flagIcon: "⚠",
      flagNote: "[Short explanation of why this matters and what's at stake]" },
    { tag: "[COMPETITOR / OPTION B]", sub: "[Sub-line: pillar, employer, or framing]",
      flag: "[Stability / opportunity]", flagColor: C.accentTeal, flagTint: C.tealTint, flagIcon: "✓",
      flagNote: "[Short explanation of the contrasting position]" }
  ];
  const colW = 6.0, startX = 0.5, startY = 2.2, gapX = 0.30;
  cols.forEach((c, i) => {
    const x = startX + i * (colW + gapX);
    s.addText(c.tag, {
      x, y: startY, w: colW, h: 0.4,
      fontFace: F.body, fontSize: 11, color: C.primaryDark,
      align: "left", bold: true, charSpacing: 4, margin: 0
    });
    s.addText(c.sub, {
      x, y: startY + 0.40, w: colW, h: 0.4,
      fontFace: F.body, fontSize: 11, color: C.textGray,
      align: "left", italic: true, margin: 0
    });
    const bullets = [
      "Current CBA: [term]",
      "Top Rate: [$XX.XX]",
      "[Differentiator: signing bonus, RRSP match, etc.]",
      "[Differentiator: signing bonus, RRSP match, etc.]"
    ];
    s.addText(
      bullets.map((b, j) => ({ text: b, options: { bullet: true, breakLine: j < bullets.length - 1 } })),
      { x, y: startY + 0.95, w: colW, h: 2.2,
        fontFace: F.body, fontSize: 12, color: C.primaryDark, paraSpaceAfter: 6, margin: 0 }
    );
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: startY + 3.30, w: colW, h: 1.2,
      fill: { color: c.flagTint }, line: { color: c.flagColor, width: 1.5 }
    });
    s.addText(c.flagIcon + "   " + c.flag, {
      x: x + 0.20, y: startY + 3.42, w: colW - 0.40, h: 0.4,
      fontFace: F.body, fontSize: 12, color: c.flagColor, bold: true, margin: 0
    });
    s.addText(c.flagNote, {
      x: x + 0.20, y: startY + 3.78, w: colW - 0.40, h: 0.65,
      fontFace: F.body, fontSize: 11, color: C.primaryDark, margin: 0
    });
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
