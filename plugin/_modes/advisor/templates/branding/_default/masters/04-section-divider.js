// =============================================================================
// 04-section-divider.js — SECTION DIVIDER
// =============================================================================
// Slide master definition + demo slide for layout 4: SECTION DIVIDER.
// Override per-org by writing branding/<org>/masters/04-section-divider.js;
// missing master files inherit from _default automatically.
// =============================================================================

function defineMaster({ pres, C, F, helpers, logoPaths }) {
  const { cornerLogoWhite, makeLayoutTagWhite, makeFooterWhite, masterObjects } = helpers;

  pres.defineSlideMaster({
    title: "04_SECTION_DIVIDER",
    background: { color: C.green },
    objects: masterObjects(cornerLogoWhite, makeLayoutTagWhite("LAYOUT 4  ·  SECTION DIVIDER"), makeFooterWhite())
  });
}

function addDemoSlide({ pres, C, F, helpers, logoPaths }) {
  let s = pres.addSlide({ masterName: "04_SECTION_DIVIDER" });
  // Decorative: oversized section numeral as tonal variation on green background
  // Using a slightly lighter green (5DAE5A vs 4AA447) fakes a translucent effect
  // without depending on opacity (unreliable for text in pptxgenjs).
  // Sized and positioned to bleed off bottom-right edge without clobbering logo.
  s.addText("0X", {
    x: 8.5, y: 3.0, w: 4.5, h: 4.0,
    fontFace: F.heading, fontSize: 280, color: "5DAE5A",
    align: "right", valign: "middle", bold: true, margin: 0
  });
  s.addText("SECTION 0X", {
    x: 0.7, y: 2.0, w: 5, h: 0.4,
    fontFace: F.body, fontSize: 14, color: C.white,
    align: "left", valign: "top", charSpacing: 3, margin: 0
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 2.45, w: 1.5, h: 0.02,
    fill: { color: C.white }, line: { color: C.white, width: 0 }
  });
  s.addText("[Section Title]", {
    x: 0.7, y: 2.65, w: 11.5, h: 1.2,
    fontFace: F.heading, fontSize: 44, color: C.white,
    align: "left", valign: "top", margin: 0
  });
  s.addText("Optional one-line description of what this section covers", {
    x: 0.7, y: 4.05, w: 11.5, h: 0.6,
    fontFace: F.body, fontSize: 14, color: C.white,
    align: "left", valign: "top", italic: true, margin: 0
  });
  s.addText("0X / 06", {
    x: 11.0, y: 6.55, w: 1.8, h: 0.4,
    fontFace: F.body, fontSize: 11, color: C.white,
    align: "right", valign: "top", opacity: 0.7, charSpacing: 2, margin: 0
  });
}

function register(deps) {
  defineMaster(deps);
  addDemoSlide(deps);
}

module.exports = { register, defineMaster, addDemoSlide };
