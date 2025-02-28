from solana.rpc import api

try:
    from solana.rpc import api
    print("Successfully imported solana.rpc.api")
except ImportError as e:
    print(f"Error importing solana.rpc.api: {e}")