from typing import Dict

# Pyth Network price feed addresses for mainnet
PRICE_FEEDS: Dict[str, str] = {
    # SOL/USD price feed
    'SOL_USD': 'H6ARHf6YXhGYeQfUzQNGk6rDNnLBQKrenN712K4AQJEG',
    # USDC/USD price feed
    'USDC_USD': 'Gnt27xtC473ZT2Mw5u8wZ68Z3gULkSTb5DuxJy7eJotD',
    # BTC/USD price feed
    'BTC_USD': 'GVXRSBjFk6e6J3NbVPXohDJetcTjaeeuykUpbQF8UoMU'
}

async def pyth_fetch_price(engine, price_feed_address: str) -> float:
    """Fetch price from Pyth Network price feed."""
    return await engine.pyth_fetch_price(price_feed_address)
