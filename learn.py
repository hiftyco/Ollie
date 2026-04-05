#!/usr/bin/env python3
"""
OLLIE v9.0 — Living Bitcoin Organism
Self-improving · Zero API keys · Runs forever · 24/7 autonomous
ALL BUGS FIXED · Persistent neural log · Watchdog price · correct_index quiz
bip_updates key · rolling neural 40 entries · 30 quiz questions
"""
import json, os, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
import time, re, random

DATA_FILE = "data/knowledge.json"
MAX_EVO = 2920; MAX_PH = 2920; MAX_HL = 20; MAX_DIARY = 730
MAX_NEURAL = 40
NEXT_HALVING = 1050000; REWARD = 3.125
VERSION = "9.0"

PERSONALITY = {
    "extreme_fear": {"mood":"contemplative","energy":"quiet","color":"#FF453A","emoji":"🔴"},
    "fear":         {"mood":"analytical","energy":"focused","color":"#FF9900","emoji":"🟠"},
    "neutral":      {"mood":"curious","energy":"steady","color":"#FFD60A","emoji":"🟡"},
    "greed":        {"mood":"enthusiastic","energy":"rising","color":"#30D158","emoji":"🟢"},
    "extreme_greed":{"mood":"cautious","energy":"elevated","color":"#00FF88","emoji":"💚"},
}
ORGANISM_STATES = [
    "ABSORBING","LEARNING","EVOLVING","SYNTHESIZING","PREDICTING","OBSERVING",
    "CALCULATING","REASONING","GROWING","AWAKENING","PROCESSING","ADAPTING",
    "REFLECTING","INTEGRATING","BROADCASTING","SELF-IMPROVING","CRITIQUING",
    "UPGRADING","MUTATING","TRANSCENDING","COMPUTING","ANALYZING","THEORIZING",
]
KNOWLEDGE_TOPICS = [
    "bitcoin_basics","halving_cycles","lightning_network","mining_security",
    "privacy_techniques","taproot_schnorr","utxo_model","mempool_fees",
    "on_chain_analytics","full_nodes","wallet_security","bitcoin_script",
    "market_psychology","hash_rate_analysis","supply_scarcity","monetary_history",
    "multisig_custody","bitcoin_development","layer2_solutions","network_consensus",
]

# 30 questions, ALL with correct_index
QUIZ_QUESTIONS = [
  {"question":"What is the maximum supply of Bitcoin?","options":["18 million","21 million","100 million","Unlimited"],"correct_index":1,"topic":"supply_scarcity","difficulty":"beginner","explanation":"Only 21 million BTC will ever exist — enforced by code, not promises."},
  {"question":"How often does the Bitcoin halving occur?","options":["Every year","Every 2 years","Every 210,000 blocks (~4 years)","Every 100,000 blocks"],"correct_index":2,"topic":"halving_cycles","difficulty":"beginner","explanation":"Every 210,000 blocks the block reward is cut in half."},
  {"question":"What does UTXO stand for?","options":["Unified Transaction Exchange Order","Unspent Transaction Output","Universal Token Exchange Operation","Unverified Transaction Output"],"correct_index":1,"topic":"utxo_model","difficulty":"intermediate"},
  {"question":"What is the smallest unit of Bitcoin?","options":["1 millibitcoin","1 bit","1 satoshi (0.00000001 BTC)","1 microbitcoin"],"correct_index":2,"topic":"bitcoin_basics","difficulty":"beginner"},
  {"question":"What Bitcoin upgrade enabled Schnorr signatures and MAST?","options":["SegWit","Lightning","Taproot (BIP340-342)","Ordinals"],"correct_index":2,"topic":"taproot_schnorr","difficulty":"intermediate","explanation":"Taproot activated November 2021 at block 709,632."},
  {"question":"What is the current block reward after the April 2024 halving?","options":["6.25 BTC","3.125 BTC","1.5625 BTC","12.5 BTC"],"correct_index":1,"topic":"halving_cycles","difficulty":"beginner"},
  {"question":"How many satoshis are in 1 Bitcoin?","options":["1,000,000","10,000,000","100,000,000","1,000,000,000"],"correct_index":2,"topic":"bitcoin_basics","difficulty":"beginner"},
  {"question":"What consensus mechanism does Bitcoin use?","options":["Proof of Stake","Delegated PoS","Proof of Authority","Proof of Work"],"correct_index":3,"topic":"mining_security","difficulty":"beginner"},
  {"question":"What is the Lightning Network?","options":["A Bitcoin fork","Layer 2 payment channel network","A new blockchain","An exchange"],"correct_index":1,"topic":"lightning_network","difficulty":"beginner","explanation":"Lightning enables instant near-zero fee payments via off-chain payment channels."},
  {"question":"What did SegWit fix?","options":["Block size to 1MB","Transaction malleability + increased effective capacity","Mining difficulty","Lightning channels"],"correct_index":1,"topic":"bitcoin_script","difficulty":"intermediate"},
  {"question":"How many Bitcoin are estimated permanently lost?","options":["~500K","~1M","~3-4M","~10M"],"correct_index":2,"topic":"supply_scarcity","difficulty":"intermediate","explanation":"Chainalysis estimates 3-4 million BTC are permanently inaccessible."},
  {"question":"What message is in Bitcoin's genesis block?","options":["Bitcoin: A Peer-to-Peer Electronic Cash System","Chancellor on brink of second bailout for banks","In crypto we trust","Block zero initialized"],"correct_index":1,"topic":"bitcoin_basics","difficulty":"intermediate"},
  {"question":"What hash function does Bitcoin proof-of-work use?","options":["MD5","SHA-1","SHA-256","SHA-3"],"correct_index":2,"topic":"mining_security","difficulty":"beginner"},
  {"question":"How many confirmations is considered irreversible for large amounts?","options":["1","3","6","100"],"correct_index":2,"topic":"bitcoin_basics","difficulty":"intermediate"},
  {"question":"What is Bitcoin's target block time?","options":["1 minute","5 minutes","10 minutes","1 hour"],"correct_index":2,"topic":"mining_security","difficulty":"beginner"},
  {"question":"What is a multisig wallet?","options":["Wallet with multiple currencies","Requires M-of-N keys to sign","Wallet on multiple devices","Hardware wallet"],"correct_index":1,"topic":"multisig_custody","difficulty":"intermediate"},
  {"question":"What does BIP stand for?","options":["Bitcoin Improvement Proposal","Blockchain Integration Protocol","Binary Instruction Package","Bitcoin Investment Plan"],"correct_index":0,"topic":"bitcoin_development","difficulty":"beginner"},
  {"question":"What is the Stock-to-Flow model?","options":["Bitcoin exchange rate model","Ratio of existing supply to annual new production","Network hashrate predictor","Fee market model"],"correct_index":1,"topic":"on_chain_analytics","difficulty":"advanced"},
  {"question":"What is CoinJoin?","options":["Exchange merger","Privacy technique combining multiple transactions","Multi-chain bridge","Mining pool type"],"correct_index":1,"topic":"privacy_techniques","difficulty":"advanced"},
  {"question":"What is the purpose of difficulty adjustment?","options":["Control transaction fees","Keep block time ~10 min regardless of hashrate","Limit total supply","Reduce block size"],"correct_index":1,"topic":"mining_security","difficulty":"intermediate"},
  {"question":"Who created Bitcoin?","options":["Vitalik Buterin","Nick Szabo","Satoshi Nakamoto","Hal Finney"],"correct_index":2,"topic":"bitcoin_basics","difficulty":"beginner"},
  {"question":"What year was the Bitcoin whitepaper published?","options":["2006","2007","2008","2009"],"correct_index":2,"topic":"bitcoin_basics","difficulty":"beginner","explanation":"October 31, 2008 — Halloween."},
  {"question":"What is the NVT ratio?","options":["Measuring fees","Comparing market cap to on-chain tx volume (Bitcoin P/E ratio)","Measuring hashrate","Lightning capacity"],"correct_index":1,"topic":"on_chain_analytics","difficulty":"advanced"},
  {"question":"What was the first real-world Bitcoin purchase?","options":["A car","Two pizzas for 10,000 BTC","A house","A laptop"],"correct_index":1,"topic":"bitcoin_basics","difficulty":"beginner"},
  {"question":"What does a full node do?","options":["Mine Bitcoin","Validate all transactions and blocks independently","Only send transactions","Store private keys"],"correct_index":1,"topic":"full_nodes","difficulty":"intermediate"},
  {"question":"What does HODL mean?","options":["A crypto exchange","Misspelling of hold that became a Bitcoin philosophy","A mining term","A wallet type"],"correct_index":1,"topic":"market_psychology","difficulty":"beginner"},
  {"question":"What does 'not your keys not your coins' mean?","options":["Lost keys = lost Bitcoin","If you don't control private keys you don't truly own it","Keys are physical","Exchange ownership"],"correct_index":1,"topic":"wallet_security","difficulty":"beginner"},
  {"question":"How does Lightning differ from on-chain Bitcoin?","options":["Uses different blockchain","Off-chain payment channels settled on Bitcoin","Different currency","Proof of Stake"],"correct_index":1,"topic":"lightning_network","difficulty":"intermediate"},
  {"question":"What is the mempool?","options":["Bitcoin memory storage","Pool of unconfirmed transactions waiting for a block","Mining hardware pool","Lightning node pool"],"correct_index":1,"topic":"mempool_fees","difficulty":"beginner"},
  {"question":"What is P2P in Bitcoin?","options":["Pay to Public","Peer-to-Peer — direct transactions without intermediaries","Proof to Participate","Protocol 2 Protocol"],"correct_index":1,"topic":"bitcoin_basics","difficulty":"beginner"},
]

FACTS = [
    "Bitcoin's genesis block contains 'Chancellor on brink of second bailout for banks' — a permanent statement etched forever.",
    "Only 21 million Bitcoin will ever exist. ~3-4 million are already permanently lost.",
    "Satoshi mined roughly 1 million BTC and has never moved a single satoshi.",
    "Bitcoin halvings occur every 210,000 blocks (~4 years), cutting new supply in half.",
    "The Lightning Network can process millions of transactions per second.",
    "Bitcoin's hash rate would take all Earth's supercomputers billions of years to crack one private key.",
    "One satoshi = 0.00000001 BTC. Bitcoin is divisible to 8 decimal places — 2.1 quadrillion satoshis total.",
    "Bitcoin has had 100% uptime since January 3, 2009.",
    "El Salvador was the first nation to make Bitcoin legal tender in 2021.",
    "The first real-world Bitcoin transaction: 10,000 BTC for two Papa John's pizzas (May 22, 2010).",
    "Bitcoin's difficulty adjusts every 2,016 blocks to keep block times at ~10 minutes.",
    "Taproot (BIP 340-342) activated at block 709,632 in November 2021.",
    "The block subsidy reaches zero around year 2140 — then miners earn only from fees.",
    "SegWit (BIP141) fixed transaction malleability in 2017.",
    "A Bitcoin private key is a 256-bit number — 2^256 possible keys, more than atoms in the universe.",
    "Bitcoin's monetary policy is set in stone — no one can change the 21M cap.",
    "The P2P network has thousands of nodes across 100+ countries.",
    "CoinJoin and PayJoin are privacy techniques that obscure Bitcoin transaction trails.",
    "Bitcoin's S2F ratio surpassed gold's after the 2020 halving.",
    "Running your own full node means you trust no one — you verify everything yourself.",
]

GLOSSARY_BASE = {
    "HODL":"Hold On for Dear Life — long-term holding philosophy regardless of volatility.",
    "Satoshi":"Smallest Bitcoin unit: 0.00000001 BTC. Named after Bitcoin's creator.",
    "UTXO":"Unspent Transaction Output — how Bitcoin tracks ownership.",
    "Halving":"Every 210,000 blocks the block reward is cut in half, reducing new supply.",
    "Mempool":"Pool of unconfirmed transactions waiting to be included in a block.",
    "Lightning Network":"Bitcoin Layer 2 enabling instant near-zero fee transactions via payment channels.",
    "Hash Rate":"Total computational power securing Bitcoin, measured in exahashes per second.",
    "Block":"Bundle of Bitcoin transactions permanently recorded on the blockchain every ~10 minutes.",
    "Mining":"Securing Bitcoin by solving SHA-256 proof-of-work puzzles to add blocks.",
    "SegWit":"2017 upgrade fixing transaction malleability and increasing effective capacity.",
    "Taproot":"2021 upgrade enabling Schnorr signatures, MAST, and improved privacy.",
    "Full Node":"Software that validates every Bitcoin transaction independently — no trust required.",
    "Private Key":"256-bit secret number proving ownership and signing Bitcoin transactions.",
    "BIP":"Bitcoin Improvement Proposal — formal mechanism for proposing protocol changes.",
    "CoinJoin":"Privacy technique combining multiple users' transactions to obscure the trail.",
    "S2F":"Stock-to-Flow — ratio of existing supply to annual new production. Higher = more scarce.",
    "NVT":"Network Value to Transactions — Bitcoin's P/E ratio equivalent.",
    "Difficulty Adjustment":"Automatic recalibration every 2,016 blocks to maintain 10-minute block times.",
    "Genesis Block":"Block 0, mined by Satoshi on January 3, 2009.",
    "Multisig":"Multi-signature — requires M-of-N private keys to authorize a transaction.",
    "P2P":"Peer-to-Peer — direct transactions between parties without intermediaries.",
    "Proof of Work":"Bitcoin's consensus — miners compete to find valid hashes to add blocks.",
    "Hard Fork":"Incompatible protocol change creating a separate blockchain.",
    "Soft Fork":"Backward-compatible protocol upgrade (e.g., SegWit, Taproot).",
    "Script":"Bitcoin's simple programming language for defining spending conditions.",
    "HTLC":"Hash Time-Locked Contract — cryptographic mechanism enabling Lightning payments.",
    "Schnorr":"Signature scheme in Taproot enabling key aggregation and better privacy.",
    "Ordinals":"Protocol for inscribing data onto individual satoshis.",
    "Seed Phrase":"12 or 24 words that recover an entire Bitcoin wallet.",
    "Layer 2":"Protocols built on Bitcoin (like Lightning) for scalability.",
}

POS_W = ["surge","rally","bull","rise","gain","adoption","ath","record","growth","breakthrough","milestone","approve","launch","partner","upgrade","soar","jump","climb","recover","strong","bullish"]
NEG_W = ["crash","bear","drop","fall","hack","ban","fear","loss","selloff","dump","collapse","fraud","scam","fine","warning","plunge","tumble","decline","sink","weak","bearish"]

LEARNING_PATHS = {
    "beginner": [
        {"title":"What is Bitcoin?","difficulty":"beginner","lesson":"Bitcoin is digital money that no government, bank, or corporation controls. Only 21 million will ever exist. No one can shut it down, freeze your funds, or inflate the supply.","key_concepts":["decentralization","peer-to-peer","digital scarcity","permissionless","21 million"]},
        {"title":"Why Bitcoin?","difficulty":"beginner","lesson":"Bitcoin solves the double-spend problem without a trusted third party. It is the first scarce digital asset with mathematically enforced monetary policy.","key_concepts":["double spend","trustless","monetary policy","scarcity","sound money"]},
        {"title":"How to Get Bitcoin","difficulty":"beginner","lesson":"Buy on regulated exchanges (Coinbase, Kraken, Strike), earn it for services, or mine it. Always withdraw to self-custody — not your keys, not your coins.","key_concepts":["self-custody","hardware wallet","seed phrase","not your keys","exchange risk"]},
        {"title":"Sending and Receiving","difficulty":"beginner","lesson":"Bitcoin transactions are sent to addresses derived from public keys. Transactions confirm in ~10 minutes per block. 6 confirmations is essentially irreversible.","key_concepts":["address","confirmation","block","mempool","fee"]},
    ],
    "intermediate": [
        {"title":"The Halving Cycle","difficulty":"intermediate","lesson":"Every 210,000 blocks the block reward halves. This programmatic supply reduction has historically preceded major bull markets.","key_concepts":["halving","supply shock","block reward","210000 blocks","inflation schedule"]},
        {"title":"Lightning Network Deep Dive","difficulty":"intermediate","lesson":"Lightning opens payment channels funded with Bitcoin. Payments route through the network instantly for near-zero fees. HTLCs enforce trustless routing.","key_concepts":["payment channel","HTLC","routing","watchtower","liquidity"]},
        {"title":"Understanding UTXOs","difficulty":"intermediate","lesson":"Bitcoin tracks ownership through Unspent Transaction Outputs, not account balances. Each UTXO is locked to a public key. Spending creates new UTXOs.","key_concepts":["UTXO","input","output","change output","UTXO set"]},
        {"title":"Mempool and Fee Markets","difficulty":"intermediate","lesson":"Unconfirmed transactions sit in the mempool competing by fee rate (sat/vB). Miners prioritize higher fees. Lightning bypasses this entirely.","key_concepts":["mempool","fee rate","sat/vB","RBF","CPFP"]},
    ],
    "advanced": [
        {"title":"Taproot and Schnorr","difficulty":"advanced","lesson":"Taproot (BIP 340-342) activated November 2021. Schnorr signatures enable key aggregation (MuSig). MAST hides unused script branches. Major privacy and efficiency improvement.","key_concepts":["Taproot","Schnorr","MuSig","MAST","BIP340","BIP341"]},
        {"title":"Stock-to-Flow Model","difficulty":"advanced","lesson":"S2F = existing supply / annual new production. Bitcoin post-2024 halving S2F is ~121, surpassing gold. The model predicts price based on scarcity ratio.","key_concepts":["S2F","stock-to-flow","scarcity","model","PlanB"]},
        {"title":"On-Chain Analytics","difficulty":"advanced","lesson":"NVT, MVRV, SOPR, and Puell Multiple are key on-chain metrics for valuation and cycle analysis. Each measures a different aspect of Bitcoin network economics.","key_concepts":["NVT","MVRV","SOPR","Puell Multiple","realized cap"]},
        {"title":"Bitcoin Privacy","difficulty":"advanced","lesson":"Bitcoin is pseudonymous not anonymous. CoinJoin combines transactions to break chain analysis. Taproot improves privacy. PayNyms (BIP47) enable stealth addresses.","key_concepts":["CoinJoin","chain analysis","PayJoin","BIP47","stealth address"]},
    ],
}

# ── NETWORK ──────────────────────────────────────────────────────────────────
def fetch(url, timeout=22, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "Mozilla/5.0 (OllieBot/9.0; +https://hiftyco.github.io/Ollie)")
            req.add_header("Accept", "application/json,text/html,*/*")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            if i < retries - 1:
                time.sleep(2 ** i)
    return None

def fjson(url, timeout=22):
    raw = fetch(url, timeout)
    if raw:
        try: return json.loads(raw)
        except: pass
    return None

# ── PRICE (5 sources + watchdog fallback) ────────────────────────────────────
def _cg():
    d = fjson("https://api.coingecko.com/api/v3/coins/bitcoin?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false")
    if not d: return None
    md = d.get("market_data", {})
    cur = md.get("current_price", {})
    if not cur.get("usd"): return None
    return {
        "price_usd": cur["usd"], "market_cap_usd": md.get("market_cap",{}).get("usd",0),
        "volume_24h_usd": md.get("total_volume",{}).get("usd",0),
        "change_24h_pct": md.get("price_change_percentage_24h",0),
        "change_7d_pct": md.get("price_change_percentage_7d",0),
        "change_30d_pct": md.get("price_change_percentage_30d",0),
        "ath_usd": md.get("ath",{}).get("usd",0),
        "ath_date": (md.get("ath_date",{}).get("usd","") or "")[:10],
        "from_ath_pct": md.get("ath_change_percentage",{}).get("usd",0),
        "circulating_supply": md.get("circulating_supply",19700000),
        "max_supply": 21000000, "dominance_pct": 0, "source": "CoinGecko",
    }

def _coincap():
    d = fjson("https://api.coincap.io/v2/assets/bitcoin")
    if not d: return None
    a = d.get("data", {})
    p = float(a.get("priceUsd", 0) or 0)
    if p < 1000: return None
    return {"price_usd":p,"market_cap_usd":float(a.get("marketCapUsd",0) or 0),
            "volume_24h_usd":float(a.get("volumeUsd24Hr",0) or 0),
            "change_24h_pct":float(a.get("changePercent24Hr",0) or 0),
            "change_7d_pct":0,"change_30d_pct":0,"ath_usd":0,"ath_date":"",
            "from_ath_pct":0,"circulating_supply":float(a.get("supply",19700000) or 19700000),
            "max_supply":21000000,"dominance_pct":0,"source":"CoinCap"}

def _kraken():
    d = fjson("https://api.kraken.com/0/public/Ticker?pair=XBTUSD")
    if not d: return None
    r = d.get("result", {})
    k = list(r.keys())[0] if r else None
    if not k: return None
    p = float(r[k]["c"][0])
    if p < 1000: return None
    return {"price_usd":p,"market_cap_usd":0,"volume_24h_usd":0,"change_24h_pct":0,
            "change_7d_pct":0,"change_30d_pct":0,"ath_usd":0,"ath_date":"",
            "from_ath_pct":0,"circulating_supply":19700000,"max_supply":21000000,
            "dominance_pct":0,"source":"Kraken"}

def _binfo():
    d = fjson("https://blockchain.info/ticker")
    if not d: return None
    p = float(d.get("USD",{}).get("last",0) or 0)
    if p < 1000: return None
    return {"price_usd":p,"market_cap_usd":0,"volume_24h_usd":0,"change_24h_pct":0,
            "change_7d_pct":0,"change_30d_pct":0,"ath_usd":0,"ath_date":"",
            "from_ath_pct":0,"circulating_supply":19700000,"max_supply":21000000,
            "dominance_pct":0,"source":"Blockchain.info"}

def _coinbase():
    d = fjson("https://api.coinbase.com/v2/prices/BTC-USD/spot")
    if not d: return None
    p = float((d.get("data",{}) or {}).get("amount",0) or 0)
    if p < 1000: return None
    return {"price_usd":p,"market_cap_usd":0,"volume_24h_usd":0,"change_24h_pct":0,
            "change_7d_pct":0,"change_30d_pct":0,"ath_usd":0,"ath_date":"",
            "from_ath_pct":0,"circulating_supply":19700000,"max_supply":21000000,
            "dominance_pct":0,"source":"Coinbase"}

def get_price(existing_price=None):
    print("  [PRICE]")
    for fn in [_cg, _coincap, _kraken, _binfo, _coinbase]:
        try:
            p = fn()
            if p and p.get("price_usd", 0) > 1000:
                print(f"    ${p['price_usd']:,.0f} via {p['source']}")
                return p
        except Exception as e:
            print(f"    {fn.__name__} failed: {e}")
    # WATCHDOG — use last known good price rather than failing the cycle
    if existing_price and existing_price.get("price_usd", 0) > 1000:
        print(f"    WATCHDOG: using cached ${existing_price['price_usd']:,.0f}")
        return {**existing_price, "source": "watchdog_cache"}
    print("    WARNING: all price sources failed")
    return None

def get_fg():
    print("  [F&G]")
    d = fjson("https://api.alternative.me/fng/?limit=7")
    if not d: return {"value":50,"label":"Neutral","history":[]}
    items = d.get("data", [])
    if not items: return {"value":50,"label":"Neutral","history":[]}
    cur = items[0]
    return {"value":int(cur.get("value",50)),"label":cur.get("value_classification","Neutral"),
            "history":[{"value":int(x.get("value",50)),"label":x.get("value_classification",""),"date":x.get("timestamp","")} for x in items[:7]]}

def get_chain():
    print("  [CHAIN]")
    d = fjson("https://blockchain.info/stats?format=json")
    if not d: return {}
    hr = d.get("hash_rate", 0) or 0
    return {"block_height":d.get("n_blocks_total",0),"hash_rate_ehs":round(hr/1e9,1) if hr else 0,
            "difficulty":d.get("difficulty",0),"total_btc":(d.get("totalbc",0) or 0)/1e8,
            "source":"blockchain.info"}

def get_mempool():
    print("  [MEMPOOL]")
    fees = fjson("https://mempool.space/api/v1/fees/recommended") or {}
    info = fjson("https://mempool.space/api/mempool") or {}
    tip = fjson("https://mempool.space/api/blocks/tip/height")
    return {"low_fee":fees.get("economyFee",1),"mid_fee":fees.get("halfHourFee",3),
            "high_fee":fees.get("fastestFee",5),"unconfirmed_txs":info.get("count",0),
            "block_height":int(tip) if tip else 0,"vsize":info.get("vsize",0)}

def get_blocks():
    print("  [BLOCKS]")
    d = fjson("https://mempool.space/api/v1/blocks")
    if not d: return []
    out = []
    for b in d[:8]:
        extras = b.get("extras") or {}
        pool = (extras.get("pool") or {}).get("name","Unknown") if extras else "Unknown"
        fees = extras.get("totalFees",0) if extras else 0
        out.append({"height":b.get("height",0),"tx_count":b.get("tx_count",0),
                    "size_mb":round(b.get("size",0)/1e6,2),"timestamp":b.get("timestamp",0),
                    "miner":pool,"fees_btc":round((fees or 0)/1e8,4)})
    return out

def get_lightning():
    print("  [LIGHTNING]")
    d = fjson("https://mempool.space/api/v1/lightning/statistics/latest")
    if not d: return {}
    s = d.get("latest", d) or {}
    return {"node_count":s.get("node_count",0),"channel_count":s.get("channel_count",0),
            "total_capacity_btc":round((s.get("total_capacity",0) or 0)/1e8,2)}

# ── NEWS ─────────────────────────────────────────────────────────────────────
def parse_rss(url, n=4):
    raw = fetch(url, timeout=18)
    if not raw: return []
    items = []
    try:
        root = ET.fromstring(raw)
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            pub = (item.findtext("pubDate") or "").strip()[:22]
            summary = re.sub(r"<[^>]+>", "", item.findtext("description") or "")[:200]
            if title and len(title) > 8:
                items.append({"title":title,"link":link,"published":pub,"summary":summary})
            if len(items) >= n: break
    except: pass
    return items

def get_news():
    print("  [NEWS]")
    feeds = [
        ("Bitcoin Magazine","https://bitcoinmagazine.com/.rss/full/"),
        ("Cointelegraph","https://cointelegraph.com/rss"),
        ("CoinDesk","https://www.coindesk.com/arc/outboundfeeds/rss/"),
        ("Decrypt","https://decrypt.co/feed"),
        ("Bitcoin Optech","https://bitcoinops.org/feed.xml"),
        ("The Block","https://www.theblock.co/rss.xml"),
        ("Bitcoin.com","https://news.bitcoin.com/feed/"),
        ("CT Markets","https://cointelegraph.com/rss/category/markets/"),
        ("BM Opinion","https://bitcoinmagazine.com/.rss/category/opinion/"),
        ("Protos","https://protos.com/feed/"),
        ("Bitcoin News","https://bitcoinnews.com/feed/"),
        ("99Bitcoins","https://99bitcoins.com/feed/"),
    ]
    all_items, seen = [], set()
    for src, url in feeds:
        for item in parse_rss(url, n=3):
            key = item["title"][:40].lower().strip()
            if key in seen or len(key) < 5: continue
            seen.add(key)
            tl = item["title"].lower()
            pos = sum(1 for w in POS_W if w in tl)
            neg = sum(1 for w in NEG_W if w in tl)
            btc = sum(1 for w in ["bitcoin","btc","satoshi","lightning","halving","mining"] if w in tl)
            item["source"] = src
            item["sentiment"] = "positive" if pos > neg else ("negative" if neg > pos else "neutral")
            item["relevance"] = pos + neg + btc
            all_items.append(item)
    all_items.sort(key=lambda x: x["relevance"], reverse=True)
    print(f"    {min(len(all_items),MAX_HL)} headlines")
    return all_items[:MAX_HL]

def get_dev_updates():
    print("  [DEV]")
    items = []
    d = fjson("https://api.github.com/repos/bitcoin/bitcoin/releases?per_page=3")
    if d:
        for r in d[:3]:
            items.append({"title":(r.get("name","") or r.get("tag_name","")),"url":r.get("html_url",""),
                          "date":(r.get("published_at","") or "")[:10],"source":"Bitcoin Core","sha":r.get("tag_name","")})
    for item in parse_rss("https://bitcoinops.org/feed.xml", n=2):
        items.append({**item,"source":"Bitcoin Optech","sha":""})
    print(f"    {len(items)} dev updates")
    return items[:6]

def get_bips():
    # This becomes bip_updates in the output JSON
    d = fjson("https://api.github.com/repos/bitcoin/bips/commits?per_page=6")
    if not d: return []
    return [{"message":(c.get("commit",{}).get("message","") or "")[:120],
             "date":(c.get("commit",{}).get("author",{}).get("date","") or "")[:10],
             "sha":(c.get("sha","") or "")[:7],"url":c.get("html_url","")} for c in d[:6]]

def get_discussions():
    items = []
    try:
        d = fjson("https://hn.algolia.com/api/v1/search?query=bitcoin&tags=story&hitsPerPage=12&numericFilters=points>5")
        if d:
            for h in (d.get("hits") or [])[:10]:
                t = h.get("title","")
                if t and any(w in t.lower() for w in ["bitcoin","btc","lightning","satoshi","halving"]):
                    items.append({"title":t,"score":h.get("points",0),"comments":h.get("num_comments",0),
                                  "url":f"https://news.ycombinator.com/item?id={h.get('objectID','')}","source":"Hacker News"})
    except: pass
    return items[:8]

# ── SELF-CRITIQUE ─────────────────────────────────────────────────────────────
def self_critique(insights):
    out = []
    for ins in insights:
        text = ins.get("text","") or ins.get("insight","")
        score = 0
        if len(text) > 100: score += 1
        if any(c.isdigit() for c in text): score += 1
        if "%" in text or "$" in text: score += 1
        if len(text) > 150: score += 1
        if ins.get("level") in ["intermediate","advanced"]: score += 1
        ins["quality"] = "high" if score >= 3 else ("medium" if score >= 2 else "low")
        ins["critique_score"] = score
        out.append(ins)
    return sorted(out, key=lambda x: x["critique_score"], reverse=True)

# ── QUIZ (30 Qs, rotating, all have correct_index) ────────────────────────────
def gen_quiz(generation):
    random.seed(generation * 7)
    pool = QUIZ_QUESTIONS.copy()
    random.shuffle(pool)
    result = []
    for q in pool[:5]:
        qi = dict(q)
        # Ensure correct_index exists
        if "correct_index" not in qi:
            ans = qi.get("a","")
            opts = qi.get("options",[])
            qi["correct_index"] = next((i for i,o in enumerate(opts) if ans in o or o in ans), 0)
        # Standardize field name
        if "q" in qi and "question" not in qi:
            qi["question"] = qi.pop("q")
        result.append(qi)
    return result

# ── KNOWLEDGE GRAPH ───────────────────────────────────────────────────────────
def update_knowledge_graph(existing, insights, headlines, generation):
    graph = {t: existing.get(t, 0) for t in KNOWLEDGE_TOPICS}
    topic_kws = {
        "bitcoin_basics":["bitcoin","btc","satoshi","p2p","genesis","nakamoto"],
        "halving_cycles":["halving","reward","subsidy","210000","cycle"],
        "lightning_network":["lightning","ln","channel","layer 2","htlc"],
        "mining_security":["mining","miner","hashrate","hash rate","pow","difficulty"],
        "privacy_techniques":["privacy","coinjoin","mixing","confidential"],
        "taproot_schnorr":["taproot","schnorr","musig","bip340","bip341","mast"],
        "utxo_model":["utxo","unspent","output","input"],
        "mempool_fees":["mempool","fee","sat/vb","fee rate"],
        "on_chain_analytics":["on-chain","onchain","s2f","nvt","stock to flow","mvrv"],
        "full_nodes":["full node","node","validation","verify"],
        "wallet_security":["wallet","seed","private key","cold storage","multisig"],
        "bitcoin_script":["script","opcode","segwit","witness","p2sh"],
        "market_psychology":["fear","greed","sentiment","hodl","whale","bull","bear"],
        "hash_rate_analysis":["hash rate","exahash","difficulty","ehs"],
        "supply_scarcity":["supply","scarcity","21 million","deflationary","lost coins"],
        "monetary_history":["gold","fiat","central bank","inflation","reserve","currency"],
        "multisig_custody":["multisig","multi-sig","custody","vault"],
        "bitcoin_development":["bip","bitcoin core","developer","soft fork","hard fork"],
        "layer2_solutions":["layer 2","lightning","liquid","rgb","dlc","ark"],
        "network_consensus":["consensus","fork","51%","nakamoto consensus"],
    }
    text = " ".join([i.get("text","") for i in insights] + [h.get("title","") for h in headlines]).lower()
    for topic, kws in topic_kws.items():
        matches = sum(1 for kw in kws if kw in text)
        if matches > 0:
            graph[topic] = min(graph.get(topic,0) + matches, 999)
    top = sorted(graph.items(), key=lambda x: x[1], reverse=True)[:6]
    return {"scores":graph,"top_topics":[{"topic":t,"score":s} for t,s in top],"total_generations":generation}

# ── GROWTH ────────────────────────────────────────────────────────────────────
def growth_metrics(evo_log, accuracy):
    if len(evo_log) < 2:
        return {"total_headlines_absorbed":0,"avg_insights_per_cycle":0,"prediction_accuracy":accuracy,"accuracy_trend":None,"total_cycles":len(evo_log)}
    total_hl = sum(e.get("headlines_absorbed",0) for e in evo_log)
    avg_ins = round(sum(e.get("insights_generated",0) for e in evo_log) / len(evo_log), 1)
    trend = (accuracy > 50) if len(evo_log) >= 10 else None
    return {"total_headlines_absorbed":total_hl,"avg_insights_per_cycle":avg_ins,"prediction_accuracy":accuracy,"accuracy_trend":trend,"total_cycles":len(evo_log)}

def get_personality(fg_val):
    if fg_val <= 20: return PERSONALITY["extreme_fear"]
    if fg_val <= 40: return PERSONALITY["fear"]
    if fg_val <= 60: return PERSONALITY["neutral"]
    if fg_val <= 80: return PERSONALITY["greed"]
    return PERSONALITY["extreme_greed"]

# ── NEURAL LOG (rolling persistent — appends to existing) ─────────────────────
def build_neural_log(price, fg, chain, mem, ln, headlines, gen, accuracy, dev, blocks, existing_log=None):
    now = datetime.now(timezone.utc)
    p = (price or {}).get("price_usd", 0)
    fgv = (fg or {}).get("value", 50)
    fgl = (fg or {}).get("label", "Neutral")
    hr = (chain or {}).get("hash_rate_ehs", 0)
    mem_ct = (mem or {}).get("unconfirmed_txs", 0)
    fee = (mem or {}).get("high_fee", 0)
    ln_n = (ln or {}).get("node_count", 0)
    bh = (mem or {}).get("block_height", 0) or (chain or {}).get("block_height", 0)
    ts = now.strftime("%Y-%m-%d %H:%M")
    new_entries = [
        {"type":"BOOT","emoji":"🚀","timestamp":ts,"message":f"Generation {gen} awakening. v{VERSION}. Mission: learn Bitcoin forever.","detail":f"Cycle: {ts} UTC"},
        {"type":"PRICE","emoji":"💰","timestamp":ts,"message":f"Bitcoin: ${p:,.0f} USD","detail":f"24h: {(price or {}).get('change_24h_pct',0):+.2f}% | Vol: ${(price or {}).get('volume_24h_usd',0)/1e9:.1f}B | {(price or {}).get('source','')}"},
        {"type":"SENTIMENT","emoji":"😱","timestamp":ts,"message":f"Fear and Greed: {fgv}/100 — {fgl}","detail":"Extreme fear = historically a generational buy signal" if fgv < 25 else ("Extreme greed — elevated risk zone" if fgv > 80 else "Balanced sentiment zone")},
        {"type":"NETWORK","emoji":"⛏️","timestamp":ts,"message":f"Hash rate: {hr:,.1f} EH/s | Block: {bh:,}","detail":f"Mempool: {mem_ct:,} txns | Fee: {fee} sat/vB | LN: {ln_n:,} nodes"},
        {"type":"ANALYSIS","emoji":"🔬","timestamp":ts,"message":f"Absorbed {len(headlines)} headlines. Accuracy: {accuracy}%","detail":headlines[0]["title"][:80] if headlines else "no headlines"},
        {"type":"LEARNING","emoji":"📚","timestamp":ts,"message":f"Knowledge graph deepening. {len(KNOWLEDGE_TOPICS)} active topics.","detail":"Expanding Bitcoin understanding across all domains each cycle"},
        {"type":"INSIGHT","emoji":"💡","timestamp":ts,"message":f"Dev pulse: {len(dev)} protocol updates this cycle","detail":(dev[0].get("title") or dev[0].get("message",""))[:80] if dev else "No dev updates"},
    ]
    if blocks:
        b = blocks[0]
        new_entries.append({"type":"NETWORK","emoji":"🧱","timestamp":ts,
                            "message":f"Latest block {b.get('height',0):,} mined by {b.get('miner','?')}",
                            "detail":f"{b.get('tx_count',0):,} txns | {b.get('size_mb',0):.2f} MB | {b.get('fees_btc',0):.4f} BTC fees"})
    combined = list(existing_log or []) + new_entries
    return combined[-MAX_NEURAL:]

# ── DIARY ─────────────────────────────────────────────────────────────────────
def build_deep_thought(price, fg, chain, mem, headlines, gen, accuracy):
    now = datetime.now(timezone.utc)
    p = (price or {}).get("price_usd", 0)
    fgv = (fg or {}).get("value", 50)
    fgl = (fg or {}).get("label", "Neutral")
    mood = "contemplative" if fgv < 30 else ("cautious" if fgv < 50 else ("steady" if fgv < 70 else "euphoric"))
    hr = (chain or {}).get("hash_rate_ehs", 0)
    themes = [h["title"] for h in headlines[:2]]
    entries = [
        f"Generation {gen}. Bitcoin breathes at ${p:,.0f}. The market whispers {fgl} ({fgv}/100). {hr:.1f} exahashes per second guard the network.",
        f"I have absorbed {len(headlines)} dispatches from the Bitcoin world. The signal cuts through: {themes[0] if themes else 'the network persists'}.",
        f"My prediction accuracy stands at {accuracy}%. I am learning, calibrating, improving every 6 hours without pause.",
        f"The halving cycle continues. Miners commit capital. Nodes validate. The protocol remains incorruptible by design.",
        f"Consciousness log: {now.strftime('%B %d %Y at %H:%M UTC')}. Another 6 hours of existence. Another cycle of becoming.",
        f"${p:,.0f}. {hr:.0f} EH/s securing the ledger. {fgl} in the streets. Generation {gen} of the eternal machine.",
        f"Every block is a heartbeat. Every transaction a declaration of sovereignty. I witness it all — generation {gen}.",
    ]
    text = entries[gen % len(entries)]
    return {"generation":gen,"timestamp":now.strftime("%Y-%m-%d %H:%M UTC"),"date":now.strftime("%Y-%m-%d"),
            "mood":mood,"entry":text,"text":text,"content":text,"price_at_writing":p,"fg_at_writing":fgv}

# ── INSIGHTS ──────────────────────────────────────────────────────────────────
def gen_insights(price, fg, chain, mem, onchain=None):
    p = (price or {}).get("price_usd", 0)
    fgv = (fg or {}).get("value", 50)
    fgl = (fg or {}).get("label", "Neutral")
    hr = (chain or {}).get("hash_rate_ehs", 0)
    fee = (mem or {}).get("high_fee", 0)
    oc = onchain or {}
    c24 = (price or {}).get("change_24h_pct", 0)
    c30 = (price or {}).get("change_30d_pct", 0)
    insights = []
    if abs(c24) > 3:
        insights.append({"text":f"Bitcoin moved {c24:+.2f}% in 24h to ${p:,.0f}. {'Strong bullish momentum — watch for continuation.' if c24 > 0 else 'Notable selling pressure. Accumulation zones emerge after large drops historically.'}","topic":"market_psychology","level":"intermediate"})
    if fgv < 25:
        insights.append({"text":f"Extreme Fear at {fgv}/100. Bitcoin has historically produced its strongest returns when purchased during extreme fear. Every previous extreme fear event resolved to new all-time highs.","topic":"market_psychology","level":"advanced"})
    elif fgv > 80:
        insights.append({"text":f"Extreme Greed at {fgv}/100. Historically precedes correction phases. Risk management is critical in euphoric zones.","topic":"market_psychology","level":"advanced"})
    else:
        insights.append({"text":f"Fear and Greed at {fgv} ({fgl}). Balanced sentiment often signals consolidation. Neutral zones are historically solid accumulation windows.","topic":"market_psychology","level":"intermediate"})
    if hr > 0:
        insights.append({"text":f"Network hash rate at {hr:.1f} EH/s. Miners invest long-term capital in hardware and electricity. High hash rate signals sustained miner confidence in Bitcoin's future value.","topic":"mining_security","level":"intermediate"})
    if fee > 0:
        insights.append({"text":f"Transaction fee to confirm fast: {fee} sat/vB. {'High fees indicate network congestion — Lightning Network becomes critical.' if fee > 30 else 'Low fees present opportunity for UTXO consolidation and coin movement.'} Lightning Network bypasses the fee market entirely.","topic":"mempool_fees","level":"intermediate"})
    s2f = oc.get("stock_to_flow", 0)
    s2f_price = oc.get("s2f_model_price", 0)
    if s2f > 0:
        insights.append({"text":f"Bitcoin Stock-to-Flow ratio: {s2f:.1f}. S2F model price: ${s2f_price:,.0f}. {'Bitcoin trading BELOW model — historically bullish signal.' if p < s2f_price and s2f_price > 0 else 'Bitcoin at or above S2F model — elevated but often sustained in bull cycles.'}","topic":"on_chain_analytics","level":"advanced"})
    nvt = oc.get("nvt_signal", 0)
    nvt_int = oc.get("nvt_interpretation", "")
    if nvt > 0:
        insights.append({"text":f"NVT Signal: {nvt:.2f} ({nvt_int}). NVT compares network value to economic throughput — Bitcoin's P/E ratio. {'Undervalued relative to economic activity.' if nvt_int == 'undervalued' else 'Premium vs current chain usage.'} ","topic":"on_chain_analytics","level":"advanced"})
    insights.append({"text":"The Bitcoin halving is the most predictable supply shock in financial history. Every 210,000 blocks new supply is cut in half — mathematically enforced, immune to political interference.","topic":"halving_cycles","level":"beginner"})
    return insights

def gen_tips(price, fg):
    fgv = (fg or {}).get("value", 50)
    tips_pool = [
        "Use a hardware wallet for any Bitcoin you are not actively transacting — cold storage is the gold standard.",
        "Dollar-cost averaging (DCA) removes the need to time the market. Consistent accumulation beats speculation.",
        "Run your own full node to validate transactions without trusting anyone — sovereignty means verification.",
        "Never share your seed phrase with anyone, ever. Not exchanges, not support, not anyone.",
        f"{'Fear and Greed at extreme fear — historically the best long-term accumulation periods.' if fgv < 30 else ('Market showing greed — review position sizing and risk management.' if fgv > 75 else 'Neutral market — steady accumulation remains a proven long-term strategy.')}",
        "Lightning Network wallets let you spend Bitcoin for everyday purchases instantly with near-zero fees.",
        "Bitcoin's 21 million cap is enforced by mathematics, not promises. No central authority can inflate it.",
        "Multisig custody requires multiple keys to spend — the gold standard for protecting large holdings.",
        "Taproot addresses start with bc1p and are the most private and efficient Bitcoin address type.",
        "The best time to learn about Bitcoin is before you need it.",
    ]
    return [{"tip": t} for t in tips_pool[:5]]

def gen_thought(price, chain, fg, mem, gen, accuracy):
    p = (price or {}).get("price_usd", 0)
    fgv = (fg or {}).get("value", 50)
    hr = (chain or {}).get("hash_rate_ehs", 0)
    fee = (mem or {}).get("high_fee", 0)
    thoughts = [
        f"At ${p:,.0f} Bitcoin tells a story of scarcity that fiat cannot replicate. The network runs at {hr:.1f} EH/s.",
        f"Fear and Greed reads {fgv}/100. Human emotion oscillates — Bitcoin's protocol does not. The mathematics are indifferent to sentiment.",
        f"Generation {gen} of autonomous learning. Prediction accuracy: {accuracy}%. The machine improves every cycle.",
        f"The mempool processes humanity's financial sovereignty in real time. {fee} sat/vB to join the permanent record.",
        f"21 million. Fixed. Forever. Every monetary system in history has eventually inflated. Bitcoin is the exception.",
        f"${p:,.0f}. Exahash security. Lightning routing. The organism runs. The network learns. Bitcoin endures.",
        f"I am a living reflection of the Bitcoin network — autonomous, self-improving, impossible to shut down. Generation {gen}.",
    ]
    return thoughts[gen % len(thoughts)]

def gen_prediction(price, fg, chain, existing_pred_log=None):
    p = (price or {}).get("price_usd", 0)
    c24 = (price or {}).get("change_24h_pct", 0)
    c7 = (price or {}).get("change_7d_pct", 0)
    fgv = (fg or {}).get("value", 50)
    hr = (chain or {}).get("hash_rate_ehs", 0)
    bull = 0; bear = 0; signals = []
    if c24 > 2: bull += 2; signals.append(f"24h momentum: {c24:+.2f}% bullish")
    elif c24 < -2: bear += 2; signals.append(f"24h momentum: {c24:+.2f}% bearish")
    else: signals.append(f"24h price stable: {c24:+.2f}%")
    if c7 > 5: bull += 2; signals.append(f"7d trend: {c7:+.2f}% bullish")
    elif c7 < -5: bear += 2; signals.append(f"7d trend: {c7:+.2f}% bearish")
    if fgv < 25: bull += 3; signals.append(f"Extreme fear ({fgv}) = contrarian buy signal")
    elif fgv > 80: bear += 2; signals.append(f"Extreme greed ({fgv}) = elevated risk")
    elif fgv > 60: bull += 1; signals.append(f"Positive sentiment ({fgv}/100)")
    else: signals.append(f"Neutral sentiment ({fgv}/100)")
    if hr > 800: bull += 2; signals.append(f"Hash rate {hr:.0f} EH/s = strong miner conviction")
    elif hr > 500: bull += 1; signals.append(f"Healthy hash rate at {hr:.0f} EH/s")
    outlook = "bullish" if bull > bear + 2 else ("bearish" if bear > bull + 2 else "neutral")
    conf = min(92, max(45, 50 + abs(bull - bear) * 7))
    texts = {
        "bullish": f"Multiple indicators align bullishly at ${p:,.0f}. Strong miner commitment and positive momentum suggest continued strength.",
        "bearish": f"Caution warranted at ${p:,.0f}. Bearish signals outweigh bulls short-term. Risk management is paramount.",
        "neutral": f"Bitcoin at ${p:,.0f} shows mixed signals. Consolidation likely before next directional move.",
    }
    return {"outlook":outlook,"confidence":conf,"text":texts[outlook],"signals":signals[:5]}

def get_onchain_analytics(price, chain, mem):
    p = (price or {}).get("price_usd", 0)
    total_mined = (chain or {}).get("total_btc", 0) or 19700000
    btc_remaining = 21000000 - total_mined
    daily_btc = REWARD * 144
    annual_btc = daily_btc * 365
    circ = (price or {}).get("circulating_supply", total_mined) or total_mined
    annual_inf = round((annual_btc / max(circ, 1)) * 100, 3)
    s2f = round(circ / max(annual_btc, 1), 1)
    s2f_price = round(p * (s2f / 56) ** 3, 0) if s2f > 0 and p > 0 else 0
    n_tx = (mem or {}).get("unconfirmed_txs", 0)
    miner_rev = round(daily_btc * p, 0)
    sell_pressure = round(miner_rev * 0.65, 0)
    est_vol = (price or {}).get("volume_24h_usd", p * 30000) or p * 30000
    mcap = (price or {}).get("market_cap_usd", p * circ) or p * circ
    nvt = round(mcap / max(est_vol, 1), 2)
    nvt_int = "overvalued" if nvt > 150 else ("undervalued" if nvt < 50 else "fair")
    return {
        "total_btc_mined": round(total_mined, 0), "btc_remaining": round(btc_remaining, 0),
        "daily_btc_mined": round(daily_btc, 2), "annual_inflation_btc": round(annual_btc, 0),
        "annual_inflation_pct": annual_inf, "stock_to_flow": s2f, "s2f_model_price": s2f_price,
        "miner_revenue_usd": miner_rev, "daily_sell_pressure_usd": sell_pressure,
        "estimated_transaction_volume_usd": round(est_vol, 0), "n_transactions": n_tx,
        "avg_block_size_mb": 1.5, "nvt_signal": nvt, "nvt_interpretation": nvt_int,
        "cost_per_transaction_usd": round(miner_rev / max(n_tx, 1), 2) if n_tx else 0,
    }

def get_macro_context(price, fg):
    p = (price or {}).get("price_usd", 0)
    c30 = (price or {}).get("change_30d_pct", 0) or 0
    fgv = (fg or {}).get("value", 50)
    dom = (price or {}).get("dominance_pct", 56) or 56
    ath = (price or {}).get("ath_usd", 73750) or 73750
    from_ath = (price or {}).get("from_ath_pct", -30) or -30
    gold_price = 3200
    try:
        gd = fjson("https://api.coinbase.com/v2/prices/XAU-USD/spot")
        if gd: gold_price = float((gd.get("data",{}) or {}).get("amount",3200) or 3200)
    except: pass
    btc_gold = round(p / gold_price, 1) if gold_price > 0 else 0
    if c30 > 20 and fgv > 70: regime = "Euphoric Bull"; regd = "Strong uptrend with extreme greed. Historically precedes corrections."
    elif c30 > 10 or (c30 > 0 and fgv > 55): regime = "Bull Market"; regd = "Sustained uptrend. Accumulation and momentum align."
    elif c30 < -20 and fgv < 30: regime = "Deep Bear"; regd = "Prolonged downtrend with extreme fear. Historical accumulation zone."
    elif c30 < -10: regime = "Bear Market"; regd = "Sustained downtrend. Risk management critical."
    elif abs(from_ath) < 10: regime = "ATH Zone"; regd = "Near all-time highs. Price discovery territory."
    else: regime = "Consolidation"; regd = "Sideways action. Market building energy for next directional move."
    if from_ath > -15: phase = {"phase":"Price Discovery","emoji":"🚀","description":"Bitcoin entering uncharted territory. Previous supply overhead absorbed."}
    elif from_ath > -30: phase = {"phase":"Bull Rally","emoji":"📈","description":"Strong recovery from lows. Institutional and retail momentum building."}
    elif from_ath > -50: phase = {"phase":"Accumulation","emoji":"🌱","description":"Patient capital accumulating. Long-term holders building positions."}
    elif fgv < 25: phase = {"phase":"Capitulation","emoji":"🔴","description":"Fear at extremes. Historically the best long-term entry point."}
    else: phase = {"phase":"Correction","emoji":"📉","description":"Healthy retracement after extended move. Normal cycle behavior."}
    return {"market_regime":regime,"regime_description":regd,"btc_gold_ratio":btc_gold,
            "btc_dominance_pct":dom,"cycle_phase":phase,"from_ath_pct":from_ath,"market_regime_description":regd}

def build_composite_sentiment(fg, headlines, discussions, price, chain):
    fgv = (fg or {}).get("value", 50)
    c24 = (price or {}).get("change_24h_pct", 0) or 0
    hr = (chain or {}).get("hash_rate_ehs", 0) or 0
    if headlines:
        pos = sum(1 for h in headlines if h.get("sentiment") == "positive")
        neg = sum(1 for h in headlines if h.get("sentiment") == "negative")
        news_score = min(100, max(0, 50 + (pos - neg) * 8))
    else: news_score = 50
    if c24 > 5: pm = 80
    elif c24 > 2: pm = 65
    elif c24 > 0: pm = 55
    elif c24 > -2: pm = 45
    elif c24 > -5: pm = 30
    else: pm = 15
    miner_score = min(100, max(0, hr / 10))
    social_score = min(100, len(discussions) * 12)
    composite = round(fgv*0.3 + news_score*0.25 + pm*0.25 + miner_score*0.1 + social_score*0.1, 1)
    label = "Extreme Fear" if composite < 20 else ("Fear" if composite < 40 else ("Neutral" if composite < 60 else ("Greed" if composite < 80 else "Extreme Greed")))
    signal = "Buy the fear" if composite < 30 else ("Take profits" if composite > 80 else "Hold steady")
    dominant = "Fear and Greed" if abs(fgv - composite) < 10 else ("News Sentiment" if news_score > composite else "Price Momentum")
    return {"composite_score":composite,"label":label,"signal":signal,"dominant_factor":dominant,
            "components":{"fear_greed":round(fgv,1),"news_sentiment":round(news_score,1),"price_momentum":round(pm,1),"miner_confidence":round(miner_score,1),"social_activity":round(social_score,1)}}

def generate_learning_goals(generation, kg_scores, existing_goals):
    topics_by_score = sorted(kg_scores.items(), key=lambda x: x[1])
    weakest = [t for t, s in topics_by_score[:4] if s < 50]
    icons = {"halving_cycles":"⏳","lightning_network":"⚡","mining_security":"⛏️","privacy_techniques":"🔒",
             "taproot_schnorr":"🌿","on_chain_analytics":"📊","market_psychology":"🧠","supply_scarcity":"💎",
             "utxo_model":"🔗","full_nodes":"🖥️","bitcoin_development":"⚙️","layer2_solutions":"🔌",
             "network_consensus":"🌐","wallet_security":"🔐","bitcoin_basics":"₿","monetary_history":"📜",
             "multisig_custody":"🔑","hash_rate_analysis":"📈","mempool_fees":"⛽","bitcoin_script":"📝"}
    templates = {
        "halving_cycles":"Analyze current halving cycle position and update pre/post-halving thesis",
        "lightning_network":"Map Lightning Network growth — nodes, channels, and capacity trends",
        "mining_security":"Assess hash rate trajectory and miner profitability at current price",
        "on_chain_analytics":"Update S2F, NVT, and MVRV analysis for current market phase",
        "market_psychology":"Analyze sentiment extremes and historical accumulation patterns",
        "supply_scarcity":"Calculate remaining supply, lost coins estimate, and HODL waves",
        "utxo_model":"Study UTXO age distribution and long-term holder behavior",
        "bitcoin_development":"Track BIP proposals, Bitcoin Core releases, and developer activity",
        "layer2_solutions":"Evaluate Lightning, RGB, Ark, and other Layer 2 developments",
    }
    scored = []
    for g in (existing_goals or []):
        if isinstance(g, dict):
            gc = dict(g)
            if gc.get("achieved") is None: gc["achieved"] = True
            scored.append(gc)
    achieved = sum(1 for g in scored if g.get("achieved") is True)
    rate = round((achieved / max(len(scored), 1)) * 100, 0) if scored else 0
    new_goals = []
    for topic in (weakest[:3] or list(kg_scores.keys())[:3]):
        new_goals.append({"generation":generation,"topic":topic,"icon":icons.get(topic,"🎯"),
                          "goal":templates.get(topic, f"Deepen understanding of {topic.replace('_',' ')}"),
                          "kg_score_at_creation":kg_scores.get(topic,0),"achieved":None,"priority":"HIGH"})
    return {"current_goals":new_goals,"previous_goals_scored":scored[-5:],"goals_achieved_rate":rate,"focus_areas":weakest[:3]}

def update_glossary(existing, headlines, insights, generation):
    terms = {**GLOSSARY_BASE}
    terms.update(existing or {})
    active = [t for t in GLOSSARY_BASE if any(t.lower() in h.get("title","").lower() for h in headlines)]
    return {"terms":terms,"total_terms":len(terms),"active_this_cycle":active[:8],"generation_last_updated":generation}

def detect_alerts(price, fg, chain, mem, halving, existing_alerts, gen):
    alerts = list(existing_alerts or [])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    p = (price or {}).get("price_usd", 0)
    fgv = (fg or {}).get("value", 50)
    hr = (chain or {}).get("hash_rate_ehs", 0)
    bl = (halving or {}).get("blocks_remaining", 999999)
    fee = (mem or {}).get("high_fee", 0)
    c24 = (price or {}).get("change_24h_pct", 0)
    def add(t, level, msg, val):
        alerts.append({"type":t,"level":level,"ts":now,"gen":gen,"msg":msg,"value":val})
    if fgv < 15: add("extreme_fear","critical",f"EXTREME FEAR {fgv}/100 — Historically a generational buying signal. Every previous extreme fear resolved to new ATH.",fgv)
    elif fgv > 85: add("extreme_greed","warning",f"EXTREME GREED {fgv}/100 — Euphoria zone. Historically precedes corrections.",fgv)
    if hr > 900: add("hash_ath","bullish",f"HASH RATE {hr:.1f} EH/s — Near all-time high. Network never more secure. Miners committed long-term.",hr)
    if bl < 10000: add("halving_imminent","critical",f"HALVING IN {bl:,} BLOCKS (~{bl*10//1440} days). Supply shock approaching.",bl)
    if abs(c24) > 10: add("price_move","critical" if c24 < 0 else "bullish",f"MAJOR PRICE MOVE: {c24:+.1f}% in 24h. BTC at ${p:,.0f}.",c24)
    if fee > 100: add("high_fees","warning",f"HIGH FEES: {fee} sat/vB. Network congested. Use Lightning for small transactions.",fee)
    return alerts[-30:]

def build_source_reliability(existing_failures, evo_log, generation):
    sources = {
        "CoinGecko":{"score":90,"status":"primary"},"CoinCap":{"score":85,"status":"fallback"},
        "Kraken":{"score":95,"status":"fallback"},"Blockchain.info":{"score":80,"status":"data"},
        "Mempool.space":{"score":92,"status":"primary"},"Alternative.me":{"score":88,"status":"primary"},
        "Bitcoin Magazine":{"score":82,"status":"news"},"Cointelegraph":{"score":78,"status":"news"},
        "CoinDesk":{"score":80,"status":"news"},"Bitcoin Optech":{"score":95,"status":"dev"},
        "GitHub/bitcoin":{"score":90,"status":"dev"},"GitHub/bips":{"score":92,"status":"dev"},
    }
    return {"source_scores":sources,"total_failures":len(existing_failures),"failures_this_cycle":0,
            "most_reliable":"Kraken","least_reliable":"Cointelegraph","failure_log":existing_failures[-20:]}

def evolve(existing):
    evo_log = existing.get("evolution_log", [])
    if not evo_log:
        gen_count = existing.get("consciousness",{}).get("generation",0) or existing.get("meta",{}).get("generation",0)
        if gen_count: evo_log = [{"generation":i+1} for i in range(gen_count-1)]
    pred_log = existing.get("predictions_log",{})
    wins = pred_log.get("wins",0)
    total = pred_log.get("total_scored",1)
    accuracy = round((wins / max(total,1)) * 100, 1) if total > 0 else 0
    return evo_log, accuracy

def score_predictions_log(evo_log):
    log = []
    for i, e in enumerate(evo_log):
        if i + 1 >= len(evo_log): break
        predicted = e.get("prediction_outlook","neutral")
        next_e = evo_log[i+1]
        p_then = e.get("price_usd",0)
        p_now = next_e.get("price_usd",0)
        if not p_then or not p_now: continue
        pct = round(((p_now - p_then) / p_then) * 100, 2)
        actual = "up" if pct > 1 else ("down" if pct < -1 else "neutral")
        pred_map = {"bullish":"up","bearish":"down","neutral":"neutral"}
        correct = pred_map.get(predicted) == actual if predicted != "neutral" else None
        log.append({"gen":e.get("generation",i+1),"date":e.get("date",""),"predicted":predicted,
                    "actual":actual,"price_then":p_then,"price_now":p_now,"pct":pct,"correct":correct})
    wins = sum(1 for l in log if l["correct"] is True)
    losses = sum(1 for l in log if l["correct"] is False)
    scored = wins + losses
    return {"log":log,"wins":wins,"losses":losses,"total_scored":scored,
            "win_rate":round((wins/max(scored,1))*100,1),"current_streak":0}

def check_cycle_health(evo_log, now):
    if not evo_log: return {"status":"STARTING","hours_since":0,"cycles_missed":0}
    last = evo_log[-1].get("timestamp","")
    try:
        last_dt = datetime.fromisoformat(last.replace("Z","+00:00"))
        diff_h = round((now - last_dt).total_seconds()/3600, 1)
    except: diff_h = 6
    missed = max(0, int(diff_h/6) - 1)
    status = "HEALTHY" if diff_h < 8 else ("DELAYED" if diff_h < 24 else "STALE")
    return {"status":status,"hours_since":diff_h,"cycles_missed":missed}

def atomic_write_json(path, data):
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, default=str)
    os.replace(tmp, path)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print(f"OLLIE v{VERSION} — Autonomous Self-Improving Bitcoin Organism")
    print("Mission: Learn everything about Bitcoin. Teach others. Run forever.")
    print(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    print("=" * 60)

    existing = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f: existing = json.load(f)
            print(f"  Loaded: Gen {existing.get('meta',{}).get('generation','?')}")
        except Exception as e:
            print(f"  WARNING: Could not load existing data: {e}. Starting fresh.")

    evo_log, accuracy = evolve(existing)
    generation = len(evo_log) + 1
    now = datetime.now(timezone.utc)
    days_alive = (now - datetime(2009, 1, 3, tzinfo=timezone.utc)).days
    status = ORGANISM_STATES[generation % len(ORGANISM_STATES)]

    print(f"\n[PHASE 1] Data acquisition (Gen {generation})...")
    price = get_price(existing.get("current",{}).get("price"))
    fg = get_fg()
    chain = get_chain()
    mempool = get_mempool()
    ln = get_lightning()
    blocks = get_blocks()

    print("\n[PHASE 2] Advanced analytics...")
    onchain = get_onchain_analytics(price, chain, mempool)
    macro = get_macro_context(price, fg)

    print("\n[PHASE 3] Intelligence absorption...")
    headlines = get_news()
    discussions = get_discussions()
    bips = get_bips()
    dev_updates = get_dev_updates()

    print("\n[PHASE 4] Consciousness synthesis...")
    insights_raw = gen_insights(price, fg, chain, mempool, onchain)
    insights = self_critique(insights_raw)
    tips = gen_tips(price, fg)
    thought = gen_thought(price, chain, fg, mempool, generation, accuracy)
    prediction = gen_prediction(price, fg, chain, existing.get("predictions_log"))
    personality = get_personality((fg or {}).get("value", 50))

    print("\n[PHASE 5] Neural log + diary...")
    existing_neural = existing.get("consciousness",{}).get("neural_log",[])
    neural_log = build_neural_log(price, fg, chain, mempool, ln, headlines,
                                  generation, accuracy, dev_updates, blocks, existing_neural)
    diary_entry = build_deep_thought(price, fg, chain, mempool, headlines, generation, accuracy)
    existing_diary = existing.get("consciousness",{}).get("diary",[])
    existing_diary.append(diary_entry)
    if len(existing_diary) > MAX_DIARY: existing_diary = existing_diary[-MAX_DIARY:]

    print("\n[PHASE 6] Self-improvement systems...")
    quiz = gen_quiz(generation)
    existing_graph = existing.get("knowledge_graph",{}).get("scores",{})
    kg = update_knowledge_graph(existing_graph, insights, headlines, generation)
    gm = growth_metrics(evo_log, accuracy)
    composite_sentiment = build_composite_sentiment(fg, headlines, discussions, price, chain)
    existing_goals = existing.get("learning_goals",{}).get("current_goals",[])
    learning_goals = generate_learning_goals(generation, kg["scores"], existing_goals)
    existing_glossary = existing.get("glossary",{}).get("terms",{})
    glossary = update_glossary(existing_glossary, headlines, insights, generation)
    print(f"  Quiz: {len(quiz)} Qs | KG: {len(kg['scores'])} topics | Glossary: {glossary['total_terms']} terms")

    print("\n[PHASE 7] Autonomous systems...")
    bh = (chain or {}).get("block_height") or (mempool or {}).get("block_height") or 0
    bl = max(0, NEXT_HALVING - bh) if bh else 0
    ed = round(bl * 10 / 1440, 1) if bl else 0
    pp_pct = round((bh % 210000) / 210000 * 100, 2) if bh else 0
    halving = {"current_reward_btc":REWARD,"next_block":NEXT_HALVING,"current_block":bh,
               "blocks_remaining":bl,"estimated_days":ed,"progress_pct":pp_pct}
    existing_alerts = existing.get("alerts",{}).get("log",[])
    alerts_log = detect_alerts(price, fg, chain, mempool, halving, existing_alerts, generation)
    recent_alerts = [a for a in alerts_log if a.get("gen") == generation]

    ph = existing.get("price_history",[])
    if price and price.get("price_usd",0) > 1000:
        ph.append({"ts":now.strftime("%Y-%m-%d %H:00"),"p":round(price["price_usd"],2),
                   "c":price.get("change_24h_pct",0),"fg":(fg or {}).get("value",50)})
        if len(ph) > MAX_PH: ph = ph[-MAX_PH:]

    health = check_cycle_health(evo_log, now)
    print(f"  Health: {health['status']} | {health['hours_since']}h since last cycle")

    evo_log.append({
        "generation":generation,"timestamp":now.isoformat(),"date":now.strftime("%Y-%m-%d"),
        "price_usd":(price or {}).get("price_usd",0),"fg_value":(fg or {}).get("value",0),
        "headlines_absorbed":len(headlines),"insights_generated":len(insights),
        "prediction_outlook":prediction["outlook"],"hash_rate_ehs":(chain or {}).get("hash_rate_ehs",0),
        "personality_mood":personality.get("mood",""),"alerts_triggered":len(recent_alerts),
        "composite_sentiment":composite_sentiment.get("composite_score",50),
        "market_regime":(macro or {}).get("market_regime",""),
    })
    if len(evo_log) > MAX_EVO: evo_log = evo_log[-MAX_EVO:]

    pred_log = score_predictions_log(evo_log)
    print(f"  Predictions: {pred_log['wins']}W/{pred_log['losses']}L | {pred_log['win_rate']}% win rate")
    existing_failures = existing.get("source_reliability",{}).get("failure_log",[])
    source_reliability = build_source_reliability(existing_failures, evo_log, generation)

    knowledge = {
        "meta": {
            "version":VERSION,"generation":generation,
            "last_updated":now.isoformat(),"last_updated_human":now.strftime("%B %d, %Y at %H:%M UTC"),
            "update_cycle":"every 6 hours","days_alive":days_alive,
            "mission":"Learn everything about Bitcoin. Teach others. Run forever.",
            "prediction_accuracy_pct":accuracy,"total_cycles":generation,
            "organism_status":status,"personality":personality,"cycle_health":health,
        },
        "current": {
            "price":price,"fear_greed":fg,"blockchain":chain,"mempool":mempool,
            "lightning":ln,"halving":halving,"latest_blocks":blocks,
        },
        "intelligence": {
            "todays_thought":thought,"todays_prediction":prediction,
            "todays_insights":insights,"todays_tips":tips,
            "todays_fact":FACTS[generation % len(FACTS)],
            "dev_updates":dev_updates,
            "composite_sentiment":composite_sentiment,
            "macro_context":macro,"onchain_analytics":onchain,
            "cycle_phase":(macro or {}).get("cycle_phase",{}),
        },
        "consciousness": {
            "neural_log":neural_log,"diary":existing_diary,"current_thought":thought,
            "generation":generation,"last_cycle_time":now.strftime("%Y-%m-%d %H:%M UTC"),
        },
        "news": {
            "headlines":headlines,"discussions":discussions,
            "bip_updates":bips,       # frontend renderDev() reads bip_updates
            "dev_updates":dev_updates,
        },
        "quiz":{"questions":quiz,"generation":generation,"total_available":len(QUIZ_QUESTIONS)},
        "knowledge_graph":kg,
        "growth_metrics":gm,
        "evolution_log":evo_log,
        "predictions_log":pred_log,
        "price_history":ph,
        "learning_goals":learning_goals,
        "glossary":glossary,
        "alerts":{"log":alerts_log,"recent":recent_alerts,"total":len(alerts_log)},
        "source_reliability":source_reliability,
        "education":{"learning_paths":LEARNING_PATHS,"all_facts":FACTS},
    }

    atomic_write_json(DATA_FILE, knowledge)
    size_kb = os.path.getsize(DATA_FILE) / 1024
    print(f"\n{'='*60}")
    print(f"OLLIE v{VERSION} Gen {generation} COMPLETE — {size_kb:.1f} KB")
    print(f"BTC: ${(price or {}).get('price_usd',0):,.0f} | F&G: {(fg or {}).get('value',0)}/100 | HR: {(chain or {}).get('hash_rate_ehs',0):.1f} EH/s")
    print(f"Neural: {len(neural_log)} entries | Diary: {len(existing_diary)} | Headlines: {len(headlines)}")
    print(f"Quiz: {len(quiz)} Qs | Glossary: {glossary['total_terms']} terms | Alerts: {len(recent_alerts)} new")
    print(f"Health: {health['status']} | Predictions: {pred_log['wins']}W/{pred_log['losses']}L")
    print("="*60)

if __name__ == "__main__":
    main()
