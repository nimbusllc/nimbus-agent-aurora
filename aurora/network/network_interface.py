import asyncio
from typing import Dict, Optional
from ..core.blockchain_engine import AuroraEngine
from ..core.blockchain_config import validate_env

async def main():
    """Main CLI entry point."""
    try:
        env = validate_env()
        engine = AuroraEngine(
            env['WALLET_PRIVATE_KEY'],
            env['BLOCKCHAIN_RPC_URL'],
            env['OPENAI_API_KEY']
        )
        
        # CLI setup
        print("Agent Aurora ready for operation")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
