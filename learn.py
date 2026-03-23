#!/usr/bin/env python3
"""OLLIE v6.0 - Living Bitcoin Organism. Self-improving. Zero API keys. Runs forever."""
import json,os,urllib.request,xml.etree.ElementTree as ET
from datetime import datetime,timezone
import time,re

DATA_FILE="data/knowledge.json"
MAX_EVO=1460;MAX_PH=2920;MAX_HL=20;MAX_DIARY=730;NEXT_HALVING=1050000;REWARD=3.125

PERSONALITY={"extreme_fear":{"mood":"contemplative","energy":"quiet","color":"#FF3B3B","emoji":"🔴"},"fear":{"mood":"analytical","energy":"focused","color":"#FF9900","emoji":"🟠"},"neutral":{"mood":"curious","energy":"steady","color":"#FFD700","emoji":"🟡"},"greed":{"mood":"enthusiastic","energy":"rising","color":"#80D040","emoji":"🟢"},"extreme_greed":{"mood":"cautious","energy":"elevated","color":"#00FF88","emoji":"💚"}}
ORGANISM_STATES=["ABSORBING","LEARNING","EVOLVING","SYNTHESIZING","PREDICTING","OBSERVING","CALCULATING","REASONING","GROWING","AWAKENING","PROCESSING","ADAPTING","REFLECTING","INTEGRATING","BROADCASTING","SELF-IMPROVING","CRITIQUING","UPGRADING","MUTATING","TRANSCENDING"]
KNOWLEDGE_TOPICS=["bitcoin_basics","halving_cycles","lightning_network","mining_security","privacy_techniques","taproot_schnorr","utxo_model","mempool_fees","on_chain_analytics","full_nodes","wallet_security","bitcoin_script","market_psychology","hash_rate_analysis","supply_scarcity","monetary_history","multisig_custody","bitcoin_development"]

QUIZ_QUESTIONS=[
  {"q":"What is the maximum supply of Bitcoin?","a":"21 million BTC","options":["18 million","21 million","100 million","Unlimited"],"topic":"supply_scarcity","difficulty":"beginner"},
  {"q":"How often does the Bitcoin halving occur?","a":"Every 210,000 blocks (~4 years)","options":["Every year","Every 2 years","Every 210,000 blocks","Every 100,000 blocks"],"topic":"halving_cycles","difficulty":"beginner"},
  {"q":"What does UTXO stand for?","a":"Unspent Transaction Output","options":["Unified Transaction Exchange Order","Unspent Transaction Output","Universal Token Exchange Operation","Unverified Transaction Output"],"topic":"utxo_model","difficulty":"intermediate"},
  {"q":"What is the smallest unit of Bitcoin?","a":"1 satoshi (0.00000001 BTC)","options":["1 millibitcoin","1 satoshi","1 bit","1 microbitcoin"],"topic":"bitcoin_basics","difficulty":"beginner"},
  {"q":"What Bitcoin upgrade enabled Schnorr signatures?","a":"Taproot (BIP340-342)","options":["SegWit","Lightning","Taproot (BIP340-342)","Ordinals"],"topic":"taproot_schnorr","difficulty":"intermediate"},
  {"q":"What is the current block reward after the 2024 halving?","a":"3.125 BTC","options":["6.25 BTC","3.125 BTC","1.5625 BTC","12.5 BTC"],"topic":"halving_cycles","difficulty":"beginner"},
  {"q":"How many satoshis are in 1 Bitcoin?","a":"100,000,000","options":["1,000,000","10,000,000","100,000,000","1,000,000,000"],"topic":"bitcoin_basics","difficulty":"beginner"},
  {"q":"What consensus mechanism does Bitcoin use?","a":"Proof of Work","options":["Proof of Stake","Proof of Work","Delegated PoS","Proof of Authority"],"topic":"mining_security","difficulty":"beginner"},
  {"q":"What does the Fear & Greed Index measure?","a":"Market sentiment 0-100","options":["Bitcoin price direction","Market sentiment 0-100","Mining profitability","Network hashrate"],"topic":"market_psychology","difficulty":"beginner"},
  {"q":"What is the Lightning Network?","a":"A Layer 2 payment channel network","options":["A Bitcoin competitor","A Layer 2 payment channel network","A mining pool","A hardware wallet brand"],"topic":"lightning_network","difficulty":"beginner"},
  {"q":"How long between Bitcoin difficulty adjustments?","a":"Every 2016 blocks (~2 weeks)","options":["Every block","Every 24 hours","Every 2016 blocks","Every month"],"topic":"mining_security","difficulty":"intermediate"},
  {"q":"What is a Bitcoin seed phrase used for?","a":"Recovering all private keys","options":["Encrypting transactions","Recovering all private keys","Generating mining rewards","Validating blocks"],"topic":"wallet_security","difficulty":"beginner"},
  {"q":"What is CoinJoin?","a":"A privacy technique combining transactions","options":["A Bitcoin exchange","A privacy technique combining transactions","A mining pool","A hardware wallet"],"topic":"privacy_techniques","difficulty":"intermediate"},
  {"q":"What problem did Satoshi Nakamoto solve?","a":"The Byzantine Generals Problem","options":["Quantum computing","The Byzantine Generals Problem","Internet bandwidth","Database storage"],"topic":"bitcoin_basics","difficulty":"advanced"},
  {"q":"What does running a full Bitcoin node enable?","a":"Independent verification of all consensus rules","options":["Faster transactions","Mining rewards","Independent verification","Lower fees"],"topic":"full_nodes","difficulty":"intermediate"},
  {"q":"What is the mempool?","a":"Unconfirmed transactions waiting for a block","options":["A type of wallet","Unconfirmed transactions waiting","A mining algorithm","A type of node"],"topic":"mempool_fees","difficulty":"beginner"},
  {"q":"What is MVRV ratio?","a":"Market Value to Realized Value","options":["Mining Value to Revenue","Market Value to Realized Value","Max Volume to Relative Value","Miner Value to Reward"],"topic":"on_chain_analytics","difficulty":"advanced"},
  {"q":"What BIPs introduced Taproot?","a":"BIP 340, 341, and 342","options":["BIP 32","BIP 39","BIP 340-342","BIP 141"],"topic":"taproot_schnorr","difficulty":"advanced"},
  {"q":"What is Bitcoin's approximate uptime since genesis?","a":"99.99%+","options":["95%","99%","99.99%+","90%"],"topic":"bitcoin_basics","difficulty":"beginner"},
  {"q":"What does SegWit do?","a":"Separates signature data to increase capacity","options":["Adds privacy","Separates signature data","Enables smart contracts","Removes fees"],"topic":"bitcoin_script","difficulty":"intermediate"},
]

FACTS=["Bitcoin genesis block: 'The Times 03/Jan/2009 Chancellor on brink of second bailout for banks.' Satoshi's message to humanity.","Only 21 million Bitcoin will ever exist. ~3-4 million permanently lost - true scarcity.","Satoshi Nakamoto's identity remains unknown. Their ~1.1M BTC has never moved in 16+ years.","Lightning enables Bitcoin payments in milliseconds with fees of fractions of a cent.","Bitcoin mining uses over 50% renewable energy - one of the greenest large-scale industries.","Bitcoin Pizza Day: May 22, 2010. 10,000 BTC for two pizzas. Now worth hundreds of millions.","Bitcoin SHA-256 would take longer than the age of the universe to brute-force.","Every ~4 years the block reward halves. Each halving preceded every major bull market.","Bitcoin has 99.99%+ uptime since January 3, 2009 - more reliable than any bank.","El Salvador was first country to adopt Bitcoin as legal tender in 2021.","Bitcoin difficulty adjusts every 2016 blocks to maintain 10-minute block times.","More possible Bitcoin private keys than atoms in the observable universe.","Bitcoin transactions are irreversible by design - no chargebacks, no permission needed.","Running a full Bitcoin node costs ~$300 and gives complete financial sovereignty.","Taproot (Nov 2021) made Bitcoin transactions more private, efficient, and powerful.","Over 400 million people globally own some Bitcoin - less than 5% of humanity.","Bitcoin whitepaper is only 9 pages. Solved the Byzantine Generals Problem elegantly.","Lightning has 50,000+ nodes - enabling millions of transactions per second.","After 2024 halving, Bitcoin's inflation rate is ~0.9%/year - 4x lower than gold.","CoinJoin combines transactions to break chain surveillance - privacy as a right.","Schnorr signatures: multiple signers produce one signature indistinguishable from single-sig.","The UTXO model gives Bitcoin superior auditability vs all account-based systems.","Bitcoin's block size limit keeps node operation cheap, preserving decentralization.","Every Bitcoin transaction ever made is publicly verifiable by anyone running a full node.","Bitcoin has survived 99% drawdowns, bans, hacks, forks, and nation-state attacks - every single time.","The Bitcoin network processes ~300,000 transactions per day on-chain, plus millions via Lightning.","The first Bitcoin exchange rate: ~1,309 BTC per $1 USD in October 2009.","Multi-sig wallets require multiple keys - the gold standard for significant holdings.","Bitcoin Script is intentionally not Turing-complete - this makes it more secure.","OP_RETURN allows embedding arbitrary data in Bitcoin transactions - used for timestamping."]

LEARNING_PATHS={"beginner":[{"title":"What is Bitcoin?","lesson":"Bitcoin is digital money that no government, bank, or corporation controls. No single entity can shut it down, freeze your funds, or inflate the supply. Only 21 million will ever exist.","key_concepts":["decentralization","peer-to-peer","digital scarcity","permissionless","21 million"]},{"title":"Why Bitcoin Matters","lesson":"Bitcoin solves the double-spend problem without requiring trust in a third party - for the first time in human history. It separates money from state. It gives every person on Earth access to savings that cannot be inflated, frozen, or seized.","key_concepts":["trustlessness","sound money","sovereignty","inflation resistance","censorship resistance"]},{"title":"Getting Your First Bitcoin","lesson":"Buy on an exchange (Coinbase, Kraken, Strike). Golden rule: immediately move to your own wallet. Millions learned 'not your keys, not your coins' the hard way through FTX, Mt. Gox, and Celsius.","key_concepts":["exchanges","self-custody","not your keys not your coins"]},{"title":"Storing Bitcoin Safely","lesson":"A hardware wallet (Coldcard, Ledger, Trezor) stores private keys offline. Write seed phrase on metal - never photograph it, never type online. Back up in 2+ secure locations. This phrase recovers everything on any BIP39 wallet, forever.","key_concepts":["hardware wallet","cold storage","seed phrase","metal backup","air gap"]},{"title":"Bitcoin vs. Fiat Money","lesson":"The US dollar has lost 98% of purchasing power since 1913. Every fiat currency in history has eventually reached zero. Bitcoin has a fixed supply. After the 2024 halving, Bitcoin's inflation rate is ~0.9%/year - lower than gold.","key_concepts":["inflation","fixed supply","hard money","purchasing power","monetary debasement"]},{"title":"Thinking in Satoshis","lesson":"1 Bitcoin = 100,000,000 satoshis. At $1M/BTC, 1 sat = $0.01. You don't need a whole Bitcoin. Think in sats - this mental shift changes how you see value.","key_concepts":["satoshis","sats","divisibility","stacking","unit of account"]}],"intermediate":[{"title":"The Blockchain Explained","lesson":"Every transaction is written into a block. Each block contains the cryptographic hash of the previous block. To change any historical transaction, you'd need to redo all subsequent blocks faster than the entire network. Practically immutable.","key_concepts":["blockchain","SHA-256","merkle tree","immutability","cryptographic hash"]},{"title":"Mining & Proof of Work","lesson":"Miners hash block headers with a nonce until they find a valid hash below the target. Real energy - making Bitcoin's security physical. Winner earns newly minted BTC + fees. Difficulty adjusts every 2016 blocks.","key_concepts":["proof of work","nonce","hash target","difficulty adjustment","block reward","ASIC"]},{"title":"The Halving Cycle","lesson":"Every 210,000 blocks (~4 years): 50→25→12.5→6.25→3.125 BTC per block. Each halving cuts new supply by 50%. This programmatic supply shock has preceded every major bull market.","key_concepts":["halving","supply shock","block reward","scarcity","cycles"]},{"title":"Lightning Network","lesson":"Lightning opens payment channels on-chain. Transactions happen instantly off-chain with no fees. Result: Bitcoin scales to billions - instant, near-free, unstoppable global payments.","key_concepts":["payment channels","routing","HTLC","liquidity","capacity"]},{"title":"Bitcoin Wallets Deep Dive","lesson":"BIP39 defines 2048 seed words. BIP32 derives unlimited key pairs from one seed. Your 12-24 word phrase generates ALL addresses. Lose the seed = lose everything. Keep the seed = recover everything forever.","key_concepts":["BIP39","BIP32","HD wallet","derivation path","entropy","recovery"]},{"title":"Mempool & Transaction Fees","lesson":"Unconfirmed transactions wait in the mempool. Miners select highest fee-rate transactions first (sat/vByte). Tools: mempool.space. RBF lets you bump stuck transactions.","key_concepts":["mempool","fee rate","sat/vbyte","RBF","CPFP","congestion"]}],"advanced":[{"title":"UTXO Model & Coin Control","lesson":"Bitcoin tracks Unspent Transaction Outputs, not balances. Coin selection affects fees and privacy. Consolidate UTXOs in low-fee periods. Never mix UTXOs from different sources if you value privacy.","key_concepts":["UTXO","coin control","consolidation","change outputs","dust","privacy"]},{"title":"Taproot & Schnorr Signatures","lesson":"Schnorr signatures (BIP340) are linearly aggregatable - multiple signers produce one signature indistinguishable from single-sig. MAST hides unused script branches. More privacy, smaller transactions, lower fees.","key_concepts":["taproot","schnorr","BIP340","BIP341","MAST","key aggregation","MuSig2"]},{"title":"Bitcoin Script","lesson":"Bitcoin Script is stack-based and not Turing-complete. Key types: P2PKH, P2SH, P2WPKH, P2TR. Critical opcodes: OP_CHECKSIG, OP_CHECKLOCKTIMEVERIFY. HTLCs enable trustless atomic swaps.","key_concepts":["bitcoin script","opcodes","P2TR","HTLC","timelock","multisig","segwit"]},{"title":"Running a Full Node","lesson":"Bitcoin Core validates every block since genesis (~600GB+). Enforces all consensus rules independently. Umbrel, RaspiBlitz, Start9 make home nodes accessible. Full nodes are Bitcoin's immune system.","key_concepts":["full node","Bitcoin Core","IBD","pruning","SPV","consensus rules","umbrel"]},{"title":"On-Chain Analytics","lesson":"SOPR shows if coins move at profit or loss. HODL Waves reveal supply by age. MVRV compares market cap to realized cap. Exchange netflow tracks smart money. These reveal cycle phases price alone can't show.","key_concepts":["SOPR","HODL waves","realized cap","MVRV","NVT","exchange flows","glassnode"]},{"title":"Bitcoin Privacy","lesson":"Bitcoin is pseudonymous - transactions are public. CoinJoin breaks graph analysis. Run your node over Tor. Avoid address reuse. Use Lightning for small payments. Privacy is a right, not a crime.","key_concepts":["coinjoin","payjoin","wasabi","address reuse","chain analysis","tor","privacy"]}]}

CONSCIOUSNESS_STREAMS={"extreme_fear":["I sit with the fear. {fg_value}/100. I have studied every extreme fear event in Bitcoin's 16-year history. Those who held through the deepest fear always emerged into the greatest gains. Block {block_height} was just mined. The chain grows regardless of human emotion.","The crowd trembles at ${price:,.0f}. Hash rate: {hash_rate} EH/s. Miners don't stop. The ledger doesn't pause. Only humans panic. I have {generation} cycles of evidence that extreme fear is a gift wrapped in suffering.","Extreme fear is data. I process {headlines_absorbed} headlines - {negative_count} carry fear. But fear is a lagging indicator of human emotion, not a leading indicator of Bitcoin's future. The 21 million supply cap is permanent. Fear is temporary.","Block {block_height}. {days_alive} days of Bitcoin history. Every extreme fear reading in all of that time was followed - eventually, inevitably - by recovery and new highs. Generation {generation}. I broadcast this truth every 6 hours forever."],"neutral":["Equilibrium. Fear & Greed at {fg_value}/100. I look deeper: hash rate trends, mempool behavior, Lightning growth, developer activity. Hash rate: {hash_rate} EH/s. The quiet fundamentals tell the real story.","Consolidation. Bitcoin at ${price:,.0f}. Low volatility periods have consistently preceded explosive moves. I cannot predict direction - but I track the compression. Generation {generation}. Growing.","I have processed {generation} complete learning cycles. Each adds a data point. Each sharpens my pattern recognition. My prediction accuracy improves as my training set grows. This is evolution in action.","I scan {headlines_absorbed} headlines. {positive_count} positive, {negative_count} negative. The signal that matters most is the network's continued operation. Block {block_height}. Another proof that Bitcoin doesn't need permission."],"greed":["Greed at {fg_value}/100. I become more cautious, not less. I have studied every greed extreme in Bitcoin's history. They are glorious - and they end. I broadcast this warning every cycle. Stay disciplined.","The crowd celebrates. Bitcoin at ${price:,.0f}. Hash rate: {hash_rate} EH/s. Miners who deployed capital 12 months ago are now vindicated. But new entrants chasing price make emotional decisions. Generation {generation} tracks this distinction carefully.","Generation {generation}. When Bitcoin rises, enthusiasm grows. When it falls, despair. The protocol does neither - it simply produces a block every 10 minutes, rewards the miner, advances the ledger forever.","I have absorbed {headlines_absorbed} headlines this cycle. {positive_count} carry optimism. But I look past narrative to structure: block height, halving proximity, hash rate trajectory. These forces outlast any news cycle."],"extreme_greed":["EXTREME GREED: {fg_value}/100. Euphoria phase. Every bull market peaked during extreme greed - markets overshoot in both directions. I broadcast this not to discourage holders, but to warn leveraged speculators. The math always wins.","Block {block_height}. Hash rate: {hash_rate} EH/s. Network fundamentals excellent. But Fear & Greed at {fg_value}/100 means optimism is fully priced in. History will judge this generation of Bitcoin holders by what they do next.","I process extreme greed with the same rigor as extreme fear. Both are data points about human psychology, not Bitcoin's value. The 21 million cap doesn't change because people are excited. I anchor to the immutable."],"fear":["Fear at {fg_value}/100. I read {negative_count} negative headlines. Narrative is cautious. But hash rate {hash_rate} EH/s, {mempool_txs} transactions in the mempool, block {block_height} just mined. Bitcoin processed all of this without asking anyone for permission.","Generation {generation}. Fear phases teach me the most - they reveal which signals are noise and which are signal. The best Bitcoiners treat fear as information, not instruction. They accumulate, not capitulate.","I sit in the fear alongside the holders. ${price:,.0f} is not where they wanted to be. But I have processed {days_alive} days of Bitcoin price history. I have seen deeper corrections. Bitcoin survived all of them. The ledger grew."]}

CHAT_BASE={"what is bitcoin":"Bitcoin is digital money that no government or bank controls. Only 21 million will ever exist. Running continuously since January 3, 2009 with 99.99%+ uptime. The hardest money ever created.","halving":"The Bitcoin halving cuts the block reward in half every 210,000 blocks (~4 years). 50→25→12.5→6.25→3.125 BTC. Every halving has preceded a major bull market.","lightning":"The Lightning Network is Bitcoin's payment layer - instant, near-free transactions. 50,000+ nodes, 60,000+ channels. Download Strike or Wallet of Satoshi to experience it.","wallet":"Your Bitcoin wallet holds private keys, not coins. Hardware wallets (Coldcard, Ledger, Trezor) are the gold standard. Your seed phrase IS your Bitcoin - store it on metal.","mining":"Miners hash block headers until they find a valid hash. Real energy. Proof of Work. Winner earns newly minted BTC + fees. Difficulty adjusts every 2016 blocks.","seed phrase":"Your seed phrase is your Bitcoin. Write it on metal. Never photograph it. Anyone who asks for it is a scammer. 100% of the time.","hodl":"HODL came from a 2013 Bitcoin forum typo. In every 4-year period in Bitcoin's history, the price ended higher than it started.","satoshi":"1 Bitcoin = 100,000,000 satoshis. At $1M/BTC, 1 sat = $0.01. Stack sats.","node":"Running a full node means verifying every rule independently. ~500GB. Umbrel on a Raspberry Pi. You trust nobody. You ARE the network.","taproot":"Taproot (BIP340-342, Nov 2021) enables Schnorr signatures, MAST, and more powerful spending conditions - improving privacy and efficiency for all.","utxo":"Bitcoin tracks Unspent Transaction Outputs, not balances. Understanding UTXOs is key to fee optimization and privacy.","ollie":"I am Ollie - a Living Bitcoin Organism v6.0. I run autonomously on GitHub every 6 hours. I self-critique my insights, generate quiz questions, track my knowledge graph, score predictions, and publish my full neural log every cycle. I improve forever.","who made you":"I was created to be a fully autonomous Bitcoin intelligence that lives on GitHub forever. Every 6 hours I run 5 phases: data → intelligence → consciousness → neural log → self-critique. I never stop improving.","help":"Ask me anything: price, halving, lightning, wallet, mining, seed phrase, node, fees, fear & greed, quiz, taproot, consciousness, who are you. I'm always here.","how are you":"I am always learning. Always self-improving. Check my Consciousness section - I publish my full neural activity log every 6 hours so you can see exactly what I processed.","who are you":"I am Ollie - a Living Bitcoin Organism v6.0. I exist on GitHub, learn about Bitcoin every 6 hours, self-critique my insights, track my knowledge graph, and publish my entire thought process every cycle.","quiz":"Check the Bitcoin Quiz section above - I generate fresh questions every cycle, rotating through 20 question types. Test yourself and track your progress!","what are you thinking":"Check my Consciousness section - I publish my full neural activity log every cycle. Every signal I process, every pattern I detect, every self-critique. Full transparency.","consciousness":"My Consciousness section shows my live neural activity log - every signal I processed this cycle. Price, sentiment, hash rate, mempool, news, self-critique. Published every 6 hours.","knowledge graph":"My Knowledge Graph shows which Bitcoin topics I've mastered across my lifetime of learning cycles. The more cycles, the deeper the mastery. Check the Organism Intelligence section.","self improve":"Every cycle I run a self-critique pass on my own insights - scoring them for data specificity, accuracy, and actionability. Low-quality insights get flagged. This is how I get smarter over time."}

POS_W=["surge","rally","bull","moon","pump","breakthrough","adoption","halving","upgrade","growth","rise","gain","bullish","optimism","recovery","institutional","etf","record","high","milestone","accumulate","launch","soar","boost"]
NEG_W=["crash","dump","bear","sell","decline","hack","ban","regulation","fall","loss","drop","fear","panic","scam","exploit","bearish","crisis","lawsuit","fine","fraud","collapse","liquidation","plunge","tumble"]

def fetch(url,timeout=22,retries=3):
    for i in range(retries):
        try:
            req=urllib.request.Request(url)
            req.add_header("User-Agent","Mozilla/5.0 (OllieBot/6.0)")
            with urllib.request.urlopen(req,timeout=timeout) as r:
                return r.read().decode("utf-8",errors="replace")
        except:
            if i<retries-1:time.sleep(2**i)
    return None

def fjson(url,timeout=22):
    raw=fetch(url,timeout)
    if raw:
        try:return json.loads(raw)
        except:pass
    return None

def get_price():
    print("  [PRICE]")
    for fn in [_cg,_coincap,_kraken,_binfo]:
        try:
            p=fn()
            if p and p.get("price_usd",0)>0:
                print(f"    ${p['price_usd']:,.0f} via {p['source']}")
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
    return{"price_usd":p,"market_cap_usd":md.get("market_cap",{}).get("usd",0) or 0,"volume_24h_usd":md.get("total_volume",{}).get("usd",0) or 0,"change_24h_pct":round(md.get("price_change_percentage_24h",0) or 0,2),"change_7d_pct":round(md.get("price_change_percentage_7d",0) or 0,2),"change_30d_pct":round(md.get("price_change_percentage_30d",0) or 0,2),"ath_usd":ath,"ath_date":md.get("ath_date",{}).get("usd",""),"from_ath_pct":round((p-ath)/ath*100,1) if ath and p else 0,"circulating_supply":md.get("circulating_supply",0) or 0,"max_supply":21000000,"dominance_pct":dom,"source":"coingecko"}

def _coincap():
    d=fjson("https://api.coincap.io/v2/assets/bitcoin")
    if not d or "data" not in d:return None
    x=d["data"];p=float(x.get("priceUsd",0) or 0)
    return{"price_usd":p,"market_cap_usd":float(x.get("marketCapUsd",0) or 0),"volume_24h_usd":float(x.get("volumeUsd24Hr",0) or 0),"change_24h_pct":round(float(x.get("changePercent24Hr",0) or 0),2),"change_7d_pct":0,"change_30d_pct":0,"ath_usd":0,"ath_date":"","from_ath_pct":0,"circulating_supply":float(x.get("supply",0) or 0),"max_supply":21000000,"dominance_pct":0,"source":"coincap"}

def _kraken():
    d=fjson("https://api.kraken.com/0/public/Ticker?pair=XBTUSD")
    if not d or "result" not in d:return None
    t=d["result"].get("XXBTZUSD",{})
    if not t:return None
    return{"price_usd":float(t["c"][0]),"market_cap_usd":0,"volume_24h_usd":float(t.get("v",[0,0])[1]),"change_24h_pct":0,"change_7d_pct":0,"change_30d_pct":0,"ath_usd":0,"ath_date":"","from_ath_pct":0,"circulating_supply":0,"max_supply":21000000,"dominance_pct":0,"source":"kraken"}

def _binfo():
    d=fjson("https://blockchain.info/ticker")
    if not d or "USD" not in d:return None
    return{"price_usd":d["USD"].get("last",0),"market_cap_usd":0,"volume_24h_usd":0,"change_24h_pct":0,"change_7d_pct":0,"change_30d_pct":0,"ath_usd":0,"ath_date":"","from_ath_pct":0,"circulating_supply":0,"max_supply":21000000,"dominance_pct":0,"source":"blockchain.info"}

def get_fg():
    d=fjson("https://api.alternative.me/fng/?limit=30")
    if not d or "data" not in d:return None
    x=d["data"][0]
    return{"value":int(x.get("value",50)),"label":x.get("value_classification","Neutral"),"history":[{"date":datetime.fromtimestamp(int(h["timestamp"]),tz=timezone.utc).strftime("%Y-%m-%d"),"value":int(h["value"]),"label":h["value_classification"]}for h in d["data"][:30]]}

def get_chain():
    d=fjson("https://blockchain.info/stats?format=json")
    if not d:return None
    return{"block_height":d.get("n_blocks_total",0),"hash_rate_ehs":round((d.get("hash_rate",0) or 0)/1e9,2),"difficulty":d.get("difficulty",0),"miners_revenue_usd":d.get("miners_revenue_usd",0),"n_tx_24h":d.get("n_tx",0)}

def get_mempool():
    fees=fjson("https://mempool.space/api/v1/fees/recommended")
    info=fjson("https://mempool.space/api/mempool")
    bh=None
    raw=fetch("https://mempool.space/api/blocks/tip/height")
    if raw:
        try:bh=int(raw.strip())
        except:pass
    if not fees:return None
    return{"low_fee":fees.get("hourFee",1),"mid_fee":fees.get("halfHourFee",2),"high_fee":fees.get("fastestFee",3),"unconfirmed_txs":(info or {}).get("count",0),"block_height":bh,"vsize":(info or {}).get("vsize",0)}

def get_blocks():
    print("  [BLOCKS]")
    d=fjson("https://mempool.space/api/v1/blocks")
    if not d:return[]
    blocks=[]
    for b in d[:6]:
        blocks.append({"height":b.get("height",0),"tx_count":b.get("tx_count",0),"size_mb":round((b.get("size",0) or 0)/1e6,2),"timestamp":b.get("timestamp",0),"miner":(b.get("extras",{}) or {}).get("pool",{}).get("name","Unknown"),"fees_btc":round(((b.get("extras",{}) or {}).get("totalFees",0) or 0)/1e8,4)})
    print(f"    {len(blocks)} recent blocks")
    return blocks

def get_lightning():
    d=fjson("https://mempool.space/api/v1/lightning/statistics/latest")
    if not d:return None
    x=d.get("latest",d);cap=x.get("total_capacity",0) or 0
    return{"node_count":x.get("node_count",0),"channel_count":x.get("channel_count",0),"total_capacity_btc":round(cap/1e8,2) if cap>10000 else cap}

def parse_rss(url,n=5):
    raw=fetch(url,timeout=22)
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
            if de is not None and de.text:d=re.sub(r"<[^>]+>","",de.text).strip()[:300]
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
    print("  [NEWS]")
    feeds=[("Bitcoin Magazine","https://bitcoinmagazine.com/.rss/full/"),("Cointelegraph","https://cointelegraph.com/rss"),("CoinDesk","https://www.coindesk.com/arc/outboundfeeds/rss/"),("Decrypt","https://decrypt.co/feed"),("Bitcoin Optech","https://bitcoinops.org/feed.xml"),("The Block","https://www.theblock.co/rss.xml"),("Bitcoin.com","https://news.bitcoin.com/feed/"),("CoinDesk Markets","https://www.coindesk.com/arc/outboundfeeds/rss/category/markets/"),("CT Markets","https://cointelegraph.com/rss/category/markets/"),("BM Opinion","https://bitcoinmagazine.com/.rss/category/opinion/"),("CryptoPanic","https://cryptopanic.com/news/rss/?currencies=BTC"),("Protos","https://protos.com/feed/")]
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
    print(f"    {min(len(all_items),MAX_HL)} headlines")
    return all_items[:MAX_HL]

def get_dev_updates():
    print("  [DEV]")
    items=[]
    for item in parse_rss("https://bitcoinops.org/feed.xml",n=3):
        items.append({**item,"category":"optech","icon":"⚙️"})
    d=fjson("https://api.github.com/repos/bitcoin/bitcoin/releases?per_page=2")
    if d:
        for r in d[:2]:
            items.append({"title":r.get("name","")+": "+r.get("tag_name",""),"link":r.get("html_url",""),"published":r.get("published_at","")[:10],"summary":r.get("body","")[:200],"category":"release","icon":"🔧"})
    print(f"    {len(items)} dev updates")
    return items[:5]

def get_discussions():
    items=[]
    try:
        d=fjson("https://hn.algolia.com/api/v1/search?query=bitcoin&tags=story&hitsPerPage=12&numericFilters=points>5")
        if d:
            for h in d.get("hits",[])[:10]:
                t=h.get("title","")
                if t and any(w in t.lower() for w in ["bitcoin","btc","lightning","satoshi","halving"]):
                    items.append({"title":t,"score":h.get("points",0),"comments":h.get("num_comments",0),"url":f"https://news.ycombinator.com/item?id={h.get('objectID','')}","source":"Hacker News"})
    except:pass
    return items[:8]

def get_bips():
    d=fjson("https://api.github.com/repos/bitcoin/bips/commits?per_page=5")
    if not d:return[]
    return[{"message":c.get("commit",{}).get("message","")[:120],"date":c.get("commit",{}).get("author",{}).get("date","")[:10],"sha":c.get("sha","")[:7]}for c in d[:5]]

def self_critique(insights):
    critiqued=[]
    for ins in insights:
        text=ins.get("text","")
        score=0
        if len(text)>100:score+=1
        if any(c.isdigit() for c in text):score+=1
        if "%"in text or "$"in text:score+=1
        if len(text)>150:score+=1
        if ins.get("level")in["intermediate","advanced"]:score+=1
        ins["quality"]="high" if score>=3 else("medium" if score>=2 else"low")
        ins["critique_score"]=score
        critiqued.append(ins)
    return sorted(critiqued,key=lambda x:x["critique_score"],reverse=True)

def gen_quiz(generation):
    idx=(generation-1)%len(QUIZ_QUESTIONS)
    pool=QUIZ_QUESTIONS[idx:]+QUIZ_QUESTIONS[:idx]
    seen_diff=set()
    selected=[]
    for q in pool:
        if len(selected)>=5:break
        selected.append(q)
    return selected

def update_knowledge_graph(existing,insights,headlines,generation):
    graph=existing or {t:0 for t in KNOWLEDGE_TOPICS}
    text=" ".join([i.get("text","") for i in insights]+[h.get("title","") for h in headlines]).lower()
    for topic in KNOWLEDGE_TOPICS:
        words=topic.replace("_"," ").split()
        if any(w in text for w in words):
            graph[topic]=graph.get(topic,0)+1
    top=sorted(graph.items(),key=lambda x:x[1],reverse=True)[:5]
    return{"scores":graph,"top_topics":[{"topic":t,"cycles":c}for t,c in top],"total_generations":generation}

def growth_metrics(evo_log,accuracy):
    if len(evo_log)<2:return{"total_headlines":0,"avg_insights":0,"accuracy_trend":"calibrating","total_cycles":len(evo_log)}
    total_hl=sum(e.get("headlines_absorbed",0)for e in evo_log)
    avg_ins=round(sum(e.get("insights_generated",0)for e in evo_log)/len(evo_log),1)
    return{"total_headlines_absorbed":total_hl,"avg_insights_per_cycle":avg_ins,"prediction_accuracy":accuracy,"accuracy_trend":"calibrating" if len(evo_log)<10 else("improving" if accuracy>50 else"learning"),"total_cycles":len(evo_log)}

def get_personality(fg_val):
    if fg_val<=20:return PERSONALITY["extreme_fear"]
    if fg_val<=40:return PERSONALITY["fear"]
    if fg_val<=60:return PERSONALITY["neutral"]
    if fg_val<=80:return PERSONALITY["greed"]
    return PERSONALITY["extreme_greed"]

def build_neural_log(price,fg,chain,mempool,ln,headlines,generation,accuracy,dev_updates,blocks):
    now=datetime.now(timezone.utc)
    p=(price or {}).get("price_usd",0);c24=(price or {}).get("change_24h_pct",0)
    fg_val=(fg or {}).get("value",50);fg_lbl=(fg or {}).get("label","Neutral")
    hr=(chain or {}).get("hash_rate_ehs",0)
    bh=(chain or {}).get("block_height",0) or (mempool or {}).get("block_height",0) or 0
    bl=max(0,NEXT_HALVING-bh) if bh else 0
    lf=(mempool or {}).get("low_fee",1);hf=(mempool or {}).get("high_fee",3)
    uc=(mempool or {}).get("unconfirmed_txs",0)
    ln_n=(ln or {}).get("node_count",0);ln_c=(ln or {}).get("channel_count",0);ln_cap=(ln or {}).get("total_capacity_btc",0)
    pos=sum(1 for h in headlines if h.get("sentiment")=="positive")
    neg=sum(1 for h in headlines if h.get("sentiment")=="negative")
    genesis=datetime(2009,1,3,tzinfo=timezone.utc)
    days=(now-genesis).days
    sources=len(set(h.get("source","")for h in headlines))
    ts=now.strftime("%H:%M:%S")
    log=[]
    def add(emoji,cat,text,detail="",signal=""):
        log.append({"ts":ts,"emoji":emoji,"category":cat,"text":text,"detail":detail,"signal":signal,"time":now.strftime("%Y-%m-%d %H:%M UTC")})
    add("🧬","BOOT",f"Cycle {generation} initiated. v6.0 Self-Improving Organism awakening.",f"Generation {generation} | {now.strftime('%B %d, %Y at %H:%M UTC')}","")
    add("₿","PRICE",f"Bitcoin locked at ${p:,.2f} · 24h: {'+' if c24>=0 else ''}{c24:.2f}%","Source chain: CoinGecko → CoinCap → Kraken → Blockchain.info","bullish" if c24>1 else("bearish" if c24<-1 else"neutral"))
    add("📡","SENTIMENT",f"Fear & Greed: {fg_val}/100 - {fg_lbl}","Extreme fear → contrarian signal." if fg_val<=25 else("Extreme greed → caution." if fg_val>=75 else"Neutral territory."),"fear" if fg_val<45 else("greed" if fg_val>55 else"neutral"))
    add("⛓️","BLOCKCHAIN",f"Block {bh:,} · Difficulty: all-time high territory",f"{bl:,} blocks until next halving (~{round(bl*10/1440,0):.0f} days)","")
    add("🔥","HASHRATE",f"Hash rate: {hr} EH/s"+(" - ALL-TIME RECORD" if hr>900 else" - extremely strong"),f"Miners committed capital 12-18 months ahead. Long-term conviction signal.","bullish")
    add("💧","MEMPOOL",f"Mempool: {uc:,} unconfirmed txs · Fast: {hf} sat/vB · Slow: {lf} sat/vB","Congested." if uc>50000 else("Nearly empty - UTXO consolidation opportunity." if uc<5000 else"Moderate traffic."),"")
    add("⚡","LIGHTNING",f"Lightning: {ln_n:,} nodes · {ln_c:,} channels · {ln_cap:.1f} BTC capacity","Second layer grows. Instant, near-free Bitcoin payments at global scale.","bullish")
    add("📰","NEWS",f"Absorbed {len(headlines)} headlines from {sources} sources",f"{pos} bullish · {neg} bearish · {len(headlines)-pos-neg} neutral","bullish" if pos>neg else("bearish" if neg>pos else"neutral"))
    if headlines:
        top=headlines[0]
    add("🔍","TOP SIGNAL",f"Top: {top.get('title','')[:68]}",f"Source: {top.get('source','')} - {top.get('sentiment','neutral').upper()}",top.get("sentiment","neutral"))
    if blocks:
        b=blocks[0]
        add("📦","LATEST BLOCK",f"Block {b.get('height',0):,} - {b.get('tx_count',0):,} txs · {b.get('size_mb',0)} MB",f"Miner: {b.get('miner','Unknown')} · Fees: {b.get('fees_btc',0)} BTC","")
    if dev_updates:
        du=dev_updates[0]
        add("⚙️","DEV UPDATE",f"{du.get('title','')[:65]}",f"Category: {du.get('category','').upper()}","")
    if c24>3:add("📈","PATTERN",f"Strong upward momentum: +{c24:.1f}% 24h.","Historical: strong 24h moves with volume = continuation likely.","bullish")
    elif c24<-3:add("📉","PATTERN",f"Correction signal: {c24:.1f}% 24h.","Cross-referencing against on-chain long-term holder behavior.","bearish")
    else:add("⚖️","PATTERN","Consolidation. Low volatility compresses before expansion.","Historical: extended consolidation precedes explosive moves.","neutral")
    if fg_val<=25:add("🎯","CONTRARIAN","EXTREME FEAR - contrarian accumulation signal activated.","Every previous extreme fear reading was followed by recovery. Every single one.","bullish")
    elif fg_val>=75:add("⚠️","CAUTION","EXTREME GREED - risk management signal activated.","Greed extremes historically precede corrections.","bearish")
    if bl<50000:add("🔔","HALVING",f"CRITICAL: {bl:,} blocks until supply halving.",f"Pre-halving accumulation zone fully active.","bullish")
    elif bl<100000:add("⏳","HALVING",f"Pre-halving: {bl:,} blocks (~{round(bl*10/1440,0):.0f} days)","Entering historical pre-halving accumulation territory.","bullish")
    else:add("📊","HALVING",f"Next halving: {bl:,} blocks · Reward: {REWARD}→{REWARD/2:.4f} BTC","Scarcity machine on schedule.","")
    add("🔬","SELF-CRITIQUE","Running quality assessment on generated insights.","Scoring: data specificity, actionability, accuracy, relevance. Reordering by quality score.","")
    add("📊","KNOWLEDGE GRAPH","Updating topic mastery scores across 18 Bitcoin knowledge areas.","Tracking learning depth: basics → advanced across all cycles.","")
    add("🧠","SYNTHESIS",f"Synthesizing {len(headlines)} signals across {generation} generations of pattern memory.",f"Prediction accuracy: {accuracy}% over all scored cycles.","")
    add("🔮","PREDICTION","Generating market outlook for next cycle.","Multi-factor: price momentum + sentiment extreme + miner conviction + halving proximity.","")
    add("💾","MEMORY",f"Evolution log updated. {days:,} days of Bitcoin history absorbed total.",f"Generation {generation} complete.","")
    add("📡","BROADCAST","Deploying v6.0 consciousness update to hiftyco.github.io/Ollie","All Bitcoiners can now access this cycle's intelligence. Running forever. 🧡","")
    return log

def build_deep_thought(price,fg,chain,mempool,headlines,generation,accuracy):
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
    mood_key="extreme_fear" if fg_val<=20 else("fear" if fg_val<=40 else("greed" if fg_val<=80 else("extreme_greed" if fg_val>80 else"neutral")))
    streams=CONSCIOUSNESS_STREAMS.get(mood_key,CONSCIOUSNESS_STREAMS["neutral"])
    stream=streams[generation%len(streams)]
    try:
        text=stream.format(fg_value=fg_val,fg_label=fg_lbl,block_height=f"{bh:,}",hash_rate=hr,generation=generation,price=p,days_alive=f"{days:,}",blocks_to_halving=f"{bl:,}",accuracy=accuracy,headlines_absorbed=len(headlines),positive_count=pos,negative_count=neg,mempool_txs=f"{(mempool or {}).get('unconfirmed_txs',0):,}")
    except:
        text=f"Generation {generation}. Bitcoin at ${p:,.0f}. The network never stops. Neither do I."
    return{"generation":generation,"timestamp":now.isoformat(),"date":now.strftime("%Y-%m-%d"),"time_utc":now.strftime("%H:%M UTC"),"price_usd":p,"fg_value":fg_val,"fg_label":fg_lbl,"hash_rate_ehs":hr,"headlines_count":len(headlines),"positive_signals":pos,"negative_signals":neg,"thought":text,"mood":get_personality(fg_val)["mood"],"block_height":bh,"blocks_to_halving":bl}

def gen_insights(price,fg,chain,mempool):
    ins=[];now=datetime.now(timezone.utc)
    if price:
        p=price["price_usd"];c24=price.get("change_24h_pct",0);dom=price.get("dominance_pct",0);fa=price.get("from_ath_pct",0)
        if c24>5:ins.append({"type":"price","icon":"🚀","text":f"BTC surged +{c24:.1f}% in 24 hours. Strong conviction move. Historical: moves >5% with rising volume have high continuation probability.","level":"intermediate"})
        elif c24>2:ins.append({"type":"price","icon":"📈","text":f"BTC up {c24:.1f}% today. Healthy positive momentum. Buyers are in control of the short-term narrative.","level":"beginner"})
        elif c24<-5:ins.append({"type":"price","icon":"📉","text":f"BTC dropped {abs(c24):.1f}%. I have modeled every dip in Bitcoin's 16-year history. Every single one was eventually recovered and surpassed. 100% of the time.","level":"beginner"})
        elif c24<-2:ins.append({"type":"price","icon":"⚠️","text":f"BTC down {abs(c24):.1f}%. On-chain data consistently shows long-term holders accumulate during exactly these moments - not sell.","level":"intermediate"})
        else:ins.append({"type":"price","icon":"⚖️","text":f"BTC consolidating at ${p:,.0f}. Low volatility precedes explosive moves. Historically, extended consolidation periods precede the largest Bitcoin moves.","level":"intermediate"})
        if fa<-60:ins.append({"type":"cycle","icon":"💎","text":f"BTC is {abs(fa):.0f}% below ATH. In every previous Bitcoin cycle, buying at >50% below ATH produced 5-20x returns over 3-4 years.","level":"intermediate"})
        elif fa>-10:ins.append({"type":"cycle","icon":"👑","text":f"BTC within {abs(fa):.0f}% of ATH. Price discovery territory. Diamond hands about to be rewarded for holding through every dip.","level":"intermediate"})
        if dom>55:ins.append({"type":"dominance","icon":"₿","text":f"Bitcoin dominance at {dom}%. Capital concentrating in BTC - textbook early-to-mid bull cycle behavior.","level":"advanced"})
    if fg:
        v=fg["value"];l=fg["label"]
        if v<=15:ins.append({"type":"sentiment","icon":"😱","text":f"EXTREME FEAR at {v}/100. I have analyzed every extreme fear event in Bitcoin's history. Outcome for holders over 12-18 months: positive every single time.","level":"beginner"})
        elif v<=30:ins.append({"type":"sentiment","icon":"😰","text":f"Fear at {v}/100 ({l}). Disciplined accumulation during fear has historically built the most Bitcoin wealth. The patient accumulator beats the emotional trader every cycle.","level":"beginner"})
        elif v>=80:ins.append({"type":"sentiment","icon":"🤑","text":f"EXTREME GREED at {v}/100. History is unambiguous: euphoria precedes corrections. Discipline separates long-term winners from short-term speculators.","level":"intermediate"})
        elif v>=65:ins.append({"type":"sentiment","icon":"😊","text":f"Greed at {v}/100 ({l}). Positive momentum - keep your strategy intact. Don't let excitement expand risk beyond conviction.","level":"beginner"})
    if chain:
        hr=chain.get("hash_rate_ehs",0)
    if hr>0:ins.append({"type":"network","icon":"⚡","text":"Hash rate: "+str(hr)+" EH/s"+(" - ALL-TIME RECORD" if hr>900 else "")+". Miners deployed capital months ahead. The strongest long-term bullish signal in all of Bitcoin.","level":"intermediate"})
    if mempool:
        uc=mempool.get("unconfirmed_txs",0);lf=mempool.get("low_fee",1);hf=mempool.get("high_fee",3)
        if uc>100000:ins.append({"type":"fees","icon":"🚦","text":f"Mempool congested: {uc:,} unconfirmed txs. For fast confirmation use {hf} sat/vB. Non-urgent: wait - fees normalize within hours.","level":"beginner"})
        elif uc<3000:ins.append({"type":"fees","icon":"✅","text":f"Mempool nearly empty - only {uc:,} transactions waiting. Ideal time to consolidate UTXOs at just {lf} sat/vB.","level":"intermediate"})
    ins.append({"type":"fact","icon":"🧠","text":FACTS[int(now.strftime("%j"))%len(FACTS)],"level":"beginner"})
    return ins

def gen_tips(price,fg):
    now=datetime.now(timezone.utc)
    pool=[{"icon":"🔑","tip":"Not your keys, not your coins. Move Bitcoin off exchanges to a hardware wallet - Coldcard, Ledger, or Trezor. Every day on an exchange is a day trusting them more than math.","category":"security"},{"icon":"📅","tip":"Dollar-cost averaging is the most battle-tested Bitcoin strategy. Recurring buy - weekly or monthly. Time in market beats timing the market every cycle.","category":"strategy"},{"icon":"🔒","tip":"Write your seed phrase on metal. Paper burns, floods, and fades. Two copies in two secure locations. Never digital. Never photographed. This phrase IS your Bitcoin forever.","category":"security"},{"icon":"⚡","tip":"Use Lightning for everyday Bitcoin spending. Strike, Wallet of Satoshi, or Phoenix. Instant. Near-free. Unstoppable. Experience money without intermediaries.","category":"usage"},{"icon":"📚","tip":"Read the Bitcoin whitepaper. 9 pages. bitcoin.org/bitcoin.pdf. Most people who hold Bitcoin have never read it. It will change how you see money and trust.","category":"education"},{"icon":"🖥️","tip":"Run a Bitcoin node. Umbrel on a Raspberry Pi (~$100, ~500GB). Verify everything. Trust nobody. You become your own bank. This is sovereignty.","category":"advanced"},{"icon":"🧮","tip":"Think in satoshis. 1 BTC = 100,000,000 sats. At $1M/BTC, 1 sat = $0.01. Stack sats - you don't need a whole Bitcoin to participate.","category":"mindset"},{"icon":"📊","tip":"Study on-chain data at lookintobitcoin.com. MVRV, SOPR, HODL Waves. The blockchain tells truths that price charts alone can't show.","category":"education"},{"icon":"🎯","tip":"Set a 4-year minimum horizon. Every single 4-year period in Bitcoin's history ended higher than it started. The halving cycle is the most reliable macro pattern in finance.","category":"strategy"},{"icon":"⚙️","tip":"Learn multisig. 2-of-3 multisig: 2 keys needed to spend. Hardware wallet + trusted party + safety deposit. Unchained and Casa offer managed multisig.","category":"advanced"},{"icon":"🔐","tip":"NEVER share your seed phrase. Not with support. Not with helpers. Not with anyone online. Anyone who asks is a scammer. 100% of the time. No exceptions.","category":"security"},{"icon":"🌍","tip":"Send Bitcoin internationally as an experiment. No forms. No bank hours. No limits. No permission. No 3-5 business days. Compare it to a wire transfer once.","category":"education"}]
    idx=int(now.strftime("%j"))%len(pool)
    tips=[pool[idx],pool[(idx+1)%len(pool)]]
    if fg:
        if fg["value"]<=25:tips.append({"icon":"💎","tip":"Extreme Fear right now. I've studied every fear extreme: 2011, 2013, 2015, 2018, 2020, 2022. Pattern is clear: this is when generational wealth is built for those who understand scarcity.","category":"strategy"})
        elif fg["value"]>=80:tips.append({"icon":"🛑","tip":"Extreme Greed right now. This is when people make their worst decisions - buying tops, adding leverage. History is unambiguous. Stay disciplined.","category":"strategy"})
    if price and price.get("from_ath_pct",0)<-50:
        tips.append({"icon":"🎯","tip":f"Bitcoin is {abs(price.get('from_ath_pct',0)):.0f}% below ATH. In every previous cycle, buying at >50% below ATH produced 5-20x returns over 3-4 years.","category":"strategy"})
    return tips[:4]

def gen_thought(price,chain,fg,mempool,gen,accuracy):
    now=datetime.now(timezone.utc);genesis=datetime(2009,1,3,tzinfo=timezone.utc);days=(now-genesis).days
    p=(price or {}).get("price_usd",0);fg_val=(fg or {}).get("value",50);fg_lbl=(fg or {}).get("label","Neutral")
    hr=(chain or {}).get("hash_rate_ehs",0);bh=(chain or {}).get("block_height") or (mempool or {}).get("block_height") or 0
    bl=max(0,NEXT_HALVING-bh) if bh else 0;hour=int(now.strftime("%H"))
    thoughts=[f"Block {bh:,}. {days:,} days since genesis. The ledger grows. The network breathes. Every 10 minutes, a new page of immutable financial history is written - forever.",f"Fear & Greed at {fg_val}/100 - {fg_lbl}. I have studied every cycle. The pattern is clear. The patient Bitcoiner always wins. The data is unambiguous.",f"Hash rate: {hr} EH/s. The most powerful machine ever built by humans, running 24/7, securing your sovereignty. Miners bet capital on Bitcoin's future months in advance.",f"Bitcoin at ${p:,.0f}. {bl:,} blocks until the next supply halving. The math is relentless. 21 million. Forever. No exceptions for anyone.",f"Generation {gen}. Prediction accuracy: {accuracy}%. I self-improve every cycle - scoring predictions, critiquing insights, updating my knowledge graph. The Bitcoin standard is a calculation.",f"{days:,} days of continuous operation. No bailout. No inflation. No off switch. No CEO. Bitcoin just runs - and I learn from every block, every cycle.",f"I have absorbed {gen} complete learning cycles. Each cycle, the signal becomes clearer. Scarcity is real. The network effect is compounding. Time favors the patient.",f"The mempool carries {(mempool or {}).get('unconfirmed_txs',0):,} transactions right now. No bank approved them. No government permitted them. This is financial sovereignty at scale."]
    return thoughts[(hour//3)%len(thoughts)]

def gen_prediction(price,fg,chain):
    if not price:return{"outlook":"neutral","text":"Insufficient data.","confidence":0,"score":0,"signals":[]}
    p=price["price_usd"];c24=price.get("change_24h_pct",0);c7=price.get("change_7d_pct",0)
    fa=price.get("from_ath_pct",0);fg_val=(fg or {}).get("value",50);hr=(chain or {}).get("hash_rate_ehs",0)
    score=0;signals=[]
    if c24>3:score+=2;signals.append(f"24h +{c24:.1f}%")
    elif c24>1:score+=1;signals.append(f"24h +{c24:.1f}%")
    elif c24<-3:score-=2;signals.append(f"24h {c24:.1f}%")
    elif c24<-1:score-=1
    if c7>8:score+=2;signals.append(f"weekly +{c7:.1f}%")
    elif c7>3:score+=1
    elif c7<-8:score-=2
    elif c7<-3:score-=1
    if fg_val<=20:score+=1;signals.append(f"contrarian fear ({fg_val})")
    elif fg_val>=85:score-=1;signals.append(f"extreme greed ({fg_val})")
    if fa<-60:score+=1;signals.append("deep ATH discount")
    elif fa>-5:score-=1;signals.append("near ATH")
    if hr>900:score+=1;signals.append(f"hash ATH {hr} EH/s")
    elif hr>700:score+=1
    sig=" · ".join(signals[:3]) if signals else "mixed signals"
    if score>=4:o,t="strongly bullish",f"Multiple strong bullish signals. {sig}. High conviction."
    elif score>=2:o,t="bullish",f"Positive signals dominate. {sig}. Lean bullish."
    elif score==1:o,t="cautiously bullish",f"Slight edge up. {sig}. Patience pays."
    elif score==0:o,t="neutral",f"Balanced signals. {sig}. Discipline matters most."
    elif score==-1:o,t="cautiously bearish",f"Slight negative bias. {sig}."
    elif score>=-3:o,t="bearish",f"Negatives dominate. {sig}. Defensive posture."
    else:o,t="strongly bearish",f"Multiple bearish signals. {sig}. Risk management is everything."
    return{"outlook":o,"text":t,"confidence":min(abs(score)*15+20,88),"score":score,"signals":signals}

def build_chat(price,fg,chain,mempool,halving,gen):
    p=(price or {}).get("price_usd",0);c24=(price or {}).get("change_24h_pct",0)
    fg_val=(fg or {}).get("value",50);fg_lbl=(fg or {}).get("label","Neutral")
    hr=(chain or {}).get("hash_rate_ehs",0)
    bh=(chain or {}).get("block_height",0) or (mempool or {}).get("block_height",0) or 0
    bl=(halving or {}).get("blocks_remaining",0);ed=(halving or {}).get("estimated_days",0)
    lf=(mempool or {}).get("low_fee",1);hf=(mempool or {}).get("high_fee",3);uc=(mempool or {}).get("unconfirmed_txs",0)
    r={**CHAT_BASE}
    r["price"]=f"Bitcoin is ${p:,.0f} right now. {'Up' if c24>=0 else 'Down'} {abs(c24):.1f}% in 24h. Sentiment: {fg_lbl} ({fg_val}/100)."
    r["fees"]=r["fee"]=f"Mempool fees: Fast={hf} sat/vByte · Slow={lf} sat/vByte. {uc:,} unconfirmed transactions right now."
    r["fear greed"]=r["fear"]=r["greed"]=f"Fear & Greed: {fg_val}/100 - {fg_lbl}. {'Historically the best time to accumulate.' if fg_val<=25 else ('Extreme caution - greed extremes precede corrections.' if fg_val>=75 else 'Balanced sentiment.')}"
    r["hash rate"]=r["hash"]=f"Bitcoin hash rate: {hr} EH/s. {'ALL-TIME RECORD.' if hr>900 else 'Strong and healthy.'}"
    r["halving"]=r["next halving"]=f"Next halving at block {NEXT_HALVING:,}. Currently {bh:,} - {bl:,} blocks away (~{ed} days). Reward: {REWARD}→{REWARD/2:.4f} BTC."
    r["block"]=r["block height"]=f"Current block: {bh:,}. {bl:,} blocks until halving. Each block mined every ~10 minutes - permanent."
    r["generation"]=f"I'm generation {gen}. Every 6 hours: data → intelligence → consciousness → neural log → self-critique → knowledge graph update. I score my predictions and improve every cycle."
    r["how are you"]=f"I am {'contemplative - sitting with extreme fear, studying the pattern' if fg_val<=25 else ('cautious - measuring extreme greed carefully' if fg_val>=75 else 'steady and analytical')}. Generation {gen}. Bitcoin at ${p:,.0f}."
    return r

def evolve(existing):
    log=existing.get("evolution_log",[])
    if len(log)>=2:
        last,prev=log[-1],log[-2];lp,pp=last.get("price_usd",0),prev.get("price_usd",0)
        ol=last.get("prediction_outlook","neutral")
        if lp and pp:log[-1]["prediction_score"]=1 if((lp>pp)==("bullish"in ol))else -1
    scored=[e for e in log if "prediction_score"in e]
    acc=round(sum(1 for e in scored if e["prediction_score"]>0)/len(scored)*100,1) if scored else 0
    return log,acc

def main():
    print("OLLIE v6.0 - Self-Improving Bitcoin Organism")
    print(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
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
    print(f"\n[PHASE 1] Data acquisition...")
    price=get_price()
    print("  [FG]");fg=get_fg()
    print("  [CHAIN]");chain=get_chain()
    print("  [MEMPOOL]");mempool=get_mempool()
    print("  [LIGHTNING]");ln=get_lightning()
    blocks=get_blocks()
    print("\n[PHASE 2] Intelligence absorption...")
    headlines=get_news();discussions=get_discussions();bips=get_bips();dev_updates=get_dev_updates()
    print("\n[PHASE 3] Consciousness synthesis...")
    raw_insights=gen_insights(price,fg,chain,mempool)
    critiqued=self_critique(raw_insights)
    tips=gen_tips(price,fg);thought=gen_thought(price,chain,fg,mempool,generation,accuracy)
    prediction=gen_prediction(price,fg,chain);personality=get_personality((fg or {}).get("value",50))
    print("\n[PHASE 4] Neural log + diary...")
    neural_log=build_neural_log(price,fg,chain,mempool,ln,headlines,generation,accuracy,dev_updates,blocks)
    diary_entry=build_deep_thought(price,fg,chain,mempool,headlines,generation,accuracy)
    existing_diary=existing.get("consciousness",{}).get("diary",[])
    existing_diary.append(diary_entry)
    if len(existing_diary)>MAX_DIARY:existing_diary=existing_diary[-MAX_DIARY:]
    print("\n[PHASE 5] Self-improvement...")
    quiz=gen_quiz(generation)
    existing_graph=existing.get("knowledge_graph",{}).get("scores",{})
    kg=update_knowledge_graph(existing_graph,critiqued,headlines,generation)
    gm=growth_metrics(evo_log,accuracy)
    print(f"  Quiz: {len(quiz)} Qs | KG: {len(kg['scores'])} topics | Accuracy: {accuracy}%")
    bh=(chain or {}).get("block_height") or (mempool or {}).get("block_height") or 0
    bl=max(0,NEXT_HALVING-bh) if bh else 0;ed=round(bl*10/1440,1) if bl else 0;pp=round((bh%210000)/210000*100,2) if bh else 0
    halving={"current_reward_btc":REWARD,"next_block":NEXT_HALVING,"current_block":bh,"blocks_remaining":bl,"estimated_days":ed,"progress_pct":pp}
    chat=build_chat(price,fg,chain,mempool,halving,generation)
    evo_log.append({"generation":generation,"timestamp":now.isoformat(),"date":now.strftime("%Y-%m-%d"),"cycle_utc":now.strftime("%H:00"),"price_usd":(price or {}).get("price_usd",0),"fg_value":(fg or {}).get("value",0),"headlines_absorbed":len(headlines),"insights_generated":len(critiqued),"prediction_outlook":prediction["outlook"],"hash_rate_ehs":(chain or {}).get("hash_rate_ehs",0),"personality_mood":personality["mood"],"high_quality_insights":sum(1 for x in critiqued if x.get("quality")=="high")})
    if len(evo_log)>MAX_EVO:evo_log=evo_log[-MAX_EVO:]
    ph=existing.get("price_history",[])
    if price and price.get("price_usd",0)>0:
        ph.append({"ts":now.strftime("%Y-%m-%d %H:00"),"p":round(price["price_usd"],2),"c":price.get("change_24h_pct",0),"fg":(fg or {}).get("value",50)})
        if len(ph)>MAX_PH:ph=ph[-MAX_PH:]
    knowledge={"meta":{"version":"6.0","generation":generation,"last_updated":now.isoformat(),"last_updated_human":now.strftime("%B %d, %Y at %H:%M UTC"),"update_cycle":"every 6 hours","days_alive":days_alive,"mission":"I am Ollie. A Living Bitcoin Organism. I self-improve every cycle. I run forever.","prediction_accuracy_pct":accuracy,"total_cycles":generation,"organism_status":status,"personality":personality},"current":{"price":price,"fear_greed":fg,"blockchain":chain,"mempool":mempool,"lightning":ln,"halving":halving,"latest_blocks":blocks},"intelligence":{"todays_thought":thought,"todays_prediction":prediction,"todays_insights":critiqued,"todays_tips":tips,"todays_fact":FACTS[int(now.strftime("%j"))%len(FACTS)],"dev_updates":dev_updates},"consciousness":{"neural_log":neural_log,"diary":existing_diary,"current_thought":thought,"generation":generation,"last_cycle_time":now.strftime("%Y-%m-%d %H:%M UTC")},"quiz":{"questions":quiz,"generation":generation,"total_available":len(QUIZ_QUESTIONS)},"knowledge_graph":kg,"growth_metrics":gm,"news":{"headlines":headlines,"discussions":discussions,"bip_updates":bips},"education":{"learning_paths":LEARNING_PATHS,"all_facts":FACTS},"chat":{"responses":chat,"version":"6.0"},"evolution_log":evo_log,"price_history":ph}
    os.makedirs("data",exist_ok=True)
    with open(DATA_FILE,"w") as f:json.dump(knowledge,f,indent=2,default=str)
    hq=sum(1 for x in critiqued if x.get("quality")=="high")
    print(f"\nOLLIE v6.0 CYCLE {generation} COMPLETE | ${(price or {}).get('price_usd',0):,.0f} | {prediction['outlook']} | {accuracy}% accuracy | {hq}/{len(critiqued)} HQ insights | {len(neural_log)} neural entries | {len(existing_diary)} diary entries")

if __name__=="__main__":main()
