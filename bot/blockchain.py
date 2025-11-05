"""Blockchain utilities for Solana/Anchor integration."""

import json
import os
import time
import hashlib
from typing import Optional, Dict, Any

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.hash import Hash
from solders.signature import Signature
import base58


PROGRAM_ID_STR = "FTV1kbDLaeVM4LG4vHrVu2qdt2cXazYTXWWUi1xFAJdK"
PROGRAM_ID = Pubkey.from_string(PROGRAM_ID_STR)
LAMPORTS_PER_SOL = 1_000_000_000


def compute_anchor_discriminator(instruction_name: str) -> bytes:
    """
    Compute Anchor instruction discriminator.
    
    Anchor uses the first 8 bytes of sha256("global:<instruction_name>")
    where instruction_name is in snake_case.
    """
    preimage = f"global:{instruction_name}".encode('utf-8')
    hash_digest = hashlib.sha256(preimage).digest()
    return hash_digest[:8]


# Precompute discriminators for common instructions
DISCRIMINATOR_PLACE_BET = compute_anchor_discriminator("place_bet")
DISCRIMINATOR_CLAIM_PAYOUT = compute_anchor_discriminator("claim_payout")
DISCRIMINATOR_CANCEL_BET = compute_anchor_discriminator("cancel_bet")
DISCRIMINATOR_CLOSE_BET = compute_anchor_discriminator("close_bet")


def get_config_pda() -> Pubkey:
    """Derive the config PDA."""
    seeds = [b"config"]
    pda, _ = Pubkey.find_program_address(seeds, PROGRAM_ID)
    return pda


def get_treasury_pda() -> Pubkey:
    """Derive the treasury PDA."""
    seeds = [b"treasury"]
    pda, _ = Pubkey.find_program_address(seeds, PROGRAM_ID)
    return pda


def get_round_pda(round_number: int) -> Pubkey:
    """Derive the round PDA for a given round number."""
    round_bytes = round_number.to_bytes(8, byteorder='little')
    seeds = [b"round", round_bytes]
    pda, _ = Pubkey.find_program_address(seeds, PROGRAM_ID)
    return pda


def get_user_bet_pda(user: Pubkey, round_number: int) -> Pubkey:
    """Derive the user bet PDA."""
    round_bytes = round_number.to_bytes(8, byteorder='little')
    seeds = [b"user_bet", bytes(user), round_bytes]
    pda, _ = Pubkey.find_program_address(seeds, PROGRAM_ID)
    return pda


def create_keypair_from_private_key(private_key: str) -> Keypair:
    """
    Create a Keypair from a private key in various formats.
    
    Supports:
    - Base58 encoded string
    - JSON array string "[1,2,3,...,64]"
    - Comma-separated string "1,2,3,...,64"
    """
    try:
        private_key = private_key.strip()
        
        # Check if JSON array format
        if private_key.startswith('[') and private_key.endswith(']'):
            secret_key = json.loads(private_key)
            if isinstance(secret_key, list) and len(secret_key) == 64:
                return Keypair.from_bytes(bytes(secret_key))
            raise ValueError('Invalid array format: must be 64 bytes')
        
        # Check if comma-separated format
        if ',' in private_key:
            secret_key = [int(x.strip()) for x in private_key.split(',')]
            if len(secret_key) == 64:
                return Keypair.from_bytes(bytes(secret_key))
            raise ValueError('Invalid comma-separated format: must be 64 bytes')
        
        # Otherwise treat as base58
        return Keypair.from_bytes(base58.b58decode(private_key))
    
    except Exception as e:
        raise ValueError(f"Failed to create keypair from private key: {e}")


async def get_config(client: AsyncClient) -> Optional[Dict[str, Any]]:
    """Fetch the config account from the blockchain."""
    try:
        config_pda = get_config_pda()
        response = await client.get_account_info(config_pda, commitment=Confirmed)
        
        if not response.value or not response.value.data:
            return None
        
        data = bytes(response.value.data)
        
        # Parse config account (simplified - in production use Anchor's IDL parser)
        # Config structure: operatorMultisig(32) + adminMultisig(32) + executor(32) + 
        #                   minBetAmount(8) + lockDuration(8) + currentRound(8) + 
        #                   isPaused(1) + bufferSeconds(8) + ...
        
        if len(data) < 8 + 32 + 32 + 32 + 8 + 8 + 8:
            return None
        
        # Skip the 8-byte discriminator
        offset = 8
        
        # Skip multisigs and executor (32 + 32 + 32 = 96 bytes)
        offset += 96
        
        # minBetAmount (8 bytes, u64 little-endian)
        min_bet_amount = int.from_bytes(data[offset:offset+8], byteorder='little')
        offset += 8
        
        # lockDuration (8 bytes, u64 little-endian)
        lock_duration = int.from_bytes(data[offset:offset+8], byteorder='little')
        offset += 8
        
        # currentRound (8 bytes, u64 little-endian)
        current_round = int.from_bytes(data[offset:offset+8], byteorder='little')
        offset += 8
        
        # isPaused (1 byte, bool)
        is_paused = data[offset] != 0
        offset += 1
        
        # bufferSeconds (8 bytes, u64 little-endian)
        buffer_seconds = int.from_bytes(data[offset:offset+8], byteorder='little')
        
        return {
            'minBetAmount': min_bet_amount,
            'lockDuration': lock_duration,
            'currentRound': current_round,
            'isPaused': is_paused,
            'bufferSeconds': buffer_seconds
        }
    
    except Exception:
        return None


async def get_round(client: AsyncClient, round_number: int) -> Optional[Dict[str, Any]]:
    """Fetch round account from the blockchain."""
    try:
        round_pda = get_round_pda(round_number)
        response = await client.get_account_info(round_pda, commitment=Confirmed)
        
        if not response.value or not response.value.data:
            return None
        
        data = bytes(response.value.data)
        
        # Parse round account (simplified)
        # Round structure: number(8) + startTime(8) + lockTime(8) + closeTime(8) +
        #                 lockPrice(8) + endPrice(8) + isActive(1) + 
        #                 totalBullAmount(8) + totalBearAmount(8) + totalAmount(8) + ...
        
        if len(data) < 8 + 8*10 + 1:
            return None
        
        offset = 8  # Skip discriminator
        
        number = int.from_bytes(data[offset:offset+8], byteorder='little')
        offset += 8
        
        start_time = int.from_bytes(data[offset:offset+8], byteorder='little', signed=True)
        offset += 8
        
        lock_time = int.from_bytes(data[offset:offset+8], byteorder='little', signed=True)
        offset += 8
        
        close_time = int.from_bytes(data[offset:offset+8], byteorder='little', signed=True)
        offset += 8
        
        lock_price = int.from_bytes(data[offset:offset+8], byteorder='little')
        offset += 8
        
        end_price = int.from_bytes(data[offset:offset+8], byteorder='little')
        offset += 8
        
        is_active = data[offset] != 0
        offset += 1
        
        total_bull_amount = int.from_bytes(data[offset:offset+8], byteorder='little')
        offset += 8
        
        total_bear_amount = int.from_bytes(data[offset:offset+8], byteorder='little')
        offset += 8
        
        total_amount = int.from_bytes(data[offset:offset+8], byteorder='little')
        offset += 8
        
        # Skip rewardBaseCalAmount
        offset += 8
        
        reward_amount = int.from_bytes(data[offset:offset+8], byteorder='little')
        offset += 8
        
        # Skip counts
        offset += 8 * 3  # totalBullCount, totalBearCount, claimedCount
        
        status = data[offset]
        
        return {
            'number': number,
            'startTime': start_time,
            'lockTime': lock_time,
            'closeTime': close_time,
            'lockPrice': lock_price,
            'endPrice': end_price,
            'isActive': is_active,
            'totalBullAmount': total_bull_amount,
            'totalBearAmount': total_bear_amount,
            'totalAmount': total_amount,
            'rewardAmount': reward_amount,
            'status': status
        }
    
    except Exception:
        return None


async def get_bet(client: AsyncClient, user: Pubkey, round_number: int) -> Optional[Dict[str, Any]]:
    """Fetch user bet account from the blockchain."""
    try:
        bet_pda = get_user_bet_pda(user, round_number)
        response = await client.get_account_info(bet_pda, commitment=Confirmed)
        
        if not response.value or not response.value.data:
            return None
        
        data = bytes(response.value.data)
        
        # Parse UserBet: user(32) + roundNumber(8) + amount(8) + predictBull(1) + claimed(1)
        if len(data) < 8 + 32 + 8 + 8 + 1 + 1:
            return None
        
        offset = 8  # Skip discriminator
        
        # Skip user pubkey (32 bytes)
        offset += 32
        
        round_num = int.from_bytes(data[offset:offset+8], byteorder='little')
        offset += 8
        
        amount = int.from_bytes(data[offset:offset+8], byteorder='little')
        offset += 8
        
        predict_bull = data[offset] != 0
        offset += 1
        
        claimed = data[offset] != 0
        
        return {
            'roundNumber': round_num,
            'amount': amount,
            'predictBull': predict_bull,
            'claimed': claimed
        }
    
    except Exception:
        return None


async def get_balance(client: AsyncClient, pubkey: Pubkey) -> float:
    """Get SOL balance of a wallet."""
    try:
        response = await client.get_balance(pubkey, commitment=Confirmed)
        return response.value / LAMPORTS_PER_SOL
    except Exception:
        return 0.0


def get_current_time() -> int:
    """Get current Unix timestamp."""
    return int(time.time())


async def place_bet(
    client: AsyncClient,
    payer: Keypair,
    round_id: int,
    direction: bool,
    amount: float
) -> Optional[str]:
    """
    Place a bet on a round.
    
    Args:
        client: Solana RPC client
        payer: User's keypair
        round_id: Round number to bet on
        direction: True for UP/Bull, False for DOWN/Bear
        amount: Bet amount in SOL
        
    Returns:
        Transaction signature if successful, None otherwise
    """
    try:
        config_pda = get_config_pda()
        round_pda = get_round_pda(round_id)
        user_bet_pda = get_user_bet_pda(payer.pubkey(), round_id)
        treasury_pda = get_treasury_pda()
        
        # Check if bet already exists (return special marker instead of None)
        existing_bet = await get_bet(client, payer.pubkey(), round_id)
        if existing_bet:
            return "ALREADY_PLACED"  # Special marker to indicate bet already exists
        
        # Build placeBet instruction
        # Instruction data: [method_discriminator(8), amount(8), predictBull(1), roundNumber(8)]
        
        amount_lamports = int(amount * LAMPORTS_PER_SOL)
        
        # Build instruction data with proper Anchor discriminator
        instruction_data = bytearray()
        instruction_data.extend(DISCRIMINATOR_PLACE_BET)  # 8 bytes
        instruction_data.extend(amount_lamports.to_bytes(8, byteorder='little'))  # u64
        instruction_data.extend(b'\x01' if direction else b'\x00')  # bool
        instruction_data.extend(round_id.to_bytes(8, byteorder='little'))  # u64
        
        accounts = [
            AccountMeta(config_pda, is_signer=False, is_writable=False),
            AccountMeta(round_pda, is_signer=False, is_writable=True),
            AccountMeta(user_bet_pda, is_signer=False, is_writable=True),
            AccountMeta(payer.pubkey(), is_signer=True, is_writable=True),
            AccountMeta(treasury_pda, is_signer=False, is_writable=True),
            AccountMeta(SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        ]
        
        instruction = Instruction(PROGRAM_ID, bytes(instruction_data), accounts)
        
        # Build and send transaction using MessageV0
        recent_blockhash_resp = await client.get_latest_blockhash(commitment=Confirmed)
        recent_blockhash = recent_blockhash_resp.value.blockhash
        
        # Create message
        message = MessageV0.try_compile(
            payer.pubkey(),
            [instruction],
            [],  # address lookup tables
            recent_blockhash
        )
        
        # Create versioned transaction
        tx = VersionedTransaction(message, [payer])
        
        # Send transaction
        opts = TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
        result = await client.send_transaction(tx, opts=opts)
        
        signature = str(result.value)
        print(f"✅ Transaction sent with signature: {signature}")
        
        # Try to confirm transaction (but don't fail if confirmation times out)
        try:
            sig_obj = Signature.from_string(signature)
            await client.confirm_transaction(sig_obj, commitment=Confirmed)
            print(f"✅ Transaction confirmed: {signature}")
        except Exception as confirm_error:
            # Transaction was sent successfully, just confirmation failed
            # This is OK - the transaction is likely processing
            print(f"⚠️ Confirmation timeout (transaction likely still processing): {confirm_error}")
        
        return signature
    
    except Exception as e:
        import traceback
        error_msg = f"Error placing bet: {type(e).__name__}: {str(e)}"
        print(error_msg)
        print("Full traceback:")
        print(traceback.format_exc())
        
        # Check for specific error types
        if hasattr(e, 'args') and len(e.args) > 0:
            print(f"Error details: {e.args}")
        
        return None


async def claim_payout(
    client: AsyncClient,
    payer: Keypair,
    round_id: int
) -> Optional[str]:
    """Claim payout for a winning bet."""
    try:
        config_pda = get_config_pda()
        round_pda = get_round_pda(round_id)
        user_bet_pda = get_user_bet_pda(payer.pubkey(), round_id)
        treasury_pda = get_treasury_pda()
        
        # Build claimPayout instruction
        instruction_data = bytearray()
        instruction_data.extend(DISCRIMINATOR_CLAIM_PAYOUT)  # 8 bytes
        instruction_data.extend(round_id.to_bytes(8, byteorder='little'))  # u64
        
        accounts = [
            AccountMeta(config_pda, is_signer=False, is_writable=True),
            AccountMeta(round_pda, is_signer=False, is_writable=True),
            AccountMeta(user_bet_pda, is_signer=False, is_writable=True),
            AccountMeta(payer.pubkey(), is_signer=True, is_writable=True),
            AccountMeta(treasury_pda, is_signer=False, is_writable=True),
        ]
        
        instruction = Instruction(PROGRAM_ID, bytes(instruction_data), accounts)
        
        recent_blockhash_resp = await client.get_latest_blockhash(commitment=Confirmed)
        recent_blockhash = recent_blockhash_resp.value.blockhash
        
        message = MessageV0.try_compile(
            payer.pubkey(),
            [instruction],
            [],
            recent_blockhash
        )
        
        tx = VersionedTransaction(message, [payer])
        
        opts = TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
        result = await client.send_transaction(tx, opts=opts)
        signature = str(result.value)
        
        # Convert string signature to Signature object for confirmation
        try:
            sig_obj = Signature.from_string(signature)
            await client.confirm_transaction(sig_obj, commitment=Confirmed)
        except TimeoutError:
            print(f"Confirmation timeout (transaction likely still processing): {signature}")
        except Exception as confirm_err:
            print(f"Confirmation error (transaction may still succeed): {confirm_err}")
        
        return signature
    
    except Exception as e:
        print(f"Error claiming payout: {e}")
        import traceback
        traceback.print_exc()
        return None


async def cancel_bet(
    client: AsyncClient,
    payer: Keypair,
    round_id: int
) -> Optional[str]:
    """Cancel a bet from a cancelled round."""
    try:
        config_pda = get_config_pda()
        round_pda = get_round_pda(round_id)
        user_bet_pda = get_user_bet_pda(payer.pubkey(), round_id)
        treasury_pda = get_treasury_pda()
        
        instruction_data = bytearray()
        instruction_data.extend(DISCRIMINATOR_CANCEL_BET)  # 8 bytes
        instruction_data.extend(round_id.to_bytes(8, byteorder='little'))  # u64
        
        accounts = [
            AccountMeta(config_pda, is_signer=False, is_writable=False),
            AccountMeta(round_pda, is_signer=False, is_writable=True),
            AccountMeta(user_bet_pda, is_signer=False, is_writable=True),
            AccountMeta(payer.pubkey(), is_signer=True, is_writable=True),
            AccountMeta(treasury_pda, is_signer=False, is_writable=True),
        ]
        
        instruction = Instruction(PROGRAM_ID, bytes(instruction_data), accounts)
        
        recent_blockhash_resp = await client.get_latest_blockhash(commitment=Confirmed)
        recent_blockhash = recent_blockhash_resp.value.blockhash
        
        message = MessageV0.try_compile(
            payer.pubkey(),
            [instruction],
            [],
            recent_blockhash
        )
        
        tx = VersionedTransaction(message, [payer])
        
        opts = TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
        result = await client.send_transaction(tx, opts=opts)
        signature = str(result.value)
        
        # Convert string signature to Signature object for confirmation
        try:
            sig_obj = Signature.from_string(signature)
            await client.confirm_transaction(sig_obj, commitment=Confirmed)
        except TimeoutError:
            print(f"Confirmation timeout (transaction likely still processing): {signature}")
        except Exception as confirm_err:
            print(f"Confirmation error (transaction may still succeed): {confirm_err}")
        
        return signature
    
    except Exception as e:
        import traceback
        print(f"Error canceling bet: {type(e).__name__}: {e}")
        print(traceback.format_exc())
        return None


async def close_bet(
    client: AsyncClient,
    payer: Keypair,
    round_id: int
) -> Optional[str]:
    """Close a completed bet to reclaim rent."""
    try:
        round_pda = get_round_pda(round_id)
        user_bet_pda = get_user_bet_pda(payer.pubkey(), round_id)
        
        instruction_data = bytearray()
        instruction_data.extend(DISCRIMINATOR_CLOSE_BET)  # 8 bytes
        instruction_data.extend(round_id.to_bytes(8, byteorder='little'))  # u64
        
        accounts = [
            AccountMeta(user_bet_pda, is_signer=False, is_writable=True),
            AccountMeta(round_pda, is_signer=False, is_writable=False),
            AccountMeta(payer.pubkey(), is_signer=True, is_writable=True),
            AccountMeta(SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        ]
        
        instruction = Instruction(PROGRAM_ID, bytes(instruction_data), accounts)
        
        recent_blockhash_resp = await client.get_latest_blockhash(commitment=Confirmed)
        recent_blockhash = recent_blockhash_resp.value.blockhash
        
        message = MessageV0.try_compile(
            payer.pubkey(),
            [instruction],
            [],
            recent_blockhash
        )
        
        tx = VersionedTransaction(message, [payer])
        
        opts = TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
        result = await client.send_transaction(tx, opts=opts)
        signature = str(result.value)
        
        # Convert string signature to Signature object for confirmation
        try:
            sig_obj = Signature.from_string(signature)
            await client.confirm_transaction(sig_obj, commitment=Confirmed)
        except TimeoutError:
            print(f"Confirmation timeout (transaction likely still processing): {signature}")
        except Exception as confirm_err:
            print(f"Confirmation error (transaction may still succeed): {confirm_err}")
        
        return signature
    
    except Exception as e:
        import traceback
        print(f"Error closing bet: {type(e).__name__}: {e}")
        print(traceback.format_exc())
        return None

