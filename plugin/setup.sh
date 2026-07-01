#!/usr/bin/env bash
# comp-suite — guided setup (macOS / Linux)
# There is NO secret to set. The market server authenticates via OAuth (Google sign-in),
# handled by Claude Code — nothing is pasted, nothing is written to your shell profile.
# This script just orients you and points at the one verification step. Safe to re-run.
#
#   bash setup.sh

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
  T1="Aucun jeton à configurer. Le serveur « market » utilise la connexion Google (OAuth) —"
  T2="Claude Code s'en occupe. Rien à coller, rien à enregistrer."
  T3="Étape 1 — Ouvrez Claude Code. À la première utilisation d'un outil « market », Claude Code"
  T4="          vous demandera d'autoriser le serveur : connectez-vous avec le compte Google"
  T5="          que David a ajouté. Si rien ne s'affiche, tapez /mcp et autorisez « market »."
  T6="Étape 2 — Vérifiez : tapez /comp-suite:comp et demandez « benchmark un développeur au Québec »."
  T7="          Des données de marché doivent revenir. Sinon, retapez /mcp pour vérifier « market »."
  T8="Perplexity est OPTIONNEL — la recherche web fonctionne déjà sans clé. Voir INSTALL.md."
  T9="Terminé."
else
  echo "  Language: English"
  T1="There is no token to configure. The 'market' server uses Google sign-in (OAuth) —"
  T2="Claude Code handles it. Nothing to paste, nothing to save."
  T3="Step 1 — Open Claude Code. The first time comp-suite uses a 'market' tool, Claude Code"
  T4="         will ask you to authorize the server: sign in with the Google account David"
  T5="         added. If you are not prompted, type /mcp and authorize 'market'."
  T6="Step 2 — Verify: type /comp-suite:comp and ask 'benchmark a software developer in Quebec'."
  T7="         Market data should come back. If not, type /mcp again and check 'market'."
  T8="Perplexity is OPTIONAL — web research already works without a key. See INSTALL.md."
  T9="Done."
fi

echo
echo "  $T1"
echo "  $T2"
echo
echo "  $T3"
echo "  $T4"
echo "  $T5"
echo
echo "  $T6"
echo "  $T7"
echo
echo "  $T8"
echo
echo "  ✓ $T9"
echo
