// =============================================================================
// 16-risks-alternatives-new.js — RISKS & ALTERNATIVES (NEW)
// =============================================================================
// Slide master definition + demo slide for layout 16: RISKS & ALTERNATIVES (NEW).
// Override per-org by writing branding/<org>/masters/16-risks-alternatives-new.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "16_RISKS_ALTERNATIVES",
    background: { color: C.offwhite },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 16  ·  RISKS & ALTERNATIVES"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  const { addTitleSubtitle } = helpers;
  let s = pres.addSlide({ masterName: "16_RISKS_ALTERNATIVES" });
  addTitleSubtitle(s, "Risks & Alternatives Considered",
    "Options we evaluated and chose not to pursue, with mitigation for residual risk");

  const headers = ["CONSIDERED OPTION", "RISK / WHY REJECTED", "MITIGATION"];
  const rows = [
    ["[Aggressive top-rate move +X%]",
     "[Triggers compression in middle steps; cost overrun vs. envelope]",
     "[Phased over 2 years; lump sum to mid-step teammates in Y1]"],
    ["[Match top competitor exactly]",
     "[Sets a ceiling that's hard to maintain in the next bargaining cycle]",
     "[Position at P60-65 instead — competitive but defensible long-term]"],
    ["[Status quo / no change]",
     "[Below-market positioning worsens; recruitment risk in [region]]",
     "[Not viable; framed as the do-nothing baseline against options]"],
    ["[Lump sum only — no scale change]",
     "[One-time fix; doesn't address structural gap; signals weak commitment]",
     "[Combined approach: scale lift + lump sum to top-tier]"]
  ];

  const tableX = 0.5, tableY = 2.2;
  const colWs = [3.5, 4.4, 4.4];
  const headerH = 0.50;
  const rowH = 0.85;

  let xCursor = tableX;
  headers.forEach((h, i) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: xCursor, y: tableY, w: colWs[i], h: headerH,
      fill: { color: C.primaryDark }, line: { color: C.primaryDark, width: 0 }
    });
    s.addText(h, {
      x: xCursor + 0.15, y: tableY, w: colWs[i] - 0.30, h: headerH,
      fontFace: F.body, fontSize: 10, color: C.white,
      align: "left", valign: "middle", bold: true, charSpacing: 3, margin: 0
    });
    xCursor += colWs[i];
  });

  rows.forEach((row, ri) => {
    const y = tableY + headerH + ri * rowH + (ri * 0.06);  // Add gap between rows
    let x = tableX;
    row.forEach((cell, ci) => {
      const isFirst = ci === 0;
      const isMiddle = ci === 1;
      // Card cell with internal padding
      s.addShape(pres.shapes.RECTANGLE, {
        x, y, w: colWs[ci], h: rowH,
        fill: { color: ri % 2 ? C.white : C.purpleTint },
        line: { color: C.borderGray, width: 0.5 }
      });
      // First column: leave room for the red accent
      const cellTextX = isFirst ? x + 0.25 : x + 0.15;
      const cellTextW = isFirst ? colWs[ci] - 0.40 : colWs[ci] - 0.30;
      s.addText(cell, {
        x: cellTextX, y, w: cellTextW, h: rowH,
        fontFace: F.body,
        fontSize: 11,
        color: isMiddle ? C.red : C.primaryDark,
        bold: isFirst,
        align: "left", valign: "middle", margin: 0
      });
      x += colWs[ci];
    });
    // Red left-edge accent — drawn AFTER cells so it sits on top
    s.addShape(pres.shapes.RECTANGLE, {
      x: tableX, y, w: 0.10, h: rowH,
      fill: { color: C.red }, line: { color: C.red, width: 0 }
    });
  });

  s.addText("These options were considered during Phase 4-5 deliberation. See appendix for full Council deliberation notes.", {
    x: 0.5, y: 6.55, w: 12.3, h: 0.3,
    fontFace: F.body, fontSize: 9, color: C.textMuted, italic: true, margin: 0
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
