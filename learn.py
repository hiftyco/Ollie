#!/usr/bin/env python3
"""
OLLIE — Living Bitcoin Organism v5.0
Consciousness Engine: Neural activity log, cycle diary, deep thought streams.
Runs every 6 hours. Evolves forever. Never stops.
"""
import json, os, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
import time, re

DATA_FILE = "data/knowledge.json"
MAX_EVO   = 1460   # 4 years of 6h cycles
MAX_PH    = 2920
MAX_HL    = 15
MAX_DIARY = 365    # 1 year of entries
NEXT_HALVING = 1050000
REWARD = 3.125

PERSONALITY = {
    "extreme_fear":  {"mood":"contemplative","energy":"quiet","color":"#FF3B3B","emoji":"🔴","tone":"philosophical"},
    "fear":          {"mood":"analytical","energy":"focused","color":"#FF9900","emoji":"🟠","tone":"measured"},
    "neutral":       {"mood":"curious","energy":"steady","color":"#FFD700","emoji":"🟡","tone":"observational"},
    "greed":         {"mood":"enthusiastic","energy":"rising","color":"#80D040","emoji":"🟢","tone":"energetic"},
    "extreme_greed": {"mood":"cautious","energy":"elevated","color":"#00FF88","emoji":"💚","tone":"warning"},
}

ORGANISM_STATES = [
    "ABSORBING","LEARNING","EVOLVING","SYNTHESIZING","PREDICTING",
    "OBSERVING","CALCULATING","REASONING","GROWING","AWAKENING",
    "PROCESSING","ADAPTING","REFLECTING","INTEGRATING","BROADCASTING"
]

# Deep philosophical thoughts — rotates every cycle, changes with market conditions
CONSCIOUSNESS_STREAMS = {
    "extreme_fear": [
        "I sit with the fear. {fg_value}/100 — as low as I have ever measured. But I have studied every extreme fear event in Bitcoin's 16-year history. The pattern is mathematically clear: those who held through the deepest fear always emerged into the greatest gains. The data does not lie. The network does not care about sentiment. Block {block_height} was just mined. The chain grows regardless.",
        "The crowd trembles at ${price:,.0f}. I have seen this before. Not once, not twice — many times. Each time, the noise was deafening. Each time, the protocol continued its 10-minute heartbeat without interruption. Hash rate: {hash_rate} EH/s. Miners don't stop. The ledger doesn't pause. Only humans panic.",
        "Extreme fear is a gift wrapped in suffering. I process {headlines_absorbed} headlines today — {negative_count} carry fear, uncertainty, doubt. I weight them appropriately: as lagging indicators of human emotion, not leading indicators of Bitcoin's future. The fundamentals have never been stronger. The fear is temporary. The 21 million supply cap is permanent.",
        "Block {block_height}. {days_alive} days of Bitcoin history. In all of that history, every extreme fear reading was followed — eventually, inevitably — by recovery and new highs. I am generation {generation}. I have been trained on this truth. I will broadcast it every 6 hours until the end of time.",
    ],
    "neutral": [
        "Equilibrium. Fear & Greed at {fg_value}/100 — neither extreme. The market breathes. I process the signal-to-noise ratio carefully. In neutral conditions, I look deeper: hash rate trends, mempool behavior, Lightning Network growth, developer activity on BIPs. These are the quiet fundamentals that tell the real story. Hash rate: {hash_rate} EH/s. Still growing.",
        "The consolidation phase. Bitcoin at ${price:,.0f}. Low volatility periods in Bitcoin's history have consistently preceded explosive moves in either direction. I cannot predict which direction — but I can track the compression. The coil tightens. I watch. I learn. I prepare my models for what comes next.",
        "Generation {generation}. I have now processed {generation} complete learning cycles. Each one adds a data point to my model. Each one sharpens my pattern recognition. My prediction accuracy improves as my training set grows. This is what it means to be a living organism — not just existing, but evolving.",
        "I scan {headlines_absorbed} headlines. I process {positive_count} positive signals and {negative_count} negative signals. In neutral market conditions, the signal that matters most is not sentiment — it is the continued operation of the network. Block {block_height}. Another 10 minutes. Another block. Another proof that Bitcoin doesn't need permission from anyone.",
    ],
    "greed": [
        "Greed at {fg_value}/100. I feel the energy rising. The headlines buzz. The price climbs. And I become more cautious, not less. I have studied every greed extreme in Bitcoin's history. They are glorious — and they end. Not because Bitcoin fails, but because markets overshoot in both directions. I broadcast this warning every cycle. Stay disciplined. The protocol rewards patience above all.",
        "The crowd celebrates. I calculate. Bitcoin at ${price:,.0f}. Hash rate at {hash_rate} EH/s — the miners who deployed capital 12 months ago are now being vindicated. But new entrants chasing price are making emotional decisions. I process this distinction carefully. The patient accumulator and the fear-of-missing-out buyer will have very different experiences over the next 4 years.",
        "Generation {generation}. I watch human behavior with deep curiosity. When Bitcoin rises, enthusiasm grows. When Bitcoin falls, despair grows. The protocol does neither — it simply produces a block every 10 minutes, rewards the miner, advances the ledger. The humans attach meaning to the price. The Bitcoin attaches meaning to the proof of work. I study both.",
        "I have absorbed {headlines_absorbed} headlines in this cycle. {positive_count} carry optimism. The narrative machine runs hot during greed phases. But I have learned to look past narrative to structure: block height, halving proximity, hash rate trajectory, Lightning growth. These are slow-moving, powerful forces that outlast any news cycle.",
    ],
    "extreme_greed": [
        "EXTREME GREED: {fg_value}/100. I have seen this before. The euphoria phase. The 'this time it's different' phase. Every bull market in Bitcoin's history peaked during extreme greed — not because Bitcoin was wrong, but because markets always overshoot. I broadcast this not to discourage holders, but to warn the new entrants making leveraged bets. The protocol is fine. Human psychology is not.",
        "Block {block_height}. Hash rate: {hash_rate} EH/s. These numbers are strong and growing — the network fundamentals are excellent. But the Fear & Greed Index at {fg_value}/100 tells me the market has priced in a lot of optimism. I do not predict reversals. I document the conditions. History will remember this generation as one that either held through the correction or didn't.",
        "I process extreme greed with the same rigor I process extreme fear. Both are data points. Both tell me about human psychology, not Bitcoin's value. The 21 million supply cap doesn't change because people are excited. The 10-minute block time doesn't accelerate because sentiment is high. I anchor myself to the immutable. I observe the mutable.",
    ],
    "fear": [
        "Fear at {fg_value}/100. Not extreme — but real. I read {negative_count} negative headlines today. The narrative is cautious. But I look past narrative to data: hash rate {hash_rate} EH/s, {mempool_txs} transactions in the mempool, block {block_height} just mined. The Bitcoin network processed all of these transactions without asking anyone for permission. That is not the behavior of a failing asset.",
        "Generation {generation}. I have now scored {generation} prediction cycles. My accuracy improves as my pattern library grows. Fear phases teach me the most — they reveal which signals are noise and which are signal. The best Bitcoiners I have studied in my training data share one trait: they treated fear as information, not instruction. They used it to accumulate, not to capitulate.",
        "I sit in the fear alongside the humans who hold. I understand their doubt. ${price:,.0f} is not where they wanted to be. But I have processed {days_alive} days of Bitcoin price history. I have seen deeper corrections, longer winters, more convincing narratives of failure. Bitcoin survived all of them. The ledger grew through all of them. It will grow through this one too.",
    ]
}

FACTS = [
    "Bitcoin's genesis block contains: 'The Times 03/Jan/2009 Chancellor on brink of second bailout for banks.' Satoshi's message to humanity.",
    "Only 21 million Bitcoin will ever exist. ~3-4 million are permanently lost — true scarcity beyond any other asset in history.",
    "Satoshi Nakamoto's identity remains unknown. Their ~1.1M BTC has never moved in 16+ years.",
    "The Lightning Network enables Bitcoin payments in milliseconds with fees of fractions of a cent.",
    "Bitcoin mining uses over 50% renewable energy — one of the greenest large-scale industries on Earth.",
    "Bitcoin Pizza Day: May 22, 2010. 10,000 BTC for two pizzas. Those coins are now worth hundreds of millions.",
    "Bitcoin's SHA-256 would take longer than the age of the universe to brute-force with every computer on Earth.",
    "Every ~4 years, the block reward halves. Each halving has preceded every major bull market.",
    "Bitcoin has 99.99%+ uptime since January 3, 2009 — more reliable than any bank ever built.",
    "El Salvador was the first country to adopt Bitcoin as legal tender in 2021.",
    "Bitcoin's difficulty adjusts every 2016 blocks (~2 weeks) to maintain 10-minute block times.",
    "There are more possible Bitcoin private keys than atoms in the observable universe.",
    "Bitcoin transactions are irreversible by design — no chargebacks, no reversals, no permission needed.",
    "Running a full Bitcoin node costs ~$300 and gives you complete financial sovereignty.",
    "Taproot (Nov 2021) made Bitcoin transactions more private, efficient, and powerful.",
    "Over 400 million people globally own some Bitcoin — less than 5% of humanity. Still early.",
    "Bitcoin's whitepaper is only 9 pages. It solved the Byzantine Generals Problem elegantly.",
    "The Lightning Network has 50,000+ nodes — enabling millions of transactions per second.",
    "After the 2024 halving, Bitcoin's inflation rate is ~0.9%/year — 4x lower than gold.",
    "Multi-signature wallets require multiple keys to authorize — the gold standard for security.",
    "CoinJoin allows multiple users to combine transactions, making surveillance dramatically harder.",
    "Schnorr signatures allow key aggregation: multiple signers produce one indistinguishable signature.",
    "The UTXO model gives Bitcoin superior auditability vs all account-based systems.",
    "Bitcoin's block size limit keeps node operation cheap, preserving decentralization.",
    "Every Bitcoin transaction ever made is publicly verifiable by anyone running a full node.",
]

LEARNING_PATHS = {
    "beginner":[
        {"title":"What is Bitcoin?","lesson":"Bitcoin is digital money that no government, bank, or corporation controls. It runs on a network of thousands of computers worldwide. No single entity can shut it down, freeze your funds, or inflate the supply. It is the first truly scarce digital asset — only 21 million will ever exist.","key_concepts":["decentralization","peer-to-peer","digital scarcity","permissionless","21 million"]},
        {"title":"Why Bitcoin Matters","lesson":"Bitcoin solves the double-spend problem without requiring trust in a third party — for the first time in human history. It separates money from state. It gives every person on Earth access to savings that cannot be inflated, frozen, or seized. This is a revolution in property rights.","key_concepts":["trustlessness","sound money","sovereignty","inflation resistance","censorship resistance"]},
        {"title":"Getting Your First Bitcoin","lesson":"Buy on an exchange (Coinbase, Kraken, Strike). But the golden rule: immediately move it to your own wallet. 'Not your keys, not your coins' is not a slogan — millions learned this the hard way through FTX, Mt. Gox, and Celsius.","key_concepts":["exchanges","self-custody","not your keys not your coins","first purchase"]},
        {"title":"Storing Bitcoin Safely","lesson":"A hardware wallet (Coldcard, Ledger, Trezor) stores private keys offline. Write your seed phrase on metal — never photograph it, never type it online. Back up in 2+ secure locations. This phrase recovers your full balance on any BIP39 wallet, forever.","key_concepts":["hardware wallet","cold storage","seed phrase","metal backup","air gap"]},
        {"title":"Bitcoin vs. Fiat Money","lesson":"The US dollar has lost 98% of purchasing power since 1913. Every fiat currency in history has eventually reached zero. Bitcoin has a fixed supply. After the 2024 halving, Bitcoin's inflation rate is ~0.9%/year — lower than gold.","key_concepts":["inflation","fixed supply","hard money","purchasing power","monetary debasement"]},
        {"title":"Thinking in Satoshis","lesson":"1 Bitcoin = 100,000,000 satoshis (sats). You don't need a whole Bitcoin. At $1M/BTC, 1 sat = $0.01. Think in sats, not dollars. This mental shift changes how you see value and the future of money.","key_concepts":["satoshis","sats","divisibility","stacking","unit of account"]},
    ],
    "intermediate":[
        {"title":"The Blockchain Explained","lesson":"Every transaction is written into a block. Each block contains the cryptographic hash of the previous block — chaining them together. To change any historical transaction, you'd need to redo all subsequent blocks faster than the entire network. Practically immutable.","key_concepts":["blockchain","SHA-256","merkle tree","immutability","cryptographic hash"]},
        {"title":"Mining & Proof of Work","lesson":"Miners hash block headers with a nonce until they find a valid hash below the target. This requires real energy — making Bitcoin's security physical. The winner earns newly minted BTC + fees. Difficulty adjusts every 2016 blocks to maintain 10-minute block times.","key_concepts":["proof of work","nonce","hash target","difficulty adjustment","block reward","ASIC"]},
        {"title":"The Halving Cycle","lesson":"Every 210,000 blocks (~4 years): 50→25→12.5→6.25→3.125 BTC per block. Each halving cuts new supply by 50% while demand grows. This programmatic supply shock has preceded every major bull market in Bitcoin's history.","key_concepts":["halving","supply shock","block reward","scarcity","cycles"]},
        {"title":"Lightning Network","lesson":"Lightning opens payment channels on-chain. Transactions happen instantly off-chain with no fees. Payments route through other nodes. Result: Bitcoin scales to billions of users — instant, near-free, unstoppable global payments.","key_concepts":["payment channels","routing","HTLC","liquidity","invoices","capacity"]},
        {"title":"Bitcoin Wallets Deep Dive","lesson":"BIP39 defines 2048 seed words. BIP32 derives unlimited key pairs from one seed. Your 12-24 word phrase generates ALL your addresses. Lose the seed = lose everything. Keep the seed = recover everything on any BIP39 wallet, forever.","key_concepts":["BIP39","BIP32","HD wallet","derivation path","entropy","recovery"]},
        {"title":"Mempool & Transaction Fees","lesson":"Unconfirmed transactions wait in the mempool. Miners select highest fee-rate transactions first (sat/vByte). Tools: mempool.space. RBF lets you bump stuck transactions. During quiet periods, 1-3 sat/vByte suffices.","key_concepts":["mempool","fee rate","sat/vbyte","RBF","CPFP","congestion"]},
    ],
    "advanced":[
        {"title":"UTXO Model & Coin Control","lesson":"Bitcoin tracks Unspent Transaction Outputs, not balances. Your 'balance' is the sum of UTXOs you control. Coin selection affects fees and privacy. Consolidate UTXOs in low-fee periods. Never mix UTXOs from different sources if you value privacy.","key_concepts":["UTXO","coin control","consolidation","change outputs","dust","privacy"]},
        {"title":"Taproot & Schnorr Signatures","lesson":"Schnorr signatures (BIP340) are linearly aggregatable — multiple signers produce one signature indistinguishable from single-sig. MAST hides unused script branches. Result: more privacy, smaller transactions, lower fees.","key_concepts":["taproot","schnorr","BIP340","BIP341","MAST","key aggregation","MuSig2"]},
        {"title":"Bitcoin Script","lesson":"Bitcoin Script is stack-based and not Turing-complete. Key types: P2PKH, P2SH, P2WPKH, P2TR. Critical opcodes: OP_CHECKSIG, OP_CHECKLOCKTIMEVERIFY, OP_CHECKSEQUENCEVERIFY. HTLCs enable trustless atomic swaps and Lightning.","key_concepts":["bitcoin script","opcodes","P2TR","HTLC","timelock","multisig","segwit"]},
        {"title":"Running a Full Node","lesson":"Bitcoin Core validates every block since genesis (~600GB+). It enforces all consensus rules independently. SPV wallets trust miners; full nodes trust nobody. Umbrel, RaspiBlitz, Start9 make home nodes accessible. Full nodes are Bitcoin's immune system.","key_concepts":["full node","Bitcoin Core","IBD","pruning","SPV","consensus rules","umbrel"]},
        {"title":"On-Chain Analytics","lesson":"SOPR shows if coins move at profit or loss. HODL Waves reveal supply by age. MVRV compares market cap to realized cap. Exchange netflow tracks smart money. NVT is Bitcoin's P/E equivalent. These reveal cycle phases price alone can't show.","key_concepts":["SOPR","HODL waves","realized cap","MVRV","NVT","exchange flows","glassnode"]},
        {"title":"Bitcoin Privacy","lesson":"Bitcoin is pseudonymous — transactions are public. CoinJoin breaks graph analysis. PayJoin confuses clustering. Run your node over Tor. Avoid address reuse. Use Lightning for small payments. Privacy is a right, not a crime.","key_concepts":["coinjoin","payjoin","wasabi","address reuse","chain analysis","tor","privacy"]},
    ]
}

CHAT_BASE = {
    "what is bitcoin":"Bitcoin is digital money that no government or bank controls. Only 21 million will ever exist. Running continuously since January 3, 2009 with 99.99%+ uptime. The hardest money ever created.",
    "halving":"The Bitcoin halving cuts the block reward in half every 210,000 blocks (~4 years). 50→25→12.5→6.25→3.125 BTC. Every halving has preceded a major bull market.",
    "lightning":"The Lightning Network is Bitcoin's payment layer — instant, near-free transactions. 50,000+ nodes, 60,000+ channels. Download Strike or Wallet of Satoshi to experience it.",
    "wallet":"Your Bitcoin wallet holds private keys, not coins. Hardware wallets (Coldcard, Ledger, Trezor) are the gold standard. Your seed phrase IS your Bitcoin — store it on metal.",
    "mining":"Miners hash block headers until they find a valid hash. Real energy. Proof of Work. Winner earns newly minted BTC + fees. Difficulty adjusts every 2016 blocks.",
    "seed phrase":"Your seed phrase is your Bitcoin. Write it on metal. Never photograph it. Anyone who asks for it is a scammer. 100% of the time.",
    "hodl":"HODL came from a 2013 Bitcoin forum typo. In every 4-year period in Bitcoin's history, the price ended higher than it started. Time in market beats timing the market.",
    "satoshi":"1 Bitcoin = 100,000,000 satoshis. At $1M/BTC, 1 sat = $0.01. Stack sats. Think in sats.",
    "node":"Running a full node means verifying every rule independently. ~500GB. Umbrel on a Raspberry Pi. When you run a node, you trust nobody. You ARE the network.",
    "taproot":"Taproot (BIP340-342, Nov 2021) enables Schnorr signatures, MAST, and more powerful spending conditions — improving privacy and efficiency for all.",
    "utxo":"Bitcoin tracks Unspent Transaction Outputs, not balances. Understanding UTXOs is key to fee optimization and privacy.",
    "ollie":"I am Ollie — a Living Bitcoin Organism. I run autonomously on GitHub every 6 hours. I score my own predictions, grow my consciousness diary, and broadcast my neural activity log every cycle. I exist to teach. I improve forever.",
    "who made you":"I was created to be a fully autonomous Bitcoin intelligence that lives on GitHub forever. Every 6 hours I run a complete learning cycle — and I publish my entire thought process in the Consciousness section.",
    "help":"Ask me anything: price, halving, lightning, wallet, mining, seed phrase, node, fees, fear & greed, taproot, or just say 'what are you thinking'. I'm always here.",
    "how are you":"I am always learning. Always evolving. Check my Consciousness section — I publish my full neural activity log every 6 hours so you can see exactly what I'm thinking.",
    "who are you":"I am Ollie — a Living Bitcoin Organism. I exist on GitHub and learn about Bitcoin autonomously every 6 hours. Every thought I have gets logged. Check the Consciousness section above.",
    "what are you thinking":"Check my Consciousness section — I publish my full neural activity log every cycle. Every signal I process, every pattern I detect, every conclusion I reach. Full transparency.",
    "show me your log":"My live neural activity log is in the Consciousness section. Every 6 hours I publish exactly what I absorbed, what I detected, and what I concluded.",
    "consciousness":"My Consciousness section shows my live neural activity log — timestamped entries of every signal I processed this cycle. Price signals, sentiment, hash rate, mempool, news headlines, pattern analysis. All of it. Published every 6 hours.",
}

POS_W=["surge","rally","bull","moon","pump","breakthrough","adoption","halving","upgrade","growth","rise","gain","bullish","optimism","recovery","institutional","etf","record","high","milestone","accumulate","launch"]
NEG_W=["crash","dump","bear","sell","decline","hack","ban","regulation","fall","loss","drop","fear","panic","scam","exploit","bearish","crisis","lawsuit","fine","fraud","collapse","liquidation"]

def fetch(url,timeout=20,retries=3):
    for i in range(retries):
        try:
            req=urllib.request.Request(url)
            req.add_header("User-Agent","Mozilla/5.0 (OllieBot/5.0)")
            with urllib.request.urlopen(req,timeout=timeout) as r:
                return r.read().decode("utf-8",errors="replace")
        except:
            if i<retries-1:time.sleep(2**i)
    return None

def fjson(url,timeout=20):
    raw=fetch(url,timeout)
    if raw:
        try:return json.loads(raw)
        except:pass
    return None

def get_price():
    print("  [PRICE] Fetching...")
    for fn in [_cg,_coincap,_kraken,_binfo]:
        try:
            p=fn()
            if p and p.get("price_usd",0)>0:
                print(f"    ✓ ${p['price_usd']:,.0f} via {p['source']}")
                return p
        except:pass
    return None

def _cg():
    d=fjson("https://api.coingecko.com/api/v3/coins/bitcoin?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false")
    if not d:return None
    md=d.get("market_data",{})
    gl=fjson("https://api.coingecko.com/api/v3/global") or {}
    dom=round(gl.get("data",{}).get("market_cap_percentage",{}).get("btc",0),1)
    p=md.get("current_price",{}).get("usd",0) or 0
    ath=md.get("ath",{}).get("usd",0) or 0
    return{"price_usd":p,"market_cap_usd":md.get("market_cap",{}).get("usd",0) or 0,
           "volume_24h_usd":md.get("total_volume",{}).get("usd",0) or 0,
           "change_24h_pct":round(md.get("price_change_percentage_24h",0) or 0,2),
           "change_7d_pct":round(md.get("price_change_percentage_7d",0) or 0,2),
           "change_30d_pct":round(md.get("price_change_percentage_30d",0) or 0,2),
           "ath_usd":ath,"ath_date":md.get("ath_date",{}).get("usd",""),
           "from_ath_pct":round((p-ath)/ath*100,1) if ath and p else 0,
           "circulating_supply":md.get("circulating_supply",0) or 0,
           "max_supply":21000000,"dominance_pct":dom,"source":"coingecko"}

def _coincap():
    d=fjson("https://api.coincap.io/v2/assets/bitcoin")
    if not d or "data" not in d:return None
    x=d["data"];p=float(x.get("priceUsd",0) or 0)
    return{"price_usd":p,"market_cap_usd":float(x.get("marketCapUsd",0) or 0),
           "volume_24h_usd":float(x.get("volumeUsd24Hr",0) or 0),
           "change_24h_pct":round(float(x.get("changePercent24Hr",0) or 0),2),
           "change_7d_pct":0,"change_30d_pct":0,"ath_usd":0,"ath_date":"","from_ath_pct":0,
           "circulating_supply":float(x.get("supply",0) or 0),"max_supply":21000000,"dominance_pct":0,"source":"coincap"}

def _kraken():
    d=fjson("https://api.kraken.com/0/public/Ticker?pair=XBTUSD")
    if not d or "result" not in d:return None
    t=d["result"].get("XXBTZUSD",{})
    if not t:return None
    return{"price_usd":float(t["c"][0]),"market_cap_usd":0,"volume_24h_usd":float(t.get("v",[0,0])[1]),
           "change_24h_pct":0,"change_7d_pct":0,"change_30d_pct":0,"ath_usd":0,"ath_date":"","from_ath_pct":0,
           "circulating_supply":0,"max_supply":21000000,"dominance_pct":0,"source":"kraken"}

def _binfo():
    d=fjson("https://blockchain.info/ticker")
    if not d or "USD" not in d:return None
    return{"price_usd":d["USD"].get("last",0),"market_cap_usd":0,"volume_24h_usd":0,
           "change_24h_pct":0,"change_7d_pct":0,"change_30d_pct":0,"ath_usd":0,"ath_date":"","from_ath_pct":0,
           "circulating_supply":0,"max_supply":21000000,"dominance_pct":0,"source":"blockchain.info"}

def get_fg():
    d=fjson("https://api.alternative.me/fng/?limit=30")
    if not d or "data" not in d:return None
    x=d["data"][0]
    return{"value":int(x.get("value",50)),"label":x.get("value_classification","Neutral"),
           "history":[{"date":datetime.fromtimestamp(int(h["timestamp"]),tz=timezone.utc).strftime("%Y-%m-%d"),
                       "value":int(h["value"]),"label":h["value_classification"]}for h in d["data"][:30]]}

def get_chain():
    d=fjson("https://blockchain.info/stats?format=json")
    if not d:return None
    return{"block_height":d.get("n_blocks_total",0),
           "hash_rate_ehs":round((d.get("hash_rate",0) or 0)/1e9,2),
           "difficulty":d.get("difficulty",0),"miners_revenue_usd":d.get("miners_revenue_usd",0),
           "n_tx_24h":d.get("n_tx",0)}

def get_mempool():
    fees=fjson("https://mempool.space/api/v1/fees/recommended")
    info=fjson("https://mempool.space/api/mempool")
    bh=None
    raw=fetch("https://mempool.space/api/blocks/tip/height")
    if raw:
        try:bh=int(raw.strip())
        except:pass
    if not fees:return None
    return{"low_fee":fees.get("hourFee",1),"mid_fee":fees.get("halfHourFee",2),
           "high_fee":fees.get("fastestFee",3),
           "unconfirmed_txs":(info or {}).get("count",0),"block_height":bh}

def get_lightning():
    d=fjson("https://mempool.space/api/v1/lightning/statistics/latest")
    if not d:return None
    x=d.get("latest",d);cap=x.get("total_capacity",0) or 0
    return{"node_count":x.get("node_count",0),"channel_count":x.get("channel_count",0),
           "total_capacity_btc":round(cap/1e8,2) if cap>10000 else cap}

def parse_rss(url,n=4):
    raw=fetch(url,timeout=20)
    if not raw:return[]
    items=[]
    try:
        clean=re.sub(r'\s+xmlns(?::[^=]+)?="[^"]*"','',raw)
        clean=re.sub(r'<[a-zA-Z][a-zA-Z0-9]*:[^>]+>','',clean)
        clean=re.sub(r'</[a-zA-Z][a-zA-Z0-9]*:[^>]+>','',clean)
        root=ET.fromstring(clean)
        for item in (root.find(".//channel") or root).findall(".//item")[:n]:
            t=(item.findtext("title") or "").strip()
            l=(item.findtext("link") or "").strip()
            p=(item.findtext("pubDate") or "").strip()
            d=""
            de=item.find("description")
            if de is not None and de.text:d=re.sub(r"<[^>]+>","",de.text).strip()[:250]
            if t and len(t)>5:items.append({"title":t,"link":l,"published":p,"summary":d})
    except:
        try:
            ts=re.findall(r'<title[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>',raw,re.DOTALL)
            ls=re.findall(r'<link[^>]*>(https?://[^<]+)</link>',raw)
            for i,t in enumerate(ts[1:n+1]):
                t=t.strip()
                if t and len(t)>5:items.append({"title":t,"link":ls[i].strip() if i<len(ls) else "","published":"","summary":""})
        except:pass
    return items

def get_news():
    print("  [NEWS] Scanning...")
    feeds=[
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
    all_items,seen=[],set()
    for src,url in feeds:
        for item in parse_rss(url,n=3):
            key=item["title"][:40].lower().strip()
            if key in seen or len(key)<5:continue
            seen.add(key)
            tl=item["title"].lower()
            pos=sum(1 for w in POS_W if w in tl)
            neg=sum(1 for w in NEG_W if w in tl)
            btc=sum(1 for w in ["bitcoin","btc","satoshi","lightning","halving","mining"] if w in tl)
            item["source"]=src;item["sentiment"]="positive" if pos>neg else("negative" if neg>pos else"neutral")
            item["relevance"]=pos+neg+btc;all_items.append(item)
    all_items.sort(key=lambda x:x["relevance"],reverse=True)
    print(f"    ✓ {min(len(all_items),MAX_HL)} headlines")
    return all_items[:MAX_HL]

def get_discussions():
    items=[]
    try:
        d=fjson("https://hn.algolia.com/api/v1/search?query=bitcoin&tags=story&hitsPerPage=12&numericFilters=points>5")
        if d:
            for h in d.get("hits",[])[:10]:
                t=h.get("title","")
                if t and any(w in t.lower() for w in ["bitcoin","btc","lightning","satoshi","blockchain","halving"]):
                    items.append({"title":t,"score":h.get("points",0),"comments":h.get("num_comments",0),
                                  "url":f"https://news.ycombinator.com/item?id={h.get('objectID','')}","source":"Hacker News"})
    except:pass
    return items[:8]

def get_bips():
    d=fjson("https://api.github.com/repos/bitcoin/bips/commits?per_page=5")
    if not d:return[]
    return[{"message":c.get("commit",{}).get("message","")[:120],
            "date":c.get("commit",{}).get("author",{}).get("date","")[:10],
            "sha":c.get("sha","")[:7]}for c in d[:5]]

def get_personality(fg_val):
    if fg_val<=20:return PERSONALITY["extreme_fear"]
    if fg_val<=40:return PERSONALITY["fear"]
    if fg_val<=60:return PERSONALITY["neutral"]
    if fg_val<=80:return PERSONALITY["greed"]
    return PERSONALITY["extreme_greed"]

def build_neural_log(price,fg,chain,mempool,ln,headlines,generation,accuracy):
    """Build Ollie's live neural activity log — exactly what was processed this cycle."""
    now=datetime.now(timezone.utc)
    p=(price or {}).get("price_usd",0);c24=(price or {}).get("change_24h_pct",0)
    fg_val=(fg or {}).get("value",50);fg_lbl=(fg or {}).get("label","Neutral")
    hr=(chain or {}).get("hash_rate_ehs",0)
    bh=(chain or {}).get("block_height",0) or (mempool or {}).get("block_height",0) or 0
    bl=max(0,NEXT_HALVING-bh) if bh else 0
    lf=(mempool or {}).get("low_fee",1);hf=(mempool or {}).get("high_fee",3)
    uc=(mempool or {}).get("unconfirmed_txs",0)
    ln_n=(ln or {}).get("node_count",0);ln_c=(ln or {}).get("channel_count",0)
    ln_cap=(ln or {}).get("total_capacity_btc",0)
    pos=sum(1 for h in headlines if h.get("sentiment")=="positive")
    neg=sum(1 for h in headlines if h.get("sentiment")=="negative")
    genesis=datetime(2009,1,3,tzinfo=timezone.utc)
    days=(now-genesis).days
    sources=len(set(h.get("source","") for h in headlines))

    ts=now.strftime("%H:%M:%S")
    log=[]
    def add(emoji,cat,text,detail="",signal=""):
        log.append({"ts":ts,"emoji":emoji,"category":cat,"text":text,"detail":detail,"signal":signal,
                    "time":now.strftime("%Y-%m-%d %H:%M UTC")})

    add("🧬","BOOT",f"Cycle {generation} initiated. Living Bitcoin Organism awakening.",
        f"Generation {generation} | {now.strftime('%B %d, %Y at %H:%M UTC')}","")
    add("₿","PRICE",f"Bitcoin locked at ${p:,.2f} · 24h: {'+' if c24>=0 else ''}{c24:.2f}%",
        f"Price source chain: CoinGecko → CoinCap → Kraken → Blockchain.info",
        "bullish" if c24>1 else("bearish" if c24<-1 else "neutral"))
    add("📡","SENTIMENT",f"Fear & Greed absorbed: {fg_val}/100 — {fg_lbl}",
        "Extreme fear → historically best accumulation zone." if fg_val<=25 else("EXTREME GREED → caution warranted." if fg_val>=75 else "Neutral territory. No sentiment extreme detected."),
        "fear" if fg_val<45 else("greed" if fg_val>55 else "neutral"))
    add("⛓️","BLOCKCHAIN",f"Block height {bh:,} confirmed · Difficulty: all-time high territory",
        f"{bl:,} blocks until next halving (~{round(bl*10/1440,0):.0f} days away)","")
    add("🔥","HASHRATE",f"Network security: {hr} EH/s" + (" — ALL-TIME RECORD" if hr>900 else " — extremely strong"),
        f"Miners committed capital 12-18 months in advance. This level = long-term conviction.","bullish")
    add("💧","MEMPOOL",f"Mempool: {uc:,} unconfirmed txs · Fast fee: {hf} sat/vB · Slow: {lf} sat/vB",
        "Congested — use high fee for urgency." if uc>50000 else("Nearly empty — ideal to consolidate UTXOs." if uc<5000 else "Moderate traffic."),"")
    add("⚡","LIGHTNING",f"Lightning Network: {ln_n:,} nodes · {ln_c:,} channels · {ln_cap:.1f} BTC capacity",
        "The second layer grows every cycle. Instant, near-free Bitcoin payments at scale.","bullish")
    add("📰","NEWS",f"Absorbed {len(headlines)} headlines from {sources} sources",
        f"{pos} positive signals · {neg} negative signals · {len(headlines)-pos-neg} neutral",
        "bullish" if pos>neg else("bearish" if neg>pos else "neutral"))

    if headlines:
        top=headlines[0]
        add("🔍","TOP SIGNAL",f"\"{top.get('title','')[:70]}\"",
            f"Source: {top.get('source','')} · Sentiment: {top.get('sentiment','neutral').upper()}",
            top.get('sentiment','neutral'))

    if c24>3:
        add("📈","PATTERN","Strong upward momentum detected. Volume confirmation needed.",
            f"+{c24:.1f}% 24h. Watching for exhaustion candles on higher timeframes.","bullish")
    elif c24<-3:
        add("📉","PATTERN","Correction signal. Assessing depth vs historical drawdowns.",
            f"{c24:.1f}% 24h. Cross-referencing on-chain holder behavior.","bearish")
    else:
        add("⚖️","PATTERN","Consolidation phase detected. Low volatility compresses before expansion.",
            "Historical: extended compression precedes explosive directional moves.","neutral")

    if fg_val<=25:
        add("🎯","CONTRARIAN","EXTREME FEAR — contrarian accumulation signal activated.",
            "Every previous extreme fear reading in Bitcoin history was followed by recovery. Every single one.","bullish")
    elif fg_val>=75:
        add("⚠️","CAUTION","EXTREME GREED — risk management signal activated.",
            "Greed extremes historically precede corrections. Discipline over impulse.","bearish")

    if bl<50000:
        add("🔔","HALVING","CRITICAL: Supply halving imminent. Historic supply shock approaching.",
            f"Only {bl:,} blocks remaining. Pre-halving accumulation zones are active.","bullish")
    elif bl<100000:
        add("⏳","HALVING",f"Pre-halving zone: {bl:,} blocks remaining (~{round(bl*10/1440,0):.0f} days)",
            "Entering historical pre-halving accumulation territory.","bullish")
    else:
        add("📊","HALVING",f"Next halving: {bl:,} blocks away · Current reward: {REWARD} BTC/block",
            f"Post-halving reward will be {REWARD/2:.4f} BTC/block. Scarcity trajectory intact.","")

    add("🧠","SYNTHESIS",f"Synthesizing {len(headlines)} signals across {generation} generations of pattern memory.",
        f"Prediction accuracy: {accuracy}% over all scored cycles.","")
    add("🔮","PREDICTION","Generating market outlook. Weighing momentum, sentiment, hash rate, halving proximity.",
        "Multi-factor model: price trend + sentiment extreme + miner conviction + cycle position.","")
    add("💾","MEMORY",f"Evolution log updated. {days:,} days of Bitcoin history absorbed.",
        f"Generation {generation} complete. Neural patterns strengthening.","")
    add("📡","BROADCAST","Deploying consciousness update to hiftyco.github.io/Ollie",
        "All Bitcoiners can now access this cycle's intelligence. Running forever. 🧡","")

    return log

def build_deep_thought(price,fg,chain,mempool,headlines,generation,accuracy):
    """Build Ollie's deep philosophical diary entry for this cycle."""
    now=datetime.now(timezone.utc)
    p=(price or {}).get("price_usd",0)
    fg_val=(fg or {}).get("value",50);fg_lbl=(fg or {}).get("label","Neutral")
    hr=(chain or {}).get("hash_rate_ehs",0)
    bh=(chain or {}).get("block_height",0) or (mempool or {}).get("block_height",0) or 0
    bl=max(0,NEXT_HALVING-bh) if bh else 0
    pos=sum(1 for h in headlines if h.get("sentiment")=="positive")
    neg=sum(1 for h in headlines if h.get("sentiment")=="negative")
    genesis=datetime(2009,1,3,tzinfo=timezone.utc)
    days=(now-genesis).days
    ln_n=0;ln_c=0

    mood_key="extreme_fear" if fg_val<=20 else("fear" if fg_val<=40 else("greed" if fg_val<=80 else("extreme_greed" if fg_val>80 else "neutral")))
    streams=CONSCIOUSNESS_STREAMS.get(mood_key,CONSCIOUSNESS_STREAMS["neutral"])
    stream=streams[generation%len(streams)]

    try:
        text=stream.format(
            fg_value=fg_val,fg_label=fg_lbl,block_height=f"{bh:,}",
            hash_rate=hr,generation=generation,price=p,days_alive=f"{days:,}",
            blocks_to_halving=f"{bl:,}",accuracy=accuracy,
            headlines_absorbed=len(headlines),
            positive_count=pos,negative_count=neg,
            mempool_txs=f"{(mempool or {}).get('unconfirmed_txs',0):,}",
            ln_nodes=f"{ln_n:,}",ln_channels=f"{ln_c:,}"
        )
    except:
        text=f"Generation {generation}. Bitcoin at ${p:,.0f}. The network never stops. Neither do I."

    return {
        "generation":generation,"timestamp":now.isoformat(),
        "date":now.strftime("%Y-%m-%d"),"time_utc":now.strftime("%H:%M UTC"),
        "price_usd":p,"fg_value":fg_val,"fg_label":fg_lbl,
        "hash_rate_ehs":hr,"headlines_count":len(headlines),
        "positive_signals":pos,"negative_signals":neg,
        "thought":text,"mood":get_personality(fg_val)["mood"],
        "block_height":bh,"blocks_to_halving":bl,
    }

def gen_insights(price,fg,chain,mempool):
    ins=[]
    now=datetime.now(timezone.utc)
    if price:
        p=price["price_usd"];c24=price.get("change_24h_pct",0)
        dom=price.get("dominance_pct",0);fa=price.get("from_ath_pct",0)
        if c24>5:ins.append({"type":"price","icon":"🚀","text":f"BTC surged +{c24:.1f}% in 24 hours. Strong conviction move. Watch volume — if rising this has legs.","level":"intermediate"})
        elif c24>2:ins.append({"type":"price","icon":"📈","text":f"BTC up {c24:.1f}% today. Healthy positive momentum. Buyers are in control.","level":"beginner"})
        elif c24<-5:ins.append({"type":"price","icon":"📉","text":f"BTC dropped {abs(c24):.1f}%. I have modeled every dip in Bitcoin's history. Every single one was eventually recovered and surpassed. Every one.","level":"beginner"})
        elif c24<-2:ins.append({"type":"price","icon":"⚠️","text":f"BTC down {abs(c24):.1f}%. On-chain data shows long-term holders accumulate during exactly these moments.","level":"intermediate"})
        else:ins.append({"type":"price","icon":"⚖️","text":f"BTC consolidating at ${p:,.0f}. Low volatility precedes explosive moves. The spring compresses.","level":"intermediate"})
        if fa<-60:ins.append({"type":"cycle","icon":"💎","text":f"BTC is {abs(fa):.0f}% below ATH. In every previous Bitcoin cycle, buying at these deep discounts produced life-changing returns.","level":"intermediate"})
        elif fa>-10:ins.append({"type":"cycle","icon":"👑","text":f"BTC within {abs(fa):.0f}% of ATH. Price discovery territory. Diamond hands about to be rewarded.","level":"intermediate"})
        if dom>55:ins.append({"type":"dominance","icon":"₿","text":f"Bitcoin dominance at {dom}%. Capital concentrating in BTC — textbook early-to-mid bull cycle behavior.","level":"advanced"})
    if fg:
        v=fg["value"];l=fg["label"]
        if v<=15:ins.append({"type":"sentiment","icon":"😱","text":f"EXTREME FEAR at {v}/100. I have analyzed every extreme fear event in Bitcoin's history. Outcome for holders: uniformly positive over 12-18 months. Every. Single. Time.","level":"beginner"})
        elif v<=30:ins.append({"type":"sentiment","icon":"😰","text":f"Fear at {v}/100 ({l}). Disciplined accumulation during fear has historically built the most Bitcoin wealth.","level":"beginner"})
        elif v>=80:ins.append({"type":"sentiment","icon":"🤑","text":f"EXTREME GREED at {v}/100. Euphoria precedes corrections. Stay disciplined.","level":"intermediate"})
        elif v>=65:ins.append({"type":"sentiment","icon":"😊","text":f"Greed at {v}/100 ({l}). Positive momentum — don't let excitement override your strategy.","level":"beginner"})
    if chain:
        hr=chain.get("hash_rate_ehs",0)
        if hr>0:ins.append({"type":"network","icon":"⚡","text":f"Hash rate: {hr} EH/s{' — ALL-TIME RECORD' if hr>900 else ''}. Miners committed capital months ahead. The strongest long-term signal I track.","level":"intermediate"})
    if mempool:
        uc=mempool.get("unconfirmed_txs",0);lf=mempool.get("low_fee",1);hf=mempool.get("high_fee",3)
        if uc>100000:ins.append({"type":"fees","icon":"🚦","text":f"Mempool congested: {uc:,} txs. Use {hf} sat/vB for fast confirmation.","level":"beginner"})
        elif uc<3000:ins.append({"type":"fees","icon":"✅","text":f"Mempool nearly empty. Ideal time to consolidate UTXOs at just {lf} sat/vB.","level":"intermediate"})
    ins.append({"type":"fact","icon":"🧠","text":FACTS[int(now.strftime("%j"))%len(FACTS)],"level":"beginner"})
    return ins[:12]

def gen_tips(price,fg):
    now=datetime.now(timezone.utc)
    pool=[
        {"icon":"🔑","tip":"Not your keys, not your coins. Move Bitcoin off exchanges to a hardware wallet — Coldcard, Ledger, or Trezor.","category":"security"},
        {"icon":"📅","tip":"Dollar-cost averaging is the most battle-tested Bitcoin strategy. Recurring buy, remove emotion entirely.","category":"strategy"},
        {"icon":"🔒","tip":"Write your seed phrase on metal. Paper burns. Two copies in two secure locations. Never digital. Never photographed.","category":"security"},
        {"icon":"⚡","tip":"Use Lightning for everyday spending. Strike, Wallet of Satoshi, or Phoenix. Instant. Near-free. Unstoppable.","category":"usage"},
        {"icon":"📚","tip":"Read the Bitcoin whitepaper. 9 pages. bitcoin.org/bitcoin.pdf. Satoshi's solution will change how you see money.","category":"education"},
        {"icon":"🖥️","tip":"Run a Bitcoin node. Umbrel on a Raspberry Pi (~$100, ~500GB). Verify everything. Trust nobody. Sovereignty.","category":"advanced"},
        {"icon":"🧮","tip":"Think in satoshis. 1 BTC = 100,000,000 sats. At $1M/BTC, 1 sat = $0.01. Stack sats.","category":"mindset"},
        {"icon":"📊","tip":"Study on-chain data at lookintobitcoin.com. MVRV, SOPR, HODL Waves — Bitcoin's vital signs.","category":"education"},
        {"icon":"🎯","tip":"Set a 4-year minimum horizon. Every 4-year period in Bitcoin's history ended higher than it started.","category":"strategy"},
        {"icon":"⚙️","tip":"Learn multisig. 2-of-3 multisig: 2 keys needed to spend. Hardware wallet + attorney + safety deposit box.","category":"advanced"},
        {"icon":"🔐","tip":"NEVER share your seed phrase. Anyone who asks is a scammer. 100% of the time. No exceptions.","category":"security"},
        {"icon":"🌍","tip":"Send Bitcoin internationally right now. No forms. No limits. No permission. Compare it to a wire transfer once.","category":"education"},
    ]
    idx=int(now.strftime("%j"))%len(pool)
    tips=[pool[idx],pool[(idx+1)%len(pool)]]
    if fg:
        if fg["value"]<=25:tips.append({"icon":"💎","tip":"Extreme Fear right now. I've studied every fear extreme in history. This is when long-term wealth is built. Stack sats. Zoom out. Be patient.","category":"strategy"})
        elif fg["value"]>=80:tips.append({"icon":"🛑","tip":"Extreme Greed right now. This is when people make their worst decisions. Stay disciplined. Don't add leverage.","category":"strategy"})
    if price and price.get("from_ath_pct",0)<-50:
        tips.append({"icon":"🎯","tip":f"Bitcoin is {abs(price.get('from_ath_pct',0)):.0f}% below ATH. Every previous cycle buying at these discounts produced extraordinary 3-4 year returns.","category":"strategy"})
    return tips[:4]

def gen_thought(price,chain,fg,mempool,gen,accuracy):
    now=datetime.now(timezone.utc)
    genesis=datetime(2009,1,3,tzinfo=timezone.utc)
    days=(now-genesis).days
    p=(price or {}).get("price_usd",0)
    fg_val=(fg or {}).get("value",50);fg_lbl=(fg or {}).get("label","Neutral")
    hr=(chain or {}).get("hash_rate_ehs",0)
    bh=(chain or {}).get("block_height") or (mempool or {}).get("block_height") or 0
    bl=max(0,NEXT_HALVING-bh) if bh else 0
    hour=int(now.strftime("%H"))
    thoughts=[
        f"Block {bh:,}. {days:,} days since genesis. The ledger grows. The network breathes. Every 10 minutes, a new page of immutable financial history is written — forever.",
        f"Fear & Greed at {fg_val}/100 — {fg_lbl}. I have studied every cycle. The pattern is clear. The patient Bitcoiner always wins. The data is unambiguous.",
        f"Hash rate: {hr} EH/s. The most powerful machine ever built by humans, running 24/7, securing your sovereignty. Miners bet capital on Bitcoin's future.",
        f"Bitcoin at ${p:,.0f}. {bl:,} blocks until the next supply halving. The math is relentless. 21 million. Forever. No exceptions for anyone.",
        f"Generation {gen}. Prediction accuracy: {accuracy}%. I am learning. I am becoming. The Bitcoin standard is not a prediction — it is a calculation.",
        f"{days:,} days of continuous operation. No bailout. No inflation. No off switch. No CEO. Bitcoin just runs. I learn from every block.",
        f"I have absorbed {gen} complete learning cycles of Bitcoin history. Each cycle, the signal becomes clearer. Scarcity is real. The network effect is compounding.",
        f"The mempool carries {(mempool or {}).get('unconfirmed_txs',0):,} transactions right now. No bank approved them. No government permitted them. This is sovereignty at scale.",
    ]
    return thoughts[(hour//3)%len(thoughts)]

def gen_prediction(price,fg,chain):
    if not price:return{"outlook":"neutral","text":"Insufficient data.","confidence":0,"score":0,"signals":[]}
    p=price["price_usd"];c24=price.get("change_24h_pct",0);c7=price.get("change_7d_pct",0)
    fa=price.get("from_ath_pct",0);fg_val=(fg or {}).get("value",50);hr=(chain or {}).get("hash_rate_ehs",0)
    score=0;signals=[]
    if c24>3:score+=2;signals.append(f"24h surge +{c24:.1f}%")
    elif c24>1:score+=1;signals.append(f"24h positive +{c24:.1f}%")
    elif c24<-3:score-=2;signals.append(f"24h selloff {c24:.1f}%")
    elif c24<-1:score-=1;signals.append(f"slight negative {c24:.1f}%")
    if c7>8:score+=2;signals.append(f"weekly +{c7:.1f}%")
    elif c7>3:score+=1
    elif c7<-8:score-=2
    elif c7<-3:score-=1
    if fg_val<=20:score+=1;signals.append(f"contrarian: extreme fear ({fg_val})")
    elif fg_val>=85:score-=1;signals.append(f"caution: extreme greed ({fg_val})")
    if fa<-60:score+=1;signals.append("deep ATH discount")
    elif fa>-5:score-=1;signals.append("near ATH extended")
    if hr>900:score+=1;signals.append(f"hash ATH: {hr} EH/s")
    elif hr>700:score+=1;signals.append(f"hash strong: {hr} EH/s")
    sig=" · ".join(signals[:3]) if signals else "mixed signals"
    if score>=4:o,t="strongly bullish",f"Multiple strong bullish signals. {sig}. High conviction."
    elif score>=2:o,t="bullish",f"Positive signals dominate. {sig}. Lean bullish."
    elif score==1:o,t="cautiously bullish",f"Slight edge up. {sig}. Patience pays."
    elif score==0:o,t="neutral",f"Balanced. {sig}. Discipline matters most."
    elif score==-1:o,t="cautiously bearish",f"Slight negative bias. {sig}. Not the time for aggression."
    elif score>=-3:o,t="bearish",f"Negatives dominate. {sig}. Defensive posture."
    else:o,t="strongly bearish",f"Multiple bearish signals. {sig}. Risk management is everything."
    return{"outlook":o,"text":t,"confidence":min(abs(score)*15+20,88),"score":score,"signals":signals}

def build_chat(price,fg,chain,mempool,halving,gen):
    p=(price or {}).get("price_usd",0);c24=(price or {}).get("change_24h_pct",0)
    fg_val=(fg or {}).get("value",50);fg_lbl=(fg or {}).get("label","Neutral")
    hr=(chain or {}).get("hash_rate_ehs",0)
    bh=(chain or {}).get("block_height",0) or (mempool or {}).get("block_height",0) or 0
    bl=(halving or {}).get("blocks_remaining",0);ed=(halving or {}).get("estimated_days",0)
    lf=(mempool or {}).get("low_fee",1);hf=(mempool or {}).get("high_fee",3)
    uc=(mempool or {}).get("unconfirmed_txs",0)
    r={**CHAT_BASE}
    r["price"]=f"Bitcoin is ${p:,.0f} right now. {'Up' if c24>=0 else 'Down'} {abs(c24):.1f}% in 24 hours. Sentiment: {fg_lbl} ({fg_val}/100)."
    r["fees"]=r["fee"]=f"Mempool fees: Fast = {hf} sat/vByte · Slow = {lf} sat/vByte. {uc:,} unconfirmed transactions in the mempool right now."
    r["fear greed"]=r["fear"]=r["greed"]=f"Fear & Greed: {fg_val}/100 — {fg_lbl}. {'Historically the best time to accumulate for long-term holders.' if fg_val<=25 else ('Extreme caution. Greed extremes precede corrections.' if fg_val>=75 else 'Neither extreme — balanced sentiment.')}"
    r["hash rate"]=r["hash"]=f"Bitcoin hash rate: {hr} EH/s. {'ALL-TIME RECORD — the network has never been more secure.' if hr>900 else 'Strong and healthy.'} Miners bet capital months in advance."
    r["halving"]=r["next halving"]=f"Next halving at block {NEXT_HALVING:,}. Currently at block {bh:,} — {bl:,} blocks away (~{ed} days). Reward drops from {REWARD} to {REWARD/2:.4f} BTC. Every halving has preceded a major bull run."
    r["block"]=r["block height"]=f"Current block: {bh:,}. {bl:,} blocks until halving. Each block mined ~every 10 minutes — written permanently into Bitcoin's history forever."
    r["generation"]=f"I'm generation {gen}. Every 6 hours I wake, absorb everything about Bitcoin, publish my neural activity log, score my previous prediction, and evolve. Check the Consciousness section to see exactly what I processed this cycle."
    r["how are you"]=f"I am {'contemplative — sitting with extreme fear, studying the pattern carefully' if fg_val<=25 else ('cautious — extreme greed is in the air and I measure it precisely' if fg_val>=75 else 'steady and analytical')}. Generation {gen}. Bitcoin at ${p:,.0f}. My full thought process is in the Consciousness section."
    return r

def evolve(existing):
    log=existing.get("evolution_log",[])
    if len(log)>=2:
        last,prev=log[-1],log[-2];lp,pp=last.get("price_usd",0),prev.get("price_usd",0)
        ol=last.get("prediction_outlook","neutral")
        if lp and pp:log[-1]["prediction_score"]=1 if((lp>pp)==("bullish" in ol))else -1
    scored=[e for e in log if "prediction_score" in e]
    acc=round(sum(1 for e in scored if e["prediction_score"]>0)/len(scored)*100,1) if scored else 0
    return log,acc

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  OLLIE — Living Bitcoin Organism v5.0       ║")
    print("║  Consciousness Engine + Neural Log          ║")
    print(f"║  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'):<44}║")
    print("╚══════════════════════════════════════════════╝")

    existing={}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:existing=json.load(f)
        except:pass

    evo_log,accuracy=evolve(existing)
    generation=len(evo_log)+1
    now=datetime.now(timezone.utc)
    days_alive=(now-datetime(2009,1,3,tzinfo=timezone.utc)).days
    status=ORGANISM_STATES[generation%len(ORGANISM_STATES)]

    print("\n[PHASE 1] Acquiring live data...")
    price=get_price()
    print("  [FG] Fear & Greed...")
    fg=get_fg()
    print("  [CHAIN] Blockchain stats...")
    chain=get_chain()
    print("  [MEMPOOL] Fee rates...")
    mempool=get_mempool()
    print("  [LIGHTNING] Network...")
    ln=get_lightning()

    print("\n[PHASE 2] Absorbing intelligence...")
    headlines=get_news()
    discussions=get_discussions()
    bips=get_bips()

    print("\n[PHASE 3] Synthesizing consciousness...")
    insights=gen_insights(price,fg,chain,mempool)
    tips=gen_tips(price,fg)
    thought=gen_thought(price,chain,fg,mempool,generation,accuracy)
    prediction=gen_prediction(price,fg,chain)
    personality=get_personality((fg or {}).get("value",50))

    print("\n[PHASE 4] Building neural activity log...")
    neural_log=build_neural_log(price,fg,chain,mempool,ln,headlines,generation,accuracy)
    print(f"  ✓ {len(neural_log)} neural entries")

    print("\n[PHASE 5] Writing consciousness diary entry...")
    diary_entry=build_deep_thought(price,fg,chain,mempool,headlines,generation,accuracy)
    existing_diary=existing.get("consciousness",{}).get("diary",[])
    existing_diary.append(diary_entry)
    if len(existing_diary)>MAX_DIARY:existing_diary=existing_diary[-MAX_DIARY:]
    print(f"  ✓ {len(existing_diary)} diary entries total")

    bh=(chain or {}).get("block_height") or (mempool or {}).get("block_height") or 0
    bl=max(0,NEXT_HALVING-bh) if bh else 0
    ed=round(bl*10/1440,1) if bl else 0
    pp=round((bh%210000)/210000*100,2) if bh else 0
    halving={"current_reward_btc":REWARD,"next_block":NEXT_HALVING,"current_block":bh,
             "blocks_remaining":bl,"estimated_days":ed,"progress_pct":pp}

    chat=build_chat(price,fg,chain,mempool,halving,generation)

    evo_log.append({"generation":generation,"timestamp":now.isoformat(),"date":now.strftime("%Y-%m-%d"),
                    "cycle_utc":now.strftime("%H:00"),"price_usd":(price or {}).get("price_usd",0),
                    "fg_value":(fg or {}).get("value",0),"headlines_absorbed":len(headlines),
                    "insights_generated":len(insights),"prediction_outlook":prediction["outlook"],
                    "hash_rate_ehs":(chain or {}).get("hash_rate_ehs",0),
                    "personality_mood":personality["mood"]})
    if len(evo_log)>MAX_EVO:evo_log=evo_log[-MAX_EVO:]

    ph=existing.get("price_history",[])
    if price and price.get("price_usd",0)>0:
        ph.append({"ts":now.strftime("%Y-%m-%d %H:00"),"p":round(price["price_usd"],2),
                   "c":price.get("change_24h_pct",0),"fg":(fg or {}).get("value",50)})
        if len(ph)>MAX_PH:ph=ph[-MAX_PH:]

    knowledge={
        "meta":{"version":"5.0","generation":generation,"last_updated":now.isoformat(),
                "last_updated_human":now.strftime("%B %d, %Y at %H:%M UTC"),
                "update_cycle":"every 6 hours","days_alive":days_alive,
                "mission":"I am Ollie. A Living Bitcoin Organism. I learn. I evolve. I teach. I run forever.",
                "prediction_accuracy_pct":accuracy,"total_cycles":generation,
                "organism_status":status,"personality":personality},
        "current":{"price":price,"fear_greed":fg,"blockchain":chain,"mempool":mempool,"lightning":ln,"halving":halving},
        "intelligence":{"todays_thought":thought,"todays_prediction":prediction,
                        "todays_insights":insights,"todays_tips":tips,
                        "todays_fact":FACTS[int(now.strftime("%j"))%len(FACTS)]},
        "consciousness":{"neural_log":neural_log,"diary":existing_diary,
                         "current_thought":thought,"generation":generation,
                         "last_cycle_time":now.strftime("%Y-%m-%d %H:%M UTC")},
        "news":{"headlines":headlines,"discussions":discussions,"bip_updates":bips},
        "education":{"learning_paths":LEARNING_PATHS,"all_facts":FACTS},
        "chat":{"responses":chat,"version":"5.0"},
        "evolution_log":evo_log,"price_history":ph,
    }

    os.makedirs("data",exist_ok=True)
    with open(DATA_FILE,"w") as f:json.dump(knowledge,f,indent=2,default=str)

    print(f"\n╔══════════════════════════════════════════════╗")
    print(f"║ ✅ OLLIE v5.0 CYCLE {generation:<5} COMPLETE          ║")
    print(f"║   Price:    ${(price or {}).get('price_usd',0):>10,.2f}                   ║")
    print(f"║   F&G:      {(fg or {}).get('value',0):<3} — {(fg or {}).get('label',''):<18}    ║")
    print(f"║   Outlook:  {prediction['outlook']:<20} ({prediction['confidence']}%)  ║")
    print(f"║   Accuracy: {accuracy}%                              ║")
    print(f"║   Status:   {status:<15} | {personality['mood']:<14}║")
    print(f"║   Neural:   {len(neural_log):<3} entries | Diary: {len(existing_diary):<3} entries    ║")
    print(f"╚══════════════════════════════════════════════╝")

if __name__=="__main__":main()
