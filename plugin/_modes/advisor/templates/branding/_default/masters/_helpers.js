// =============================================================================
// _helpers.js — shared layout-tag, footer, and corner-logo factories
// =============================================================================
// Each master file requires this helpers module and uses the factories to
// build its slide-master objects array. Helpers consume tokens from the loaded
// theme (palette + typography + logo paths) plus the INCLUDE_LAYOUT_TAGS flag
// from the entry point.
//
// Override discipline: do NOT copy this file into branding/<org>/masters/.
// Per-org overrides edit individual master files (e.g. masters/01-title.js)
// and continue to require this _helpers.js from _default.
// =============================================================================

function makeHelpers(C, F, logoPaths, includeLayoutTags) {
  const cornerLogo = {
    image: { path: logoPaths.small, x: 11.55, y: 0.30, w: 1.55, h: 0.42 }
  };
  const cornerLogoWhite = {
    image: { path: logoPaths.whiteSmall, x: 11.55, y: 0.30, w: 1.55, h: 0.42 }
  };

  function makeLayoutTag(text) {
    if (!includeLayoutTags) return null;
    return {
      text: {
        text,
        options: {
          x: 0.5, y: 0.32, w: 7.0, h: 0.35,
          fontFace: F.body, fontSize: 9, color: C.textMuted,
          charSpacing: 4, bold: false, margin: 0
        }
      }
    };
  }

  function makeLayoutTagWhite(text) {
    if (!includeLayoutTags) return null;
    return {
      text: {
        text,
        options: {
          x: 0.5, y: 0.32, w: 7.0, h: 0.35,
          fontFace: F.body, fontSize: 9, color: C.white,
          charSpacing: 4, opacity: 0.7, margin: 0
        }
      }
    };
  }

  function makeFooter(label) {
    return {
      text: {
        text: label || "CONFIDENTIAL  ·  [MONTH YEAR]",
        options: {
          x: 0.5, y: 7.10, w: 12.3, h: 0.30,
          fontFace: F.body, fontSize: 9, color: C.textMuted,
          align: "center", charSpacing: 3, margin: 0
        }
      }
    };
  }

  function makeFooterWhite(label) {
    return {
      text: {
        text: label || "CONFIDENTIAL  ·  [MONTH YEAR]",
        options: {
          x: 0.5, y: 7.10, w: 12.3, h: 0.30,
          fontFace: F.body, fontSize: 9, color: C.offwhite,
          align: "center", charSpacing: 3, margin: 0
        }
      }
    };
  }

  function masterObjects(...items) {
    return items.filter(Boolean);
  }

  function addTitleSubtitle(slide, title, subtitle, titleColor) {
    slide.addText(title, {
      x: 0.5, y: 0.85, w: 12.0, h: 0.7,
      fontFace: F.heading, fontSize: 28, color: titleColor || C.primaryDark,
      align: "left", valign: "top", margin: 0
    });
    if (subtitle) {
      slide.addText(subtitle, {
        x: 0.5, y: 1.55, w: 12.3, h: 0.4,
        fontFace: F.body, fontSize: 13, color: C.textGray,
        align: "left", valign: "top", italic: true, margin: 0
      });
    }
  }

  return {
    cornerLogo,
    cornerLogoWhite,
    makeLayoutTag,
    makeLayoutTagWhite,
    makeFooter,
    makeFooterWhite,
    masterObjects,
    addTitleSubtitle
  };
}

module.exports = { makeHelpers };
