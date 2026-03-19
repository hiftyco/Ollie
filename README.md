# 🟠 OLLIE — Autonomous Bitcoin Intelligence

> A self-learning Bitcoin intelligence that runs 24/7 on GitHub Pages.  
> No APIs keys. No servers. No paid services. Fully autonomous.

## How It Works

```
Every 24 hours at 00:30 UTC (with a midday refresh at 12:30 UTC):
  GitHub Actions triggers → learn.py runs → fetches from 8 free sources →
  synthesizes insights → commits data/knowledge.json → GitHub Pages serves it
```

Ollie learns from:
- **CoinGecko** — Price, market cap, volume, ATH, supply
- **Alternative.me** — Fear & Greed Index
- **Blockchain.info** — Block height, hash rate, difficulty
- **Mempool.space** — Fees, unconfirmed transactions
- **Bitcoin Magazine RSS** — News headlines
- **CoinDesk RSS** — News headlines
- **Decrypt RSS** — News headlines
- **Reddit r/Bitcoin** — Community top posts

---

## Setup (5 minutes)

### 1. Fork or create the repository

Go to [github.com](https://github.com) → **New repository** → name it `ollie` or anything you like.

Upload all these files maintaining the folder structure:
```
ollie/
├── index.html
├── learn.py
├── README.md
├── data/
│   └── knowledge.json
└── .github/
    └── workflows/
        └── daily-learn.yml
```

### 2. Enable GitHub Pages

1. Go to your repo → **Settings** → **Pages**
2. Under **Source**, select **Deploy from a branch**
3. Branch: `main` (or `master`) · Folder: `/ (root)`
4. Click **Save**

Your site will be live at: `https://YOUR-USERNAME.github.io/REPO-NAME/`

### 3. Enable GitHub Actions

1. Go to your repo → **Actions** tab
2. You should see **"Ollie — Daily Bitcoin Learning"** workflow
3. Click **"Enable workflow"** if prompted
4. To run it immediately: click **"Run workflow"** → **"Run workflow"** (green button)

### 4. That's it!

- Ollie will run automatically every day at **00:30 UTC**
- Each run takes ~2 minutes
- The site updates immediately after each run
- On **GitHub Free** plan: Actions are **unlimited for public repos**

---

## File Structure

| File | Purpose |
|------|---------|
| `index.html` | Ollie's website — reads `data/knowledge.json` |
| `learn.py` | The learning engine — fetches data from free APIs |
| `data/knowledge.json` | Ollie's brain — grows every day |
| `.github/workflows/daily-learn.yml` | GitHub Actions cron job |

---

## What Grows Over Time

After 30 days, Ollie will have:
- 30 days of price history → price chart appears
- 30 days of Fear & Greed history
- Accumulated knowledge nodes from all trending topics
- 30 evolution log entries with timestamps and snapshots

After 365 days:
- Full year of Bitcoin price memory
- Ranked knowledge base of most-discussed topics
- Complete evolution history

---

## Manually Trigger a Learning Cycle

1. GitHub repo → **Actions** → **Ollie — Daily Bitcoin Learning**
2. **Run workflow** → **Run workflow**

---

## Customise Ollie

Open `learn.py` to add more data sources:
- Add more RSS feeds in the `get_news()` function
- Adjust `NEXT_HALVING_BLOCK` when halving occurs
- Add on-chain analytics APIs (Glassnode free tier, etc.)

---

## Requirements

- GitHub account (free)
- Public repository (Actions are free on public repos)
- Zero ongoing costs

---

*Ollie never stops learning. Every block is a heartbeat.*
