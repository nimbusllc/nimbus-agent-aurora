from os import environ
from dotenv import load_dotenv

def validate_env():
    """Validate required environment variables are set."""
    load_dotenv()
    
    required_vars = [
        'OPENAI_API_KEY',
        'BLOCKCHAIN_RPC_URL',
        'WALLET_PRIVATE_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not environ.get(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return {var: environ[var] for var in required_vars}
