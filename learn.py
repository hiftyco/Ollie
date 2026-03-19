#!/usr/bin/env python3
"""
OLLIE — Autonomous Bitcoin Intelligence Engine v3.1
Runs every 6 hours via GitHub Actions.
Mission: Learn everything about Bitcoin. Teach and guide every Bitcoiner.
"""

import json, os, urllib.request, urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import time, re

DATA_FILE = "data/knowledge.json"
MAX_EVOLUTION_LOG = 365
MAX_PRICE_HISTORY = 1460
MAX_HEADLINES = 12
MAX_INSIGHTS = 15
NEXT_HALVING_BLOCK = 1050000
HALVING_REWARD = 3.125

POSITIVE_WORDS = ["surge","rally","bull","moon","pump","breakthrough","adoption","halving","upgrade","growth","rise","gain","profit","success","bullish","optimism","recovery","institutional","etf","record","high","milestone","accumulate","approve","launch"]
NEGATIVE_WORDS = ["crash","dump","bear","sell","decline","hack","ban","regulation","fall","loss","drop","fear","panic","scam","exploit","bearish","pessimism","crisis","lawsuit","fine","restrict","warning","fraud","theft","collapse"]

BITCOIN_FACTS = [
    "Bitcoin's genesis block contains: 'The Times 03/Jan/2009 Chancellor on brink of second bailout for banks.' — Satoshi's message to the world.",
    "Only 21 million Bitcoin will ever exist. ~3-4 million are estimated lost forever, making scarcity even more extreme.",
    "Satoshi Nakamoto's identity remains unknown. Their ~1.1M BTC wallet has never moved — the greatest HODLer of all time.",
    "The Lightning Network enables Bitcoin payments in milliseconds with fees of fractions of a cent.",
    "Bitcoin mining uses over 50% renewable energy — more than almost any other industry globally.",
    "The first real-world Bitcoin purchase: 10,000 BTC for two pizzas on May 22, 2010. Bitcoin Pizza Day is celebrated every year.",
    "Bitcoin's SHA-256 cryptography would take longer than the age of the universe to brute-force with classical computers.",
    "Every ~4 years, the block reward halves. This programmatic supply shock has historically preceded massive bull markets.",
    "Bitcoin has 99.99% uptime since January 3, 2009 — more reliable than any bank in human history.",
    "El Salvador was the first country to adopt Bitcoin as legal tender in September 2021.",
    "The UTXO model makes Bitcoin transactions verifiable, auditable, and more privacy-preserving than account-based systems.",
    "Bitcoin's difficulty adjusts every 2016 blocks (~2 weeks) to maintain 10-minute block times — automatically.",
    "There are more possible Bitcoin private keys than atoms in the observable universe. Your wallet is mathematically unbreakable.",
    "A Bitcoin transaction is irreversible by design — no chargebacks, no reversals, no third party needed.",
    "Bitcoin Script is intentionally not Turing-complete, making it more secure than smart contract platforms.",
    "The total value of all gold ever mined is ~$13 trillion. Bitcoin's market cap has exceeded $1 trillion multiple times.",
    "Running a Bitcoin full node costs ~$300 in hardware and gives you complete financial sovereignty.",
    "Taproot (activated Nov 2021) makes Bitcoin transactions more private, efficient, and powerful.",
    "Over 400 million people globally are estimated to own some Bitcoin as of 2024.",
    "Bitcoin's whitepaper is only 9 pages. Satoshi solved a decades-old computer science problem with elegant simplicity.",
]

LEARNING_PATHS = {
    "beginner": [
        {"title": "What is Bitcoin?", "lesson": "Bitcoin is digital money that no government, bank, or corporation controls. It runs on a decentralized network of thousands of computers worldwide. Anyone can use it, anywhere, without permission.", "key_concepts": ["decentralization","peer-to-peer","digital scarcity","permissionless"]},
        {"title": "Why Does Bitcoin Matter?", "lesson": "Bitcoin solves the double-spend problem without requiring trust in a third party — for the first time in human history. It's censorship-resistant money that can't be inflated away or easily confiscated.", "key_concepts": ["trustlessness","censorship resistance","sound money","store of value"]},
        {"title": "How to Get Your First Bitcoin", "lesson": "You can buy Bitcoin on exchanges like Coinbase, Kraken, or Strike. The most important next step: move it to your own wallet. 'Not your keys, not your coins' is the golden rule.", "key_concepts": ["exchanges","wallets","self-custody","seed phrase"]},
        {"title": "Storing Bitcoin Safely", "lesson": "A hardware wallet (Ledger, Coldcard, Trezor) keeps your private keys offline. Write your 12-24 word seed phrase on paper or metal — never store it digitally. Back it up in 2+ secure locations.", "key_concepts": ["hardware wallet","cold storage","seed phrase","backup","security"]},
        {"title": "Bitcoin vs. Fiat Money", "lesson": "Fiat currency loses purchasing power through inflation — the dollar has lost 98% of its value since 1913. Bitcoin has a fixed supply of 21 million. It cannot be inflated. It is the hardest money ever created.", "key_concepts": ["inflation","fixed supply","hard money","purchasing power"]},
        {"title": "Understanding Satoshis", "lesson": "1 Bitcoin = 100,000,000 satoshis (sats). You don't need to buy a whole Bitcoin. Most people start by stacking sats. Think in sats — it reframes your entire perspective.", "key_concepts": ["satoshis","sats","divisibility","stacking"]},
    ],
    "intermediate": [
        {"title": "The Blockchain Explained", "lesson": "Every Bitcoin transaction is recorded on a public ledger. Blocks are chained together cryptographically using SHA-256 hashes — once written, history is practically immutable forever.", "key_concepts": ["blockchain","SHA-256","merkle tree","immutability","hash"]},
        {"title": "Mining & Proof of Work", "lesson": "Miners compete to solve a cryptographic puzzle. The winner adds the next block and earns freshly minted BTC plus transaction fees. This secures the network and issues new supply.", "key_concepts": ["mining","proof of work","difficulty","hash rate","block reward"]},
        {"title": "The Halving Cycle", "lesson": "Every 210,000 blocks (~4 years), the block reward halves. This creates programmatic supply shocks. Combined with growing demand, halvings have historically preceded major price appreciation.", "key_concepts": ["halving","supply shock","block reward","cycles","scarcity"]},
        {"title": "Lightning Network", "lesson": "Lightning enables instant, near-free Bitcoin payments by opening off-chain payment channels. Two parties can transact millions of times without touching the main chain. It scales Bitcoin to billions.", "key_concepts": ["lightning","payment channels","routing","liquidity","HTLC"]},
        {"title": "Bitcoin Wallets Deep Dive", "lesson": "HD wallets derive unlimited addresses from one seed phrase using BIP32/BIP39. Your seed phrase IS your Bitcoin — it restores all funds on any compatible wallet, forever.", "key_concepts": ["HD wallet","BIP32","BIP39","derivation path","xpub","seed phrase"]},
        {"title": "Transaction Fees & Mempool", "lesson": "Miners prioritize transactions by fee rate (sat/vByte). The mempool is the waiting room for unconfirmed transactions. During congestion fees spike — during quiet times you can transact for 1-2 sats/vByte.", "key_concepts": ["mempool","fee rate","sat/vbyte","RBF","CPFP","congestion"]},
    ],
    "advanced": [
        {"title": "UTXO Model", "lesson": "Bitcoin doesn't use account balances — it uses Unspent Transaction Outputs (UTXOs). Understanding UTXO selection is key to optimizing fees, privacy, and wallet management.", "key_concepts": ["UTXO","coin selection","change outputs","consolidation","fee optimization"]},
        {"title": "Taproot & Schnorr Signatures", "lesson": "Taproot (BIP340-342, activated Nov 2021) enables key aggregation, more private multisig, and efficient complex scripts. Schnorr signatures are smaller and allow signature aggregation.", "key_concepts": ["taproot","schnorr","MAST","scriptpath","keypath","BIP340"]},
        {"title": "Bitcoin Script", "lesson": "Bitcoin's stack-based scripting language enables complex spending conditions: multisig, timelocks (CSV/CLTV), HTLCs for Lightning. Intentionally not Turing-complete for security.", "key_concepts": ["script","multisig","timelock","CLTV","CSV","HTLC","opcodes"]},
        {"title": "Running a Full Node", "lesson": "A full node downloads and independently verifies every block since genesis. You trust nobody — you verify everything. It protects you and strengthens the network. Start with Umbrel on a Raspberry Pi.", "key_concepts": ["full node","verification","SPV","pruning","IBD","Bitcoin Core"]},
        {"title": "On-Chain Analytics", "lesson": "Reading the blockchain reveals market psychology: HODL waves show conviction, SOPR measures profit-taking, exchange flows track institutional moves, NVT compares value to usage.", "key_concepts": ["SOPR","HODL waves","realized cap","NVT","MVRV","exchange flows"]},
        {"title": "Privacy in Bitcoin", "lesson": "Bitcoin is pseudonymous, not anonymous. CoinJoin, PayJoin, and Lightning improve privacy. Avoid address reuse. Use Tor. Understand chain analysis to protect yourself.", "key_concepts": ["coinjoin","payjoin","address reuse","chain analysis","privacy","tor"]},
    ]
}

THOUGHT_TEMPLATES = [
    "At block {block_height}, Bitcoin's ledger is {days_alive} days old and has never been hacked, reversed, or stopped. Every block is a heartbeat of the most secure financial system ever built.",
    "Fear & Greed at {fg_value} — {fg_label}. {crowd_signal} The patient accumulator has always won. Every cycle, the same lesson. Zoom out.",
    "Hash rate: {hash_rate} EH/s. The most powerful computational network in human history grows stronger every day. Miners bet their capital on Bitcoin's future. Watch what they do.",
    "${price:,.0f} per Bitcoin today. {blocks_to_halving} blocks until the next supply halving. The clock ticks. The math doesn't change. 21 million, forever.",
    "Ollie has completed {generation} learning cycles — absorbing prices, news, network data, and on-chain signals. Each cycle deepens the map. The signal gets clearer.",
    "The mempool holds {mempool_txs} transactions right now. {fee_signal} Borderless. Permissionless. Unstoppable. This is what financial sovereignty looks like.",
    "Since January 3, 2009: {days_alive} days of uptime. No outage. No bailout. No CEO to blame. Bitcoin just works — and Ollie is here to help you understand why that matters.",
    "Sentiment: {fg_label} at {fg_value}/100. In {days_alive} days of Bitcoin history, extreme fear has been the greatest gift for those who understood what they owned.",
]

def fetch(url, timeout=20, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "Mozilla/5.0 (compatible; OllieBot/3.1; +https://hiftyco.github.io/Ollie)")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    return None

def fetch_json(url, timeout=20):
    raw = fetch(url, timeout=timeout)
    if raw:
        try: return json.loads(raw)
        except: pass
    return None

def get_price():
    print("  Fetching price...")
    for fn in [_cg, _coincap, _kraken, _blockchain_info]:
        try:
            p = fn()
            if p and p.get("price_usd", 0) > 0:
                print(f"    ${p['price_usd']:,.0f} from {p['source']}")
                return p
        except: pass
    return None

def _cg():
    d = fetch_json("https://api.coingecko.com/api/v3/coins/bitcoin?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false")
    if not d: return None
    md = d.get("market_data", {})
    gl = fetch_json("https://api.coingecko.com/api/v3/global") or {}
    dom = round(gl.get("data",{}).get("market_cap_percentage",{}).get("btc",0),1)
    p = md.get("current_price",{}).get("usd",0) or 0
    ath = md.get("ath",{}).get("usd",0) or 0
    return {"price_usd":p,"market_cap_usd":md.get("market_cap",{}).get("usd",0) or 0,
            "volume_24h_usd":md.get("total_volume",{}).get("usd",0) or 0,
            "change_24h_pct":round(md.get("price_change_percentage_24h",0) or 0,2),
            "change_7d_pct":round(md.get("price_change_percentage_7d",0) or 0,2),
            "change_30d_pct":round(md.get("price_change_percentage_30d",0) or 0,2),
            "ath_usd":ath,"ath_date":md.get("ath_date",{}).get("usd",""),
            "from_ath_pct":round((p-ath)/ath*100,1) if ath and p else 0,
            "circulating_supply":md.get("circulating_supply",0) or 0,
            "max_supply":21000000,"dominance_pct":dom,"source":"coingecko"}

def _coincap():
    d = fetch_json("https://api.coincap.io/v2/assets/bitcoin")
    if not d or "data" not in d: return None
    x = d["data"]
    p = float(x.get("priceUsd",0) or 0)
    return {"price_usd":p,"market_cap_usd":float(x.get("marketCapUsd",0) or 0),
            "volume_24h_usd":float(x.get("volumeUsd24Hr",0) or 0),
            "change_24h_pct":round(float(x.get("changePercent24Hr",0) or 0),2),
            "change_7d_pct":0,"change_30d_pct":0,"ath_usd":0,"ath_date":"","from_ath_pct":0,
            "circulating_supply":float(x.get("supply",0) or 0),"max_supply":21000000,
            "dominance_pct":0,"source":"coincap"}

def _kraken():
    d = fetch_json("https://api.kraken.com/0/public/Ticker?pair=XBTUSD")
    if not d or "result" not in d: return None
    t = d["result"].get("XXBTZUSD",{})
    if not t: return None
    return {"price_usd":float(t["c"][0]),"market_cap_usd":0,
            "volume_24h_usd":float(t.get("v",[0,0])[1]),
            "change_24h_pct":0,"change_7d_pct":0,"change_30d_pct":0,
            "ath_usd":0,"ath_date":"","from_ath_pct":0,
            "circulating_supply":0,"max_supply":21000000,"dominance_pct":0,"source":"kraken"}

def _blockchain_info():
    d = fetch_json("https://blockchain.info/ticker")
    if not d or "USD" not in d: return None
    return {"price_usd":d["USD"].get("last",0),"market_cap_usd":0,"volume_24h_usd":0,
            "change_24h_pct":0,"change_7d_pct":0,"change_30d_pct":0,
            "ath_usd":0,"ath_date":"","from_ath_pct":0,
            "circulating_supply":0,"max_supply":21000000,"dominance_pct":0,"source":"blockchain.info"}

def get_fear_greed():
    print("  Fetching Fear & Greed...")
    d = fetch_json("https://api.alternative.me/fng/?limit=30")
    if not d or "data" not in d: return None
    latest = d["data"][0]
    return {"value":int(latest.get("value",50)),
            "label":latest.get("value_classification","Neutral"),
            "history":[{"date":datetime.fromtimestamp(int(x["timestamp"]),tz=timezone.utc).strftime("%Y-%m-%d"),
                        "value":int(x["value"]),"label":x["value_classification"]}
                       for x in d["data"][:30]]}

def get_chain_stats():
    print("  Fetching blockchain stats...")
    d = fetch_json("https://blockchain.info/stats?format=json")
    if not d: return None
    return {"block_height":d.get("n_blocks_total",0),
            "hash_rate_ehs":round((d.get("hash_rate",0) or 0)/1e9,2),
            "difficulty":d.get("difficulty",0),
            "miners_revenue_usd":d.get("miners_revenue_usd",0),
            "n_tx_24h":d.get("n_tx",0)}

def get_mempool():
    print("  Fetching mempool...")
    fees = fetch_json("https://mempool.space/api/v1/fees/recommended")
    info = fetch_json("https://mempool.space/api/mempool")
    bh = None
    raw = fetch("https://mempool.space/api/blocks/tip/height")
    if raw:
        try: bh = int(raw.strip())
        except: pass
    if not fees: return None
    return {"low_fee":fees.get("hourFee",1),"mid_fee":fees.get("halfHourFee",2),
            "high_fee":fees.get("fastestFee",3),
            "unconfirmed_txs":(info or {}).get("count",0),"block_height":bh}

def get_lightning():
    print("  Fetching Lightning stats...")
    d = fetch_json("https://mempool.space/api/v1/lightning/statistics/latest")
    if not d: return None
    latest = d.get("latest", d)
    cap = latest.get("total_capacity",0) or 0
    return {"node_count":latest.get("node_count",0),
            "channel_count":latest.get("channel_count",0),
            "total_capacity_btc":round(cap/1e8,2) if cap>10000 else cap}

def parse_rss(url, max_items=5):
    raw = fetch(url, timeout=20)
    if not raw: return []
    items = []
    # Method 1: clean namespaces and parse XML
    try:
        clean = re.sub(r'\s+xmlns(?::[^=]+)?="[^"]*"','',raw)
        clean = re.sub(r'<[a-zA-Z][a-zA-Z0-9]*:[a-zA-Z][^>]*>','',clean)
        clean = re.sub(r'</[a-zA-Z][a-zA-Z0-9]*:[a-zA-Z][^>]*>','',clean)
        root = ET.fromstring(clean)
        ch = root.find(".//channel") or root
        for item in ch.findall(".//item")[:max_items]:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            pub = (item.findtext("pubDate") or "").strip()
            desc = ""
            de = item.find("description")
            if de is not None and de.text:
                desc = re.sub(r"<[^>]+>","",de.text).strip()[:250]
            if title and len(title) > 5:
                items.append({"title":title,"link":link,"published":pub,"summary":desc})
    except:
        # Method 2: regex fallback
        try:
            titles = re.findall(r'<title[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>',raw,re.DOTALL)
            links = re.findall(r'<link[^>]*>(https?://[^<]+)</link>',raw)
            for i,t in enumerate(titles[1:max_items+1]):
                t = t.strip()
                if t and len(t)>5:
                    lnk = links[i] if i < len(links) else ""
                    items.append({"title":t,"link":lnk.strip(),"published":"","summary":""})
        except: pass
    return items

def get_news():
    print("  Fetching news...")
    feeds = [
        ("Bitcoin Magazine","https://bitcoinmagazine.com/.rss/full/"),
        ("Cointelegraph","https://cointelegraph.com/rss"),
        ("CoinDesk","https://www.coindesk.com/arc/outboundfeeds/rss/"),
        ("Decrypt","https://decrypt.co/feed"),
        ("Bitcoin Optech","https://bitcoinops.org/feed.xml"),
        ("The Block","https://www.theblock.co/rss.xml"),
        ("Bitcoin.com","https://news.bitcoin.com/feed/"),
        ("Cointelegraph Markets","https://cointelegraph.com/rss/category/markets/"),
    ]
    all_items = []
    seen = set()
    for source, url in feeds:
        for item in parse_rss(url, max_items=3):
            key = item["title"][:40].lower().strip()
            if key in seen or len(key) < 5: continue
            seen.add(key)
            tl = item["title"].lower()
            pos = sum(1 for w in POSITIVE_WORDS if w in tl)
            neg = sum(1 for w in NEGATIVE_WORDS if w in tl)
            btc = sum(1 for w in ["bitcoin","btc","satoshi","lightning","halving","mining"] if w in tl)
            item["source"] = source
            item["sentiment"] = "positive" if pos>neg else ("negative" if neg>pos else "neutral")
            item["relevance"] = pos+neg+btc
            all_items.append(item)
    all_items.sort(key=lambda x: x["relevance"], reverse=True)
    print(f"    Got {len(all_items)} headlines")
    return all_items[:MAX_HEADLINES]

def get_discussions():
    print("  Fetching community discussions (Hacker News)...")
    items = []
    try:
        d = fetch_json("https://hn.algolia.com/api/v1/search?query=bitcoin&tags=story&hitsPerPage=10&numericFilters=points>5")
        if d and "hits" in d:
            for h in d["hits"][:8]:
                title = h.get("title","")
                if title and any(w in title.lower() for w in ["bitcoin","btc","lightning","crypto","satoshi","blockchain","halving"]):
                    items.append({"title":title,"score":h.get("points",0),
                                  "comments":h.get("num_comments",0),
                                  "url":f"https://news.ycombinator.com/item?id={h.get('objectID','')}",
                                  "source":"Hacker News"})
    except Exception as e:
        print(f"    Failed: {e}")
    print(f"    Got {len(items)} discussions")
    return items[:8]

def get_bip_updates():
    print("  Fetching BIP updates...")
    d = fetch_json("https://api.github.com/repos/bitcoin/bips/commits?per_page=5")
    if not d: return []
    return [{"message":c.get("commit",{}).get("message","")[:120],
             "date":c.get("commit",{}).get("author",{}).get("date","")[:10],
             "sha":c.get("sha","")[:7]} for c in d[:5]]

def generate_insights(price, fg, chain, mempool):
    print("  Generating insights...")
    insights = []
    now = datetime.now(timezone.utc)

    if price:
        p = price["price_usd"]
        c24 = price.get("change_24h_pct",0)
        c7 = price.get("change_7d_pct",0)
        dom = price.get("dominance_pct",0)
        fath = price.get("from_ath_pct",0)
        if c24 > 5: insights.append({"type":"price","icon":"🚀","text":f"BTC surged +{c24:.1f}% in 24 hours. Strong buying pressure. Watch volume — is this conviction or a wick? Zoom out before reacting.","level":"intermediate"})
        elif c24 > 2: insights.append({"type":"price","icon":"📈","text":f"BTC up {c24:.1f}% today. Healthy positive momentum. Conviction buyers are active.","level":"beginner"})
        elif c24 < -5: insights.append({"type":"price","icon":"📉","text":f"BTC dropped {abs(c24):.1f}% today. In Bitcoin's history, every single dip was eventually recovered. Long-term holders know this.","level":"beginner"})
        elif c24 < -2: insights.append({"type":"price","icon":"⚠️","text":f"BTC down {abs(c24):.1f}%. Market shaking out weak hands. On-chain data still shows strong holder conviction.","level":"intermediate"})
        else: insights.append({"type":"price","icon":"⚖️","text":f"BTC consolidating at ${p:,.0f}. Low volatility often precedes large moves. The coil tightens.","level":"intermediate"})
        if c7 > 15: insights.append({"type":"trend","icon":"🔥","text":f"7-day return: +{c7:.1f}%. Weekly momentum is explosive. Monitor for exhaustion signals.","level":"advanced"})
        if fath < -60: insights.append({"type":"cycle","icon":"💎","text":f"BTC is {abs(fath):.0f}% below its all-time high. Historically buying at 50%+ below ATH has been one of the best risk/reward setups in all of finance.","level":"intermediate"})
        elif fath > -10: insights.append({"type":"cycle","icon":"👑","text":f"BTC is within {abs(fath):.0f}% of its all-time high. Price discovery mode — uncharted territory.","level":"intermediate"})
        if dom > 55: insights.append({"type":"dominance","icon":"₿","text":f"Bitcoin dominance at {dom}%. Capital concentrating in BTC — often seen in early-to-mid bull cycles.","level":"advanced"})

    if fg:
        v = fg["value"]
        lbl = fg["label"]
        if v <= 15: insights.append({"type":"sentiment","icon":"😱","text":f"EXTREME FEAR at {v}/100. Historically rare. Every previous extreme fear reading was followed by recovery for those who held. 'Be greedy when others are fearful.'","level":"beginner"})
        elif v <= 30: insights.append({"type":"sentiment","icon":"😰","text":f"Fear at {v}/100 ({lbl}). Smart money accumulates during fear. Dollar-cost averaging through fear is a time-tested strategy.","level":"beginner"})
        elif v >= 80: insights.append({"type":"sentiment","icon":"🤑","text":f"EXTREME GREED at {v}/100. Everyone is euphoric — this is when discipline matters most. Markets correct from greed extremes.","level":"intermediate"})
        elif v >= 65: insights.append({"type":"sentiment","icon":"😊","text":f"Greed at {v}/100 ({lbl}). Positive vibes — stay humble. Stick to your strategy.","level":"beginner"})

    if chain:
        hr = chain.get("hash_rate_ehs",0)
        if hr > 0: insights.append({"type":"network","icon":"⛏️","text":f"Hash rate: {hr} EH/s. {'Record territory — ' if hr > 800 else ''}Miners are deploying massive capital to secure Bitcoin. They vote with their hardware.","level":"intermediate"})

    if mempool:
        unconf = mempool.get("unconfirmed_txs",0)
        low = mempool.get("low_fee",1)
        high = mempool.get("high_fee",3)
        if unconf > 100000: insights.append({"type":"fees","icon":"🚦","text":f"Mempool congested: {unconf:,} unconfirmed txs. Use {high} sat/vB for fast confirmation. Not urgent? Wait for fees to drop.","level":"beginner"})
        elif unconf < 3000: insights.append({"type":"fees","icon":"✅","text":f"Mempool nearly empty — only {unconf:,} transactions. Best time to consolidate UTXOs or do non-urgent on-chain transactions at {low} sat/vB.","level":"intermediate"})

    day_idx = int(now.strftime("%j")) % len(BITCOIN_FACTS)
    insights.append({"type":"fact","icon":"🧠","text":BITCOIN_FACTS[day_idx],"level":"beginner"})
    return insights[:MAX_INSIGHTS]

def generate_tips(price, fg):
    now = datetime.now(timezone.utc)
    pool = [
        {"icon":"🔑","tip":"Not your keys, not your coins. If your Bitcoin sits on an exchange, you don't truly own it. Move it to a hardware wallet today.","category":"security"},
        {"icon":"📅","tip":"Dollar-cost averaging (DCA) removes emotion from Bitcoin. Set a fixed weekly or monthly buy — never look at the price when you buy.","category":"strategy"},
        {"icon":"📝","tip":"Write your seed phrase on metal, not paper. Paper burns and floods. Your seed phrase should survive a house fire.","category":"security"},
        {"icon":"⚡","tip":"Try Lightning Network for your first Bitcoin payment. Download Strike or Wallet of Satoshi and experience instant, near-free transactions.","category":"usage"},
        {"icon":"📚","tip":"Read the Bitcoin whitepaper — it's only 9 pages. Find it at bitcoin.org/bitcoin.pdf. It's clearer and more elegant than most people expect.","category":"education"},
        {"icon":"🖥️","tip":"Run your own Bitcoin node. Start with Umbrel on a Raspberry Pi (~$100). When you verify your own transactions, you trust nobody.","category":"advanced"},
        {"icon":"🧮","tip":"Think in satoshis, not dollars. 1 sat = $0.0007 today. When Bitcoin reaches $1M, that same sat = $0.01. Stack sats.","category":"mindset"},
        {"icon":"🌍","tip":"Bitcoin is borderless money. Try sending BTC internationally and compare it to a wire transfer. No forms. No waiting. No permission needed.","category":"education"},
        {"icon":"🔒","tip":"NEVER share your seed phrase — ever, with anyone, under any circumstances. Anyone who asks is a scammer. Full stop.","category":"security"},
        {"icon":"📊","tip":"Check lookintobitcoin.com for on-chain data. The blockchain tells truths that price charts alone don't show.","category":"education"},
        {"icon":"🎯","tip":"Set a 4-year horizon minimum. Bitcoin's halving cycle means the best returns come to those who can wait through the full cycle.","category":"strategy"},
        {"icon":"⚙️","tip":"Learn about multisig. 2-of-3 multisig means you need 2 of 3 keys to spend. It's the gold standard for securing significant holdings.","category":"advanced"},
    ]
    idx = int(now.strftime("%j")) % len(pool)
    tips = [pool[idx], pool[(idx+1) % len(pool)]]
    if fg:
        if fg["value"] <= 25: tips.append({"icon":"💎","tip":"The market is in extreme fear right now. History says: this is when long-term wealth is built. Stay humble, stack sats, zoom out.","category":"strategy"})
        elif fg["value"] >= 80: tips.append({"icon":"🛑","tip":"Extreme greed is dangerous. This is when people buy tops and use leverage. Stay disciplined — the market always reverts.","category":"strategy"})
    if price and price.get("from_ath_pct",0) < -50:
        tips.append({"icon":"🎯","tip":"Bitcoin is over 50% below its ATH. In every previous cycle, buying this deep below ATH produced extraordinary 3-4 year returns.","category":"strategy"})
    return tips[:4]

def generate_thought(price, chain, fg, mempool, generation):
    now = datetime.now(timezone.utc)
    genesis = datetime(2009,1,3,tzinfo=timezone.utc)
    days_alive = (now-genesis).days
    p = (price or {}).get("price_usd",0)
    fg_val = (fg or {}).get("value",50)
    fg_label = (fg or {}).get("label","Neutral")
    hr = (chain or {}).get("hash_rate_ehs",0)
    block_h = (chain or {}).get("block_height") or (mempool or {}).get("block_height") or 0
    blocks_left = max(0,NEXT_HALVING_BLOCK-block_h) if block_h else 0
    mempool_txs = f"{(mempool or {}).get('unconfirmed_txs',0):,}"
    low_fee = (mempool or {}).get("low_fee",1)
    crowd = "The crowd trembles." if fg_val<=30 else ("The crowd chases." if fg_val>=70 else "The crowd watches.")
    fee_signal = f"Fees: {low_fee} sat/vB." if low_fee else "Fees are normal."
    tmpl_idx = (int(now.strftime("%H"))//6) % len(THOUGHT_TEMPLATES)
    try:
        return THOUGHT_TEMPLATES[tmpl_idx].format(
            block_height=f"{block_h:,}" if block_h else "unknown",
            blocks_to_halving=f"{blocks_left:,}" if blocks_left else "soon",
            fg_value=fg_val, fg_label=fg_label, crowd_signal=crowd,
            hash_rate=hr, price=p, generation=generation,
            mempool_txs=mempool_txs, fee_signal=fee_signal,
            days_alive=f"{days_alive:,}")
    except:
        return f"Ollie has completed {generation} learning cycles. Bitcoin at ${p:,.0f}. {days_alive:,} days of uptime. The network never stops."

def generate_prediction(price, fg, chain):
    if not price: return {"outlook":"neutral","text":"Insufficient data this cycle.","confidence":0,"score":0,"signals":[]}
    p = price["price_usd"]
    c24 = price.get("change_24h_pct",0)
    c7 = price.get("change_7d_pct",0)
    fath = price.get("from_ath_pct",0)
    fg_val = (fg or {}).get("value",50)
    hr = (chain or {}).get("hash_rate_ehs",0)
    score = 0; signals = []
    if c24>3: score+=2; signals.append(f"24h surge +{c24:.1f}%")
    elif c24>1: score+=1; signals.append(f"24h positive +{c24:.1f}%")
    elif c24<-3: score-=2; signals.append(f"24h selloff {c24:.1f}%")
    elif c24<-1: score-=1; signals.append(f"24h slight negative {c24:.1f}%")
    if c7>8: score+=2; signals.append(f"Weekly strong +{c7:.1f}%")
    elif c7>3: score+=1
    elif c7<-8: score-=2
    elif c7<-3: score-=1
    if fg_val<=20: score+=1; signals.append(f"Contrarian: extreme fear ({fg_val})")
    elif fg_val>=85: score-=1; signals.append(f"Caution: extreme greed ({fg_val})")
    if fath<-60: score+=1; signals.append("Deep ATH discount")
    if hr>700: score+=1; signals.append(f"Hash rate strong {hr} EH/s")
    sig = " · ".join(signals[:3]) if signals else "Mixed signals"
    if score>=4: o,t = "strongly bullish",f"Multiple strong bullish signals. {sig}. Short-term bias: significantly higher."
    elif score>=2: o,t = "bullish",f"Positive signals outweigh negatives. {sig}. Lean bullish."
    elif score==1: o,t = "cautiously bullish",f"Slight positive edge. {sig}. Stay patient."
    elif score==0: o,t = "neutral",f"Balanced signals. {sig}. Discipline matters most here."
    elif score==-1: o,t = "cautiously bearish",f"Slight negative bias. {sig}. Not a crisis — not the time for aggression."
    elif score>=-3: o,t = "bearish",f"Negative signals dominate. {sig}. Defensive posture suggested."
    else: o,t = "strongly bearish",f"Multiple bearish signals. {sig}. Risk management is priority."
    return {"outlook":o,"text":t,"confidence":min(abs(score)*15+20,85),"score":score,"signals":signals}

def evolve(existing):
    print("  Self-improvement cycle...")
    log = existing.get("evolution_log",[])
    if len(log)>=2:
        last,prev = log[-1],log[-2]
        lp,pp = last.get("price_usd",0),prev.get("price_usd",0)
        outlook = last.get("prediction_outlook","neutral")
        if lp and pp:
            log[-1]["prediction_score"] = 1 if ((lp>pp)==("bullish" in outlook)) else -1
    scored = [e for e in log if "prediction_score" in e]
    acc = round(sum(1 for e in scored if e["prediction_score"]>0)/len(scored)*100,1) if scored else 0
    return log, acc

def main():
    print("="*60)
    print(f"OLLIE v3.1 — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("="*60)
    existing = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f: existing = json.load(f)
        except: pass
    evo_log, accuracy = evolve(existing)
    generation = len(evo_log)+1

    print("\n[PHASE 1] Live Bitcoin data...")
    price = get_price()
    fg = get_fear_greed()
    chain = get_chain_stats()
    mempool = get_mempool()
    lightning = get_lightning()

    print("\n[PHASE 2] News & community intelligence...")
    headlines = get_news()
    discussions = get_discussions()
    bip_updates = get_bip_updates()

    print("\n[PHASE 3] Synthesizing wisdom...")
    insights = generate_insights(price,fg,chain,mempool)
    tips = generate_tips(price,fg)
    thought = generate_thought(price,chain,fg,mempool,generation)
    prediction = generate_prediction(price,fg,chain)

    now = datetime.now(timezone.utc)
    genesis = datetime(2009,1,3,tzinfo=timezone.utc)
    block_h = (chain or {}).get("block_height") or (mempool or {}).get("block_height") or 0
    blocks_left = max(0,NEXT_HALVING_BLOCK-block_h) if block_h else 0
    est_days = round(blocks_left*10/1440,1) if blocks_left else 0
    progress_pct = round((block_h%210000)/210000*100,2) if block_h else 0

    evo_log.append({"generation":generation,"timestamp":now.isoformat(),
                    "date":now.strftime("%Y-%m-%d"),"cycle_utc":now.strftime("%H:00"),
                    "price_usd":(price or {}).get("price_usd",0),
                    "fg_value":(fg or {}).get("value",0),
                    "headlines_absorbed":len(headlines),
                    "insights_generated":len(insights),
                    "prediction_outlook":prediction["outlook"],
                    "hash_rate_ehs":(chain or {}).get("hash_rate_ehs",0)})
    if len(evo_log)>MAX_EVOLUTION_LOG: evo_log=evo_log[-MAX_EVOLUTION_LOG:]

    ph = existing.get("price_history",[])
    if price and price.get("price_usd",0)>0:
        ph.append({"ts":now.strftime("%Y-%m-%d %H:00"),"p":round(price["price_usd"],2),
                   "c":price.get("change_24h_pct",0),"fg":(fg or {}).get("value",50)})
        if len(ph)>MAX_PRICE_HISTORY: ph=ph[-MAX_PRICE_HISTORY:]

    knowledge = {
        "meta":{"version":"3.1","generation":generation,
                "last_updated":now.isoformat(),
                "last_updated_human":now.strftime("%B %d, %Y at %H:%M UTC"),
                "update_cycle":"every 6 hours",
                "mission":"Learn everything about Bitcoin. Teach and guide every Bitcoiner on their journey.",
                "prediction_accuracy_pct":accuracy,
                "days_alive":(now-genesis).days,
                "total_cycles":generation},
        "current":{"price":price,"fear_greed":fg,"blockchain":chain,
                   "mempool":mempool,"lightning":lightning,
                   "halving":{"current_reward_btc":HALVING_REWARD,"next_block":NEXT_HALVING_BLOCK,
                              "current_block":block_h,"blocks_remaining":blocks_left,
                              "estimated_days":est_days,"progress_pct":progress_pct}},
        "intelligence":{"todays_thought":thought,"todays_prediction":prediction,
                        "todays_insights":insights,"todays_tips":tips,
                        "todays_fact":BITCOIN_FACTS[int(now.strftime("%j"))%len(BITCOIN_FACTS)]},
        "news":{"headlines":headlines,"discussions":discussions,"bip_updates":bip_updates},
        "education":{"learning_paths":LEARNING_PATHS,"all_facts":BITCOIN_FACTS},
        "evolution_log":evo_log,"price_history":ph,
    }

    os.makedirs("data",exist_ok=True)
    with open(DATA_FILE,"w") as f: json.dump(knowledge,f,indent=2,default=str)

    print(f"\n{'='*60}")
    print(f"✅ OLLIE CYCLE {generation} COMPLETE")
    print(f"   Price:      ${(price or {}).get('price_usd',0):,.2f}")
    print(f"   F&G:        {(fg or {}).get('value',0)} ({(fg or {}).get('label','N/A')})")
    print(f"   Headlines:  {len(headlines)}")
    print(f"   Insights:   {len(insights)}")
    print(f"   Prediction: {prediction['outlook']} ({prediction['confidence']}% confidence)")
    print(f"   Accuracy:   {accuracy}% lifetime")
    print(f"{'='*60}")

if __name__=="__main__":
    main()
