"""Service for closing completed bets to reclaim rent."""

import asyncio
from datetime import datetime
from typing import Callable, List, Dict, Optional

from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair

from .blockchain import close_bet
from .api import FortuvaApi


class CloseService:
    """Handles automatic closing of completed bets to reclaim rent."""
    
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
    
    async def close_single_bet(self, round_number: int) -> Dict:
        """
        Close a completed bet to reclaim rent.
        
        Returns:
            Dict with success status and details
        """
        try:
            signature = await close_bet(self.client, self.wallet, round_number)
            
            if signature:
                self._log(f"✅ Closed bet for Round {round_number}")
                self._log(f"🔗 https://solscan.io/tx/{signature}")
                
                return {
                    'success': True,
                    'signature': signature,
                    'round_number': round_number
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to close bet',
                    'round_number': round_number
                }
        
        except Exception as e:
            self._log(f"❌ Failed to close bet for round {round_number}: {e}")
            return {
                'success': False,
                'error': str(e),
                'round_number': round_number
            }
    
    async def close_all_bets(self) -> List[Dict]:
        """
        Close all completed bets.
        
        Returns:
            List of close results
        """
        results = []
        
        try:
            # Fetch closeable bets from API
            closeable_bets = await asyncio.to_thread(
                self.api.get_closeable_bets,
                str(self.wallet.pubkey())
            )
            
            if not closeable_bets:
                return results
            
            self._log(f"📋 Found {len(closeable_bets)} closeable bet(s)")
            
            # Close each bet
            for bet in closeable_bets:
                round_number = bet['epoch']
                
                result = await self.close_single_bet(round_number)
                results.append(result)
                
                # Small delay between closes
                await asyncio.sleep(0.5)
        
        except Exception as e:
            self._log(f"❌ Error fetching closeable bets: {e}")
        
        return results
    
    async def start_close_loop(self, interval_seconds: int = 60) -> None:
        """
        Start the automatic close loop.
        
        Args:
            interval_seconds: How often to check for closeable bets (default 60s)
        """
        self._log("🔄 Starting automatic close loop...")
        
        while True:
            try:
                await self.close_all_bets()
            except Exception as e:
                self._log(f"❌ Error in close loop: {e}")
            
            await asyncio.sleep(interval_seconds)

