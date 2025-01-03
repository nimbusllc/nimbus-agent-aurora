import unittest
import asyncio
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from pythclient.pythclient import PythClient
from aurora.core.blockchain_engine import AuroraEngine

class TestBlockchainSetup(unittest.TestCase):
    """Test cases for blockchain setup and basic functionality."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after each test."""
        self.loop.close()
    
    def test_solana_imports(self):
        """Test that Solana imports are working."""
        async def _test():
            client = AsyncClient("https://api.mainnet-beta.solana.com")
            keypair = Keypair()
            self.assertIsNotNone(client)
            self.assertIsNotNone(keypair)
            return True
        
        result = self.loop.run_until_complete(_test())
        self.assertTrue(result)
    
    def test_pyth_imports(self):
        """Test that Pyth Network imports are working."""
        async def _test():
            connection = AsyncClient("https://api.mainnet-beta.solana.com")
            pyth_client = PythClient(connection)
            self.assertIsNotNone(pyth_client)
            return True
            
        result = self.loop.run_until_complete(_test())
        self.assertTrue(result)
    
    def test_aurora_engine_init(self):
        """Test AuroraEngine initialization."""
        keypair = Keypair()
        engine = AuroraEngine(
            private_key=keypair.to_base58_string(),
            rpc_url="https://api.mainnet-beta.solana.com",
            openai_api_key="dummy-key-for-testing"
        )
        self.assertIsNotNone(engine)

if __name__ == '__main__':
    unittest.main()
