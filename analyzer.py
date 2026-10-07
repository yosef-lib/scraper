"""Logika sinyal. Inti 'Edge' dari produk.

Sinyal dihasilkan dari:
1. Perubahan harga ekstrem (Price Alert)
2. Lonjakan Volume (Whale Alert)
"""
from dataclasses import dataclass
import config
from sources import CoinPrice
import storage

@dataclass
class Signal:
    coin: str
    price: float
    change_24h: float
    volume_24h: float
    direction: str  # "naik" / "turun"
    magnitude: float
    is_alert: bool
    is_whale: bool

    def format_line(self) -> str:
        arrow = "dY"^" if self.direction == "naik" else "dY"%"
        base = (
            f"{arrow} {self.coin.upper()}: "
            f"{self.price:,.2f} {config.VS_CURRENCY.upper()} "
            f"({self.change_24h:+.2f}%)"
        )
        if self.is_whale:
            vol_m = self.volume_24h / 1_000_000
            return f"dYs" *WHALE DETECTED!*\n{base} | Vol: ${vol_m:,.1f}M"
        return base

def analyze(prices: list[CoinPrice]) -> list[Signal]:
    signals: list[Signal] = []
    
    for p in prices:
        direction = "naik" if p.change_24h >= 0 else "turun"
        magnitude = abs(p.change_24h)
        is_alert = magnitude >= config.ALERT_PERCENT
        
        # Logika Whale / Anomali Volume
        is_whale = False
        
        # Ambil history 2 jam terakhir (asumsi cron jalan per jam, limit 2)
        history = storage.get_price_history(p.coin, limit=2)
        if len(history) >= 2:
            prev_vol = history[-1]["volume_24h"]
            # Jika volume melonjak tajam dalam waktu singkat (contoh: naik > 20% tiba-tiba)
            # Karena 24h volume bergerak lambat, kalau ada lonjakan 5-10% dalam 1 jam itu masif.
            if prev_vol and prev_vol > 0:
                vol_change = (p.volume_24h - prev_vol) / prev_vol * 100
                if vol_change >= 5.0 and magnitude >= 2.0:
                    is_whale = True
                    is_alert = True # Otomatis jadi alert
                    
        # Fallback jika koin meme/kecil dan tiba-tiba volume tembus $100M
        if p.volume_24h > 100_000_000 and magnitude >= config.ALERT_PERCENT + 2:
            is_whale = True

        signals.append(
            Signal(
                coin=p.coin,
                price=p.price,
                change_24h=p.change_24h,
                volume_24h=p.volume_24h,
                direction=direction,
                magnitude=magnitude,
                is_alert=is_alert,
                is_whale=is_whale
            )
        )
    return signals

def only_alerts(signals: list[Signal]) -> list[Signal]:
    return [s for s in signals if s.is_alert]
