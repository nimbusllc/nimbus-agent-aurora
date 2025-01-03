from typing import Dict, List, Optional, Any
from base58 import b58decode
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from pythclient.pythclient import PythClient

class Constants:
    """Solana blockchain constants."""
    # Token mint addresses
    SOL_MINT = "So11111111111111111111111111111111111111111"
    USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    
    # Pyth price feed addresses
    PRICE_FEEDS = {
        "SOL/USD": "H6ARHf6YXhGYeQfUzQNGk6rDNnLBQKrenN712K4AQJEG",
        "USDC/USD": "Gnt27xtC473ZT2Mw5u8wZ68Z3gULkSTb5DuxJy7eJotD",
        "BTC/USD": "GVXRSBjFk6e6J3NbVPXohDJetcTjaeeuykUpbQF8UoMU"
    }

class AuroraEngine:
    def __init__(
        self,
        private_key: str,
        rpc_url: str,
        openai_api_key: str
    ):
        """Initialize Agent Aurora with provided authentication."""
        self.keypair = Keypair.from_bytes(b58decode(private_key))
        self.client = AsyncClient(rpc_url)
        self.pyth_client = PythClient(rpc_url)
        
    async def get_token_balance(self, token_mint: str) -> float:
        """Get token balance for the current wallet."""
        try:
            from spl.token.client import Token
            from solders.pubkey import Pubkey
            
            # Get token account
            token = Token(
                conn=self.client,
                pubkey=Pubkey.from_string(token_mint),
                program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
                payer=self.keypair
            )
            
            # Get token account owned by this wallet
            token_accounts = await token.get_accounts(owner=self.keypair.pubkey())
            if not token_accounts:
                return 0.0
                
            # Get balance of first account
            balance = await token.get_balance(token_accounts[0].pubkey)
            decimals = await token.get_mint_info()
            
            # Convert to float considering decimals
            return float(balance.ui_amount_float)
            
        except Exception as e:
            print(f"Failed to get token balance: {str(e)}")
            return 0.0
    
    async def execute_trade(
        self,
        from_token: str,
        to_token: str,
        amount: float
    ) -> bool:
        """Execute a trade between two tokens using Jupiter."""
        try:
            import aiohttp
            from solders.pubkey import Pubkey
            from solders.instruction import Instruction
            from solders.transaction import Transaction
            
            # Jupiter API endpoint for quote
            JUPITER_QUOTE_API = "https://quote-api.jup.ag/v6/quote"
            
            # Get quote from Jupiter
            params = {
                "inputMint": from_token,
                "outputMint": to_token,
                "amount": str(int(amount * 1e6)),  # Convert to smallest unit
                "slippageBps": 50  # 0.5% slippage
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(JUPITER_QUOTE_API, params=params) as response:
                    quote = await response.json()
                    
            # Get transaction data from Jupiter
            route_map = quote['routesInfos'][0]  # Get best route
            tx_data = {
                "route": route_map,
                "userPublicKey": str(self.keypair.pubkey())
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{JUPITER_QUOTE_API}/swap", json=tx_data) as response:
                    swap_data = await response.json()
            
            # Create and sign transaction
            tx = Transaction.from_json(swap_data['transaction'])
            tx.sign(self.keypair)
            
            # Send transaction
            tx_signature = await self.client.send_transaction(tx)
            await self.client.confirm_transaction(tx_signature)
            
            return True
            
        except Exception as e:
            print(f"Trade execution failed: {str(e)}")
            return False
    
    async def stake_assets(
        self,
        amount: float,
        duration: int
    ) -> bool:
        """Stake SOL tokens in a staking pool."""
        try:
            from solders.pubkey import Pubkey
            from solders.system_program import create_account, CreateAccountParams
            from solders.stake.program import create_stake, CreateStakeParams
            from solders.stake.state import Authorized, Lockup
            from solders.transaction import Transaction
            from solders.keypair import Keypair
            
            # Create stake account
            stake_account = Keypair.generate()
            stake_rent = await self.client.get_minimum_balance_for_rent_exemption(
                200  # Stake account size
            )
            
            # Build transaction
            tx = Transaction()
            
            # Add create account instruction
            tx.add(
                create_account(
                    CreateAccountParams(
                        from_pubkey=self.keypair.pubkey(),
                        to_pubkey=stake_account.pubkey(),
                        lamports=stake_rent + int(amount * 1e9),  # Convert SOL to lamports
                        space=200,
                        owner=Pubkey.from_string("Stake11111111111111111111111111111111111111")
                    )
                )
            )
            
            # Add initialize stake instruction
            tx.add(
                create_stake(
                    CreateStakeParams(
                        stake_pubkey=stake_account.pubkey(),
                        authorized=Authorized(
                            staker=self.keypair.pubkey(),
                            withdrawer=self.keypair.pubkey()
                        ),
                        lockup=Lockup(
                            unix_timestamp=0,  # No lockup
                            epoch=0,
                            custodian=Pubkey.default()
                        )
                    )
                )
            )
            
            # Sign and send transaction
            tx.sign(self.keypair, stake_account)
            tx_signature = await self.client.send_transaction(tx)
            await self.client.confirm_transaction(tx_signature)
            
            return True
            
        except Exception as e:
            print(f"Staking failed: {str(e)}")
            return False
    
    async def lend_assets(
        self,
        token: str,
        amount: float,
        duration: int
    ) -> bool:
        """Lend assets using Solend protocol."""
        try:
            from solders.pubkey import Pubkey
            from solders.instruction import Instruction
            from solders.transaction import Transaction
            from spl.token.client import Token
            
            # Solend program ID
            SOLEND_PROGRAM_ID = Pubkey.from_string("So1endDq2YkqhipRh3WViPa8hdiSpxWy6z3Z6tMCpAo")
            
            # Get lending pool for token
            pool_address = await self._get_lending_pool(token)
            if not pool_address:
                raise ValueError(f"No lending pool found for token {token}")
                
            # Create deposit instruction
            deposit_ix = Instruction(
                program_id=SOLEND_PROGRAM_ID,
                accounts=[
                    {"pubkey": pool_address, "is_signer": False, "is_writable": True},
                    {"pubkey": self.keypair.pubkey(), "is_signer": True, "is_writable": False},
                    {"pubkey": Pubkey.from_string(token), "is_signer": False, "is_writable": True}
                ],
                data=bytes([1, *int(amount * 1e6).to_bytes(8, 'little')])  # Deposit instruction
            )
            
            # Create transaction
            tx = Transaction()
            tx.add(deposit_ix)
            
            # Sign and send transaction
            tx.sign(self.keypair)
            tx_signature = await self.client.send_transaction(tx)
            await self.client.confirm_transaction(tx_signature)
            
            return True
            
        except Exception as e:
            print(f"Lending failed: {str(e)}")
            return False
            
    async def _get_lending_pool(self, token: str) -> Optional[Pubkey]:
        """Helper method to find Solend lending pool for a token."""
        # Mapping of known Solend pools (would be fetched from API in production)
        POOLS = {
            Constants.SOL_MINT: "8PbodeaosQP19SjYFqr1VfQgWGKhdqdEyMk3blk3wzc7",
            Constants.USDC_MINT: "BgxfHJDzm44T7XG68MYKx7YisTjZu73tVovyZSjJMpmw"
        }
        return Pubkey.from_string(POOLS.get(token)) if token in POOLS else None
    
    # Smart contract deployment and management functions will be implemented here
    # These functions will handle:
    # - Contract deployment
    # - Contract validation
    # - Scheduled deployments
    # - Contract customization
    
    async def pyth_fetch_price(
        self,
        symbol: str
    ) -> Optional[float]:
        """Fetch price from Pyth Network price feed."""
        try:
            price_feed_address = Constants.PRICE_FEEDS.get(symbol)
            if not price_feed_address:
                raise ValueError(f"No price feed found for {symbol}")
            
            price_data = await self.pyth_client.get_price_feed(price_feed_address)
            if not price_data:
                return None
                
            return float(price_data.aggregate_price)
        except Exception as e:
            print(f"Failed to fetch price: {str(e)}")
            return None
