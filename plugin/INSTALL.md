# comp-suite — Installation

A Claude Code plugin for compensation work: market benchmarks, pay-equity analysis,
decision documents, and branded decks.

> **Choose your language / Choisissez votre langue :**
> **[🇫🇷 Français](#français)**  ·  **[🇬🇧 English](#english)**

You set **one** thing: a market-data token that David gives you. Web research works on its own.
It's four quick steps — about five minutes.

---

## Français

### Étape 1 : Installer le plugin

Dans Claude Code, collez la commande d'installation que David vous envoie. Elle ressemble à :

```
/plugin marketplace add david-deji/comp-suite
/plugin install comp-suite@comp-suite
```

### Étape 2 : Lancer le script de configuration

Le plugin contient un petit script qui enregistre votre jeton. Choisissez votre système :

**Windows**
- Faites un clic droit sur `setup.ps1` → **« Exécuter avec PowerShell »**. C'est le plus simple.
- S'il ne se lance pas : ouvrez le dossier du plugin, faites **Maj + clic droit** dans le dossier →
  **« Ouvrir la fenêtre PowerShell ici »**, puis tapez :
  ```
  powershell -ExecutionPolicy Bypass -File setup.ps1
  ```

**macOS / Linux**
- Ouvrez le **Terminal** dans le dossier du plugin et tapez :
  ```
  bash setup.sh
  ```

Le script demande votre langue, puis votre jeton (la saisie reste **masquée** — c'est normal de ne
rien voir s'afficher), puis l'enregistre.

### Étape 3 : Redémarrer Claude Code

**Fermez complètement Claude Code, puis rouvrez-le.** Les variables ne sont lues qu'au démarrage.

- **Windows** : fermez aussi le terminal d'où vous avez lancé le script, le cas échéant.
- **macOS** : ⚠ **lancer Claude Code depuis l'icône (Dock/Applications) ne fonctionne pas** — l'app
  n'y voit pas la variable et vous auriez une erreur 401. Lancez-le depuis le **Terminal** en tapant
  `claude`. (Si vous n'utilisez que le Terminal, ignorez ceci.)

### Étape 4 : Vérifier que ça marche

Dans Claude Code, tapez **`/comp-suite:comp`** (le nom complet du plugin — `/comp` seul peut ne pas
fonctionner). Demandez par exemple : « *benchmark un développeur logiciel au Québec* ».

- ✅ Si des données de marché reviennent, tout fonctionne.
- ❌ Une erreur **401 / non autorisé** = le jeton est incorrect. Relancez le script de l'étape 2.

### En cas de problème

- **`/comp-suite:comp` introuvable** → le plugin n'est pas installé : refaites l'étape 1.
- **401 / non autorisé** → mauvais jeton ou jeton non enregistré : relancez `setup`.
- **Rien ne change** → vous n'avez pas redémarré Claude Code (étape 3), ou (macOS) vous l'avez lancé
  depuis le Dock au lieu du Terminal.

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

### Step 2: Run the setup script

The plugin includes a small script that saves your token. Pick your system:

**Windows**
- Right-click `setup.ps1` → **"Run with PowerShell"**. This is the easiest way.
- If it won't start: open the plugin folder, **Shift + right-click** inside it →
  **"Open PowerShell window here"**, then type:
  ```
  powershell -ExecutionPolicy Bypass -File setup.ps1
  ```

**macOS / Linux**
- Open the **Terminal** in the plugin folder and type:
  ```
  bash setup.sh
  ```

The script asks for your language, then your token (input stays **hidden** — it's normal to see
nothing as you type), then saves it.

### Step 3: Restart Claude Code

**Fully quit Claude Code, then reopen it.** Variables are only read at launch.

- **Windows**: also close the terminal you ran the script from, if any.
- **macOS**: ⚠ **launching Claude Code from its icon (Dock/Applications) will not work** — the app
  won't see the variable and you'll get a 401. Start it from the **Terminal** by typing `claude`.
  (If you only use the Terminal/CLI, ignore this.)

### Step 4: Verify it works

In Claude Code, type **`/comp-suite:comp`** (the full plugin name — bare `/comp` may not work).
Then try: "*benchmark a software developer in Quebec*".

- ✅ If market data comes back, you're set.
- ❌ A **401 / unauthorized** error = the token is wrong. Re-run the Step 2 script.

### Troubleshooting

- **`/comp-suite:comp` not found** → the plugin isn't installed: redo Step 1.
- **401 / unauthorized** → wrong token or token not saved: re-run `setup`.
- **Nothing changed** → you didn't restart Claude Code (Step 3), or (macOS) you launched it from the
  Dock instead of the Terminal.

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

*Your token lives only in your own computer's user environment — it is never written into the
plugin or sent anywhere except the market server you query. There is no personal data in
comp-suite.*
