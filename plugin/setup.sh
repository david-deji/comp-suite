#!/usr/bin/env bash
# comp-suite — guided setup (macOS / Linux)
# Sets the one required secret (MARKET_INTEL_TOKEN) in your user shell profile so
# Claude Code picks it up at launch. Run once. Safe to re-run (it replaces, never duplicates).
#
#   bash setup.sh
#
# This script never prints your token. Hidden input + filtered write — nothing reaches the screen.

{ set +x; } 2>/dev/null      # never xtrace a script that handles a secret
set -u

bar() { printf '%s\n' "------------------------------------------------------------"; }

# ----- language selector -----------------------------------------------------
echo
bar
echo "  comp-suite — setup  /  installation"
bar
echo
echo "  [1] Français"
echo "  [2] English"
echo
printf "  Choix / Choice [1/2]: "
read -r LANG_CHOICE
LANG_CHOICE=$(printf '%s' "${LANG_CHOICE:-}" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')
case "$LANG_CHOICE" in
  2|en|eng|english|anglais) L=en ;;
  *)                        L=fr ;;   # default: Français (bare Enter, or anything else)
esac

# ----- localized strings -----------------------------------------------------
if [ "$L" = "fr" ]; then
  echo "  Langue : Français"
  T_INTRO="Ce script enregistre votre jeton d'accès aux données de marché dans votre profil."
  T_INTRO2="Claude Code le lira à son prochain démarrage. Votre saisie reste masquée."
  T_PROMPT="  Collez le jeton fourni par David (commence par tm_) puis Entrée : "
  T_EMPTY="  Aucun jeton saisi — annulé. Relancez le script quand vous l'aurez."
  T_WARN="  Ce jeton ne commence pas par « tm_ » — vérifiez que vous avez collé le bon."
  T_CONFIRM="  L'enregistrer quand même ? [o/N] : "
  T_CANCEL="  Annulé. Relancez le script avec le bon jeton."
  T_SAVED="  Enregistré dans :"
  T_FAIL="  Échec de l'écriture dans :"
  T_RESTART="  IMPORTANT — fermez complètement Claude Code, puis rouvrez-le."
  T_RESTART2="  Lancez Claude Code depuis un Terminal (tapez « claude »)."
  T_RESTART3="  ⚠ Sur macOS, l'icône du Dock NE voit PAS la variable — vous auriez une erreur 401."
  T_VERIFY="  Vérifier : dans Claude Code, tapez /comp-suite:comp et demandez un benchmark."
  T_VERIFY2="  Les outils « market » doivent répondre. Erreur 401 / non autorisé = mauvais jeton (relancez)."
  T_PPLX="  Perplexity est OPTIONNEL — la recherche web fonctionne déjà sans clé. Voir INSTALL.md."
  T_DONE="  Terminé."
else
  echo "  Language: English"
  T_INTRO="This script saves your market-data access token to your shell profile."
  T_INTRO2="Claude Code reads it the next time it starts. Your typing stays hidden."
  T_PROMPT="  Paste the token David gave you (starts with tm_) then press Enter: "
  T_EMPTY="  No token entered — cancelled. Re-run this script once you have it."
  T_WARN="  This token does not start with 'tm_' — check you pasted the right one."
  T_CONFIRM="  Save it anyway? [y/N]: "
  T_CANCEL="  Cancelled. Re-run the script with the correct token."
  T_SAVED="  Saved to:"
  T_FAIL="  Failed to write to:"
  T_RESTART="  IMPORTANT — fully quit Claude Code, then reopen it."
  T_RESTART2="  Launch Claude Code from a Terminal (type 'claude')."
  T_RESTART3="  ⚠ On macOS, the Dock icon will NOT see the variable — you'd get a 401."
  T_VERIFY="  Verify: in Claude Code type /comp-suite:comp and ask for a benchmark."
  T_VERIFY2="  The 'market' tools should answer. A 401 / unauthorized = wrong token (re-run)."
  T_PPLX="  Perplexity is OPTIONAL — web research already works without a key. See INSTALL.md."
  T_DONE="  Done."
fi

echo
echo "  $T_INTRO"
echo "  $T_INTRO2"
echo

# ----- prompt for the token (hidden) -----------------------------------------
printf '%s' "$T_PROMPT"
read -rs MARKET_INTEL_TOKEN
echo
if [ -z "${MARKET_INTEL_TOKEN:-}" ]; then
  echo "$T_EMPTY"; exit 1
fi
case "$MARKET_INTEL_TOKEN" in
  tm_*) : ;;
  *)
    echo "$T_WARN"
    printf '%s' "$T_CONFIRM"
    read -r ANS
    case "$(printf '%s' "$ANS" | tr '[:upper:]' '[:lower:]')" in
      o|oui|y|yes) : ;;
      *) echo "$T_CANCEL"; unset MARKET_INTEL_TOKEN; exit 1 ;;
    esac ;;
esac

# ----- pick the shell profile + the right export syntax ----------------------
case "${SHELL:-}" in
  *fish)
    mkdir -p "$HOME/.config/fish"
    PROFILE="$HOME/.config/fish/config.fish"; SYNTAX=fish ;;
  *zsh)
    PROFILE="$HOME/.zshrc"; SYNTAX=posix ;;
  *bash)
    if [ "$(uname)" = "Darwin" ]; then PROFILE="$HOME/.bash_profile"; else PROFILE="$HOME/.bashrc"; fi
    SYNTAX=posix ;;
  *)
    PROFILE="$HOME/.profile"; SYNTAX=posix ;;
esac
touch "$PROFILE"

# ----- persist: build the whole new file in TMP, then one atomic mv ----------
# Filter removes ONLY the lines this script writes (our marker + our exact
# assignment line, either syntax) — anchored, so unrelated user lines that merely
# mention the variable name are preserved. The token is never echoed.
TMP="$PROFILE.cs-tmp.$$"
grep -vE '^# comp-suite-setup|^[[:space:]]*export MARKET_INTEL_TOKEN=|^[[:space:]]*set -gx MARKET_INTEL_TOKEN ' \
  "$PROFILE" > "$TMP" 2>/dev/null || : > "$TMP"
if [ "$SYNTAX" = "fish" ]; then
  printf '\n# comp-suite-setup — market intelligence token\nset -gx MARKET_INTEL_TOKEN %q\n' "$MARKET_INTEL_TOKEN" >> "$TMP"
else
  printf '\n# comp-suite-setup — market intelligence token\nexport MARKET_INTEL_TOKEN=%q\n' "$MARKET_INTEL_TOKEN" >> "$TMP"
fi
unset MARKET_INTEL_TOKEN
if ! mv "$TMP" "$PROFILE"; then
  rm -f "$TMP" 2>/dev/null
  echo; echo "  ✗ $T_FAIL $PROFILE"; exit 1
fi

# ----- confirm the write landed (names only, never the value) ----------------
if ! grep -qE '^[[:space:]]*(export|set -gx) MARKET_INTEL_TOKEN' "$PROFILE"; then
  echo; echo "  ✗ $T_FAIL $PROFILE"; exit 1
fi

# ----- done ------------------------------------------------------------------
echo
echo "  ✓ $T_SAVED $PROFILE"
echo
echo "$T_RESTART"
echo "$T_RESTART2"
echo "$T_RESTART3"
echo
echo "$T_VERIFY"
echo "$T_VERIFY2"
echo
echo "$T_PPLX"
echo
echo "$T_DONE"
echo
