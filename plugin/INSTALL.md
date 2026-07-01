# comp-suite — Installation

A Claude Code plugin for compensation work: market benchmarks, pay-equity analysis,
decision documents, and branded decks.

> **Choose your language / Choisissez votre langue :**
> **[🇫🇷 Français](#français)**  ·  **[🇬🇧 English](#english)**

There is **nothing to configure** — no token, no key. The market server signs you in with
Google (OAuth) the first time you use it. Two quick steps.

---

## Français

### Étape 1 : Installer le plugin

Dans Claude Code, collez la commande d'installation que David vous envoie. Elle ressemble à :

```
/plugin marketplace add david-deji/comp-suite
/plugin install comp-suite@comp-suite
```

Si les commandes `/comp-suite:*` n'apparaissent pas tout de suite, fermez puis rouvrez Claude Code.

### Étape 2 : Se connecter au serveur « market » (Google)

Il n'y a **aucun jeton à saisir**. Le serveur « market » utilise la connexion Google (OAuth).
La première fois que comp-suite utilise un outil « market », Claude Code vous demande d'autoriser
le serveur : connectez-vous avec le compte Google que David a ajouté.

- Si rien ne s'affiche, tapez **`/mcp`** dans Claude Code et autorisez le serveur **`market`**.

*(Optionnel : `setup.sh` (macOS / Linux) ou `setup.ps1` (Windows) affiche ce même rappel — aucun
jeton, juste un guide.)*

### Étape 3 : Vérifier que ça marche

Dans Claude Code, tapez **`/comp-suite:comp`** (le nom complet du plugin — `/comp` seul peut ne pas
fonctionner). Demandez par exemple : « *benchmark un développeur logiciel au Québec* ».

- ✅ Si des données de marché reviennent, tout fonctionne.
- ❌ Une erreur d'autorisation = le serveur « market » n'est pas encore autorisé : tapez `/mcp` et
  connectez-vous avec Google.

### En cas de problème

- **`/comp-suite:comp` introuvable** → le plugin n'est pas installé : refaites l'étape 1, puis
  redémarrez Claude Code.
- **« market » ne répond pas / non autorisé** → tapez `/mcp` et autorisez le serveur `market`
  (connexion Google).
- **Toujours rien** → vérifiez votre connexion internet ; le serveur « market » est distant
  (`https://mcp.dallaire-jette.com`), il n'y a aucun processus local à déboguer.

### Pour aller plus loin : Perplexity (optionnel)

Vous n'en avez **pas besoin** — la recherche web fonctionne déjà. Ajoutez Perplexity seulement si
vous voulez une recherche multi-sources plus riche (cela demande une clé payante).

1. Obtenez une clé : https://www.perplexity.ai/settings/api
2. Dans un terminal :
   ```
   claude mcp add perplexity -s user -e PERPLEXITY_API_KEY=VOTRE_CLE -- npx -y @perplexity-ai/mcp-server
   ```
3. Redémarrez complètement Claude Code.

---

## English

### Step 1: Install the plugin

In Claude Code, paste the install command David sends you. It looks like:

```
/plugin marketplace add david-deji/comp-suite
/plugin install comp-suite@comp-suite
```

If the `/comp-suite:*` commands don't appear right away, fully quit and reopen Claude Code.

### Step 2: Sign in to the 'market' server (Google)

There is **no token to enter**. The 'market' server uses Google sign-in (OAuth). The first time
comp-suite uses a 'market' tool, Claude Code asks you to authorize the server: sign in with the
Google account David added.

- If you're not prompted, type **`/mcp`** in Claude Code and authorize the **`market`** server.

*(Optional: `setup.sh` (macOS / Linux) or `setup.ps1` (Windows) prints this same reminder — no
token, just a guide.)*

### Step 3: Verify it works

In Claude Code, type **`/comp-suite:comp`** (the full plugin name — bare `/comp` may not work).
Then try: "*benchmark a software developer in Quebec*".

- ✅ If market data comes back, you're set.
- ❌ An authorization error = the 'market' server isn't authorized yet: type `/mcp` and sign in
  with Google.

### Troubleshooting

- **`/comp-suite:comp` not found** → the plugin isn't installed: redo Step 1, then restart Claude Code.
- **'market' not responding / unauthorized** → type `/mcp` and authorize the `market` server
  (Google sign-in).
- **Still nothing** → check your internet connection; the market server is remote
  (`https://mcp.dallaire-jette.com`) — there is no local process to debug.

### Optional power-up: Perplexity

You do **not** need this — web research already works (comp-suite uses Claude Code's built-in web
search). Add Perplexity only if you want richer, multi-source research (it needs a paid key).

1. Get a key: https://www.perplexity.ai/settings/api
2. In a terminal:
   ```
   claude mcp add perplexity -s user -e PERPLEXITY_API_KEY=YOUR_KEY -- npx -y @perplexity-ai/mcp-server
   ```
3. Fully restart Claude Code.

---

*The market server signs you in with Google (OAuth) — there is no token or password to store, and
the plugin writes no credential to your computer. There is no personal data in comp-suite.*
