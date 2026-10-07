"""Sumber data harga.

Fetch dari CoinGecko, sekarang termasuk volume 24 jam untuk deteksi whale/anomali.
"""
from dataclasses import dataclass
from typing import Iterable
import requests
import config

@dataclass
class CoinPrice:
    coin: str
    price: float
    change_24h: float
    volume_24h: float
    currency: str

def fetch_prices(coins: Iterable[str] | None = None) -> list[CoinPrice]:
    coins = list(coins) if coins else config.COINS
    if not coins:
        return []

    url = f"{config.COINGECKO_API}/simple/price"
    params = {
        "ids": ",".join(coins),
        "vs_currencies": config.VS_CURRENCY,
        "include_24hr_change": "true",
        "include_24hr_vol": "true",
    }
    headers = {"User-Agent": "vps-money-machine/2.0"}

    resp = requests.get(url, params=params, headers=headers, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    result: list[CoinPrice] = []
    for coin in coins:
        entry = data.get(coin)
        if not entry:
            continue
        price = entry.get(config.VS_CURRENCY)
        change = entry.get(f"{config.VS_CURRENCY}_24h_change")
        volume = entry.get(f"{config.VS_CURRENCY}_24h_vol")
        
        if price is None:
            continue
            
        result.append(
            CoinPrice(
                coin=coin,
                price=float(price),
                change_24h=float(change) if change is not None else 0.0,
                volume_24h=float(volume) if volume is not None else 0.0,
                currency=config.VS_CURRENCY,
            )
        )
    return result
