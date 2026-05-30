// =============================================================================
// 14-methodology-new.js — METHODOLOGY (NEW)
// =============================================================================
// Slide master definition + demo slide for layout 14: METHODOLOGY (NEW).
// Override per-org by writing branding/<org>/masters/14-methodology-new.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "14_METHODOLOGY",
    background: { color: C.offwhite },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 14  ·  METHODOLOGY"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  const { addTitleSubtitle } = helpers;
  let s = pres.addSlide({ masterName: "14_METHODOLOGY" });
  addTitleSubtitle(s, "Methodology",
    "How we built this analysis — what's in, what's out, and what we relied on");
  const cols = [
    {
      header: "SOURCES",
      items: [
        "Statistics Canada Table 14-10-0064-01 — wage rates by NOC, [year]",
        "[Org] HRIS data extract — [date], [N] active teammates",
        "Indeed postings — [N] postings, last [N] months",
        "Verified CBA scales — [list of competitors / unions]",
        "[Internal stakeholder interviews / survey panel]"
      ]
    },
    {
      header: "INCLUSIONS",
      items: [
        "All scales in scope: [CODE 1], [CODE 2], [CODE 3]",
        "Hourly teammates only ([scope: full-time / part-time / both])",
        "Geo: [Province / Region]",
        "Effective date: [DATE]",
        "Fully-loaded cost (base + payroll burden + [other])"
      ]
    },
    {
      header: "EXCLUSIONS",
      items: [
        "Salaried / management roles — separate review",
        "Temporary or seasonal classifications",
        "Non-[scope] provinces / regions",
        "One-time bonuses outside the [program] envelope",
        "Benefits and equity programs (separate scope)"
      ]
    }
  ];
  const colW = 4.0, startX = 0.5, startY = 2.2, gapX = 0.20;
  const cardH = 4.20;
  cols.forEach((col, i) => {
    const x = startX + i * (colW + gapX);
    // Full card with subtle border + tinted body
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: startY, w: colW, h: cardH,
      fill: { color: C.purpleTint }, line: { color: C.borderGray, width: 0.5 }
    });
    // Header band — deep purple
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: startY, w: colW, h: 0.50,
      fill: { color: C.primaryDark }, line: { color: C.primaryDark, width: 0 }
    });
    // Corner accent — top-right of header in teal
    s.addShape(pres.shapes.RIGHT_TRIANGLE, {
      x: x + colW - 0.30, y: startY, w: 0.30, h: 0.30,
      fill: { color: C.accentTeal }, line: { color: C.accentTeal, width: 0 },
      flipH: true
    });
    s.addText(col.header, {
      x: x + 0.20, y: startY, w: colW - 0.40, h: 0.50,
      fontFace: F.body, fontSize: 11, color: C.white,
      align: "left", valign: "middle", bold: true, charSpacing: 4, margin: 0
    });
    // Bullet content with internal padding
    s.addText(
      col.items.map((item, j) => ({
        text: item,
        options: { bullet: true, breakLine: j < col.items.length - 1 }
      })),
      { x: x + 0.20, y: startY + 0.65, w: colW - 0.40, h: cardH - 0.80,
        fontFace: F.body, fontSize: 11, color: C.primaryDark,
        align: "left", valign: "top", paraSpaceAfter: 6, margin: 0 }
    );
  });

  s.addText("Last updated: [DATE] · Author: [Name]", {
    x: 0.5, y: 6.55, w: 12.3, h: 0.3,
    fontFace: F.body, fontSize: 10, color: C.textMuted,
    align: "right", italic: true, margin: 0
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
