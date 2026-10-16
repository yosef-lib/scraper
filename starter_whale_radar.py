#!/usr/bin/env python3
"""
DexScreener Whale Radar Starter Scanner
Real-time on-chain anomaly and breakout hunter (Open-Source Starter Edition).
"""
import time
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def scan_dex_anomalies():
    print("🔍 [WHALE RADAR] Querying DexScreener real-time liquidity pools...\n")
    try:
        url = "https://api.dexscreener.com/token-boosts/latest/v1"
        res = requests.get(url, headers=HEADERS, timeout=12)
        if res.status_code != 200:
            print(f"Error fetching data: HTTP {res.status_code}")
            return

        boosts = res.json()
        addresses = [item.get("tokenAddress") for item in boosts if item.get("tokenAddress")][:10]

        if not addresses:
            print("No active boosts detected.")
            return

        print(f"Analyzing {len(addresses)} high-activity token pairs...\n" + "━" * 55)

        for addr in addresses:
            pair_url = f"https://api.dexscreener.com/latest/dex/tokens/{addr}"
            p_res = requests.get(pair_url, headers=HEADERS, timeout=12)
            if p_res.status_code != 200:
                continue

            data = p_res.json()
            pairs = data.get("pairs") or []
            if not pairs:
                continue

            pairs.sort(key=lambda p: float((p.get("liquidity") or {}).get("usd") or 0), reverse=True)
            top = pairs[0]

            symbol = top.get("baseToken", {}).get("symbol", "N/A")
            name = top.get("baseToken", {}).get("name", "N/A")
            chain = top.get("chainId", "N/A").upper()
            price = float(top.get("priceUsd") or 0.0)
            change_1h = float((top.get("priceChange") or {}).get("h1") or 0.0)
            vol_1h = float((top.get("volume") or {}).get("h1") or 0.0)
            liq = float((top.get("liquidity") or {}).get("usd") or 0.0)
            buys = int((top.get("txns", {}).get("h1") or {}).get("buys") or 0)
            sells = int((top.get("txns", {}).get("h1") or {}).get("sells") or 0)
            ratio = round(buys / max(1, sells), 2)

            if liq >= 10000 and vol_1h >= 5000:
                print(f"🔥 BREAKOUT DETECTED: ${symbol} ({name}) | {chain}")
                print(f"   • Price: ${price:.6f} | 1h Change: {change_1h:+.2f}%")
                print(f"   • 1h Volume: ${vol_1h:,.2f} | Liquidity: ${liq:,.2f}")
                print(f"   • Txns: {buys} Buys / {sells} Sells ({ratio}x Pressure)")
                print(f"   • CA: {addr}")
                print("   • Chart: " + top.get("url", "N/A") + "\n" + "─" * 55)

    except Exception as e:
        print(f"Scanner exception: {e}")

if __name__ == "__main__":
    scan_dex_anomalies()
