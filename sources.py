"""Sumber data harga. Default: CoinGecko API publik (gratis, tanpa API key).

Fungsi utama: fetch_prices(coins) -> list[CoinPrice]
Untuk menambah sumber lain (saham, marketplace, dll), buat fungsi fetch_*
baru dan petakan ke CoinPrice.
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
    }
    headers = {"User-Agent": "vps-money-machine/1.0"}

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
        if price is None:
            continue
        result.append(
            CoinPrice(
                coin=coin,
                price=float(price),
                change_24h=float(change) if change is not None else 0.0,
                currency=config.VS_CURRENCY,
            )
        )
    return result


def fetch_market_chart(coin: str, days: int = 1) -> list[tuple[int, float]]:
    """Riwayat harga (timestamp_ms, price) untuk indikator sederhana."""
    url = f"{config.COINGECKO_API}/coins/{coin}/market_chart"
    params = {"vs_currency": config.VS_CURRENCY, "days": days}
    resp = requests.get(url, params=params, timeout=20, headers={"User-Agent": "vps-money-machine/1.0"})
    resp.raise_for_status()
    return resp.json().get("prices", [])
