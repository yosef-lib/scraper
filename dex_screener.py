"""DEX Screener — Radar Meme Coin & Token Baru.

Mendeteksi koin baru/meme di jaringan Solana & Ethereum
yang volumenya meledak dalam waktu singkat.
Sumber data: DexScreener API (gratis, tanpa API key)
"""
import logging
import sys
import requests

import config
import notifier

log = logging.getLogger("dex_screener")

DEX_API = "https://api.dexscreener.com/latest/dex"

def get_trending_pairs(chain: str = "solana", min_vol_usd: float = 500_000) -> list[dict]:
    """Ambil pasangan trading yang sedang trending di chain tertentu."""
    try:
        url = f"{DEX_API}/search?q={chain}"
        resp = requests.get(url, timeout=15)
        data = resp.json()
        pairs = data.get("pairs", [])
        if not pairs:
            return []
        
        # Filter: chain yang diminta & volume cukup besar
        result = []
        seen = set()
        for p in pairs:
            if p.get("chainId", "").lower() != chain.lower():
                continue
            vol = float(p.get("volume", {}).get("h24", 0) or 0)
            if vol < min_vol_usd:
                continue
            symbol = p.get("baseToken", {}).get("symbol", "")
            if symbol in seen:
                continue
            seen.add(symbol)
            result.append(p)
            if len(result) >= 5:
                break
        return result
    except Exception as e:
        log.error(f"Error DexScreener: {e}")
        return []

def format_dex_alert(pair: dict) -> str:
    symbol   = pair.get("baseToken", {}).get("symbol", "?")
    name     = pair.get("baseToken", {}).get("name", "")
    price    = float(pair.get("priceUsd") or 0)
    change1h = float(pair.get("priceChange", {}).get("h1", 0) or 0)
    change6h = float(pair.get("priceChange", {}).get("h6", 0) or 0)
    vol24h   = float(pair.get("volume", {}).get("h24", 0) or 0)
    liq      = float(pair.get("liquidity", {}).get("usd", 0) or 0)
    url      = pair.get("url", "")

    arrow = "🚀" if change1h > 0 else "📉"
    vol_k = vol24h / 1000
    liq_k = liq / 1000

    return (
        f"{arrow} *{symbol}* ({name})\n"
        f"💲 Harga  : ${price:,.8f}\n"
        f"📊 1h     : {change1h:+.2f}%\n"
        f"📊 6h     : {change6h:+.2f}%\n"
        f"💧 Likuiditas : ${liq_k:,.0f}K\n"
        f"📦 Vol 24h : ${vol_k:,.0f}K\n"
        f"🔗 [Lihat Chart]({url})"
    )

def run_dex_radar(broadcast: bool = True) -> int:
    """Jalankan radar, kirim ke channel jika ada yang menarik."""
    channel_id = config._get("TELEGRAM_CHANNEL_ID", "")

    sol_pairs = get_trending_pairs("solana")
    eth_pairs = get_trending_pairs("ethereum")
    all_pairs = sol_pairs[:3] + eth_pairs[:2]

    if not all_pairs:
        log.info("Tidak ada koin meme yang lolos filter saat ini.")
        return 0

    header = (
        "🐕 *RADAR MEME COIN — SOLANA & ETH* 🐕\n\n"
        "Koin-koin di bawah ini sedang *trending* di pasar DEX. "
        "Volume meledak, likuiditas ada. *DYOR sebelum beli!*\n\n"
        "─────────────────────\n\n"
    )

    body = "\n\n─────────────────────\n\n".join(format_dex_alert(p) for p in all_pairs)

    footer = (
        "\n\n─────────────────────\n\n"
        "⚠️ *DISCLAIMER:* Meme coin sangat berisiko tinggi. "
        "Sinyal ini bukan anjuran investasi — hanya data pasar.\n\n"
        "🤖 Ingin sinyal *Entry + TP + SL* untuk koin ini?\n"
        "👉 Bank Mandiri: 1420019877454 a.n YOSEF PASKAH WAHYUTO"
    )

    msg = header + body + footer

    if broadcast and channel_id:
        notifier.send_message(channel_id, msg, parse_mode="Markdown", disable_web_page_preview=True)
        log.info(f"DEX Radar: {len(all_pairs)} koin dikirim ke channel.")
    
    return 0

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    sys.exit(run_dex_radar())
