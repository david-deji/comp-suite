# comp-suite - guided setup (Windows / PowerShell)
# Saves the one required secret (MARKET_INTEL_TOKEN) to your Windows user environment so
# Claude Code picks it up at launch. Run once. Safe to re-run (it replaces, never duplicates).
# No administrator rights needed (User-scope variable).
#
#   Right-click this file -> "Run with PowerShell"
#   ...or in a terminal:  powershell -ExecutionPolicy Bypass -File setup.ps1
#
# This script never prints your token. Hidden input - nothing reaches the screen.

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
  $T_INTRO    = "Ce script enregistre votre jeton d'acces aux donnees de marche dans Windows."
  $T_INTRO2   = "Claude Code le lira a son prochain demarrage. Votre saisie reste masquee."
  $T_PROMPT   = "  Collez le jeton fourni par David (commence par tm_)"
  $T_EMPTY    = "  Aucun jeton saisi - annule. Relancez le script quand vous l'aurez."
  $T_WARN     = "  Ce jeton ne commence pas par 'tm_' - verifiez que vous avez colle le bon."
  $T_CONFIRM  = "  L'enregistrer quand meme ? [o/N]"
  $T_CANCEL   = "  Annule. Relancez le script avec le bon jeton."
  $T_SAVED    = "  Enregistre dans votre environnement utilisateur Windows (variable MARKET_INTEL_TOKEN)."
  $T_RESTART  = "  IMPORTANT - fermez completement Claude Code, puis rouvrez-le."
  $T_RESTART2 = "  Si vous lancez Claude Code depuis un terminal, fermez aussi cette fenetre et ouvrez-en une neuve."
  $T_VERIFY   = "  Verifier : dans Claude Code, tapez /comp-suite:comp et demandez un benchmark."
  $T_VERIFY2  = "  Les outils 'market' doivent repondre. Erreur 401 / non autorise = mauvais jeton (relancez)."
  $T_PPLX     = "  Perplexity est OPTIONNEL - la recherche web fonctionne deja sans cle. Voir INSTALL.md."
  $T_DONE     = "  Termine."
} else {
  Write-Host "  Language: English"
  $T_INTRO    = "This script saves your market-data access token to your Windows user environment."
  $T_INTRO2   = "Claude Code reads it the next time it starts. Your typing stays hidden."
  $T_PROMPT   = "  Paste the token David gave you (starts with tm_)"
  $T_EMPTY    = "  No token entered - cancelled. Re-run this script once you have it."
  $T_WARN     = "  This token does not start with 'tm_' - check you pasted the right one."
  $T_CONFIRM  = "  Save it anyway? [y/N]"
  $T_CANCEL   = "  Cancelled. Re-run the script with the correct token."
  $T_SAVED    = "  Saved to your Windows user environment (variable MARKET_INTEL_TOKEN)."
  $T_RESTART  = "  IMPORTANT - fully quit Claude Code, then reopen it."
  $T_RESTART2 = "  If you launch Claude Code from a terminal, close that window too and open a fresh one."
  $T_VERIFY   = "  Verify: in Claude Code type /comp-suite:comp and ask for a benchmark."
  $T_VERIFY2  = "  The 'market' tools should answer. A 401 / unauthorized = wrong token (re-run)."
  $T_PPLX     = "  Perplexity is OPTIONAL - web research already works without a key. See INSTALL.md."
  $T_DONE     = "  Done."
}

Write-Host ""
Write-Host "  $T_INTRO"
Write-Host "  $T_INTRO2"
Write-Host ""

# ----- prompt for the token (hidden) -----------------------------------------
$secure = Read-Host -Prompt $T_PROMPT -AsSecureString
$bstr   = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
$token  = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)

if ([string]::IsNullOrWhiteSpace($token)) {
  Write-Host ""
  Write-Host $T_EMPTY
  exit 1
}
if (-not $token.StartsWith("tm_")) {
  Write-Host $T_WARN
  $ans = (Read-Host $T_CONFIRM).Trim().ToLower()
  if ($ans -notin @("o", "oui", "y", "yes")) {
    $token = $null
    Write-Host $T_CANCEL
    exit 1
  }
}

# ----- persist (User scope = no admin, survives restart) ---------------------
[Environment]::SetEnvironmentVariable("MARKET_INTEL_TOKEN", $token, "User")
$token = $null

# ----- confirm it landed (name only, never the value) ------------------------
if ([string]::IsNullOrEmpty([Environment]::GetEnvironmentVariable("MARKET_INTEL_TOKEN", "User"))) {
  Write-Host ""
  Write-Host "  [x] Could not save the variable. Try again, or ask David."
  Read-Host "  Press Enter to close" | Out-Null
  exit 1
}

# ----- done ------------------------------------------------------------------
Write-Host ""
Write-Host "  [ok] $T_SAVED"
Write-Host ""
Write-Host $T_RESTART
Write-Host $T_RESTART2
Write-Host ""
Write-Host $T_VERIFY
Write-Host $T_VERIFY2
Write-Host ""
Write-Host $T_PPLX
Write-Host ""
Write-Host $T_DONE
Write-Host ""
Read-Host "  Press Enter to close" | Out-Null
