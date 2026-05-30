// =============================================================================
// 02-toc.js — TOC
// =============================================================================
// Slide master definition + demo slide for layout 2: TOC.
// Override per-org by writing branding/<org>/masters/02-toc.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "02_TOC",
    background: { color: C.offwhite },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 2  ·  TABLE OF CONTENTS"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  let s = pres.addSlide({ masterName: "02_TOC" });
  s.addText("Table of Contents", {
    x: 0.5, y: 0.85, w: 9.0, h: 0.7,
    fontFace: F.heading, fontSize: 32, color: C.primaryDark,
    align: "left", valign: "top", margin: 0
  });
  s.addText("Discussion structure for today", {
    x: 0.5, y: 1.55, w: 9.0, h: 0.4,
    fontFace: F.body, fontSize: 13, color: C.textGray,
    align: "left", valign: "top", italic: true, margin: 0
  });
  const items = [
    { num: "01", title: "Strategic Priorities",  sub: "Key priorities driving this review",   page: "→ slide 4"  },
    { num: "02", title: "Market Context",         sub: "External economic and competitive trends", page: "→ slide 6"  },
    { num: "03", title: "Market Analysis",        sub: "Per-role benchmarking summary",        page: "→ slide 9"  },
    { num: "04", title: "Wage Scale Proposal",    sub: "Recommended structure",                page: "→ slide 14" },
    { num: "05", title: "Cost Analysis",          sub: "Cost of each option, by employee group", page: "→ slide 18" },
    { num: "06", title: "Next Steps & Timelines", sub: "Decision points and implementation",   page: "→ slide 22" }
  ];
  // Card grid vertically centered between subtitle (~y=2.0) and footer (y=7.10)
  // Total grid height: 2 rows × 1.1" + 1 gap × 0.30" = 2.50"
  // Available band: 2.0 → 7.10 = 5.10". Centering: startY = 2.0 + (5.10 - 2.50) / 2 = 3.30
  const colW = 4.0, rowH = 1.1, startX = 0.5, startY = 3.50, gapX = 0.20, gapY = 0.30;
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
    // Corner accent triangle — top-right, teal
    s.addShape(pres.shapes.RIGHT_TRIANGLE, {
      x: x + colW - 0.25, y, w: 0.25, h: 0.25,
      fill: { color: C.accentTeal }, line: { color: C.accentTeal, width: 0 },
      flipH: true
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
      fontFace: F.heading, fontSize: 15, color: C.primaryDark,
      align: "left", valign: "top", margin: 0
    });
    s.addText(it.sub, {
      x: x + 1.00, y: y + 0.55, w: colW - 1.80, h: 0.35,
      fontFace: F.body, fontSize: 10, color: C.textGray,
      align: "left", valign: "top", margin: 0
    });
    s.addText(it.page, {
      x: x + 2.50, y: y + 0.55, w: colW - 2.60, h: 0.35,
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
