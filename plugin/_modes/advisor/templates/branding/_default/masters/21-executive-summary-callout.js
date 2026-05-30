// =============================================================================
// 21-executive-summary-callout.js — EXECUTIVE SUMMARY CALLOUT
// =============================================================================
// Slide master definition + demo slide for layout 21: EXECUTIVE SUMMARY CALLOUT.
// Single high-impact summary slide for VP/exec audiences. One-sentence headline
// (large, bold, top), 3 bullet points (middle, supporting), small footer
// attribution (bottom). Used at the top of pre-reads and at the close of
// approval pitches when a single slide must carry the whole argument.
//
// Override per-org by writing branding/<org>/masters/21-executive-summary-callout.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "21_EXECUTIVE_SUMMARY_CALLOUT",
    background: { color: C.white },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 21  ·  EXECUTIVE SUMMARY CALLOUT"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  let s = pres.addSlide({ masterName: "21_EXECUTIVE_SUMMARY_CALLOUT" });

  // Eyebrow label (small, all-caps, accent)
  s.addText("EXECUTIVE SUMMARY", {
    x: 0.7, y: 1.0, w: 12.0, h: 0.35,
    fontFace: F.body, fontSize: 11, color: C.green || C.accent || "4AA447",
    align: "left", valign: "top", bold: true, charSpacing: 5, margin: 0
  });

  // Thin accent rule under eyebrow
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 1.4, w: 1.5, h: 0.04,
    fill: { color: C.green || C.accent || "4AA447" },
    line: { color: C.green || C.accent || "4AA447", width: 0 }
  });

  // One-sentence headline (large, bold, the whole argument)
  s.addText("[One-sentence headline that captures the whole argument in plain language.]", {
    x: 0.7, y: 1.7, w: 11.6, h: 1.8,
    fontFace: F.heading, fontSize: 32, color: C.text,
    align: "left", valign: "top", bold: true, margin: 0
  });

  // Three supporting bullets
  const bullets = [
    "[First supporting point — the most important evidence or rationale, one line.]",
    "[Second supporting point — the implication or tradeoff, one line.]",
    "[Third supporting point — the recommended next step or decision ask, one line.]"
  ];

  bullets.forEach((text, i) => {
    const yPos = 4.0 + (i * 0.65);
    // Bullet marker (small accent square)
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.7, y: yPos + 0.15, w: 0.12, h: 0.12,
      fill: { color: C.green || C.accent || "4AA447" },
      line: { color: C.green || C.accent || "4AA447", width: 0 }
    });
    // Bullet text
    s.addText(text, {
      x: 1.0, y: yPos, w: 11.3, h: 0.5,
      fontFace: F.body, fontSize: 15, color: C.text,
      align: "left", valign: "top", margin: 0
    });
  });

  // Footer attribution (smaller, muted)
  s.addText("[Author / function · Decision needed by: date]", {
    x: 0.7, y: 6.5, w: 12.0, h: 0.3,
    fontFace: F.body, fontSize: 10, color: C.textMuted,
    align: "left", valign: "top", italic: true, margin: 0
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
