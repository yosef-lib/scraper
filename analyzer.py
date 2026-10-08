"""Logika sinyal. Inti 'Edge' dari produk.

Sinyal dihasilkan dari:
1. Perubahan harga ekstrem (Price Alert)
2. Lonjakan Volume (Smart Money Alert)
3. Kalkulasi Entry/TP/SL otomatis (Copy Trade Signal)
"""
from dataclasses import dataclass, field
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
    # Copy Trade fields
    entry_low: float = 0.0
    entry_high: float = 0.0
    target1: float = 0.0
    target2: float = 0.0
    stop_loss: float = 0.0
    confidence: int = 0  # 0-100

    def format_line(self) -> str:
        arrow = "🚀" if self.direction == "naik" else "📉"
        base = (
            f"{arrow} {self.coin.upper()}: "
            f"{self.price:,.4f} {config.VS_CURRENCY.upper()} "
            f"({self.change_24h:+.2f}%)"
        )
        if self.is_whale:
            vol_m = self.volume_24h / 1_000_000
            return f"🚨 *SMART MONEY DETECTED!*\n{base} | Vol: ${vol_m:,.1f}M"
        return base

    def format_copy_trade(self) -> str:
        """Format pesan sinyal Copy Trade bergaya profesional."""
        if self.confidence == 0:
            return self.format_line()

        action = "BUY 🟢" if self.direction == "naik" else "SELL 🔴"
        stars = "⭐" * min(5, max(1, self.confidence // 20))
        vol_m = self.volume_24h / 1_000_000 if self.volume_24h else 0

        msg = (
            f"🚨 *SINYAL MASUK — {self.coin.upper()}*\n\n"
            f"🏷️ AKSI      : {action}\n"
            f"💰 ENTRY     : ${self.entry_low:,.4f} — ${self.entry_high:,.4f}\n"
            f"🎯 TARGET 1  : ${self.target1:,.4f} (+{((self.target1/self.price)-1)*100:.1f}%)\n"
            f"🎯 TARGET 2  : ${self.target2:,.4f} (+{((self.target2/self.price)-1)*100:.1f}%)\n"
            f"🛑 STOP LOSS : ${self.stop_loss:,.4f} (-{((self.price/self.stop_loss)-1)*100:.1f}%)\n\n"
            f"📊 Vol 24j   : ${vol_m:,.1f}M\n"
            f"💡 Kekuatan  : {stars}\n"
            f"🤖 AI Confidence : {self.confidence}%\n\n"
            f"⚡ _Sinyal ini dibuat secara otomatis oleh AI Whale Radar_"
        )
        return msg


def _calc_copy_trade(price: float, direction: str, magnitude: float, volume_24h: float) -> dict:
    """Menghitung parameter Entry, TP, SL secara otomatis."""
    if direction == "naik":
        entry_low  = price * 0.995   # Beli sedikit di bawah harga sekarang
        entry_high = price * 1.005   # Atau sedikit di atas (breakout)
        target1    = price * 1.05    # Target konservatif +5%
        target2    = price * 1.12    # Target agresif +12%
        stop_loss  = price * 0.96    # Batas rugi -4%
    else:
        entry_low  = price * 0.995
        entry_high = price * 1.005
        target1    = price * 0.95    # Untuk short, target di bawah
        target2    = price * 0.88
        stop_loss  = price * 1.04

    # Hitung confidence berdasarkan magnitude & volume
    vol_score = min(40, int(volume_24h / 10_000_000))  # Max 40 poin dari volume
    mag_score = min(40, int(magnitude * 5))             # Max 40 poin dari magnitude
    base_score = 20                                      # Base 20 poin
    confidence = min(95, base_score + vol_score + mag_score)

    return {
        "entry_low": entry_low,
        "entry_high": entry_high,
        "target1": target1,
        "target2": target2,
        "stop_loss": stop_loss,
        "confidence": confidence,
    }


def analyze(prices: list[CoinPrice]) -> list[Signal]:
    signals: list[Signal] = []
    
    for p in prices:
        direction = "naik" if p.change_24h >= 0 else "turun"
        magnitude = abs(p.change_24h)
        is_alert = magnitude >= config.ALERT_PERCENT
        
        is_whale = False
        history = storage.get_price_history(p.coin, limit=2)
        if len(history) >= 2:
            prev_vol = history[-1]["volume_24h"]
            if prev_vol and prev_vol > 0:
                vol_change = (p.volume_24h - prev_vol) / prev_vol * 100
                if vol_change >= 5.0 and magnitude >= 2.0:
                    is_whale = True
                    is_alert = True
                    
        if p.volume_24h > 100_000_000 and magnitude >= config.ALERT_PERCENT + 2:
            is_whale = True

        # Hitung Copy Trade Signal untuk semua alert
        ct = {}
        if is_alert or is_whale:
            ct = _calc_copy_trade(p.price, direction, magnitude, p.volume_24h)

        signals.append(
            Signal(
                coin=p.coin,
                price=p.price,
                change_24h=p.change_24h,
                volume_24h=p.volume_24h,
                direction=direction,
                magnitude=magnitude,
                is_alert=is_alert,
                is_whale=is_whale,
                entry_low=ct.get("entry_low", 0),
                entry_high=ct.get("entry_high", 0),
                target1=ct.get("target1", 0),
                target2=ct.get("target2", 0),
                stop_loss=ct.get("stop_loss", 0),
                confidence=ct.get("confidence", 0),
            )
        )
    return signals

def only_alerts(signals: list[Signal]) -> list[Signal]:
    return [s for s in signals if s.is_alert]
