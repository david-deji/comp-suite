// =============================================================================
// 20-narrative-section-divider.js — NARRATIVE SECTION DIVIDER
// =============================================================================
// Slide master definition + demo slide for layout 20: NARRATIVE SECTION DIVIDER.
// Lighter-weight visual section break for narrative-first decks. Differs from
// 04-section-divider.js (data-deck divider with green background + oversized
// numeral) — this one uses a pale tint background and centered narrative
// language (no section number, no decorative numeral).
//
// Override per-org by writing branding/<org>/masters/20-narrative-section-divider.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogo, makeLayoutTag, makeFooter, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "20_NARRATIVE_SECTION_DIVIDER",
    background: { color: C.offwhite || "F7F7F4" },
    objects: masterObjects(cornerLogo, makeLayoutTag("LAYOUT 20  ·  NARRATIVE SECTION DIVIDER"), makeFooter())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  let s = pres.addSlide({ masterName: "20_NARRATIVE_SECTION_DIVIDER" });

  // Thin accent rule above title
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.65, y: 2.85, w: 2.0, h: 0.04,
    fill: { color: C.green || C.accent || "4AA447" },
    line: { color: C.green || C.accent || "4AA447", width: 0 }
  });

  // Section label (small, all-caps, muted)
  s.addText("WHAT'S NEXT", {
    x: 0.5, y: 3.0, w: 12.3, h: 0.4,
    fontFace: F.body, fontSize: 12, color: C.textMuted,
    align: "center", valign: "top", charSpacing: 6, margin: 0
  });

  // Large narrative title (centered, no section number)
  s.addText("[Narrative section title — speaks to where the story goes next]", {
    x: 0.5, y: 3.45, w: 12.3, h: 1.4,
    fontFace: F.heading, fontSize: 38, color: C.text,
    align: "center", valign: "middle", bold: true, margin: 0
  });

  // Optional one-line context underneath
  s.addText("Optional one-line context that primes the audience for what's coming.", {
    x: 1.5, y: 4.95, w: 10.3, h: 0.5,
    fontFace: F.body, fontSize: 14, color: C.textMuted,
    align: "center", valign: "top", italic: true, margin: 0
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
