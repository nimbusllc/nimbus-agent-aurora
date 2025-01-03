from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from pythclient.pythclient import PythClient
import asyncio

async def test_imports():
    """Test that all required imports are working."""
    try:
        # Test Solana imports
        client = AsyncClient("https://api.mainnet-beta.solana.com")
        keypair = Keypair()
        print("Solana imports successful")
        
        # Test Pyth Network imports
        pyth_client = PythClient("https://api.mainnet-beta.solana.com")
        print("Pyth Network imports successful")
        
        return True
    except Exception as e:
        print(f"Import test failed: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_imports())
