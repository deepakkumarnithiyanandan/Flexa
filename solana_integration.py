from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.keypair import Keypair
from solana.publickey import PublicKey
from anchorpy import Program, Provider, Wallet
import json
import base58
import os
from pathlib import Path

class SolanaIntegration:
    def __init__(self, network="devnet"):
        self.client = AsyncClient(f"https://api.{network}.solana.com")
        self.program_id = PublicKey("YOUR_PROGRAM_ID")  # Replace with your deployed program ID
        
    async def setup_provider(self, keypair):
        wallet = Wallet(keypair)
        provider = Provider(self.client, wallet)
        program = Program(self.idl, self.program_id, provider)
        return provider, program

    async def store_json_data(self, file_path: str, keypair: Keypair):
        """Store JSON data on Solana blockchain"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Convert data to string and then to bytes
            data_bytes = json.dumps(data).encode('utf-8')
            
            # Create account to store data
            space = len(data_bytes)
            lamports = await self.client.get_minimum_balance_for_rent_exemption(space)
            
            new_account = Keypair()
            transaction = Transaction()
            
            # Create account and store data
            create_account_ix = self.program.accounts["DataAccount"].create_instruction(
                payer=keypair.public_key,
                space=space
            )
            
            store_data_ix = self.program.instruction["store_data"](
                data_bytes,
                accounts={
                    "data_account": new_account.public_key,
                    "authority": keypair.public_key,
                }
            )
            
            transaction.add(create_account_ix)
            transaction.add(store_data_ix)
            
            # Send and confirm transaction
            result = await self.client.send_and_confirm_transaction(
                transaction,
                [keypair, new_account]
            )
            
            return {
                "success": True,
                "signature": result["result"],
                "account": str(new_account.public_key)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def retrieve_json_data(self, account_pubkey: str):
        """Retrieve JSON data from Solana blockchain"""
        try:
            account_data = await self.client.get_account_info(PublicKey(account_pubkey))
            data = json.loads(account_data["result"]["value"]["data"][0].decode('utf-8'))
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def process_sol_payment(self, sender_keypair: Keypair, receiver_pubkey: str, amount_sol: float):
        """Process SOL payment between users"""
        try:
            amount_lamports = int(amount_sol * 10**9)  # Convert SOL to lamports
            
            transaction = Transaction()
            transfer_ix = transfer(
                TransferParams(
                    from_pubkey=sender_keypair.public_key,
                    to_pubkey=PublicKey(receiver_pubkey),
                    lamports=amount_lamports
                )
            )
            
            transaction.add(transfer_ix)
            
            # Send and confirm transaction
            result = await self.client.send_and_confirm_transaction(
                transaction,
                [sender_keypair]
            )
            
            return {
                "success": True,
                "signature": result["result"],
                "amount": amount_sol,
                "receiver": receiver_pubkey
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def sync_database_to_chain(self):
        """Sync all JSON files from ./database to Solana blockchain"""
        results = []
        database_path = Path("./database")
        
        if not database_path.exists():
            return {"success": False, "error": "Database directory not found"}
            
        for file_path in database_path.glob("*.json"):
            result = await self.store_json_data(str(file_path), self.keypair)
            results.append({
                "file": file_path.name,
                "result": result
            })
            
        return {"success": True, "results": results}

# Smart Contract for Bill Splitting
class BillSplitContract:
    def __init__(self, program_id: str):
        self.program_id = PublicKey(program_id)
        
    async def create_bill(self, bill_data: dict, payer_keypair: Keypair):
        """Create a new bill on-chain"""
        try:
            # Initialize bill account
            bill_account = Keypair()
            
            # Create transaction for bill creation
            transaction = Transaction()
            create_bill_ix = self.program.instruction["create_bill"](
                {
                    "total_amount": bill_data["total_amount"],
                    "split_type": bill_data["split_type"],
                    "participants": bill_data["participants"]
                },
                accounts={
                    "bill_account": bill_account.public_key,
                    "payer": payer_keypair.public_key,
                }
            )
            
            transaction.add(create_bill_ix)
            
            # Send and confirm transaction
            result = await self.client.send_and_confirm_transaction(
                transaction,
                [payer_keypair, bill_account]
            )
            
            return {
                "success": True,
                "bill_account": str(bill_account.public_key),
                "signature": result["result"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def pay_share(self, bill_account: str, payer_keypair: Keypair, amount: float):
        """Pay share of a bill"""
        try:
            amount_lamports = int(amount * 10**9)
            
            transaction = Transaction()
            pay_share_ix = self.program.instruction["pay_share"](
                amount_lamports,
                accounts={
                    "bill_account": PublicKey(bill_account),
                    "payer": payer_keypair.public_key,
                }
            )
            
            transaction.add(pay_share_ix)
            
            result = await self.client.send_and_confirm_transaction(
                transaction,
                [payer_keypair]
            )
            
            return {
                "success": True,
                "signature": result["result"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}