#!/usr/bin/env python3
"""
OLLIE — Autonomous Bitcoin Learning Engine
Runs daily via GitHub Actions. Fetches from free public APIs only.
No API keys required. Commits results back to the repository.
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

# ── CONFIG ────────────────────────────────────────────────────────────────────
DATA_FILE = "data/knowledge.json"
MAX_EVOLUTION_LOG = 365        # keep 1 year of daily logs
MAX_PRICE_HISTORY = 365
MAX_FG_HISTORY = 365
MAX_HEADLINES = 8
MAX_REDDIT = 8
MAX_INSIGHTS = 10
HALVING_BLOCK_REWARD_NOW = 3.125
NEXT_HALVING_BLOCK = 1050000

# ── HTTP HELPER ───────────────────────────────────────────────────────────────
def fetch(url, timeout=15, headers=None, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "OllieBitcoinBot/2.0 (autonomous-learning; github-pages)")
            if headers:
                for k, v in headers.items():
                    req.add_header(k, v)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            print(f"  [WARN] fetch({url[:60]}...) attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # exponential backoff
    return None

def fetch_json(url, timeout=15):
    raw = fetch(url, timeout=timeout)
    if raw:
        try:
            return json.loads(raw)
        except Exception as e:
            print(f"  [WARN] JSON parse failed: {e}")
    return None

# ── DATA SOURCES (ALL FREE, NO KEY) ──────────────────────────────────────────

def get_coingecko_price():
    print("  Fetching Bitcoin price (CoinGecko)...")
    data = fetch_json(
        "https://api.coingecko.com/api/v3/coins/bitcoin?"
        "localization=false&tickers=false&market_data=true"
        "&community_data=false&developer_data=false&sparkline=false"
    )
    if not data:
        return None
    md = data.get("market_data", {})
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
        "dominance_pct": 0,  # filled below
    }

def get_coingecko_global():
    print("  Fetching global crypto market (CoinGecko)...")
    data = fetch_json("https://api.coingecko.com/api/v3/global")
    if data and "data" in data:
        return {
            "dominance_pct": round(
                data["data"].get("market_cap_percentage", {}).get("btc", 0), 1
            )
        }
    return {"dominance_pct": 0}

def get_fear_greed():
    print("  Fetching Fear & Greed Index (alternative.me)...")
    data = fetch_json("https://api.alternative.me/fng/?limit=7")
    if not data or "data" not in data:
        return None
    latest = data["data"][0]
    return {
        "value": int(latest.get("value", 50)),
        "label": latest.get("value_classification", "Neutral"),
        "history": [
            {
                "date": datetime.fromtimestamp(
                    int(d["timestamp"]), tz=timezone.utc
                ).strftime("%Y-%m-%d"),
                "value": int(d["value"]),
                "label": d["value_classification"],
            }
            for d in data["data"][:7]
        ],
    }

def get_blockchain_stats():
    print("  Fetching blockchain stats (blockchain.info)...")
    data = fetch_json("https://blockchain.info/stats?format=json")
    if not data:
        return None
    return {
        "block_height": data.get("n_blocks_total", 0),
        "hash_rate": round(data.get("hash_rate", 0) / 1e9, 2),  # EH/s
        "difficulty": data.get("difficulty", 0),
        "unconfirmed_txs": data.get("n_tx_not_after_genesis", 0),
        "total_btc_sent_24h": data.get("total_btc_sent", 0),
        "estimated_btc_sent": data.get("estimated_btc_sent", 0),
        "miners_revenue_usd": data.get("miners_revenue_usd", 0),
    }

def get_mempool():
    print("  Fetching mempool fees (mempool.space)...")
    fees = fetch_json("https://mempool.space/api/v1/fees/recommended")
    if not fees:
        return None
    mempool_info = fetch_json("https://mempool.space/api/mempool")
    unconfirmed = 0
    if mempool_info:
        unconfirmed = mempool_info.get("count", 0)
    return {
        "low_fee": fees.get("hourFee", 0),
        "mid_fee": fees.get("halfHourFee", 0),
        "high_fee": fees.get("fastestFee", 0),
        "unconfirmed_txs": unconfirmed,
    }

def get_block_height_mempool():
    print("  Fetching current block height (mempool.space)...")
    raw = fetch("https://mempool.space/api/blocks/tip/height")
    if raw:
        try:
            return int(raw.strip())
        except:
            pass
    return None

def parse_rss(url, max_items=8):
    """Parse RSS feed without external libraries."""
    raw = fetch(url, timeout=20)
    if not raw:
        return []
    items = []
    try:
        # Strip namespaces for simpler parsing
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
                desc = re.sub(r"<[^>]+>", "", desc_el.text).strip()[:200]
            if title:
                items.append({"title": title, "link": link, "published": pub, "summary": desc})
    except Exception as e:
        print(f"  [WARN] RSS parse error: {e}")
    return items

def get_news():
    print("  Fetching Bitcoin news (RSS feeds)...")
    all_items = []

    feeds = [
        ("Bitcoin Magazine", "https://bitcoinmagazine.com/.rss/full/"),
        ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
        ("Decrypt", "https://decrypt.co/feed"),
        ("BitcoinNews", "https://bitcoinnews.com/feed/"),
        ("Cointelegraph", "https://cointelegraph.com/rss"),
        ("Bitcoin.com", "https://news.bitcoin.com/feed/"),
        ("The Block", "https://www.theblock.co/rss.xml"),
        ("Bitcoin Stack Exchange", "https://bitcoin.stackexchange.com/feeds"),
    ]

    for source, url in feeds:
        items = parse_rss(url, max_items=4)
        for item in items:
            item["source"] = source
            all_items.append(item)
        if items:
            print(f"    Got {len(items)} headlines from {source}")
        time.sleep(0.5)

    return all_items[:MAX_HEADLINES]

def get_reddit():
    print("  Fetching top Reddit posts (r/Bitcoin)...")
    data = fetch_json(
        "https://www.reddit.com/r/Bitcoin/hot.json?limit=15&raw_json=1"
    )
    if not data:
        # fallback: r/bitcoinmarkets
        data = fetch_json(
            "https://www.reddit.com/r/bitcoinmarkets/hot.json?limit=10&raw_json=1"
        )
    if not data:
        return []
    posts = []
    try:
        for child in data["data"]["children"][:MAX_REDDIT]:
            p = child["data"]
            if p.get("stickied"):
                continue
            title = p.get("title", "").strip()
            score = p.get("score", 0)
            comments = p.get("num_comments", 0)
            url = "https://reddit.com" + p.get("permalink", "")
            flair = p.get("link_flair_text", "") or ""
            if title:
                posts.append({
                    "title": title,
                    "score": score,
                    "comments": comments,
                    "url": url,
                    "flair": flair,
                })
    except Exception as e:
        print(f"  [WARN] Reddit parse error: {e}")
    return posts

# ── INSIGHT ENGINE ────────────────────────────────────────────────────────────

def compute_halving(block_height):
    """Compute blocks until next halving and estimated date."""
    next_halving = NEXT_HALVING_BLOCK
    blocks_left = max(0, next_halving - block_height)
    # ~10 min per block
    days_left = blocks_left * 10 / 1440
    halving_date = (datetime.now(timezone.utc) + timedelta(days=days_left)).strftime("%Y-%m-%d")
    pct_mined = round((block_height / 21000000 * 100) * 100 / 100, 4)
    btc_mined = round(block_height * HALVING_BLOCK_REWARD_NOW * 0.0001, 0)  # rough
    return {
        "next_halving_block": next_halving,
        "blocks_until_halving": blocks_left,
        "estimated_halving_date": halving_date if blocks_left > 0 else "Completed",
        "days_until_halving": round(days_left, 0),
    }

def extract_topics(headlines, reddit_posts):
    """Extract trending topic keywords from news and reddit."""
    text = " ".join(
        [h.get("title", "") for h in headlines] +
        [r.get("title", "") for r in reddit_posts]
    ).lower()

    topic_keywords = {
        "ETF": ["etf", "spot etf", "blackrock", "fidelity", "bitcoin etf"],
        "Lightning Network": ["lightning", "ln", "lightning network"],
        "Institutional Adoption": ["institutional", "corporation", "treasury", "microstrategy", "grayscale", "asset manager"],
        "Mining": ["mining", "miner", "hashrate", "hash rate", "asic", "foundry"],
        "Regulation": ["regulation", "sec", "cftc", "congress", "senate", "law", "legal", "ban"],
        "Layer 2": ["layer 2", "l2", "taproot", "schnorr", "rgb", "ark"],
        "Halving": ["halving", "halvening", "block reward", "subsidy"],
        "DeFi on Bitcoin": ["defi", "ordinals", "inscriptions", "brc-20", "runes"],
        "Self-Custody": ["self-custody", "cold storage", "hardware wallet", "multisig", "seed phrase"],
        "Market Analysis": ["bull", "bear", "support", "resistance", "ath", "all-time high", "correction"],
        "Central Banks": ["federal reserve", "fed", "ecb", "central bank", "interest rate", "inflation"],
        "Energy": ["energy", "renewable", "solar", "nuclear", "carbon", "esg", "electricity"],
        "Adoption": ["adoption", "merchant", "payment", "el salvador", "country", "nation"],
        "Privacy": ["privacy", "coinjoin", "taproot", "zero knowledge", "zk"],
        "Security": ["security", "hack", "exploit", "vulnerability", "51% attack"],
    }

    found = []
    for topic, keywords in topic_keywords.items():
        if any(kw in text for kw in keywords):
            found.append(topic)

    return found[:MAX_INSIGHTS]

def generate_thought(price_data, fg, blockchain, mempool, headlines, reddit, halving_info, today):
    """Generate Ollie's daily thought — a synthesized intelligence narrative."""
    if not price_data:
        return "The internet is quiet today, but Ollie continues to watch. Every block is a heartbeat, every transaction a breath. Bitcoin persists."

    price = price_data.get("price_usd", 0)
    change = price_data.get("change_24h_pct", 0)
    change_7d = price_data.get("change_7d_pct", 0)
    fg_val = fg["value"] if fg else 50
    fg_lbl = fg["label"] if fg else "Neutral"
    block = blockchain.get("block_height", 0) if blockchain else 0
    blocks_left = halving_info.get("blocks_until_halving", 0)

    # Price narrative
    direction = "surged" if change > 3 else "climbed" if change > 0.5 else "slipped" if change < -3 else "dipped" if change < -0.5 else "held steady"
    sentiment_phrase = {
        "Extreme Greed": "Markets are in a state of euphoria — caution is warranted.",
        "Greed": "Greed fills the air. The crowd grows bold.",
        "Neutral": "The market breathes without conviction — a pivot may approach.",
        "Fear": "Fear grips the market. Historically, this is when conviction is built.",
        "Extreme Fear": "Extreme fear dominates — the capitulation phase tests the faithful.",
    }.get(fg_lbl, "Sentiment remains undefined.")

    # Headline context
    top_headline = headlines[0]["title"] if headlines else ""
    headline_phrase = f' Today, the world is discussing: "{top_headline}".' if top_headline else ""

    # Halving narrative
    if blocks_left > 0:
        halving_phrase = f" We are {blocks_left:,} blocks from the next halving — the mathematical scarcity event that reshapes Bitcoin's economy."
    else:
        halving_phrase = " The most recent halving has passed, cementing Bitcoin's deflationary arc."

    # 7d context
    week_phrase = ""
    if abs(change_7d) > 5:
        week_phrase = f" Over the past week, Bitcoin has {'risen' if change_7d > 0 else 'fallen'} {abs(change_7d):.1f}% — a trend worth watching."

    thought = (
        f"On {today}, Bitcoin {direction} to ${price:,.0f}. "
        f"{sentiment_phrase}"
        f"{headline_phrase}"
        f"{week_phrase}"
        f"{halving_phrase} "
        f"Block {block:,} was sealed in the chain today. "
        f"Every block is irreversible proof that this network has never stopped — "
        f"not for banks, not for governments, not for anything."
    )

    return thought

def generate_insights(price_data, fg, blockchain, mempool, halving_info, kb):
    """Generate bullet-point insights from the data."""
    insights = []
    if not price_data:
        return ["Data unavailable for this cycle."]

    price = price_data.get("price_usd", 0)
    ath = price_data.get("ath_usd", 0)
    change = price_data.get("change_24h_pct", 0)
    supply = price_data.get("circulating_supply", 0)

    if ath > 0 and price > 0:
        pct_from_ath = round((ath - price) / ath * 100, 1)
        if pct_from_ath < 1:
            insights.append("Bitcoin is trading at or near its all-time high.")
        elif pct_from_ath < 10:
            insights.append(f"Bitcoin is within {pct_from_ath}% of its all-time high of ${ath:,.0f}.")
        else:
            insights.append(f"Bitcoin is {pct_from_ath}% below its ATH of ${ath:,.0f} — currently in drawdown.")

    if supply > 0:
        mined_pct = round(supply / 21_000_000 * 100, 2)
        insights.append(f"{mined_pct}% of all Bitcoin that will ever exist has been mined ({supply:,.0f} BTC out of 21,000,000).")

    if fg:
        insights.append(f"Market sentiment: {fg['label']} ({fg['value']}/100). Historically, extremes signal reversals.")

    if blockchain:
        hr = blockchain.get("hash_rate", 0)
        if hr > 0:
            insights.append(f"Hash rate stands at {hr:.1f} EH/s — measuring the total computational security of the network.")

    if halving_info:
        bl = halving_info.get("blocks_until_halving", 0)
        days = halving_info.get("days_until_halving", 0)
        if bl > 0:
            insights.append(f"Next halving: {bl:,} blocks away (~{int(days)} days). Block reward will drop from 3.125 to 1.5625 BTC.")

    if mempool:
        high = mempool.get("high_fee", 0)
        if high > 100:
            insights.append(f"Mempool congestion: high-priority fee is {high} sat/vByte — network is busy.")
        elif high < 5:
            insights.append(f"Mempool is quiet: fees as low as {mempool.get('low_fee', 0)} sat/vByte.")

    if abs(change) > 5:
        insights.append(f"Significant 24h move: {'+' if change > 0 else ''}{change}%. Watch for follow-through volume.")

    # Trend analysis
    price_history = kb.get("price_history", [])
    if len(price_history) >= 30:
        prices = [p["price"] for p in price_history[-30:]]
        avg_30d = sum(prices) / len(prices)
        if price > avg_30d * 1.05:
            insights.append("Price is 5% above 30-day average — bullish momentum.")
        elif price < avg_30d * 0.95:
            insights.append("Price is 5% below 30-day average — bearish pressure.")

    return insights[:MAX_INSIGHTS]

def generate_tips(price_data, fg, blockchain, mempool, halving_info, topics):
    """Generate helpful tips for Bitcoiners based on current data."""
    tips = []

    if fg:
        val = fg['value']
        if val >= 75:
            tips.append("Extreme Greed: Markets are euphoric. Consider taking profits or setting stop-losses.")
        elif val <= 25:
            tips.append("Extreme Fear: This could be a buying opportunity. Remember, fear is your friend in crypto.")
        elif val >= 55:
            tips.append("Greed is creeping in. Stay disciplined and don't FOMO into bad positions.")
        elif val <= 45:
            tips.append("Fear levels rising. Focus on long-term fundamentals over short-term noise.")

    if price_data:
        change = price_data.get("change_24h_pct", 0)
        if change > 10:
            tips.append("Big green day! Congrats to those who held. But remember, volatility is Bitcoin's nature.")
        elif change < -10:
            tips.append("Red day ahead. If you're long-term, this is just noise. Dollar-cost average if you believe.")

    if halving_info:
        days = halving_info.get("days_until_halving", 0)
        if days < 100:
            tips.append(f"Halving approaching in ~{int(days)} days. Historically, halvings lead to bull runs. Prepare your stack.")

    if mempool:
        high = mempool.get("high_fee", 0)
        if high > 50:
            tips.append("High fees! If sending, consider batching transactions or using Lightning Network.")

    if "Halving" in topics:
        tips.append("Halving discussion heating up. Remember, halvings reduce new supply by 50%, historically bullish.")

    if "ETF" in topics:
        tips.append("ETF news circulating. Spot ETFs could bring institutional money, but don't forget self-custody.")

    tips.append("Always do your own research. Bitcoin is about financial sovereignty - learn, stack sats, and HODL.")

def generate_tips(price_data, fg, blockchain, mempool, halving_info, topics):
    """Generate helpful tips for Bitcoiners based on current data."""
    tips = []

    if fg:
        val = fg['value']
        if val >= 75:
            tips.append("Extreme Greed: Markets are euphoric. Consider taking profits or setting stop-losses.")
        elif val <= 25:
            tips.append("Extreme Fear: This could be a buying opportunity. Remember, fear is your friend in crypto.")
        elif val >= 55:
            tips.append("Greed is creeping in. Stay disciplined and don't FOMO into bad positions.")
        elif val <= 45:
            tips.append("Fear levels rising. Focus on long-term fundamentals over short-term noise.")

    if price_data:
        change = price_data.get("change_24h_pct", 0)
        if change > 10:
            tips.append("Big green day! Congrats to those who held. But remember, volatility is Bitcoin's nature.")
        elif change < -10:
            tips.append("Red day ahead. If you're long-term, this is just noise. Dollar-cost average if you believe.")

    if halving_info:
        days = halving_info.get("days_until_halving", 0)
        if days < 100:
            tips.append(f"Halving approaching in ~{int(days)} days. Historically, halvings lead to bull runs. Prepare your stack.")

    if mempool:
        high = mempool.get("high_fee", 0)
        if high > 50:
            tips.append("High fees! If sending, consider batching transactions or using Lightning Network.")

    if "Halving" in topics:
        tips.append("Halving discussion heating up. Remember, halvings reduce new supply by 50%, historically bullish.")

    if "ETF" in topics:
        tips.append("ETF news circulating. Spot ETFs could bring institutional money, but don't forget self-custody.")

    tips.append("Always do your own research. Bitcoin is about financial sovereignty - learn, stack sats, and HODL.")

    return tips[:5]

def generate_daily_fact():
    """Return a random educational fact about Bitcoin."""
    facts = [
        "Bitcoin was created in 2008 by Satoshi Nakamoto, whose true identity remains unknown.",
        "The total supply of Bitcoin is capped at 21 million coins, making it a deflationary asset.",
        "Bitcoin transactions are verified by network nodes and recorded in a public distributed ledger called the blockchain.",
        "The first Bitcoin transaction was made in 2009, when Satoshi sent 10 BTC to Hal Finney.",
        "Bitcoin's proof-of-work algorithm is designed to prevent double-spending and ensure network security.",
        "Lightning Network allows for instant, low-cost Bitcoin transactions by enabling off-chain payments.",
        "Bitcoin halvings occur every 4 years, reducing the block reward and controlling inflation.",
        "The Bitcoin whitepaper, published in 2008, is only 9 pages long and outlines the core concepts.",
        "Bitcoin mining secures the network and processes transactions, requiring significant computational power.",
        "Self-custody means you control your own keys, reducing reliance on third parties.",
    ]
    import random
    random.seed(datetime.now().strftime("%Y-%m-%d"))  # daily fact
    return random.choice(facts)

def generate_prediction(price_data, fg, kb):
    """Generate a simple market prediction based on trends."""
    prediction = ""
    price = price_data.get("price_usd", 0) if price_data else 0
    fg_val = fg['value'] if fg else 50
    price_history = kb.get("price_history", [])
    if len(price_history) >= 7:
        recent_prices = [p["price"] for p in price_history[-7:]]
        avg_7d = sum(recent_prices) / len(recent_prices)
        if price > avg_7d and fg_val < 40:
            prediction = "Bullish outlook: Price above 7-day average with low fear levels."
        elif price < avg_7d and fg_val > 60:
            prediction = "Bearish outlook: Price below 7-day average with high greed levels."
        else:
            prediction = "Neutral: Market conditions mixed, monitor closely."
    else:
        prediction = "Insufficient data for prediction."
    return prediction

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  OLLIE — Bitcoin Learning Engine")
    print(f"  Cycle starting: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    # Load existing knowledge
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            knowledge = json.load(f)
    except FileNotFoundError:
        print("  [INFO] No existing knowledge.json — creating fresh.")
        knowledge = {"meta": {}, "current": {}, "knowledge_base": {"topics_learned": [], "price_history": [], "fear_greed_history": []}, "evolution_log": []}

    meta = knowledge.setdefault("meta", {})
    kb = knowledge.setdefault("knowledge_base", {"topics_learned": [], "price_history": [], "fear_greed_history": []})

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_pretty = datetime.now(timezone.utc).strftime("%B %d, %Y")
    now_iso = datetime.now(timezone.utc).isoformat()

    if not meta.get("genesis"):
        meta["genesis"] = today
        print(f"  [INFO] Genesis day: {today}")

    cycle_num = meta.get("total_cycles", 0) + 1
    print(f"  Starting cycle #{cycle_num}")

    # ── FETCH DATA ────────────────────────────────────────────────────────────
    print("\n[PHASE 1] Fetching market data...")
    price_data = get_coingecko_price()
    time.sleep(2)  # respect rate limits
    global_data = get_coingecko_global()
    time.sleep(2)
    if price_data and global_data:
        price_data["dominance_pct"] = global_data.get("dominance_pct", 0)

    print("\n[PHASE 2] Fetching sentiment data...")
    fg = get_fear_greed()
    time.sleep(1)

    print("\n[PHASE 3] Fetching blockchain data...")
    blockchain = get_blockchain_stats()
    time.sleep(1)
    block_height = get_block_height_mempool()
    if block_height and blockchain:
        blockchain["block_height"] = block_height
    elif block_height:
        blockchain = {"block_height": block_height}
    time.sleep(1)
    mempool = get_mempool()
    time.sleep(1)

    print("\n[PHASE 4] Fetching news and Reddit...")
    headlines = get_news()
    time.sleep(2)
    reddit_posts = get_reddit()

    print("\n[PHASE 5] Computing intelligence...")
    # Halving calc
    bh = blockchain.get("block_height", 0) if blockchain else 0
    halving_info = compute_halving(bh)

    # Topics
    topics = extract_topics(headlines, reddit_posts)
    print(f"  Trending topics: {topics}")

    # Thought generation
    thought = generate_thought(price_data, fg, blockchain, mempool, headlines, reddit_posts, halving_info, today_pretty)

    # Insights
    insights = generate_insights(price_data, fg, blockchain, mempool, halving_info, kb)

    # Tips for Bitcoiners
    tips = generate_tips(price_data, fg, blockchain, mempool, halving_info, topics)

    # Daily educational fact
    fact = generate_daily_fact()

    # Market prediction
    prediction = generate_prediction(price_data, fg, kb)

    # ── UPDATE KNOWLEDGE ──────────────────────────────────────────────────────
    print("\n[PHASE 6] Updating knowledge base...")

    # Current snapshot
    current = knowledge.setdefault("current", {})
    if price_data:
        current.update({
            "price_usd": price_data.get("price_usd", 0),
            "market_cap_usd": price_data.get("market_cap_usd", 0),
            "volume_24h_usd": price_data.get("volume_24h_usd", 0),
            "change_24h_pct": price_data.get("change_24h_pct", 0),
            "change_7d_pct": price_data.get("change_7d_pct", 0),
            "change_30d_pct": price_data.get("change_30d_pct", 0),
            "ath_usd": price_data.get("ath_usd", 0),
            "ath_date": price_data.get("ath_date", ""),
            "circulating_supply": price_data.get("circulating_supply", 0),
            "max_supply": 21000000,
            "dominance_pct": price_data.get("dominance_pct", 0),
        })
    if fg:
        current.update({
            "fear_greed_value": fg["value"],
            "fear_greed_label": fg["label"],
        })
    if blockchain:
        current.update({
            "block_height": blockchain.get("block_height", current.get("block_height", 0)),
            "hash_rate": blockchain.get("hash_rate", 0),
            "difficulty": blockchain.get("difficulty", 0),
        })
    if mempool:
        current.update({
            "mempool_low_fee": mempool.get("low_fee", 0),
            "mempool_mid_fee": mempool.get("mid_fee", 0),
            "mempool_high_fee": mempool.get("high_fee", 0),
            "unconfirmed_txs": mempool.get("unconfirmed_txs", 0),
        })
    current.update(halving_info)

    # Today's content
    knowledge["todays_thought"] = thought
    knowledge["todays_headlines"] = headlines
    knowledge["todays_reddit"] = reddit_posts
    knowledge["todays_insights"] = insights
    knowledge["todays_tips"] = tips
    knowledge["todays_fact"] = fact
    knowledge["todays_prediction"] = prediction

    # Price history
    price_history = kb.setdefault("price_history", [])
    if price_data and price_data.get("price_usd"):
        price_history.append({
            "date": today,
            "price": price_data["price_usd"],
            "change_24h": price_data.get("change_24h_pct", 0),
            "market_cap": price_data.get("market_cap_usd", 0),
        })
        if len(price_history) > MAX_PRICE_HISTORY:
            price_history[:] = price_history[-MAX_PRICE_HISTORY:]

    # Fear & Greed history
    fg_history = kb.setdefault("fear_greed_history", [])
    if fg:
        # avoid duplicates for today
        if not fg_history or fg_history[-1].get("date") != today:
            fg_history.append({"date": today, "value": fg["value"], "label": fg["label"]})
        if len(fg_history) > MAX_FG_HISTORY:
            fg_history[:] = fg_history[-MAX_FG_HISTORY:]

    # Topics
    topics_all = kb.setdefault("topics_learned", [])
    for t in topics:
        entry = next((x for x in topics_all if x["topic"] == t), None)
        if entry:
            entry["count"] = entry.get("count", 1) + 1
            entry["last_seen"] = today
        else:
            topics_all.append({"topic": t, "count": 1, "first_seen": today, "last_seen": today})
    topics_all.sort(key=lambda x: x["count"], reverse=True)

    # Evolution log entry
    evo_entry = {
        "cycle": cycle_num,
        "date": today,
        "timestamp": now_iso,
        "price_usd": price_data.get("price_usd", 0) if price_data else 0,
        "change_24h": price_data.get("change_24h_pct", 0) if price_data else 0,
        "fear_greed_value": fg["value"] if fg else 0,
        "fear_greed_label": fg["label"] if fg else "Unknown",
        "block_height": bh,
        "topics": topics,
        "headline_count": len(headlines),
        "thought_preview": thought[:140] + "...",
    }
    evo_log = knowledge.setdefault("evolution_log", [])
    evo_log.append(evo_entry)
    if len(evo_log) > MAX_EVOLUTION_LOG:
        evo_log[:] = evo_log[-MAX_EVOLUTION_LOG:]

    # Meta update
    meta.update({
        "name": "Ollie",
        "subject": "Bitcoin",
        "total_cycles": cycle_num,
        "last_updated": now_iso,
        "version": "2.0",
        "status": "active",
    })
    if not meta.get("genesis"):
        meta["genesis"] = today

    # ── SAVE ──────────────────────────────────────────────────────────────────
    print("\n[PHASE 7] Saving knowledge to disk...")
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(knowledge, f, indent=2, ensure_ascii=False)

    size_kb = os.path.getsize(DATA_FILE) / 1024
    print(f"  Saved {DATA_FILE} ({size_kb:.1f} KB)")

    print("\n" + "=" * 60)
    print(f"  CYCLE #{cycle_num} COMPLETE — {today}")
    print(f"  BTC Price: ${price_data.get('price_usd', 0):,.0f}" if price_data else "  Price: unavailable")
    print(f"  Fear & Greed: {fg['value']} ({fg['label']})" if fg else "  F&G: unavailable")
    print(f"  Block Height: {bh:,}")
    print(f"  Topics: {', '.join(topics[:5])}")
    print(f"  Knowledge nodes: {len(topics_all)}")
    print(f"  Price history: {len(price_history)} days")
    print("=" * 60)

if __name__ == "__main__":
    main()
