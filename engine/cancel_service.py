"""Service for auto-canceling bets from cancelled rounds."""

import asyncio
from datetime import datetime
from typing import Callable, List, Dict, Optional

from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair

from .blockchain import cancel_bet, get_balance, LAMPORTS_PER_SOL
from .api import FortuvaApi


class CancelService:
    """Handles automatic cancellation of bets from cancelled rounds."""
    
    def __init__(
        self,
        client: AsyncClient,
        wallet: Keypair,
        api: FortuvaApi,
        log_callback: Optional[Callable[[str], None]] = None
    ):
        self.client = client
        self.wallet = wallet
        self.api = api
        self.log_callback = log_callback
    
    def _log(self, message: str) -> None:
        """Log a message with timestamp."""
        if self.log_callback:
            self.log_callback(message)
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
    
    async def cancel_single_bet(self, round_number: int) -> Dict:
        """
        Cancel a bet from a cancelled round.
        
        Returns:
            Dict with success status and details
        """
        try:
            # Get balance before cancel
            balance_before = await get_balance(self.client, self.wallet.pubkey())
            
            signature = await cancel_bet(self.client, self.wallet, round_number)
            
            if signature:
                # Get balance after cancel
                balance_after = await get_balance(self.client, self.wallet.pubkey())
                refund = balance_after - balance_before
                
                self._log(
                    f"✅ Cancelled bet and refunded {refund:.4f} SOL for Round {round_number}"
                )
                self._log(f"🔗 https://solscan.io/tx/{signature}")
                
                return {
                    'success': True,
                    'signature': signature,
                    'refund_amount': refund,
                    'round_number': round_number
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to cancel bet',
                    'refund_amount': 0,
                    'round_number': round_number
                }
        
        except Exception as e:
            self._log(f"❌ Failed to cancel bet for round {round_number}: {e}")
            return {
                'success': False,
                'error': str(e),
                'refund_amount': 0,
                'round_number': round_number
            }
    
    async def cancel_all_bets(self) -> List[Dict]:
        """
        Cancel all bets from cancelled rounds.
        
        Returns:
            List of cancel results
        """
        results = []
        
        try:
            # Fetch cancelable bets from API
            cancelable_bets = await asyncio.to_thread(
                self.api.get_cancelable_bets,
                str(self.wallet.pubkey())
            )
            
            if not cancelable_bets:
                return results
            
            self._log(f"📋 Found {len(cancelable_bets)} cancelable bet(s)")
            
            # Cancel each bet
            for bet in cancelable_bets:
                round_number = bet['epoch']
                
                result = await self.cancel_single_bet(round_number)
                results.append(result)
                
                # Small delay between cancels
                await asyncio.sleep(0.5)
        
        except Exception as e:
            self._log(f"❌ Error fetching cancelable bets: {e}")
        
        return results
    
    async def start_cancel_loop(self, interval_seconds: int = 60) -> None:
        """
        Start the automatic cancel loop.
        
        Args:
            interval_seconds: How often to check for cancelable bets (default 60s)
        """
        self._log("🔄 Starting automatic cancel loop...")
        
        while True:
            try:
                await self.cancel_all_bets()
            except Exception as e:
                self._log(f"❌ Error in cancel loop: {e}")
            
            await asyncio.sleep(interval_seconds)

