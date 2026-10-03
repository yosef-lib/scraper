"""Logika sinyal. Inilah inti 'produk' yang dijual.

Sinyal dihasilkan dari:
- perubahan harga 24 jam dibanding ambang (ALERT_PERCENT)
- arah (naik/turun) untuk label yang mudah dibaca
"""
from dataclasses import dataclass

import config
from sources import CoinPrice


@dataclass
class Signal:
    coin: str
    price: float
    change_24h: float
    direction: str  # "naik" / "turun"
    magnitude: float  # nilai absolut persen
    is_alert: bool  # True bila melewati ambang

    def format_line(self) -> str:
        arrow = "📈" if self.direction == "naik" else "📉"
        return (
            f"{arrow} {self.coin.upper()}: "
            f"{self.price:,.2f} {config.VS_CURRENCY.upper()} "
            f"({self.change_24h:+.2f}% / 24j)"
        )


def analyze(prices: list[CoinPrice]) -> list[Signal]:
    signals: list[Signal] = []
    for p in prices:
        direction = "naik" if p.change_24h >= 0 else "turun"
        magnitude = abs(p.change_24h)
        signals.append(
            Signal(
                coin=p.coin,
                price=p.price,
                change_24h=p.change_24h,
                direction=direction,
                magnitude=magnitude,
                is_alert=magnitude >= config.ALERT_PERCENT,
            )
        )
    return signals


def only_alerts(signals: list[Signal]) -> list[Signal]:
    return [s for s in signals if s.is_alert]
