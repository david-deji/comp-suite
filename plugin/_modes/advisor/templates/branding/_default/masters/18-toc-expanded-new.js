// =============================================================================
// 18-toc-expanded-new.js — TOC EXPANDED (NEW)
// =============================================================================
// Slide master definition + demo slide for layout 18: TOC EXPANDED (NEW).
// Override per-org by writing branding/<org>/masters/18-toc-expanded-new.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "18_TOC_EXPANDED",
    background: { color: C.offwhite },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 18  ·  TABLE OF CONTENTS — EXPANDED"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  let s = pres.addSlide({ masterName: "18_TOC_EXPANDED" });
  s.addText("Table of Contents", {
    x: 0.5, y: 0.85, w: 9.0, h: 0.7,
    fontFace: F.heading, fontSize: 32, color: C.primaryDark,
    align: "left", valign: "top", margin: 0
  });
  s.addText("Discussion structure for today — expanded for 7-9 sections", {
    x: 0.5, y: 1.55, w: 9.0, h: 0.4,
    fontFace: F.body, fontSize: 13, color: C.textGray,
    align: "left", valign: "top", italic: true, margin: 0
  });

  const items = [
    { num: "01", title: "Strategic Priorities",   sub: "Key priorities driving this review",   page: "→ slide 4" },
    { num: "02", title: "Market Context",          sub: "Economic and competitive trends",      page: "→ slide 6" },
    { num: "03", title: "[Banner 1] Market Analysis", sub: "Per-role benchmarking — [Banner 1]", page: "→ slide 9" },
    { num: "04", title: "[Banner 2] Market Analysis", sub: "Per-role benchmarking — [Banner 2]", page: "→ slide 12" },
    { num: "05", title: "[Banner 3] Market Analysis", sub: "Per-role benchmarking — [Banner 3]", page: "→ slide 15" },
    { num: "06", title: "Wage Scale Proposal",     sub: "Recommended structure",                page: "→ slide 18" },
    { num: "07", title: "Cost Analysis",           sub: "Cost of each option",                  page: "→ slide 22" },
    { num: "08", title: "Risks & Alternatives",    sub: "What we considered, what we rejected", page: "→ slide 25" },
    { num: "09", title: "Next Steps & Timelines",  sub: "Decision points and implementation",   page: "→ slide 27" }
  ];

  const colW = 4.0, rowH = 1.30, startX = 0.5, startY = 2.30, gapX = 0.20, gapY = 0.20;
  items.forEach((it, i) => {
    const c = i % 3, r = Math.floor(i / 3);
    const x = startX + c * (colW + gapX);
    const y = startY + r * (rowH + gapY);
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: colW, h: rowH,
      fill: { color: C.white }, line: { color: C.borderGray, width: 0.5 }
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 0.18, h: rowH,
      fill: { color: C.green }, line: { color: C.green, width: 0 }
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: x + 0.40, y: y + 0.20, w: 0.45, h: 0.45,
      fill: { color: C.primaryDark }, line: { color: C.primaryDark, width: 0 }
    });
    s.addText(it.num, {
      x: x + 0.40, y: y + 0.20, w: 0.45, h: 0.45,
      fontFace: F.body, fontSize: 12, color: C.white,
      align: "center", valign: "middle", bold: true, margin: 0
    });
    s.addText(it.title, {
      x: x + 1.00, y: y + 0.16, w: colW - 1.10, h: 0.38,
      fontFace: F.heading, fontSize: 14, color: C.primaryDark,
      align: "left", valign: "top", margin: 0
    });
    s.addText(it.sub, {
      x: x + 1.00, y: y + 0.55, w: colW - 1.80, h: 0.55,
      fontFace: F.body, fontSize: 10, color: C.textGray,
      align: "left", valign: "top", margin: 0
    });
    s.addText(it.page, {
      x: x + 2.50, y: y + 0.85, w: colW - 2.60, h: 0.30,
      fontFace: F.body, fontSize: 9, color: C.textMuted,
      align: "right", valign: "top", italic: true, margin: 0
    });
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
