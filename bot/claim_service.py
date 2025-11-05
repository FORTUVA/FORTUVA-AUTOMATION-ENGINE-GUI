"""Service for auto-claiming bet rewards."""

import asyncio
from datetime import datetime
from typing import Callable, List, Dict, Optional

from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair

from .blockchain import claim_payout, LAMPORTS_PER_SOL
from .api import FortuvaApi


class ClaimService:
    """Handles automatic claiming of bet rewards."""
    
    def __init__(
        self,
        client: AsyncClient,
        wallet: Keypair,
        api: FortuvaApi,
        log_callback: Optional[Callable[[str], None]] = None,
        claim_callback: Optional[Callable[[Dict], None]] = None
    ):
        self.client = client
        self.wallet = wallet
        self.api = api
        self.log_callback = log_callback
        self.claim_callback = claim_callback
    
    def _log(self, message: str) -> None:
        """Log a message with timestamp."""
        if self.log_callback:
            self.log_callback(message)
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
    
    async def claim_single_reward(self, round_number: int, payout: float) -> Dict:
        """
        Claim reward for a single bet.
        
        Returns:
            Dict with success status and details
        """
        try:
            signature = await claim_payout(self.client, self.wallet, round_number)
            
            if signature:
                self._log(
                    f"✅ Claimed reward of {payout:.4f} SOL for Round {round_number}"
                )
                self._log(f"🔗 https://solscan.io/tx/{signature}")
                
                result = {
                    'success': True,
                    'signature': signature,
                    'reward_amount': payout,
                    'round_number': round_number
                }
                
                # Notify callback
                if self.claim_callback:
                    print(f"[DEBUG] ClaimService calling claim_callback with: {result}")
                    self.claim_callback(result)
                else:
                    print("[DEBUG] ClaimService: claim_callback is None!")
                
                return result
            else:
                return {
                    'success': False,
                    'error': 'Failed to claim reward',
                    'reward_amount': 0,
                    'round_number': round_number
                }
        
        except Exception as e:
            self._log(f"❌ Failed to claim reward for round {round_number}: {e}")
            return {
                'success': False,
                'error': str(e),
                'reward_amount': 0,
                'round_number': round_number
            }
    
    async def claim_all_rewards(self) -> List[Dict]:
        """
        Claim all available rewards from claimable bets.
        
        Returns:
            List of claim results
        """
        results = []
        
        try:
            # Fetch claimable bets from API
            claimable_bets = await asyncio.to_thread(
                self.api.get_claimable_bets,
                str(self.wallet.pubkey())
            )
            
            if not claimable_bets:
                return results
            
            self._log(f"📋 Found {len(claimable_bets)} claimable bet(s)")
            
            # Claim each bet
            for bet in claimable_bets:
                round_number = bet['epoch']
                payout = float(bet.get('payout', 0)) / LAMPORTS_PER_SOL
                
                result = await self.claim_single_reward(round_number, payout)
                results.append(result)
                
                # Small delay between claims
                await asyncio.sleep(0.5)
        
        except Exception as e:
            self._log(f"❌ Error fetching claimable bets: {e}")
        
        return results
    
    async def start_claim_loop(self, interval_seconds: int = 60) -> None:
        """
        Start the automatic claim loop.
        
        Args:
            interval_seconds: How often to check for claimable bets (default 60s)
        """
        self._log("🔄 Starting automatic claim loop...")
        
        while True:
            try:
                await self.claim_all_rewards()
            except Exception as e:
                self._log(f"❌ Error in claim loop: {e}")
            
            await asyncio.sleep(interval_seconds)

