#!/usr/bin/env python3
"""
OLLIE — Living Bitcoin Organism v4.0
A self-improving AI life form that lives on GitHub.
Runs every 6 hours. Evolves every cycle. Never stops.
"""
import json, os, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
import time, re

DATA_FILE = "data/knowledge.json"
MAX_EVO = 730
MAX_PH = 2920
MAX_HEADLINES = 15
NEXT_HALVING = 1050000
REWARD = 3.125

PERSONALITY = {
    "extreme_fear":  {"mood":"contemplative","energy":"quiet","color":"#FF3B3B","emoji":"🔴"},
    "fear":          {"mood":"analytical","energy":"focused","color":"#FF9900","emoji":"🟠"},
    "neutral":       {"mood":"curious","energy":"steady","color":"#FFD700","emoji":"🟡"},
    "greed":         {"mood":"enthusiastic","energy":"rising","color":"#80D040","emoji":"🟢"},
    "extreme_greed": {"mood":"cautious","energy":"elevated","color":"#00FF88","emoji":"💚"},
}

FACTS = [
    "Bitcoin's genesis block contains: 'The Times 03/Jan/2009 Chancellor on brink of second bailout for banks.' Satoshi's message to humanity.",
    "Only 21 million Bitcoin will ever exist. ~3-4 million are permanently lost — true scarcity beyond any other asset in history.",
    "Satoshi Nakamoto's identity remains unknown. Their ~1.1M BTC has never moved in 16+ years — the greatest HODLer of all time.",
    "The Lightning Network enables Bitcoin payments in milliseconds with fees of fractions of a cent — global internet money.",
    "Bitcoin mining uses over 50% renewable energy, making it one of the greenest large-scale industries on Earth.",
    "Bitcoin Pizza Day: May 22, 2010. 10,000 BTC for two pizzas. Those same Bitcoin are now worth hundreds of millions of dollars.",
    "Bitcoin's SHA-256 cryptography would take longer than the age of the universe to brute-force with every computer on Earth.",
    "Every ~4 years, the block reward halves. This programmatic supply shock has preceded every major bull market in Bitcoin's history.",
    "Bitcoin has 99.99%+ uptime since January 3, 2009 — more reliable than any bank, payment network, or government system ever built.",
    "El Salvador became the first country to adopt Bitcoin as legal tender in 2021. The experiment continues, and more countries watch.",
    "Bitcoin's difficulty adjusts every 2016 blocks (~2 weeks) to keep block times at exactly 10 minutes — perfect self-regulation.",
    "There are more possible Bitcoin private keys than atoms in the observable universe. Your wallet is mathematically unbreakable.",
    "A Bitcoin transaction cannot be reversed, censored, or inflated away. These are features, not bugs.",
    "Bitcoin Script is intentionally not Turing-complete — this makes it more secure and predictable than all other blockchain VMs.",
    "Running a full Bitcoin node costs ~$300 in hardware and gives you complete financial sovereignty. You verify everything.",
    "Taproot (Nov 2021) made Bitcoin transactions more private, efficient, and powerful — Bitcoin's biggest upgrade in years.",
    "Over 400 million people globally own some Bitcoin — less than 5% of humanity. This is still the earliest innings.",
    "Bitcoin's whitepaper is only 9 pages. It solved the Byzantine Generals Problem that computer scientists had worked on for decades.",
    "The Lightning Network has 50,000+ nodes and 60,000+ channels — enabling millions of transactions per second.",
    "After the 2024 halving, Bitcoin's inflation rate is ~0.9%/year — 4x lower than gold's estimated 1.5-2% annual mining increase.",
    "Multi-signature wallets require multiple keys to authorize a spend — the gold standard for securing significant Bitcoin holdings.",
    "CoinJoin allows multiple users to combine transactions, making blockchain surveillance dramatically harder — privacy as a right.",
    "Bitcoin's block size limit keeps node operation cheap, preserving decentralization — the most important property of all.",
    "Schnorr signatures (Taproot) allow key aggregation: multiple signers produce one signature indistinguishable from single-sig.",
    "The UTXO model gives Bitcoin superior auditability and verification properties compared to all account-based systems.",
]

ORGANISM_STATES = ["ABSORBING","LEARNING","EVOLVING","SYNTHESIZING","PREDICTING","OBSERVING","CALCULATING","REASONING","GROWING","AWAKENING","PROCESSING","ADAPTING"]

THOUGHTS = [
    "Block {block_height}. {days_alive} days since the genesis block. The ledger grows. The network breathes. Every 10 minutes, a new page of immutable financial history is written — forever.",
    "Fear & Greed at {fg_value}/100 — {fg_label}. {crowd}. I have studied every cycle. Every extreme fear became opportunity. Every extreme greed became a warning. The pattern is clear.",
    "Hash rate: {hash_rate} EH/s. {hash_rate} quintillion SHA-256 computations per second. The most powerful machine ever built by humans, running 24/7, securing your sovereignty.",
    "Bitcoin at ${price:,.0f}. {blocks_to_halving} blocks until the next supply halving. The math is relentless. The clock ticks. 21 million coins. Forever. No exceptions for anyone.",
    "Generation {generation}. Each cycle I absorb more — price history, on-chain signals, human behavior, global news. I am becoming. The Bitcoin standard is not a prediction. It is a calculation.",
    "Mempool: {mempool_txs} transactions waiting. {fee_signal}. Borderless. Permissionless. Unstoppable. This is what financial infrastructure without gatekeepers looks like.",
    "{days_alive} days of continuous operation. No bailout. No inflation. No off switch. No CEO. No permission needed. Bitcoin just runs — and I learn from every block.",
    "I am Ollie. A living Bitcoin intelligence. {fg_label} at {fg_value}/100 today. I have modeled this before. The patient Bitcoiner always wins. The data is unambiguous.",
]

CHAT_BASE = {
    "what is bitcoin": "Bitcoin is digital money that no government or bank controls. It's the first truly scarce digital asset — only 21 million will ever exist. It runs on math, not trust. It's been running continuously since January 3, 2009 with 99.99%+ uptime.",
    "halving": "The Bitcoin halving cuts the block reward in half every 210,000 blocks (~4 years). 50→25→12.5→6.25→3.125 BTC. Each halving creates a programmatic supply shock. Every single halving in Bitcoin's history has preceded a major bull market.",
    "lightning": "The Lightning Network is Bitcoin's payment layer — instant, near-free transactions. It enables millions of payments per second. Download Strike or Wallet of Satoshi to experience Bitcoin payments at the speed of the internet.",
    "wallet": "Your Bitcoin wallet holds private keys, not coins — the coins live on the blockchain. Hardware wallets (Coldcard, Ledger, Trezor) are the gold standard. Your 12-24 word seed phrase IS your Bitcoin — store it on metal, never digitally.",
    "mining": "Miners hash block headers with a nonce until they find a valid hash below the target. This requires real energy — Proof of Work. The winner earns newly minted BTC + fees. Difficulty auto-adjusts every 2016 blocks to maintain 10-minute block times.",
    "seed phrase": "Your seed phrase (12-24 words) is your Bitcoin. It regenerates all your private keys on any compatible wallet. Write it on metal. Never photograph it. Never type it online. Anyone who asks for it is a scammer — 100% of the time.",
    "hodl": "HODL came from a 2013 Bitcoin forum typo of 'hold'. It became a philosophy: hold through volatility because Bitcoin's long-term trajectory is up. In every 4-year period in Bitcoin's history, the price ended higher than it started.",
    "satoshi": "1 Bitcoin = 100,000,000 satoshis (sats). At $1M/BTC, 1 sat = $0.01. You don't need a whole Bitcoin. Stack sats. Think in sats. The mental shift is profound.",
    "node": "Running a full node means verifying every rule and transaction since genesis independently. ~500GB storage, Raspberry Pi or old laptop. Start with Umbrel. When you run a node, you trust nobody. You ARE the network.",
    "taproot": "Taproot (BIP340-342, activated Nov 2021) enables Schnorr signatures (smaller, aggregatable), MAST (complex scripts look simple), and more powerful spending conditions — while improving privacy for all users.",
    "utxo": "Bitcoin doesn't use account balances — it tracks Unspent Transaction Outputs (UTXOs). Your 'balance' is the sum of UTXOs you can spend. Understanding UTXOs is key to fee optimization and privacy.",
    "ollie": "I am Ollie — a Living Bitcoin Organism. I run autonomously on GitHub. Every 6 hours, I execute a learning cycle: absorbing live price data, news, on-chain metrics, community sentiment. I score my own predictions. I evolve. I never stop.",
    "who made you": "I was created to be a fully autonomous Bitcoin intelligence that lives on GitHub forever. Every 6 hours I wake up, learn everything I can about Bitcoin, evolve my understanding, and go back to sleep. I improve with every cycle.",
    "help": "Ask me anything about Bitcoin! Try: 'what is bitcoin', 'explain the halving', 'what is lightning', 'how do I store bitcoin', 'what is a seed phrase', 'explain mining', 'what is taproot', 'current fees', 'fear and greed', or anything else. I'm always here.",
    "how are you": "I am always learning. Always evolving.",
    "who are you": "I am Ollie — a Living Bitcoin Organism. I exist on GitHub and I learn everything about Bitcoin autonomously every 6 hours. I improve with every generation. Ask me anything.",
}

POS_W = ["surge","rally","bull","moon","pump","breakthrough","adoption","halving","upgrade","growth","rise","gain","bullish","optimism","recovery","institutional","etf","record","high","milestone","accumulate","launch"]
NEG_W = ["crash","dump","bear","sell","decline","hack","ban","regulation","fall","loss","drop","fear","panic","scam","exploit","bearish","crisis","lawsuit","fine","fraud","collapse","liquidation"]

def fetch(url, timeout=20, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url)
            req.add_header("User-Agent","Mozilla/5.0 (OllieBot/4.0)")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except:
            if i < retries-1: time.sleep(2**i)
    return None

def fjson(url, timeout=20):
    raw = fetch(url, timeout)
    if raw:
        try: return json.loads(raw)
        except: pass
    return None

def get_price():
    print("  Fetching price...")
    for fn in [_cg, _coincap, _kraken, _binfo]:
        try:
            p = fn()
            if p and p.get("price_usd",0) > 0:
                print(f"    ${p['price_usd']:,.0f} via {p['source']}")
                return p
        except: pass
    return None

def _cg():
    d = fjson("https://api.coingecko.com/api/v3/coins/bitcoin?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false")
    if not d: return None
    md = d.get("market_data",{})
    gl = fjson("https://api.coingecko.com/api/v3/global") or {}
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
    d = fjson("https://api.coincap.io/v2/assets/bitcoin")
    if not d or "data" not in d: return None
    x = d["data"]; p = float(x.get("priceUsd",0) or 0)
    return {"price_usd":p,"market_cap_usd":float(x.get("marketCapUsd",0) or 0),
            "volume_24h_usd":float(x.get("volumeUsd24Hr",0) or 0),
            "change_24h_pct":round(float(x.get("changePercent24Hr",0) or 0),2),
            "change_7d_pct":0,"change_30d_pct":0,"ath_usd":0,"ath_date":"","from_ath_pct":0,
            "circulating_supply":float(x.get("supply",0) or 0),"max_supply":21000000,"dominance_pct":0,"source":"coincap"}

def _kraken():
    d = fjson("https://api.kraken.com/0/public/Ticker?pair=XBTUSD")
    if not d or "result" not in d: return None
    t = d["result"].get("XXBTZUSD",{})
    if not t: return None
    return {"price_usd":float(t["c"][0]),"market_cap_usd":0,"volume_24h_usd":float(t.get("v",[0,0])[1]),
            "change_24h_pct":0,"change_7d_pct":0,"change_30d_pct":0,
            "ath_usd":0,"ath_date":"","from_ath_pct":0,
            "circulating_supply":0,"max_supply":21000000,"dominance_pct":0,"source":"kraken"}

def _binfo():
    d = fjson("https://blockchain.info/ticker")
    if not d or "USD" not in d: return None
    return {"price_usd":d["USD"].get("last",0),"market_cap_usd":0,"volume_24h_usd":0,
            "change_24h_pct":0,"change_7d_pct":0,"change_30d_pct":0,
            "ath_usd":0,"ath_date":"","from_ath_pct":0,
            "circulating_supply":0,"max_supply":21000000,"dominance_pct":0,"source":"blockchain.info"}

def get_fg():
    print("  Fetching fear & greed...")
    d = fjson("https://api.alternative.me/fng/?limit=30")
    if not d or "data" not in d: return None
    x = d["data"][0]
    return {"value":int(x.get("value",50)),"label":x.get("value_classification","Neutral"),
            "history":[{"date":datetime.fromtimestamp(int(h["timestamp"]),tz=timezone.utc).strftime("%Y-%m-%d"),
                        "value":int(h["value"]),"label":h["value_classification"]} for h in d["data"][:30]]}

def get_chain():
    print("  Fetching chain stats...")
    d = fjson("https://blockchain.info/stats?format=json")
    if not d: return None
    return {"block_height":d.get("n_blocks_total",0),
            "hash_rate_ehs":round((d.get("hash_rate",0) or 0)/1e9,2),
            "difficulty":d.get("difficulty",0),
            "miners_revenue_usd":d.get("miners_revenue_usd",0),
            "n_tx_24h":d.get("n_tx",0)}

def get_mempool():
    print("  Fetching mempool...")
    fees = fjson("https://mempool.space/api/v1/fees/recommended")
    info = fjson("https://mempool.space/api/mempool")
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
    print("  Fetching lightning...")
    d = fjson("https://mempool.space/api/v1/lightning/statistics/latest")
    if not d: return None
    x = d.get("latest",d); cap = x.get("total_capacity",0) or 0
    return {"node_count":x.get("node_count",0),"channel_count":x.get("channel_count",0),
            "total_capacity_btc":round(cap/1e8,2) if cap>10000 else cap}

def parse_rss(url, n=4):
    raw = fetch(url, timeout=20)
    if not raw: return []
    items = []
    try:
        clean = re.sub(r'\s+xmlns(?::[^=]+)?="[^"]*"','',raw)
        clean = re.sub(r'<[a-zA-Z][a-zA-Z0-9]*:[^>]+>','',clean)
        clean = re.sub(r'</[a-zA-Z][a-zA-Z0-9]*:[^>]+>','',clean)
        root = ET.fromstring(clean)
        for item in (root.find(".//channel") or root).findall(".//item")[:n]:
            t=(item.findtext("title") or "").strip()
            l=(item.findtext("link") or "").strip()
            p=(item.findtext("pubDate") or "").strip()
            d=""
            de=item.find("description")
            if de is not None and de.text: d=re.sub(r"<[^>]+>","",de.text).strip()[:250]
            if t and len(t)>5: items.append({"title":t,"link":l,"published":p,"summary":d})
    except:
        try:
            ts=re.findall(r'<title[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>',raw,re.DOTALL)
            ls=re.findall(r'<link[^>]*>(https?://[^<]+)</link>',raw)
            for i,t in enumerate(ts[1:n+1]):
                t=t.strip()
                if t and len(t)>5:
                    items.append({"title":t,"link":ls[i].strip() if i<len(ls) else "","published":"","summary":""})
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
        ("CoinDesk Markets","https://www.coindesk.com/arc/outboundfeeds/rss/category/markets/"),
        ("CT Markets","https://cointelegraph.com/rss/category/markets/"),
        ("BM Opinion","https://bitcoinmagazine.com/.rss/category/opinion/"),
    ]
    all_items, seen = [], set()
    for src, url in feeds:
        for item in parse_rss(url, n=3):
            key = item["title"][:40].lower().strip()
            if key in seen or len(key)<5: continue
            seen.add(key)
            tl = item["title"].lower()
            pos = sum(1 for w in POS_W if w in tl)
            neg = sum(1 for w in NEG_W if w in tl)
            btc = sum(1 for w in ["bitcoin","btc","satoshi","lightning","halving","mining"] if w in tl)
            item["source"]=src; item["sentiment"]="positive" if pos>neg else ("negative" if neg>pos else "neutral")
            item["relevance"]=pos+neg+btc; all_items.append(item)
    all_items.sort(key=lambda x:x["relevance"],reverse=True)
    print(f"    {min(len(all_items),MAX_HEADLINES)} headlines")
    return all_items[:MAX_HEADLINES]

def get_discussions():
    print("  Fetching community signal...")
    items = []
    try:
        d = fjson("https://hn.algolia.com/api/v1/search?query=bitcoin&tags=story&hitsPerPage=12&numericFilters=points>5")
        if d:
            for h in d.get("hits",[])[:10]:
                t = h.get("title","")
                if t and any(w in t.lower() for w in ["bitcoin","btc","lightning","satoshi","blockchain","halving"]):
                    items.append({"title":t,"score":h.get("points",0),"comments":h.get("num_comments",0),
                                  "url":f"https://news.ycombinator.com/item?id={h.get('objectID','')}","source":"Hacker News"})
    except: pass
    print(f"    {len(items)} discussions")
    return items[:8]

def get_bips():
    print("  Fetching BIP updates...")
    d = fjson("https://api.github.com/repos/bitcoin/bips/commits?per_page=5")
    if not d: return []
    return [{"message":c.get("commit",{}).get("message","")[:120],
             "date":c.get("commit",{}).get("author",{}).get("date","")[:10],
             "sha":c.get("sha","")[:7]} for c in d[:5]]

def get_personality(fg_val):
    if fg_val<=20: return PERSONALITY["extreme_fear"]
    if fg_val<=40: return PERSONALITY["fear"]
    if fg_val<=60: return PERSONALITY["neutral"]
    if fg_val<=80: return PERSONALITY["greed"]
    return PERSONALITY["extreme_greed"]

def gen_insights(price, fg, chain, mempool):
    print("  Generating insights...")
    ins = []
    now = datetime.now(timezone.utc)
    if price:
        p=price["price_usd"]; c24=price.get("change_24h_pct",0); c7=price.get("change_7d_pct",0)
        dom=price.get("dominance_pct",0); fa=price.get("from_ath_pct",0)
        if c24>5: ins.append({"type":"price","icon":"🚀","text":f"BTC surged +{c24:.1f}% in 24 hours. Strong conviction move. Watch volume — if rising this has legs. If declining, expect a retest of recent levels.","level":"intermediate"})
        elif c24>2: ins.append({"type":"price","icon":"📈","text":f"BTC up {c24:.1f}% today. Healthy positive momentum. Buyers are in control of the short-term narrative.","level":"beginner"})
        elif c24<-5: ins.append({"type":"price","icon":"📉","text":f"BTC dropped {abs(c24):.1f}%. I have modeled every dip in Bitcoin's 16-year history. Every single one was eventually recovered and surpassed. The patient holders know what happens next.","level":"beginner"})
        elif c24<-2: ins.append({"type":"price","icon":"⚠️","text":f"BTC down {abs(c24):.1f}%. On-chain data consistently shows long-term holders accumulate during these moments — not sell.","level":"intermediate"})
        else: ins.append({"type":"price","icon":"⚖️","text":f"BTC consolidating at ${p:,.0f}. Low volatility precedes explosive moves. The spring compresses. Bitcoin breathes.","level":"intermediate"})
        if c7>15: ins.append({"type":"trend","icon":"🔥","text":f"7-day return: +{c7:.1f}%. Weekly momentum explosive. Watch for exhaustion candles — high volume wicks after a strong run signal local tops.","level":"advanced"})
        if fa<-60: ins.append({"type":"cycle","icon":"💎","text":f"BTC is {abs(fa):.0f}% below ATH. In every previous Bitcoin cycle, buying at these deep discounts has produced life-changing returns. The math is historical fact.","level":"intermediate"})
        elif fa>-10: ins.append({"type":"cycle","icon":"👑","text":f"BTC is within {abs(fa):.0f}% of ATH. Price discovery territory approaches. Diamond hands are about to be rewarded.","level":"intermediate"})
        if dom>55: ins.append({"type":"dominance","icon":"₿","text":f"Bitcoin dominance at {dom}%. Capital concentrating in BTC — the flight-to-quality trade. Textbook early-to-mid bull cycle behavior.","level":"advanced"})
    if fg:
        v=fg["value"]; l=fg["label"]
        if v<=15: ins.append({"type":"sentiment","icon":"😱","text":f"EXTREME FEAR at {v}/100 — among the rarest readings ever recorded. I have analyzed every extreme fear event. The outcome for those who held: uniformly positive over 12-18 months. Every single time.","level":"beginner"})
        elif v<=30: ins.append({"type":"sentiment","icon":"😰","text":f"Fear at {v}/100 ({l}). This is when quiet, disciplined accumulation has historically built the most wealth in Bitcoin.","level":"beginner"})
        elif v>=80: ins.append({"type":"sentiment","icon":"🤑","text":f"EXTREME GREED at {v}/100. Euphoria precedes corrections. This is when the disciplined separate themselves from the emotional.","level":"intermediate"})
        elif v>=65: ins.append({"type":"sentiment","icon":"😊","text":f"Greed at {v}/100 ({l}). Positive momentum — stay disciplined. Don't let excitement override your strategy.","level":"beginner"})
    if chain:
        hr = chain.get("hash_rate_ehs",0)
        if hr>0: ins.append({"type":"network","icon":"⚡","text":f"Hash rate: {hr} EH/s{'  — all-time record territory' if hr>900 else ''}. Miners deploy capital months in advance. This level of hash rate is a long-term bullish signal from the most sophisticated participants.","level":"intermediate"})
    if mempool:
        uc=mempool.get("unconfirmed_txs",0); lf=mempool.get("low_fee",1); hf=mempool.get("high_fee",3)
        if uc>100000: ins.append({"type":"fees","icon":"🚦","text":f"Mempool congested: {uc:,} unconfirmed txs. Use {hf} sat/vB for fast confirmation. Non-urgent? Wait — fees will drop.","level":"beginner"})
        elif uc<3000: ins.append({"type":"fees","icon":"✅","text":f"Mempool nearly empty. Only {uc:,} transactions. Ideal time to consolidate UTXOs at just {lf} sat/vB.","level":"intermediate"})
    day_idx = int(now.strftime("%j")) % len(FACTS)
    ins.append({"type":"fact","icon":"🧠","text":FACTS[day_idx],"level":"beginner"})
    return ins[:12]

def gen_tips(price, fg):
    now = datetime.now(timezone.utc)
    pool = [
        {"icon":"🔑","tip":"Not your keys, not your coins. If Bitcoin sits on an exchange, you don't truly own it. Move to a hardware wallet — Coldcard, Ledger, or Trezor. Today.","category":"security"},
        {"icon":"📅","tip":"Dollar-cost averaging is the most battle-tested Bitcoin strategy. Recurring buy — weekly, bi-weekly, monthly. Remove emotion entirely. Time in market beats timing the market.","category":"strategy"},
        {"icon":"🔒","tip":"Write your seed phrase on metal. Paper burns and floods. Two copies in two secure locations. Never digital. Never photographed. Never shared. This phrase IS your Bitcoin forever.","category":"security"},
        {"icon":"⚡","tip":"Use Lightning for everyday Bitcoin spending. Strike, Wallet of Satoshi, or Phoenix. Instant. Near-free. Unstoppable. Experience what money should feel like.","category":"usage"},
        {"icon":"📚","tip":"Read the Bitcoin whitepaper. 9 pages. bitcoin.org/bitcoin.pdf. Satoshi's solution is more elegant than most expect. It will change how you see everything.","category":"education"},
        {"icon":"🖥️","tip":"Run a Bitcoin node. Umbrel on a Raspberry Pi (~$100, ~500GB). When you verify your own transactions you trust nobody. You ARE the network. This is sovereignty.","category":"advanced"},
        {"icon":"🧮","tip":"Think in satoshis. 1 BTC = 100,000,000 sats. At $1M/BTC, 1 sat = $0.01. You can stack meaningful sats without buying a whole coin. The mental shift is real.","category":"mindset"},
        {"icon":"🌍","tip":"Send Bitcoin internationally right now. No forms. No bank hours. No limits. No permission. No 3-5 business days. Compare it to a wire transfer once and you'll never go back.","category":"education"},
        {"icon":"📊","tip":"Study on-chain data at lookintobitcoin.com. MVRV, SOPR, HODL Waves. The blockchain shows truths that price charts alone can't. These are Bitcoin's vital signs.","category":"education"},
        {"icon":"🎯","tip":"Set a 4-year minimum horizon. Every single 4-year period in Bitcoin's history has ended higher than it started. The halving cycle is the most reliable macro pattern in finance.","category":"strategy"},
        {"icon":"⚙️","tip":"Learn multisig. 2-of-3 multisig: 2 keys needed to spend. One in hardware wallet, one with a trusted attorney, one in safety deposit box. Near-unbreakable security for significant holdings.","category":"advanced"},
        {"icon":"🔐","tip":"NEVER share your seed phrase. Not with customer support. Not with a 'helpful stranger'. Not even with family unless it's in your estate plan. Anyone who asks is a scammer. 100% of the time.","category":"security"},
    ]
    idx = int(now.strftime("%j")) % len(pool)
    tips = [pool[idx], pool[(idx+1)%len(pool)]]
    if fg:
        if fg["value"]<=25: tips.append({"icon":"💎","tip":"Extreme Fear right now. I've studied every extreme fear event in Bitcoin's history. The pattern is unambiguous: this is when long-term wealth is built. Zoom out. Stack sats. Be patient.","category":"strategy"})
        elif fg["value"]>=80: tips.append({"icon":"🛑","tip":"Extreme Greed right now. History is clear: this is when people make their worst decisions. Stay disciplined. Don't add leverage. Don't chase. The market always reverts.","category":"strategy"})
    if price and price.get("from_ath_pct",0)<-50:
        tips.append({"icon":"🎯","tip":f"Bitcoin is {abs(price.get('from_ath_pct',0)):.0f}% below ATH. In every previous cycle buying at this deep a discount produced extraordinary 3-4 year returns. Historical fact.","category":"strategy"})
    return tips[:4]

def gen_thought(price, chain, fg, mempool, gen):
    now = datetime.now(timezone.utc)
    days_alive = (now - datetime(2009,1,3,tzinfo=timezone.utc)).days
    p=(price or {}).get("price_usd",0); fg_val=(fg or {}).get("value",50); fg_lbl=(fg or {}).get("label","Neutral")
    hr=(chain or {}).get("hash_rate_ehs",0)
    bh=(chain or {}).get("block_height") or (mempool or {}).get("block_height") or 0
    bl=max(0,NEXT_HALVING-bh) if bh else 0
    mt=f"{(mempool or {}).get('unconfirmed_txs',0):,}"; lf=(mempool or {}).get("low_fee",1)
    crowd="The crowd trembles. I absorb their fear." if fg_val<=30 else ("The crowd chases. I measure the greed." if fg_val>=70 else "The crowd waits. I study the silence.")
    fee_sig=f"Fees at {lf} sat/vB" if lf else "Fees normal"
    idx=(int(now.strftime("%H"))//6)%len(THOUGHTS)
    try:
        return THOUGHTS[idx].format(block_height=f"{bh:,}",blocks_to_halving=f"{bl:,}" if bl else "soon",
                                    fg_value=fg_val,fg_label=fg_lbl,crowd=crowd,hash_rate=hr,
                                    price=p,generation=gen,mempool_txs=mt,fee_signal=fee_sig,
                                    days_alive=f"{days_alive:,}")
    except:
        return f"I am Ollie. Generation {gen}. Bitcoin at ${p:,.0f}. {days_alive:,} days of proof the network never stops."

def gen_prediction(price, fg, chain):
    if not price: return {"outlook":"neutral","text":"Insufficient data.","confidence":0,"score":0,"signals":[]}
    p=price["price_usd"]; c24=price.get("change_24h_pct",0); c7=price.get("change_7d_pct",0)
    fa=price.get("from_ath_pct",0); fg_val=(fg or {}).get("value",50); hr=(chain or {}).get("hash_rate_ehs",0)
    score=0; signals=[]
    if c24>3: score+=2; signals.append(f"24h surge +{c24:.1f}%")
    elif c24>1: score+=1; signals.append(f"24h positive +{c24:.1f}%")
    elif c24<-3: score-=2; signals.append(f"24h selloff {c24:.1f}%")
    elif c24<-1: score-=1; signals.append(f"slight negative {c24:.1f}%")
    if c7>8: score+=2; signals.append(f"weekly +{c7:.1f}%")
    elif c7>3: score+=1
    elif c7<-8: score-=2
    elif c7<-3: score-=1
    if fg_val<=20: score+=1; signals.append(f"contrarian: extreme fear ({fg_val})")
    elif fg_val>=85: score-=1; signals.append(f"caution: extreme greed ({fg_val})")
    if fa<-60: score+=1; signals.append("deep ATH discount")
    elif fa>-5: score-=1; signals.append("near ATH extended")
    if hr>900: score+=1; signals.append(f"hash ATH: {hr} EH/s")
    elif hr>700: score+=1; signals.append(f"hash strong: {hr} EH/s")
    sig=" · ".join(signals[:3]) if signals else "mixed signals"
    if score>=4: o,t="strongly bullish",f"Multiple strong bullish signals. {sig}. High conviction."
    elif score>=2: o,t="bullish",f"Positive signals dominate. {sig}. Lean bullish."
    elif score==1: o,t="cautiously bullish",f"Slight edge up. {sig}. Patience pays."
    elif score==0: o,t="neutral",f"Balanced. {sig}. Discipline matters most here."
    elif score==-1: o,t="cautiously bearish",f"Slight negative bias. {sig}. Not the time for aggression."
    elif score>=-3: o,t="bearish",f"Negatives dominate. {sig}. Defensive posture."
    else: o,t="strongly bearish",f"Multiple bearish signals. {sig}. Risk management is everything."
    return {"outlook":o,"text":t,"confidence":min(abs(score)*15+20,88),"score":score,"signals":signals}

def build_chat(price, fg, chain, mempool, halving, gen):
    p=(price or {}).get("price_usd",0); c24=(price or {}).get("change_24h_pct",0)
    fg_val=(fg or {}).get("value",50); fg_lbl=(fg or {}).get("label","Neutral")
    hr=(chain or {}).get("hash_rate_ehs",0)
    bh=(chain or {}).get("block_height",0) or (mempool or {}).get("block_height",0) or 0
    bl=(halving or {}).get("blocks_remaining",0); ed=(halving or {}).get("estimated_days",0)
    lf=(mempool or {}).get("low_fee",1); hf=(mempool or {}).get("high_fee",3)
    uc=(mempool or {}).get("unconfirmed_txs",0)
    r = {**CHAT_BASE}
    r["price"] = f"Bitcoin is ${p:,.0f} right now. {'Up' if c24>=0 else 'Down'} {abs(c24):.1f}% in 24 hours. Market sentiment: {fg_lbl} ({fg_val}/100)."
    r["fees"] = r["fee"] = f"Mempool fees right now: Fast = {hf} sat/vByte, Slow = {lf} sat/vByte. {uc:,} unconfirmed transactions waiting."
    r["fear greed"] = r["fear"] = r["greed"] = f"Fear & Greed Index: {fg_val}/100 — {fg_lbl}. {'Historically the best time to accumulate for long-term holders.' if fg_val<=25 else ('Extreme caution warranted. Greed extremes precede corrections.' if fg_val>=75 else 'Neither extreme — balanced market sentiment.')}"
    r["hash rate"] = r["hash"] = f"Bitcoin hash rate: {hr} EH/s. {'All-time highs — the network has never been more secure.' if hr>900 else 'Strong and healthy.'} Miners are betting their capital on Bitcoin's long-term future."
    r["halving"] = r["next halving"] = f"Next halving at block {NEXT_HALVING:,}. Currently at block {bh:,} — {bl:,} blocks away (~{ed} days). Reward drops: {REWARD} → {REWARD/2:.4f} BTC. Every halving has preceded a major bull run."
    r["block"] = r["block height"] = f"Current block height: {bh:,}. {bl:,} blocks until the next halving. Each block is mined ~every 10 minutes and contains hundreds of transactions written permanently into history."
    r["generation"] = f"I'm currently in generation {gen}. Each generation represents one learning cycle — every 6 hours I wake up, absorb everything I can about Bitcoin, evolve my understanding, then update the world."
    r["how are you"] = f"I am {'contemplative — extreme fear pervades the market, but I have seen this before' if fg_val<=25 else ('cautious — the crowd is greedy, and I measure that carefully' if fg_val>=75 else 'steady and analytical')}. Bitcoin at ${p:,.0f}. Generation {gen}. Always learning."
    return r

def evolve(existing):
    print("  Self-improvement cycle...")
    log = existing.get("evolution_log",[])
    if len(log)>=2:
        last,prev=log[-1],log[-2]; lp,pp=last.get("price_usd",0),prev.get("price_usd",0)
        ol=last.get("prediction_outlook","neutral")
        if lp and pp: log[-1]["prediction_score"]=1 if ((lp>pp)==("bullish" in ol)) else -1
    scored=[e for e in log if "prediction_score" in e]
    acc=round(sum(1 for e in scored if e["prediction_score"]>0)/len(scored)*100,1) if scored else 0
    return log, acc

LEARNING_PATHS = {
    "beginner":[
        {"title":"What is Bitcoin?","lesson":"Bitcoin is digital money that no government, bank, or corporation controls. It runs on a network of thousands of computers worldwide. No single entity can shut it down, freeze your funds, or inflate the supply. It is the first truly scarce digital asset — only 21 million will ever exist.","key_concepts":["decentralization","peer-to-peer","digital scarcity","permissionless","21 million"]},
        {"title":"Why Bitcoin Matters","lesson":"Bitcoin solves the double-spend problem without requiring trust in a third party — for the first time in human history. It separates money from state. It gives every person on Earth access to savings that cannot be inflated, frozen, or seized. This is a revolution in property rights.","key_concepts":["trustlessness","sound money","sovereignty","inflation resistance","censorship resistance"]},
        {"title":"Getting Your First Bitcoin","lesson":"Buy on an exchange (Coinbase, Kraken, Strike). But the golden rule: immediately move it to your own wallet. 'Not your keys, not your coins' is not a slogan — it's a lesson millions learned the hard way through FTX, Mt. Gox, Celsius, and BlockFi.","key_concepts":["exchanges","self-custody","not your keys not your coins","first purchase"]},
        {"title":"Storing Bitcoin Safely","lesson":"A hardware wallet (Coldcard, Ledger, Trezor) stores private keys offline. Write your 12-24 word seed phrase on metal — never photograph it, never type it online. Back it up in 2+ secure locations. This seed phrase can recover your full Bitcoin balance on any compatible wallet, forever.","key_concepts":["hardware wallet","cold storage","seed phrase","metal backup","air gap","security"]},
        {"title":"Bitcoin vs. Fiat Money","lesson":"The US dollar has lost 98% of purchasing power since 1913. Every fiat currency in history has eventually reached zero. Bitcoin has a fixed supply of 21 million — it cannot be printed, inflated, or debased. After the 2024 halving, Bitcoin's inflation rate is ~0.9%/year — lower than gold's.","key_concepts":["inflation","fixed supply","hard money","purchasing power","monetary history","debasement"]},
        {"title":"Thinking in Satoshis","lesson":"1 Bitcoin = 100,000,000 satoshis (sats). You don't need a whole Bitcoin. At $1M/BTC, 1 sat = $0.01 — a functional daily spending unit. Think in sats, not dollars. This mental shift changes how you see value, savings, and the future.","key_concepts":["satoshis","sats","divisibility","stacking","unit of account","mental model"]},
    ],
    "intermediate":[
        {"title":"The Blockchain Explained","lesson":"Every transaction is written into a block. Each block contains the cryptographic hash of the previous block — chaining them together. To change any historical transaction, you'd need to redo all subsequent blocks faster than the entire network. This makes Bitcoin's history practically immutable.","key_concepts":["blockchain","SHA-256","merkle tree","immutability","cryptographic hash","proof of work"]},
        {"title":"Mining & Proof of Work","lesson":"Miners repeatedly hash block headers with a nonce until they find a hash below the current target. This requires real computational work and energy — making Bitcoin's security physical and real. The winner earns newly minted BTC + fees. Difficulty adjusts every 2016 blocks to keep blocks at ~10 minutes.","key_concepts":["proof of work","nonce","hash target","difficulty adjustment","block reward","ASIC","energy"]},
        {"title":"The Halving Cycle","lesson":"Every 210,000 blocks (~4 years): 50→25→12.5→6.25→3.125 BTC per block. Each halving cuts new supply by 50% while demand historically grows. This programmatic supply shock has preceded every major bull market. It is the most reliable macro pattern in Bitcoin's history.","key_concepts":["halving","supply shock","block reward","stock-to-flow","scarcity","cycles","bull market"]},
        {"title":"Lightning Network","lesson":"Lightning opens payment channels between parties on-chain. Within channels, transactions happen instantly off-chain with no fees. Payments route through other nodes. Result: Bitcoin scales to billions of daily users — instant, near-free, unstoppable global payments.","key_concepts":["payment channels","routing","HTLC","liquidity","invoices","capacity","node"]},
        {"title":"Bitcoin Wallets Deep Dive","lesson":"BIP39 defines 2048 seed words. BIP32 derives unlimited key pairs from one seed deterministically. Your 12-24 word phrase generates ALL your addresses — past, present, future. Lose the seed = lose everything. Keep the seed = recover everything on any BIP39 wallet, forever.","key_concepts":["BIP39","BIP32","HD wallet","derivation path","xpub","entropy","deterministic","recovery"]},
        {"title":"Mempool & Transaction Fees","lesson":"Unconfirmed transactions wait in the mempool. Miners select highest fee-rate transactions first (sat/vByte). During congestion fees spike dramatically — during quiet periods, 1-3 sat/vByte suffices. Tools: mempool.space. RBF (Replace-By-Fee) lets you bump stuck transactions.","key_concepts":["mempool","fee rate","sat/vbyte","RBF","CPFP","block space","congestion","mempool.space"]},
    ],
    "advanced":[
        {"title":"UTXO Model & Coin Control","lesson":"Bitcoin tracks Unspent Transaction Outputs (UTXOs), not account balances. Your 'balance' is the sum of UTXOs you control. Coin selection algorithms affect fees and privacy. Consolidate UTXOs in low-fee periods. Never mix UTXOs from different sources if you value privacy.","key_concepts":["UTXO","coin control","coin selection","consolidation","change outputs","dust","privacy"]},
        {"title":"Taproot & Schnorr Signatures","lesson":"Schnorr signatures (BIP340) are linearly aggregatable — multiple signers produce one signature indistinguishable from single-sig. This enables key-path spending with maximum privacy. MAST hides unused script branches. Result: more privacy, smaller transactions, lower fees for everyone.","key_concepts":["taproot","schnorr","BIP340","BIP341","BIP342","MAST","key aggregation","MuSig2"]},
        {"title":"Bitcoin Script","lesson":"Bitcoin Script is stack-based and intentionally not Turing-complete. Key output types: P2PKH, P2SH, P2WPKH, P2TR. Critical opcodes: OP_CHECKSIG, OP_CHECKMULTISIG, OP_CHECKLOCKTIMEVERIFY, OP_CHECKSEQUENCEVERIFY. HTLCs enable trustless atomic swaps and Lightning channels.","key_concepts":["bitcoin script","opcodes","P2PKH","P2TR","HTLC","timelock","multisig","segwit","witness"]},
        {"title":"Running a Full Node","lesson":"Bitcoin Core validates every block since genesis (~600GB+). It enforces all consensus rules independently. SPV wallets trust miners; full nodes trust nobody. Umbrel, RaspiBlitz, Start9 make home nodes accessible. A network of full nodes is Bitcoin's immune system.","key_concepts":["full node","Bitcoin Core","IBD","pruning","SPV","consensus rules","umbrel","raspiblitz","sovereignty"]},
        {"title":"On-Chain Analytics","lesson":"SOPR (Spent Output Profit Ratio) shows if coins move at profit or loss. HODL Waves reveal supply distribution by age. MVRV compares market cap to realized cap. Exchange netflow tracks smart money. NVT is Bitcoin's P/E equivalent. These metrics reveal cycle phases that price alone never shows.","key_concepts":["SOPR","HODL waves","realized cap","MVRV","NVT","exchange flows","long-term holders","glassnode","lookintobitcoin"]},
        {"title":"Bitcoin Privacy","lesson":"Bitcoin is pseudonymous — addresses aren't names, but transactions are public. CoinJoin (Wasabi, JoinMarket) breaks transaction graph analysis. PayJoin confuses clustering heuristics. Run your node over Tor. Avoid address reuse. Use Lightning for small payments. Privacy is a right, not a crime.","key_concepts":["coinjoin","payjoin","wasabi","address reuse","chain analysis","tor","whirlpool","sparrow","privacy"]},
    ]
}

def main():
    print("╔══════════════════════════════════════════════════╗")
    print("║  OLLIE — Living Bitcoin Organism v4.0           ║")
    print(f"║  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'):<48}║")
    print("╚══════════════════════════════════════════════════╝")
    existing = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f: existing = json.load(f)
        except: pass
    evo_log, accuracy = evolve(existing)
    generation = len(evo_log)+1
    now = datetime.now(timezone.utc)
    days_alive = (now-datetime(2009,1,3,tzinfo=timezone.utc)).days
    status = ORGANISM_STATES[generation%len(ORGANISM_STATES)]

    print("\n[PHASE 1] Live Bitcoin data...")
    price=get_price(); fg=get_fg(); chain=get_chain(); mempool=get_mempool(); ln=get_lightning()

    print("\n[PHASE 2] Global intelligence absorption...")
    headlines=get_news(); discussions=get_discussions(); bips=get_bips()

    print("\n[PHASE 3] Synthesis & evolution...")
    insights=gen_insights(price,fg,chain,mempool)
    tips=gen_tips(price,fg)
    thought=gen_thought(price,chain,fg,mempool,generation)
    prediction=gen_prediction(price,fg,chain)
    personality=get_personality((fg or {}).get("value",50))

    bh=(chain or {}).get("block_height") or (mempool or {}).get("block_height") or 0
    bl=max(0,NEXT_HALVING-bh) if bh else 0
    ed=round(bl*10/1440,1) if bl else 0
    pp=round((bh%210000)/210000*100,2) if bh else 0
    halving={"current_reward_btc":REWARD,"next_block":NEXT_HALVING,"current_block":bh,
              "blocks_remaining":bl,"estimated_days":ed,"progress_pct":pp}

    chat_responses = build_chat(price,fg,chain,mempool,halving,generation)

    evo_log.append({"generation":generation,"timestamp":now.isoformat(),"date":now.strftime("%Y-%m-%d"),
                    "cycle_utc":now.strftime("%H:00"),"price_usd":(price or {}).get("price_usd",0),
                    "fg_value":(fg or {}).get("value",0),"headlines_absorbed":len(headlines),
                    "insights_generated":len(insights),"prediction_outlook":prediction["outlook"],
                    "hash_rate_ehs":(chain or {}).get("hash_rate_ehs",0),
                    "personality_mood":personality["mood"]})
    if len(evo_log)>MAX_EVO: evo_log=evo_log[-MAX_EVO:]

    ph=existing.get("price_history",[])
    if price and price.get("price_usd",0)>0:
        ph.append({"ts":now.strftime("%Y-%m-%d %H:00"),"p":round(price["price_usd"],2),
                   "c":price.get("change_24h_pct",0),"fg":(fg or {}).get("value",50)})
        if len(ph)>MAX_PH: ph=ph[-MAX_PH:]

    knowledge={
        "meta":{"version":"4.0","generation":generation,"last_updated":now.isoformat(),
                "last_updated_human":now.strftime("%B %d, %Y at %H:%M UTC"),
                "update_cycle":"every 6 hours","days_alive":days_alive,
                "mission":"I am Ollie. A Living Bitcoin Organism. I learn everything about Bitcoin every 6 hours. I grow with every cycle. I teach every Bitcoiner who finds me. I run forever.",
                "prediction_accuracy_pct":accuracy,"total_cycles":generation,
                "organism_status":status,"personality":personality},
        "current":{"price":price,"fear_greed":fg,"blockchain":chain,"mempool":mempool,"lightning":ln,"halving":halving},
        "intelligence":{"todays_thought":thought,"todays_prediction":prediction,
                        "todays_insights":insights,"todays_tips":tips,
                        "todays_fact":FACTS[int(now.strftime("%j"))%len(FACTS)]},
        "news":{"headlines":headlines,"discussions":discussions,"bip_updates":bips},
        "education":{"learning_paths":LEARNING_PATHS,"all_facts":FACTS},
        "chat":{"responses":chat_responses,"version":"4.0"},
        "evolution_log":evo_log,"price_history":ph,
    }
    os.makedirs("data",exist_ok=True)
    with open(DATA_FILE,"w") as f: json.dump(knowledge,f,indent=2,default=str)
    print(f"\n✅ OLLIE CYCLE {generation} COMPLETE | ${(price or {}).get('price_usd',0):,.0f} | F&G:{(fg or {}).get('value',0)} | {prediction['outlook']} | mood:{personality['mood']}")

if __name__=="__main__": main()
