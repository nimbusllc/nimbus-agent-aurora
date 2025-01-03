from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from typing import Optional

# Token mint addresses
SOL_MINT = "So11111111111111111111111111111111111111111"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

async def trade(engine, from_token: str, to_token: str, amount: float) -> bool:
    """Execute a trade between two tokens."""
    return await engine.execute_trade(from_token, to_token, amount)

async def stake(engine, amount: float, duration: int) -> bool:
    """Stake assets for a specified duration."""
    return await engine.stake_assets(amount, duration)

async def lend_assets(engine, token: str, amount: float, duration: int) -> bool:
    """Lend assets for a specified duration."""
    return await engine.lend_assets(token, amount, duration)
