# Setup Guide — GitHub, Clone, Test, Push

How to connect this project to GitHub, clone it on a new machine, test the skills, and push changes back.

Repository: [hkstechlabs/mm-claude-skills](https://github.com/hkstechlabs/mm-claude-skills)

---

## 1. Reconnect GitHub to Claude Code

Claude Code uses the GitHub CLI (`gh`) for any GitHub action (creating PRs, reading issues, pushing). If auth has dropped, reconnect it.

### Check current status

```bash
gh auth status
```

Expected output: `✓ Logged in to github.com account <your-username>`

### If not logged in

```bash
gh auth login
```

Follow the prompts:
1. **GitHub.com** (not Enterprise)
2. **HTTPS** (protocol)
3. **Yes** — authenticate Git with your GitHub credentials
4. **Login with a web browser** (easier) or paste a token
5. Copy the one-time code shown, press Enter, paste it in the browser

After login, verify:

```bash
gh auth status
gh repo view hkstechlabs/mm-claude-skills
```

### If git is asking for a password every push

Your credential helper isn't set up. Fix:

```bash
gh auth setup-git
```

This makes git use your `gh` token automatically.

---

## 2. Clone the repository

### First time on a new machine

```bash
cd ~/Documents
gh repo clone hkstechlabs/mm-claude-skills
cd mm-claude-skills
```

Or with plain git:

```bash
git clone https://github.com/hkstechlabs/mm-claude-skills.git
cd mm-claude-skills
```

### Add your `.env` credentials

`.env` is **not** in the repo (intentionally — it holds API tokens). Create it:

```bash
cat > .env <<'EOF'
OZMOBILES_SHOPIFY_TOKEN=shpat_xxx
OZMOBILES_SHOPIFY_STORE=ozmobiles-com-au.myshopify.com
FRANKMOBILES_SHOPIFY_TOKEN=shpat_xxx
FRANKMOBILES_SHOPIFY_STORE=frank-mobile.myshopify.com
SHOPIFY_API_VERSION=2025-01
BUBBLE_CSRF_KEY=<your-bubble-csrf-key>
BUBBLE_API_BASE=https://portal.mobilemonster.com.au/version-live/api/1.1
EOF
chmod 600 .env
```

Grab the real token values from your password manager or the source machine's `.env`.

### Verify the folder structure

```bash
ls -la .claude/skills/
```

Expected: `bubble-analytics/` and `shopify-analytics/` folders, each with `SKILL.md`.

---

## 3. Test the skills

Open Claude Code in this directory and run these sanity checks.

### Shopify analytics smoke test

```
/shopify-analytics
```

Then ask: **"How many sales orders today for OzMobiles?"**

Expected: Claude loads the skill, asks which store (or answers directly), fetches live data, and returns a count.

### Bubble analytics smoke test

```
/bubble-analytics
```

Then ask: **"Working price for iPhone 15 Pro Max 256GB"**

Expected: Claude fetches the PPT, returns the buyback price for the Working grade.

### Chart style helper (optional, quick)

```bash
python3 -c "
import sys; sys.path.insert(0, '.claude/skills/shopify-analytics')
from chart_style import apply_style, PALETTE
apply_style()
print('OK — palette keys:', list(PALETTE.keys()))
"
```

Expected: prints the 9 palette keys without errors.

### Disambiguation test

Ask Claude: **"total orders today"**

Expected: Claude asks whether you mean sales orders (Shopify) or purchase orders (Bubble) — it should **not** guess.

---

## 4. Push changes to the repo

### Daily workflow

```bash
# See what changed
git status

# Review the diff
git diff

# Stage specific files (avoid `git add .` — protects against committing .env by accident)
git add .claude/skills/shopify-analytics/SKILL.md
git add CLAUDE.md

# Commit with a clear message
git commit -m "Tighten refund-date rule in shopify-analytics"

# Push
git push
```

### Never commit

- `.env` — API tokens. Already in `.gitignore` but double-check with `git status` before pushing.
- `.claude/settings.local.json` — local-machine settings. Also gitignored.
- `__pycache__/` — Python bytecode. Gitignored.

### Verify `.env` is safe before pushing

```bash
git check-ignore -v .env
# Should print: .gitignore:2:.env	.env
```

If that command prints nothing, `.env` is **not** ignored — stop and fix `.gitignore` before committing.

### Create a pull request (for bigger changes)

```bash
git checkout -b feature/my-change
# ... make changes ...
git add <files> && git commit -m "..."
git push -u origin feature/my-change
gh pr create --title "Short title" --body "What and why"
```

---

## 5. Keep the local clone in sync

If you edit on one machine and want the changes on another:

```bash
# On the other machine:
cd ~/Documents/mm-claude-skills
git pull
```

### Sidecar mirror on this machine

A second copy lives at `/Users/macbook162019/Documents/MM Claude-Skills 1/` and is kept identical by a Stop hook. **Never edit the mirror directly** — edit this repo, and the mirror auto-syncs.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `fatal: not a git repository` | `cd` into the project folder before running git commands |
| `Permission denied (publickey)` on push | Run `gh auth setup-git` to use HTTPS + gh token |
| `.env` shows up in `git status` | It's not gitignored — check `.gitignore` contains a plain line `.env` |
| `gh: command not found` | Install: `brew install gh` (macOS) |
| Claude can't find the skill | You're not in the project directory, or `.claude/skills/<name>/SKILL.md` is missing |
| "Authentication failed" on Shopify/Bubble | Check `.env` values — tokens may have been rotated |
