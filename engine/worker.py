"""Engine worker with full TypeScript implementation."""

from __future__ import annotations

import asyncio
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Literal, Optional

from PyQt5 import QtCore
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed

from .api import FortuvaApi
from .blockchain import create_keypair_from_private_key, get_config
from .betting_service import BettingService, RuntimeConfig
from .claim_service import ClaimService
from .cancel_service import CancelService
from .close_service import CloseService


Mode = Literal["GENERAL", "PAYOUT"]
Direction = Literal["UP", "DOWN"]


@dataclass
class BotConfig:
    rpc_url: str
    bet_time: int
    interval_time: int
    min_wallet_balance: float
    even_min_bet: float
    even_max_bet: float
    even_multiplier: float
    even_mode: Mode
    even_direction: Direction
    odd_min_bet: float
    odd_max_bet: float
    odd_multiplier: float
    odd_mode: Mode
    odd_direction: Direction
    considering_old_bets: bool
    auto_bet: bool


class BotWorker(QtCore.QThread):
    """Engine worker that orchestrates all betting, claiming, canceling, and closing services."""
    
    status = QtCore.pyqtSignal(str)
    round_update = QtCore.pyqtSignal(dict)  # Signal for round card updates
    bet_placed = QtCore.pyqtSignal(dict)  # Signal when bet is successfully placed
    claim_success = QtCore.pyqtSignal(dict)  # Signal when claim is successful
    bet_placing = QtCore.pyqtSignal(bool)  # Signal when bet placement starts/ends (True=placing, False=done)

    def __init__(self, wallet: Dict[str, str], config: BotConfig, api: Optional[FortuvaApi] = None) -> None:
        super().__init__()
        self._stop_event = threading.Event()
        self.wallet_data = wallet
        self.config = config
        self.api = api or FortuvaApi()
        
        # Will be initialized in run()
        self.client: Optional[AsyncClient] = None
        self.wallet_keypair = None
        self.betting_service = None
        self.claim_service = None
        self.cancel_service = None
        self.close_service = None
        self.runtime_config = None
        
        # Manual bet queue
        self._manual_bet_request = None
        self._manual_bet_lock = threading.Lock()

    def stop(self) -> None:
        """Stop the engine"""
        self._stop_event.set()

    def _log(self, message: str) -> None:
        """Emit a timestamped log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status.emit(f"[{timestamp}] {message}")
    
    def _emit_round_update(self, round_data: Dict) -> None:
        """Emit round update signal for UI."""
        self.round_update.emit(round_data)
    
    def _emit_bet_placed(self, bet_data: Dict) -> None:
        """Emit bet placed signal for UI (works for both manual and automatic bets)."""
        print(f"[DEBUG] Worker emitting bet_placed signal: {bet_data}")
        self.bet_placed.emit(bet_data)
    
    def _emit_bet_placing(self, is_placing: bool) -> None:
        """Emit bet placing signal for UI (True=placing, False=done)."""
        print(f"[DEBUG] Worker emitting bet_placing signal: {is_placing}")
        self.bet_placing.emit(is_placing)
    
    def _on_claim_success(self, claim_data: Dict) -> None:
        """Emit claim success signal for UI."""
        print(f"[DEBUG] Worker emitting claim_success signal: {claim_data}")
        self.claim_success.emit(claim_data)
    
    def place_manual_bet(self, round_number: int, direction: str, amount: float) -> None:
        """Queue a manual bet to be placed immediately."""
        with self._manual_bet_lock:
            self._manual_bet_request = {
                'round': round_number,
                'direction': direction,
                'amount': amount
            }
            self._log(f"📥 Manual bet queued: {amount:.4f} SOL on {direction} for round #{round_number}")

    def _initialize_wallet(self) -> None:
        """Initialize wallet keypair from provided wallet data."""
        try:
            # Always use seed_or_private (keypair file is auto-loaded into this field)
            if self.wallet_data.get("seed_or_private"):
                private_key = self.wallet_data['seed_or_private']
                self.wallet_keypair = create_keypair_from_private_key(private_key)
                
                # Show source information
                if self.wallet_data.get("keypair_file"):
                    keypair_file = self.wallet_data['keypair_file']
                    import os
                    self._log(f"🔑 Wallet loaded from: {os.path.basename(keypair_file)}")
                else:
                    self._log(f"🔑 Wallet loaded from seed/private key")
                    
                self._log(f"📍 Address: {self.wallet_keypair.pubkey()}")
            
            else:
                raise ValueError("No wallet configuration provided. Please enter a private key or select a keypair file.")
        
        except Exception as e:
            self._log(f"❌ Failed to load wallet: {e}")
            raise

    async def _initialize_services(self) -> None:
        """Initialize all engine services."""
        try:
            # Create Solana RPC client
            self.client = AsyncClient(self.config.rpc_url, commitment=Confirmed)
            self._log(f"🌐 Connected to Solana RPC: {self.config.rpc_url}")
            
            # Get blockchain config to initialize runtime config
            blockchain_config = await get_config(self.client)
            
            # Initialize runtime configuration
            current_round = blockchain_config['currentRound'] if blockchain_config else 1
            
            self.runtime_config = RuntimeConfig(
                direction=None,
                bet_amounts=[-1, -1],  # Will use strategy defaults
                start_calc_rounds=(
                    [current_round, current_round]
                    if not self.config.considering_old_bets and blockchain_config
                    else [0, 0]
                )
            )
            
            # Convert config to dict for services
            config_dict = {
                'bet_time': self.config.bet_time,
                'interval_time': self.config.interval_time,
                'min_wallet_balance': self.config.min_wallet_balance,
                'even_min_bet': self.config.even_min_bet,
                'even_max_bet': self.config.even_max_bet,
                'even_multiplier': self.config.even_multiplier,
                'even_mode': self.config.even_mode,
                'even_direction': self.config.even_direction,
                'odd_min_bet': self.config.odd_min_bet,
                'odd_max_bet': self.config.odd_max_bet,
                'odd_multiplier': self.config.odd_multiplier,
                'odd_mode': self.config.odd_mode,
                'odd_direction': self.config.odd_direction,
                'auto_bet': self.config.auto_bet,
            }
            
            # Initialize services with logging callback
            self.betting_service = BettingService(
                self.client,
                self.wallet_keypair,
                self.api,
                config_dict,
                self.runtime_config,
                log_callback=self._log,
                round_update_callback=self._emit_round_update,
                bet_placed_callback=self._emit_bet_placed,
                bet_placing_callback=self._emit_bet_placing,
                worker_ref=self,  # Pass self reference for manual bet queue
                stop_event=self._stop_event  # Pass stop event
            )
            
            self.claim_service = ClaimService(
                self.client,
                self.wallet_keypair,
                self.api,
                log_callback=self._log,
                claim_callback=self._on_claim_success
            )
            
            self.cancel_service = CancelService(
                self.client,
                self.wallet_keypair,
                self.api,
                log_callback=self._log
            )
            
            self.close_service = CloseService(
                self.client,
                self.wallet_keypair,
                self.api,
                log_callback=self._log
            )
            
            self._log("✅ All services initialized successfully")
        
        except Exception as e:
            self._log(f"❌ Failed to initialize services: {e}")
            raise

    async def _run_maintenance_loop(self) -> None:
        """Run maintenance tasks (claim, cancel, close) periodically."""
        self._log("🔄 Starting maintenance loop (claim/cancel/close every 60s)")
        
        while not self._stop_event.is_set():
            try:
                # Run all maintenance tasks
                await self.claim_service.claim_all_rewards()
                await self.cancel_service.cancel_all_bets()
                await self.close_service.close_all_bets()
                
            except Exception as e:
                self._log(f"❌ Error in maintenance loop: {e}")
            
            # Wait 60 seconds before next maintenance cycle (check stop every second)
            for _ in range(60):
                if self._stop_event.is_set():
                    break
                await asyncio.sleep(1)
        
        self._log("🛑 Maintenance loop stopped")

    async def _async_run(self) -> None:
        """Main async run method."""
        try:
            self._log("🚀 Engine started")
            self._log(f"⚙️  Config: RPC={self.config.rpc_url}")
            self._log(f"⚙️  Interval: {self.config.interval_time}s, Bet Time: {self.config.bet_time}s")
            self._log(f"⚙️  Even: {self.config.even_min_bet}-{self.config.even_max_bet} SOL, "
                     f"Mode={self.config.even_mode}, Dir={self.config.even_direction}, "
                     f"Multiplier={self.config.even_multiplier}x")
            self._log(f"⚙️  Odd: {self.config.odd_min_bet}-{self.config.odd_max_bet} SOL, "
                     f"Mode={self.config.odd_mode}, Dir={self.config.odd_direction}, "
                     f"Multiplier={self.config.odd_multiplier}x")
            self._log(f"⚙️  Considering old bets: {self.config.considering_old_bets}")
            
            # Initialize wallet
            self._initialize_wallet()
            
            # Initialize services
            await self._initialize_services()
            
            self._log("🎮 Starting engine services...")
            
            # Run betting and maintenance loops concurrently
            await asyncio.gather(
                self.betting_service.show_message_loop(),
                self.betting_service.execute_bet_loop(),
                self._run_maintenance_loop(),
                return_exceptions=True
            )
        
        except Exception as e:
            self._log(f"❌ Engine error: {e}")
        
        finally:
            # Cleanup
            if self.client:
                await self.client.close()
            self._log("🛑 Engine stopped")

    def run(self) -> None:
        """Qt thread run method - bridges sync and async."""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the async main function
            loop.run_until_complete(self._async_run())
        
        except Exception as e:
            self._log(f"❌ Critical error: {e}")
        
        finally:
            try:
                loop.close()
            except:
                pass
