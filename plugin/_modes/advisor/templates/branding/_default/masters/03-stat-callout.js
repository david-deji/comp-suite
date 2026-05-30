// =============================================================================
// 03-stat-callout.js — STAT CALLOUT
// =============================================================================
// Slide master definition + demo slide for layout 3: STAT CALLOUT.
// Override per-org by writing branding/<org>/masters/03-stat-callout.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "03_STAT_CALLOUT",
    background: { color: C.offwhite },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 3  ·  HEADLINE STAT CALLOUT"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  const { addTitleSubtitle } = helpers;
  let s = pres.addSlide({ masterName: "03_STAT_CALLOUT" });
  addTitleSubtitle(s, "Market Context — At a Glance",
    "Shared baseline numbers for this review — minimum wage, CPI, unemployment, budget envelope");
  const stats = [
    { val: "$XX.XX", label: "MIN. WAGE",      color: C.green,         delta: "▲ +X.X% YoY",     note: "[Province] · effective [date]" },
    { val: "+X.X%",  label: "CPI YoY",        color: C.accentTeal,          delta: "▼ −X.X pp vs LY", note: "[Geo] · Statistics Canada"    },
    { val: "X.X%",   label: "UNEMPLOYMENT",   color: C.primaryDark,    delta: "—  flat YoY",     note: "[Geo] · LFS, [month]"         },
    { val: "X.X%",   label: "BUDGET ENVELOPE",color: C.vibrantPurple, delta: "Comp Team target",note: "% of payroll · [FY]"          }
  ];
  const colW = 2.95, startX = 0.5, startY = 2.4, gapX = 0.18;
  stats.forEach((st, i) => {
    const x = startX + i * (colW + gapX);
    // Card: subtle off-white fill with thin border
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: startY, w: colW, h: 3.6,
      fill: { color: C.white }, line: { color: C.borderGray, width: 0.5 }
    });
    // Top accent strip — semantic color matching the stat
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: startY, w: colW, h: 0.10,
      fill: { color: st.color }, line: { color: st.color, width: 0 }
    });
    // Corner accent — small triangle top-right in matching color
    s.addShape(pres.shapes.RIGHT_TRIANGLE, {
      x: x + colW - 0.18, y: startY + 0.10, w: 0.18, h: 0.18,
      fill: { color: st.color }, line: { color: st.color, width: 0 },
      flipH: true
    });
    // Big number — inside card with internal padding
    s.addText(st.val, {
      x: x + 0.20, y: startY + 0.55, w: colW - 0.40, h: 1.3,
      fontFace: F.heading, fontSize: 44, color: st.color,
      align: "left", valign: "top", margin: 0
    });
    // Label band
    s.addText(st.label, {
      x: x + 0.20, y: startY + 1.95, w: colW - 0.40, h: 0.4,
      fontFace: F.body, fontSize: 12, color: C.primaryDark,
      align: "left", bold: true, charSpacing: 2, margin: 0
    });
    // Delta tag
    s.addText(st.delta, {
      x: x + 0.20, y: startY + 2.40, w: colW - 0.40, h: 0.35,
      fontFace: F.body, fontSize: 11, color: C.textGray,
      align: "left", margin: 0
    });
    // Source/context note
    s.addText(st.note, {
      x: x + 0.20, y: startY + 2.85, w: colW - 0.40, h: 0.5,
      fontFace: F.body, fontSize: 10, color: C.textMuted,
      align: "left", italic: true, margin: 0
    });
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
