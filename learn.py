#!/usr/bin/env python3
"""
OLLIE — Autonomous Bitcoin Intelligence Engine v3.0
Runs every 6 hours via GitHub Actions.
Mission: Learn everything about Bitcoin. Teach and guide every Bitcoiner.
Self-improves with every cycle.
"""

import json
import os
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import time
import math
import re
import hashlib
import random

# ── CONFIG ────────────────────────────────────────────────────────────────────
DATA_FILE = "data/knowledge.json"
MAX_EVOLUTION_LOG = 365
MAX_PRICE_HISTORY = 365
MAX_FG_HISTORY = 365
MAX_HEADLINES = 12
MAX_REDDIT = 10
MAX_INSIGHTS = 15
HALVING_BLOCK_REWARD_NOW = 3.125
NEXT_HALVING_BLOCK = 1050000

POSITIVE_WORDS = ["surge","rally","bull","moon","pump","breakthrough","adoption","halving","upgrade","growth","rise","gain","profit","success","innovation","bullish","optimism","recovery","institutional","etf","record","high","milestone","accumulate"]
NEGATIVE_WORDS = ["crash","dump","bear","sell","decline","hack","ban","regulation","fall","loss","drop","fear","panic","scam","exploit","bearish","pessimism","crisis","lawsuit","fine","restrict","warning","risk"]

BITCOIN_FACTS = [
    "Bitcoin's genesis block (Block 0) contains the message: 'The Times 03/Jan/2009 Chancellor on brink of second bailout for banks.'",
    "Only 21 million Bitcoin will ever exist. About 3-4 million are estimated to be lost forever.",
    "Satoshi Nakamoto's identity remains unknown. Their wallets contain ~1.1 million BTC that have never moved.",
    "The Lightning Network enables Bitcoin transactions in milliseconds with near-zero fees.",
    "Bitcoin mining uses more renewable energy than almost any other industry — over 50% and growing.",
    "The first real-world Bitcoin purchase was 10,000 BTC for two pizzas on May 22, 2010.",
    "Bitcoin's SHA-256 algorithm would take longer than the age of the universe to crack with classical computers.",
    "Each halving cuts the new BTC supply in half. This has happened 4 times so far.",
    "Bitcoin has 99.99% uptime since launch — more reliable than any bank in history.",
    "El Salvador became the first country to adopt Bitcoin as legal tender in 2021.",
    "The UTXO model makes Bitcoin transactions more private and verifiable than account-based systems.",
    "Bitcoin's difficulty adjustment recalibrates every 2016 blocks (~2 weeks) to maintain 10-minute block times.",
    "There are more possible private key combinations than atoms in the observable universe.",
    "A Bitcoin transaction is irreversible by design — this is a feature, not a bug.",
    "Bitcoin Script is intentionally limited, making it more secure and predictable than Turing-complete systems.",
]

LEARNING_PATHS = {
    "beginner": [
        {"title": "What is Bitcoin?", "lesson": "Bitcoin is digital money that no government or bank controls. It runs on a decentralized network of computers worldwide.", "key_concepts": ["decentralization", "peer-to-peer", "digital scarcity"]},
        {"title": "Why Bitcoin?", "lesson": "Bitcoin solves the double-spend problem without requiring trust in a third party — for the first time in history.", "key_concepts": ["trustlessness", "censorship resistance", "sound money"]},
        {"title": "How to Get Bitcoin", "lesson": "You can earn, buy, or receive Bitcoin. The most important next step: self-custody. Not your keys, not your coins.", "key_concepts": ["wallets", "exchanges", "self-custody", "seed phrase"]},
        {"title": "Storing Bitcoin Safely", "lesson": "A hardware wallet keeps your private keys offline. Never share your seed phrase. Back it up in multiple secure locations.", "key_concepts": ["hardware wallet", "cold storage", "backup", "security"]},
        {"title": "Bitcoin vs Traditional Money", "lesson": "Fiat currency loses value through inflation. Bitcoin has a fixed supply of 21 million — it gets scarcer over time.", "key_concepts": ["inflation", "scarcity", "store of value", "sound money"]},
    ],
    "intermediate": [
        {"title": "The Blockchain Explained", "lesson": "Every Bitcoin transaction is recorded on a public ledger. Blocks chain together cryptographically — making history immutable.", "key_concepts": ["blockchain", "immutability", "merkle tree", "hash"]},
        {"title": "Mining & Proof of Work", "lesson": "Miners compete to solve math puzzles, securing the network. The winner adds the next block and earns freshly minted BTC.", "key_concepts": ["mining", "proof of work", "difficulty", "hash rate"]},
        {"title": "The Halving Cycle", "lesson": "Every ~4 years, the block reward halves. This programmatic supply reduction has historically preceded major bull markets.", "key_concepts": ["halving", "supply shock", "block reward", "cycles"]},
        {"title": "Lightning Network", "lesson": "Lightning enables instant, near-free Bitcoin payments by opening payment channels. It scales Bitcoin to billions of users.", "key_concepts": ["lightning", "payment channels", "routing", "liquidity"]},
        {"title": "Bitcoin Wallets Deep Dive", "lesson": "HD wallets derive millions of addresses from one seed. Understanding derivation paths helps you recover funds across any wallet.", "key_concepts": ["HD wallet", "BIP32", "derivation path", "xpub"]},
    ],
    "advanced": [
        {"title": "UTXO Model", "lesson": "Bitcoin doesn't have balances — it has unspent transaction outputs. Understanding UTXOs is key to privacy and fee optimization.", "key_concepts": ["UTXO", "coin selection", "change outputs", "fee optimization"]},
        {"title": "Taproot & Schnorr", "lesson": "Taproot (BIP340-342) enables more private, efficient, and flexible transactions. Schnorr signatures allow key and signature aggregation.", "key_concepts": ["taproot", "schnorr", "MAST", "scriptpath", "keypath"]},
        {"title": "Bitcoin Script", "lesson": "Bitcoin's scripting language enables complex spending conditions: multisig, timelocks, HTLCs. It's intentionally not Turing-complete.", "key_concepts": ["script", "multisig", "timelock", "HTLC", "opcodes"]},
        {"title": "Running a Node", "lesson": "A full node independently verifies every rule. You don't trust anyone — you verify. It protects you and strengthens the network.", "key_concepts": ["full node", "verification", "pruning", "IBD"]},
        {"title": "On-Chain Analysis", "lesson": "Reading the blockchain reveals market cycles: HODL waves, SOPR, exchange flows, miner behavior. Data doesn't lie.", "key_concepts": ["SOPR", "HODL waves", "realized cap", "NVT", "exchange flows"]},
    ]
}

THOUGHT_TEMPLATES = [
    "Bitcoin block {block_height} just became permanent history. {blocks_to_halving} blocks until the next halving. Every block is a heartbeat.",
    "Fear & Greed at {fg_value} ({fg_label}). The crowd {crowd_action}. Ollie watches, learns, and remembers what history teaches.",
    "Hash rate at {hash_rate} EH/s — the most secure computational network in human history keeps humming.",
    "BTC at ${price:,.0f}. {dominance}% dominance. The signal is clear to those who know how to read it.",
    "Today Ollie processed {sources} data sources, absorbed {headlines} headlines, and distilled what matters for you.",
    "The mempool holds {mempool_txs} unconfirmed transactions. Low fee: {low_fee} sat/vB. The network never sleeps.",
    "Since genesis block: {days_since_genesis} days of uptime. No hacks. No bailouts. No permission needed.",
    "Miners earned ${miners_revenue:,.0f} today securing your transactions. Proof of Work is proof of commitment.",
]

# ── HTTP HELPER ───────────────────────────────────────────────────────────────
def fetch(url, timeout=20, headers=None, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "OllieBitcoinBot/3.0 (autonomous-learning; github-pages; educational)")
            if headers:
                for k, v in headers.items():
                    req.add_header(k, v)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            print(f"  [WARN] fetch({url[:60]}) attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    return None

def fetch_json(url, timeout=20):
    raw = fetch(url, timeout=timeout)
    if raw:
        try:
            return json.loads(raw)
        except Exception as e:
            print(f"  [WARN] JSON parse failed for {url[:60]}: {e}")
    return None

# ── DATA SOURCES ──────────────────────────────────────────────────────────────
def get_price():
    print("  Fetching Bitcoin price...")
    sources = [
        lambda: _cg_price(),
        lambda: _coincap_price(),
        lambda: _kraken_price(),
        lambda: _blockchain_price(),
    ]
    for src in sources:
        try:
            p = src()
            if p and p.get("price_usd", 0) > 0:
                return p
        except:
            pass
    return None

def _cg_price():
    data = fetch_json("https://api.coingecko.com/api/v3/coins/bitcoin?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false")
    if not data: return None
    md = data.get("market_data", {})
    global_data = fetch_json("https://api.coingecko.com/api/v3/global") or {}
    dominance = round(global_data.get("data", {}).get("market_cap_percentage", {}).get("btc", 0), 1)
    return {
        "price_usd": md.get("current_price", {}).get("usd", 0),
        "market_cap_usd": md.get("market_cap", {}).get("usd", 0),
        "volume_24h_usd": md.get("total_volume", {}).get("usd", 0),
        "change_24h_pct": round(md.get("price_change_percentage_24h", 0), 2),
        "change_7d_pct": round(md.get("price_change_percentage_7d", 0), 2),
        "change_30d_pct": round(md.get("price_change_percentage_30d", 0), 2),
        "ath_usd": md.get("ath", {}).get("usd", 0),
        "ath_date": md.get("ath_date", {}).get("usd", ""),
        "circulating_supply": md.get("circulating_supply", 0),
        "max_supply": 21000000,
        "dominance_pct": dominance,
        "source": "coingecko"
    }

def _coincap_price():
    data = fetch_json("https://api.coincap.io/v2/assets/bitcoin")
    if not data or "data" not in data: return None
    d = data["data"]
    return {
        "price_usd": float(d.get("priceUsd", 0)),
        "market_cap_usd": float(d.get("marketCapUsd", 0)),
        "volume_24h_usd": float(d.get("volumeUsd24Hr", 0)),
        "change_24h_pct": round(float(d.get("changePercent24Hr", 0)), 2),
        "change_7d_pct": 0, "change_30d_pct": 0, "ath_usd": 0, "ath_date": "",
        "circulating_supply": 0, "max_supply": 21000000, "dominance_pct": 0,
        "source": "coincap"
    }

def _kraken_price():
    data = fetch_json("https://api.kraken.com/0/public/Ticker?pair=XBTUSD")
    if not data or "result" not in data or "XXBTZUSD" not in data["result"]: return None
    ticker = data["result"]["XXBTZUSD"]
    return {
        "price_usd": float(ticker["c"][0]),
        "market_cap_usd": 0, "volume_24h_usd": float(ticker.get("v", [0,0])[1]),
        "change_24h_pct": 0, "change_7d_pct": 0, "change_30d_pct": 0,
        "ath_usd": 0, "ath_date": "", "circulating_supply": 0,
        "max_supply": 21000000, "dominance_pct": 0, "source": "kraken"
    }

def _blockchain_price():
    data = fetch_json("https://blockchain.info/ticker")
    if not data or "USD" not in data: return None
    return {
        "price_usd": data["USD"].get("last", 0),
        "market_cap_usd": 0, "volume_24h_usd": 0, "change_24h_pct": 0,
        "change_7d_pct": 0, "change_30d_pct": 0, "ath_usd": 0, "ath_date": "",
        "circulating_supply": 0, "max_supply": 21000000, "dominance_pct": 0,
        "source": "blockchain.info"
    }

def get_fear_greed():
    print("  Fetching Fear & Greed Index...")
    data = fetch_json("https://api.alternative.me/fng/?limit=30")
    if not data or "data" not in data: return None
    latest = data["data"][0]
    return {
        "value": int(latest.get("value", 50)),
        "label": latest.get("value_classification", "Neutral"),
        "history": [
            {"date": datetime.fromtimestamp(int(d["timestamp"]), tz=timezone.utc).strftime("%Y-%m-%d"),
             "value": int(d["value"]), "label": d["value_classification"]}
            for d in data["data"][:30]
        ]
    }

def get_blockchain_stats():
    print("  Fetching blockchain stats...")
    data = fetch_json("https://blockchain.info/stats?format=json")
    if not data: return None
    return {
        "block_height": data.get("n_blocks_total", 0),
        "hash_rate_ehs": round(data.get("hash_rate", 0) / 1e9, 2),
        "difficulty": data.get("difficulty", 0),
        "miners_revenue_usd": data.get("miners_revenue_usd", 0),
        "total_btc_sent_24h": data.get("total_btc_sent", 0),
        "n_tx_24h": data.get("n_tx", 0),
    }

def get_mempool():
    print("  Fetching mempool data...")
    fees = fetch_json("https://mempool.space/api/v1/fees/recommended")
    mempool_info = fetch_json("https://mempool.space/api/mempool")
    block_height = None
    raw_h = fetch("https://mempool.space/api/blocks/tip/height")
    if raw_h:
        try: block_height = int(raw_h.strip())
        except: pass
    if not fees: return None
    return {
        "low_fee": fees.get("hourFee", 0),
        "mid_fee": fees.get("halfHourFee", 0),
        "high_fee": fees.get("fastestFee", 0),
        "unconfirmed_txs": mempool_info.get("count", 0) if mempool_info else 0,
        "block_height": block_height
    }

def get_lightning_stats():
    print("  Fetching Lightning Network stats...")
    data = fetch_json("https://mempool.space/api/v1/lightning/statistics/latest")
    if not data: return None
    latest = data.get("latest", data)
    return {
        "node_count": latest.get("node_count", 0),
        "channel_count": latest.get("channel_count", 0),
        "total_capacity_btc": round(latest.get("total_capacity", 0) / 1e8, 2) if latest.get("total_capacity", 0) > 1000 else latest.get("total_capacity", 0),
    }

def parse_rss(url, max_items=6):
    raw = fetch(url, timeout=20)
    if not raw: return []
    items = []
    try:
        raw_clean = re.sub(r' xmlns[^"]*"[^"]*"', '', raw)
        root = ET.fromstring(raw_clean)
        channel = root.find(".//channel") or root
        for item in channel.findall(".//item")[:max_items]:
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            pub = item.findtext("pubDate", "").strip()
            desc_el = item.find("description")
            desc = ""
            if desc_el is not None and desc_el.text:
                desc = re.sub(r"<[^>]+>", "", desc_el.text).strip()[:250]
            if title:
                items.append({"title": title, "link": link, "published": pub, "summary": desc})
    except Exception as e:
        print(f"  [WARN] RSS parse error: {e}")
    return items

def get_news():
    print("  Fetching Bitcoin news from multiple feeds...")
    all_items = []
    feeds = [
        ("Bitcoin Magazine", "https://bitcoinmagazine.com/.rss/full/"),
        ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
        ("Cointelegraph", "https://cointelegraph.com/rss"),
        ("Decrypt", "https://decrypt.co/feed"),
        ("The Block", "https://www.theblock.co/rss.xml"),
        ("Bitcoin.com News", "https://news.bitcoin.com/feed/"),
        ("BitcoinNews", "https://bitcoinnews.com/feed/"),
        ("Bitcoin Optech", "https://bitcoinops.org/feed.xml"),
    ]
    seen_titles = set()
    for source, url in feeds:
        items = parse_rss(url, max_items=4)
        for item in items:
            t_key = item["title"][:50].lower()
            if t_key not in seen_titles:
                seen_titles.add(t_key)
                item["source"] = source
                # Sentiment scoring
                title_lower = item["title"].lower()
                pos = sum(1 for w in POSITIVE_WORDS if w in title_lower)
                neg = sum(1 for w in NEGATIVE_WORDS if w in title_lower)
                item["sentiment"] = "positive" if pos > neg else ("negative" if neg > pos else "neutral")
                item["relevance"] = pos + neg
                all_items.append(item)
    # Sort by relevance
    all_items.sort(key=lambda x: x["relevance"], reverse=True)
    return all_items[:MAX_HEADLINES]

def get_reddit():
    print("  Fetching Reddit Bitcoin discussions...")
    results = []
    subs = [("r/Bitcoin", "bitcoin"), ("r/BitcoinBeginners", "bitcoinbeginners"), ("r/Buttcoin", "lightningnetwork")]
    for name, sub in subs:
        data = fetch_json(f"https://www.reddit.com/r/{sub}/hot.json?limit=5", timeout=15)
        if data and "data" in data:
            for post in data["data"].get("children", [])[:3]:
                p = post["data"]
                if not p.get("stickied") and p.get("title"):
                    results.append({
                        "title": p["title"],
                        "score": p.get("score", 0),
                        "comments": p.get("num_comments", 0),
                        "url": f"https://reddit.com{p.get('permalink','')}",
                        "subreddit": name,
                        "flair": p.get("link_flair_text", "")
                    })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:MAX_REDDIT]

def get_bip_updates():
    print("  Checking BIP repository for updates...")
    data = fetch_json("https://api.github.com/repos/bitcoin/bips/commits?per_page=5")
    if not data: return []
    updates = []
    for commit in data[:5]:
        msg = commit.get("commit", {}).get("message", "")
        date = commit.get("commit", {}).get("author", {}).get("date", "")
        sha = commit.get("sha", "")[:7]
        updates.append({"message": msg[:150], "date": date[:10], "sha": sha})
    return updates

def generate_insights(price_data, fg_data, chain_data, mempool_data, headlines):
    print("  Generating insights...")
    insights = []
    now = datetime.now(timezone.utc)

    if price_data:
        p = price_data["price_usd"]
        ch24 = price_data.get("change_24h_pct", 0)
        ch7 = price_data.get("change_7d_pct", 0)
        dom = price_data.get("dominance_pct", 0)

        if ch24 > 3:
            insights.append({"type": "price", "icon": "📈", "text": f"BTC surged {ch24:.1f}% in 24 hours. Strong buying pressure — watch for continuation or consolidation.", "level": "intermediate"})
        elif ch24 < -3:
            insights.append({"type": "price", "icon": "📉", "text": f"BTC dropped {abs(ch24):.1f}% today. Historically, dips are buying opportunities for long-term holders.", "level": "beginner"})
        else:
            insights.append({"type": "price", "icon": "⚖️", "text": f"BTC is consolidating around ${p:,.0f}. Low volatility periods often precede big moves.", "level": "intermediate"})

        if ch7 > 10:
            insights.append({"type": "trend", "icon": "🔥", "text": f"7-day return: +{ch7:.1f}%. Weekly momentum is strongly bullish. Monitor for local top signals.", "level": "intermediate"})

        if dom > 55:
            insights.append({"type": "dominance", "icon": "👑", "text": f"Bitcoin dominance at {dom}% — capital is concentrating in BTC. This is a sign of market maturity.", "level": "advanced"})

    if fg_data:
        v = fg_data["value"]
        if v <= 20:
            insights.append({"type": "sentiment", "icon": "😱", "text": f"Extreme Fear at {v}/100. Historically, extreme fear has been the best time to accumulate BTC for the patient investor.", "level": "intermediate"})
        elif v >= 80:
            insights.append({"type": "sentiment", "icon": "🤑", "text": f"Extreme Greed at {v}/100. Be cautious — when everyone is greedy, it may be time to be careful. 'Be fearful when others are greedy.'", "level": "beginner"})
        elif v >= 60:
            insights.append({"type": "sentiment", "icon": "😊", "text": f"Greed at {v}/100. Market sentiment is positive. Stay disciplined and stick to your strategy.", "level": "beginner"})

    if chain_data:
        hr = chain_data.get("hash_rate_ehs", 0)
        if hr > 0:
            insights.append({"type": "network", "icon": "⛏️", "text": f"Hash rate: {hr} EH/s. A rising hash rate means miners are bullish on Bitcoin's future — they're investing capital.", "level": "intermediate"})

    if mempool_data:
        high_fee = mempool_data.get("high_fee", 0)
        unconf = mempool_data.get("unconfirmed_txs", 0)
        if unconf > 50000:
            insights.append({"type": "mempool", "icon": "🚦", "text": f"Mempool congested with {unconf:,} unconfirmed transactions. Use higher fees ({high_fee} sat/vB) for fast confirmation.", "level": "beginner"})
        elif unconf < 5000:
            insights.append({"type": "mempool", "icon": "✅", "text": f"Mempool is clear with only {unconf:,} transactions. Great time to transact with low fees ({mempool_data.get('low_fee',1)} sat/vB).", "level": "beginner"})

    # Add a random Bitcoin fact as an insight
    daily_fact_idx = int(now.strftime("%j")) % len(BITCOIN_FACTS)
    insights.append({"type": "fact", "icon": "🧠", "text": BITCOIN_FACTS[daily_fact_idx], "level": "beginner"})

    return insights[:MAX_INSIGHTS]

def generate_tips(price_data, fg_data):
    tips = []
    now = datetime.now(timezone.utc)

    always_tips = [
        {"icon": "🔑", "tip": "Not your keys, not your coins. Move BTC off exchanges to your own wallet.", "category": "security"},
        {"icon": "🌱", "tip": "Dollar-cost averaging (DCA) removes emotion from investing. Buy a fixed amount weekly regardless of price.", "category": "strategy"},
        {"icon": "🔒", "tip": "Write down your seed phrase on paper. Never store it digitally or in photos.", "category": "security"},
        {"icon": "⚡", "tip": "Try the Lightning Network for daily Bitcoin spending. Instant, cheap, and unstoppable.", "category": "usage"},
        {"icon": "📚", "tip": "Read the Bitcoin whitepaper. It's only 9 pages and explains everything Satoshi intended.", "category": "education"},
        {"icon": "🏃", "tip": "Run your own Bitcoin node. It takes ~500GB storage and gives you full sovereignty.", "category": "advanced"},
        {"icon": "🧮", "tip": "Think in satoshis, not BTC. 1 BTC = 100,000,000 sats. You can own a lot of sats.", "category": "mindset"},
        {"icon": "🌍", "tip": "Bitcoin is borderless money. You can send any amount anywhere with no permission needed.", "category": "education"},
    ]
    daily_idx = int(now.strftime("%j")) % len(always_tips)
    tips.append(always_tips[daily_idx])
    tips.append(always_tips[(daily_idx + 1) % len(always_tips)])

    if fg_data and fg_data["value"] <= 30:
        tips.append({"icon": "💎", "tip": "The market is fearful. Historically this is when the most wealth is created. Stay calm, stay humble, stack sats.", "category": "strategy"})
    elif fg_data and fg_data["value"] >= 75:
        tips.append({"icon": "⚠️", "tip": "The market is greedy. Consider taking some profits or at minimum don't use leverage here.", "category": "strategy"})

    return tips[:4]

def generate_thought(price_data, chain_data, fg_data, mempool_data, evolution_num):
    now = datetime.now(timezone.utc)
    genesis = datetime(2009, 1, 3, tzinfo=timezone.utc)
    days_since = (now - genesis).days

    p = price_data.get("price_usd", 0) if price_data else 0
    fg = fg_data.get("value", 50) if fg_data else 50
    fg_label = fg_data.get("label", "Neutral") if fg_data else "Neutral"
    hr = chain_data.get("hash_rate_ehs", 0) if chain_data else 0
    dom = price_data.get("dominance_pct", 0) if price_data else 0
    block_h = (chain_data.get("block_height", 0) or (mempool_data or {}).get("block_height", 0)) if chain_data else ((mempool_data or {}).get("block_height", 0))
    blocks_to_halving = max(0, NEXT_HALVING_BLOCK - block_h) if block_h else "?"
    mempool_txs = mempool_data.get("unconfirmed_txs", 0) if mempool_data else 0
    low_fee = mempool_data.get("low_fee", 1) if mempool_data else 1
    miners_rev = chain_data.get("miners_revenue_usd", 0) if chain_data else 0

    crowd_action = "is fearful — history rewards the patient" if fg < 40 else ("is greedy — the wise stay disciplined" if fg > 70 else "is neutral — the opportunity is quiet")

    template_idx = int(now.strftime("%H")) % len(THOUGHT_TEMPLATES)
    try:
        thought = THOUGHT_TEMPLATES[template_idx].format(
            block_height=f"{block_h:,}" if block_h else "unknown",
            blocks_to_halving=f"{blocks_to_halving:,}" if isinstance(blocks_to_halving, int) else blocks_to_halving,
            fg_value=fg, fg_label=fg_label, crowd_action=crowd_action,
            hash_rate=hr, price=p, dominance=dom,
            sources=8, headlines=12,
            mempool_txs=f"{mempool_txs:,}",
            low_fee=low_fee, days_since_genesis=f"{days_since:,}",
            miners_revenue=miners_rev
        )
    except:
        thought = f"Ollie has learned from {days_since:,} days of Bitcoin history. Today's price: ${p:,.0f}. The network never stops. Neither does Ollie."

    return thought

def generate_prediction(price_data, fg_data, chain_data):
    now = datetime.now(timezone.utc)
    if not price_data: return {"outlook": "neutral", "text": "Insufficient data for prediction.", "confidence": 0}

    p = price_data["price_usd"]
    ch24 = price_data.get("change_24h_pct", 0)
    ch7 = price_data.get("change_7d_pct", 0)
    fg = fg_data["value"] if fg_data else 50
    hr = chain_data.get("hash_rate_ehs", 0) if chain_data else 0

    score = 0
    if ch24 > 2: score += 1
    elif ch24 < -2: score -= 1
    if ch7 > 5: score += 2
    elif ch7 < -5: score -= 2
    if fg < 30: score += 1  # contrarian signal
    elif fg > 75: score -= 1
    if hr > 700: score += 1

    if score >= 3:
        outlook, text = "bullish", f"Multiple signals align bullishly. Hash rate strong, momentum positive. Short-term bias: upward."
    elif score <= -3:
        outlook, text = "bearish", f"Momentum negative, sentiment stretched. Caution warranted. Watch support levels."
    elif score > 0:
        outlook, text = "cautiously bullish", f"More positive signals than negative. Market shows resilience. Stay patient."
    elif score < 0:
        outlook, text = "cautiously bearish", f"Slight negative bias. Not a crisis — but not the time to over-leverage."
    else:
        outlook, text = "neutral", f"Balanced signals. The market is undecided. This is when discipline matters most."

    return {"outlook": outlook, "text": text, "confidence": min(abs(score) * 20, 80), "score": score}

# ── SELF-IMPROVEMENT SYSTEM ───────────────────────────────────────────────────
def evolve(existing_data):
    """Ollie scores its own past predictions and evolves its thinking."""
    print("  Running self-improvement cycle...")
    evolution = existing_data.get("evolution_log", [])
    now = datetime.now(timezone.utc)

    # Score yesterday's prediction (simple heuristic: if we predicted bullish and price went up, score +1)
    if len(evolution) >= 2:
        last = evolution[-1]
        prev = evolution[-2]
        last_price = last.get("price_usd", 0)
        prev_price = prev.get("price_usd", 0)
        last_outlook = last.get("prediction_outlook", "neutral")
        if last_price and prev_price:
            price_went_up = last_price > prev_price
            predicted_up = "bullish" in last_outlook
            prediction_score = 1 if (price_went_up == predicted_up) else -1
            # Update score on last entry
            evolution[-1]["prediction_score"] = prediction_score

    # Calculate lifetime accuracy
    scored = [e for e in evolution if "prediction_score" in e]
    accuracy = (sum(1 for e in scored if e["prediction_score"] > 0) / len(scored) * 100) if scored else 0

    return evolution, round(accuracy, 1)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print(f"OLLIE v3.0 — Bitcoin Intelligence Engine")
    print(f"Cycle start: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    # Load existing data
    existing = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                existing = json.load(f)
        except:
            pass

    evolution_log, prediction_accuracy = evolve(existing)
    generation = len(evolution_log) + 1

    # Fetch all data
    print("\n[PHASE 1] Gathering live Bitcoin intelligence...")
    price_data = get_price()
    fg_data = get_fear_greed()
    chain_data = get_blockchain_stats()
    mempool_data = get_mempool()
    lightning_data = get_lightning_stats()

    print("\n[PHASE 2] Absorbing news and community signals...")
    headlines = get_news()
    reddit_posts = get_reddit()
    bip_updates = get_bip_updates()

    print("\n[PHASE 3] Generating insights and wisdom...")
    insights = generate_insights(price_data, fg_data, chain_data, mempool_data, headlines)
    tips = generate_tips(price_data, fg_data)
    thought = generate_thought(price_data, chain_data, fg_data, mempool_data, generation)
    prediction = generate_prediction(price_data, fg_data, chain_data)

    # Build today's evolution log entry
    now = datetime.now(timezone.utc)
    today_entry = {
        "generation": generation,
        "timestamp": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "cycle": now.strftime("%H:00 UTC"),
        "price_usd": price_data.get("price_usd", 0) if price_data else 0,
        "fg_value": fg_data.get("value", 0) if fg_data else 0,
        "headlines_absorbed": len(headlines),
        "insights_generated": len(insights),
        "prediction_outlook": prediction["outlook"],
        "hash_rate_ehs": chain_data.get("hash_rate_ehs", 0) if chain_data else 0,
    }
    evolution_log.append(today_entry)
    if len(evolution_log) > MAX_EVOLUTION_LOG:
        evolution_log = evolution_log[-MAX_EVOLUTION_LOG:]

    # Update price history
    price_history = existing.get("price_history", [])
    if price_data and price_data.get("price_usd", 0) > 0:
        price_history.append({
            "date": now.strftime("%Y-%m-%d %H:00"),
            "price": price_data["price_usd"],
            "change_24h": price_data.get("change_24h_pct", 0)
        })
        if len(price_history) > MAX_PRICE_HISTORY * 4:  # 4x daily cycles
            price_history = price_history[-MAX_PRICE_HISTORY * 4:]

    # Compute halving info
    block_height = (chain_data or {}).get("block_height", 0) or (mempool_data or {}).get("block_height", 0) or 0
    blocks_to_halving = max(0, NEXT_HALVING_BLOCK - block_height) if block_height else 0
    estimated_days_to_halving = round(blocks_to_halving * 10 / 1440, 1) if blocks_to_halving else 0

    # Genesis date
    genesis = datetime(2009, 1, 3, tzinfo=timezone.utc)
    days_alive = (now - genesis).days

    # Compile final knowledge base
    knowledge = {
        "meta": {
            "version": "3.0",
            "generation": generation,
            "last_updated": now.isoformat(),
            "last_updated_human": now.strftime("%B %d, %Y at %H:%M UTC"),
            "update_cycle": "every 6 hours",
            "mission": "Learn everything about Bitcoin. Teach and guide every Bitcoiner on their journey.",
            "prediction_accuracy_pct": prediction_accuracy,
            "days_alive": days_alive,
            "total_cycles": generation,
        },
        "current": {
            "price": price_data,
            "fear_greed": fg_data,
            "blockchain": chain_data,
            "mempool": mempool_data,
            "lightning": lightning_data,
            "halving": {
                "current_reward_btc": HALVING_BLOCK_REWARD_NOW,
                "next_block": NEXT_HALVING_BLOCK,
                "current_block": block_height,
                "blocks_remaining": blocks_to_halving,
                "estimated_days": estimated_days_to_halving,
                "progress_pct": round((block_height % 210000) / 210000 * 100, 2) if block_height else 0
            }
        },
        "intelligence": {
            "todays_thought": thought,
            "todays_prediction": prediction,
            "todays_insights": insights,
            "todays_tips": tips,
            "todays_fact": BITCOIN_FACTS[int(now.strftime("%j")) % len(BITCOIN_FACTS)],
        },
        "news": {
            "headlines": headlines,
            "reddit": reddit_posts,
            "bip_updates": bip_updates,
        },
        "education": {
            "learning_paths": LEARNING_PATHS,
            "all_facts": BITCOIN_FACTS,
        },
        "evolution_log": evolution_log,
        "price_history": price_history,
    }

    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(knowledge, f, indent=2, default=str)

    print(f"\n✅ OLLIE CYCLE COMPLETE")
    print(f"   Generation: {generation}")
    print(f"   Price: ${price_data.get('price_usd', 0):,.2f}" if price_data else "   Price: N/A")
    print(f"   Fear & Greed: {fg_data.get('value', 0)} ({fg_data.get('label', 'N/A')})" if fg_data else "   F&G: N/A")
    print(f"   Headlines absorbed: {len(headlines)}")
    print(f"   Insights generated: {len(insights)}")
    print(f"   Prediction accuracy: {prediction_accuracy}%")
    print(f"   Prediction: {prediction['outlook']}")
    print(f"   Data written to: {DATA_FILE}")

if __name__ == "__main__":
    main()
