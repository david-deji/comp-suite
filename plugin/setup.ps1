# comp-suite - guided setup (Windows / PowerShell)
# There is NO secret to set. The market server authenticates via OAuth (Google sign-in),
# handled by Claude Code - nothing is pasted, nothing is written to your environment.
# This script just orients you and points at the one verification step. Safe to re-run.
#
#   Right-click this file -> "Run with PowerShell"
#   ...or in a terminal:  powershell -ExecutionPolicy Bypass -File setup.ps1

try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
$ErrorActionPreference = "Stop"

function Bar { Write-Host "------------------------------------------------------------" }

# ----- language selector -----------------------------------------------------
Write-Host ""
Bar
Write-Host "  comp-suite - setup  /  installation"
Bar
Write-Host ""
Write-Host "  [1] Francais"
Write-Host "  [2] English"
Write-Host ""
$LangChoice = (Read-Host "  Choix / Choice [1/2]").Trim().ToLower()
if ($LangChoice -in @("2", "en", "eng", "english", "anglais")) { $L = "en" } else { $L = "fr" }

# ----- localized strings (ASCII-safe for Windows PowerShell 5.1) -------------
if ($L -eq "fr") {
  Write-Host "  Langue : Francais"
  $T1 = "Aucun jeton a configurer. Le serveur 'market' utilise la connexion Google (OAuth) -"
  $T2 = "Claude Code s'en occupe. Rien a coller, rien a enregistrer."
  $T3 = "Etape 1 - Ouvrez Claude Code. A la premiere utilisation d'un outil 'market', Claude Code"
  $T4 = "         vous demandera d'autoriser le serveur : connectez-vous avec le compte Google"
  $T5 = "         que David a ajoute. Si rien ne s'affiche, tapez /mcp et autorisez 'market'."
  $T6 = "Etape 2 - Verifiez : tapez /comp-suite:comp et demandez 'benchmark un developpeur au Quebec'."
  $T7 = "         Des donnees de marche doivent revenir. Sinon, retapez /mcp pour verifier 'market'."
  $T8 = "Perplexity est OPTIONNEL - la recherche web fonctionne deja sans cle. Voir INSTALL.md."
  $T9 = "Termine."
} else {
  Write-Host "  Language: English"
  $T1 = "There is no token to configure. The 'market' server uses Google sign-in (OAuth) -"
  $T2 = "Claude Code handles it. Nothing to paste, nothing to save."
  $T3 = "Step 1 - Open Claude Code. The first time comp-suite uses a 'market' tool, Claude Code"
  $T4 = "         will ask you to authorize the server: sign in with the Google account David"
  $T5 = "         added. If you are not prompted, type /mcp and authorize 'market'."
  $T6 = "Step 2 - Verify: type /comp-suite:comp and ask 'benchmark a software developer in Quebec'."
  $T7 = "         Market data should come back. If not, type /mcp again and check 'market'."
  $T8 = "Perplexity is OPTIONAL - web research already works without a key. See INSTALL.md."
  $T9 = "Done."
}

Write-Host ""
Write-Host "  $T1"
Write-Host "  $T2"
Write-Host ""
Write-Host "  $T3"
Write-Host "  $T4"
Write-Host "  $T5"
Write-Host ""
Write-Host "  $T6"
Write-Host "  $T7"
Write-Host ""
Write-Host "  $T8"
Write-Host ""
Write-Host "  [ok] $T9"
Write-Host ""
Read-Host "  Press Enter to close" | Out-Null
