"""Betting service with full strategy logic."""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, Literal, Optional

from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair

from .blockchain import (
    get_config, get_bet, get_balance, get_current_time,
    place_bet, LAMPORTS_PER_SOL
)
from .api import FortuvaApi


Mode = Literal["GENERAL", "PAYOUT"]
Direction = Literal["UP", "DOWN"]


@dataclass
class BettingStrategy:
    min_bet_amount: float
    max_bet_amount: float
    multiplier: float
    mode: Mode
    direction: Direction


@dataclass
class RuntimeConfig:
    direction: Optional[Direction]
    bet_amounts: list[float]  # [even_round_amount, odd_round_amount]
    start_calc_rounds: list[int]  # [even_round_start, odd_round_start]


class BettingService:
    """Handles betting logic with strategy calculations."""
    
    def __init__(
        self,
        client: AsyncClient,
        wallet: Keypair,
        api: FortuvaApi,
        config: Dict,
        runtime_config: RuntimeConfig,
        log_callback: Optional[Callable[[str], None]] = None,
        round_update_callback: Optional[Callable[[Dict], None]] = None,
        bet_placed_callback: Optional[Callable[[Dict], None]] = None,
        bet_placing_callback: Optional[Callable[[bool], None]] = None,
        worker_ref=None,
        stop_event=None
    ):
        self.client = client
        self.wallet = wallet
        self.api = api
        self.config = config  # Bot configuration
        self.runtime_config = runtime_config
        self.log_callback = log_callback
        self.round_update_callback = round_update_callback
        self.bet_placed_callback = bet_placed_callback
        self.bet_placing_callback = bet_placing_callback
        self.worker_ref = worker_ref  # Reference to worker for manual bet queue
        self.stop_event = stop_event  # Stop event from worker
        
        # Current state
        self.current_round: Optional[int] = None
        self.round_info: Optional[Dict] = None
        self.blockchain_config: Optional[Dict] = None
        self.bet_placed_for_round: Optional[int] = None  # Track which round we placed bet for
        self.current_bet_direction: Optional[str] = None  # Track bet direction
        self.current_bet_amount: Optional[float] = None  # Track bet amount
        
    def _log(self, message: str) -> None:
        """Log a message with timestamp."""
        if self.log_callback:
            self.log_callback(message)
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
    
    def get_betting_strategy(self, round_number: int) -> BettingStrategy:
        """Get betting strategy based on round number (even/odd)."""
        is_even = round_number % 2 == 0
        
        if is_even:
            return BettingStrategy(
                min_bet_amount=self.config['even_min_bet'],
                max_bet_amount=self.config['even_max_bet'],
                multiplier=self.config['even_multiplier'],
                mode=self.config['even_mode'],
                direction=self.config['even_direction']
            )
        else:
            return BettingStrategy(
                min_bet_amount=self.config['odd_min_bet'],
                max_bet_amount=self.config['odd_max_bet'],
                multiplier=self.config['odd_multiplier'],
                mode=self.config['odd_mode'],
                direction=self.config['odd_direction']
            )
    
    def determine_bet_direction(self, round_info: Dict, strategy: BettingStrategy) -> bool:
        """
        Determine bet direction based on strategy.
        
        Returns:
            True for UP/Bull, False for DOWN/Bear
        """
        # If runtime config has a direction override, use it
        if self.runtime_config.direction:
            return self.runtime_config.direction == 'UP'
        
        is_bull = False
        
        if strategy.mode == 'GENERAL':
            # Simple mode: always bet in configured direction
            is_bull = (strategy.direction == 'UP')
        
        elif strategy.mode == 'PAYOUT':
            # Payout mode: bet on the side with higher payout
            total_bull = round_info.get('totalBullAmount', 0)
            total_bear = round_info.get('totalBearAmount', 0)
            
            if total_bull >= total_bear:
                # More money on bull side, so bear has higher payout
                # If direction is UP, bet opposite (bear/down)
                is_bull = not (strategy.direction == 'UP')
            else:
                # More money on bear side, so bull has higher payout
                # If direction is UP, bet bull/up
                is_bull = (strategy.direction == 'UP')
        
        return is_bull
    
    async def calculate_bet_amount(self, current_round: int, strategy: BettingStrategy) -> float:
        """Calculate bet amount using martingale strategy based on failed bets."""
        round_idx = current_round % 2
        
        # Get failed bet count from API
        failed_count = await asyncio.to_thread(
            self.api.get_failed_bet_count,
            str(self.wallet.pubkey()),
            current_round,
            self.runtime_config.start_calc_rounds[round_idx]
        )
        
        # Base amount
        base_amount = (
            self.runtime_config.bet_amounts[round_idx]
            if self.runtime_config.bet_amounts[round_idx] > 0
            else strategy.min_bet_amount
        )
        
        # Apply multiplier for failed bets (martingale)
        bet_amount = base_amount * (strategy.multiplier ** failed_count)
        
        return bet_amount
    
    async def should_proceed_with_bet(self) -> bool:
        """Check if we should proceed with betting."""
        if not self.blockchain_config:
            self._log("⚠️  No blockchain configuration available")
            return False
        
        if self.blockchain_config.get('isPaused'):
            self._log("⚠️  Market is paused")
            return False
        
        return True
    
    async def show_message_loop(self) -> None:
        """Loop to show round information periodically."""
        while True:
            try:
                # Check if stop requested
                if self.stop_event and self.stop_event.is_set():
                    break
                
                # Sleep but check stop event more frequently
                interval = self.config['interval_time']
                for _ in range(interval):
                    if self.stop_event and self.stop_event.is_set():
                        break
                    await asyncio.sleep(1)
                
                # Fetch blockchain config
                self.blockchain_config = await get_config(self.client)
                
                if not await self.should_proceed_with_bet():
                    continue
                
                self.current_round = self.blockchain_config['currentRound']
                
                # Get round info from API
                self.round_info = await asyncio.to_thread(
                    self.api.get_round_info,
                    self.current_round
                )
                
                if not self.round_info:
                    self._log("⚠️  No round information available")
                    continue
                
                current_time = get_current_time()
                remaining_time = self.round_info['lockTime'] - current_time
                
                if remaining_time < 0:
                    continue
                
                # Get balance
                balance = await get_balance(self.client, self.wallet.pubkey())
                
                # Calculate prize pool and payouts
                total_bull = self.round_info.get('totalBullAmount', 0) / LAMPORTS_PER_SOL
                total_bear = self.round_info.get('totalBearAmount', 0) / LAMPORTS_PER_SOL
                prize_pool = total_bull + total_bear
                
                up_payout = self.round_info.get('upPayout', 0)
                down_payout = self.round_info.get('downPayout', 0)
                
                self._log(
                    f"ℹ️  Current Round: {self.current_round}, "
                    f"RemainingTime: {remaining_time}s, "
                    f"Balance: {balance:.4f} SOL, "
                    f"PrizePool: {prize_pool:.3f} SOL, "
                    f"UpPayout: {up_payout:.2f}x, "
                    f"DownPayout: {down_payout:.2f}x"
                )
                
                # Update round card if callback is set
                if self.round_update_callback:
                    # Get lock price from round info (convert from lamports)
                    lock_price_lamports = self.round_info.get('lockPrice', 0)
                    # Lock price is stored as lamports, but represents a price with decimals
                    # Typically SOL price * 10^8, so divide by 10^8 to get dollar price
                    lock_price = lock_price_lamports / 100_000_000 if lock_price_lamports > 0 else 0
                    
                    # Check if we need to load existing bet details
                    if self.bet_placed_for_round != self.current_round:
                        # Check blockchain for existing bet
                        existing_bet = await get_bet(self.client, self.wallet.pubkey(), self.current_round)
                        if existing_bet:
                            # Found existing bet - extract and store details
                            self.bet_placed_for_round = self.current_round
                            bet_amount_lamports = existing_bet.get('amount', 0)
                            self.current_bet_amount = bet_amount_lamports / LAMPORTS_PER_SOL
                            self.current_bet_direction = 'UP' if existing_bet.get('predictBull', False) else 'DOWN'
                            self._log(f"ℹ️  Loaded existing bet: {self.current_bet_amount:.4f} SOL on {self.current_bet_direction}")
                    
                    # Check if bet already exists for current round
                    has_bet = (self.bet_placed_for_round == self.current_round)
                    
                    self.round_update_callback({
                        'round_number': self.current_round,
                        'up_payout': up_payout,
                        'down_payout': down_payout,
                        'prize_pool': prize_pool,
                        'remaining_time': remaining_time,
                        'lock_price': lock_price,
                        'balance': balance,
                        'wallet_address': str(self.wallet.pubkey()),
                        'has_bet': has_bet,
                        'bet_direction': self.current_bet_direction if has_bet else None,
                        'bet_amount': self.current_bet_amount if has_bet else None
                    })
                
            except Exception as e:
                self._log(f"❌ Error in show_message_loop: {e}")
        
        self._log("🛑 Show message loop stopped")
    
    async def execute_bet_loop(self) -> None:
        """Main betting execution loop."""
        while True:
            try:
                # Check if stop requested
                if self.stop_event and self.stop_event.is_set():
                    break
                
                await asyncio.sleep(0.1)  # Fast polling
                
                # Check for manual bet request
                if self.worker_ref:
                    with self.worker_ref._manual_bet_lock:
                        manual_bet = self.worker_ref._manual_bet_request
                        if manual_bet:
                            self.worker_ref._manual_bet_request = None  # Clear it
                            # Process manual bet immediately
                            await self._place_manual_bet(
                                manual_bet['round'],
                                manual_bet['direction'],
                                manual_bet['amount']
                            )
                
                if not self.current_round or not self.blockchain_config or not self.round_info:
                    continue
                
                current_time = get_current_time()
                remaining_time = self.round_info['lockTime'] - current_time
                
                if remaining_time < 0:
                    # Reset flags when round ends
                    self.bet_placed_for_round = None
                    self.current_bet_direction = None
                    self.current_bet_amount = None
                    continue
                
                # Check if auto betting is enabled
                if not self.config.get('auto_bet', True):
                    # Auto betting is disabled, skip automated bets
                    continue
                
                # Only bet within bet_time window
                if remaining_time > self.config['bet_time']:
                    continue
                
                # Skip if we already attempted a bet for this round
                if self.bet_placed_for_round == self.current_round:
                    continue
                
                # Check if bet already placed on-chain
                existing_bet = await get_bet(self.client, self.wallet.pubkey(), self.current_round)
                if existing_bet:
                    self.bet_placed_for_round = self.current_round
                    # Extract bet details from existing bet
                    bet_amount_lamports = existing_bet.get('amount', 0)
                    self.current_bet_amount = bet_amount_lamports / LAMPORTS_PER_SOL
                    self.current_bet_direction = 'UP' if existing_bet.get('predictBull', False) else 'DOWN'
                    self._log(f"ℹ️  Found existing bet: {self.current_bet_amount:.4f} SOL on {self.current_bet_direction}")
                    continue
                
                # Check if previous round was cancelled
                if self.current_round > 1:
                    prev_round_info = await asyncio.to_thread(
                        self.api.get_round_info,
                        self.current_round - 1
                    )
                    if prev_round_info and prev_round_info.get('status') == 4:
                        self._log(f"⚠️  Previous round {self.current_round - 1} was cancelled, skipping bet")
                        continue
                
                # Mark that we're attempting a bet for this round
                self.bet_placed_for_round = self.current_round
                
                # Place bet with strategy
                result = await self.place_bet_with_strategy()
                
                if result:
                    # Wait before checking next round to avoid rapid repeated attempts
                    wait_time = max(self.config['bet_time'], 5)  # At least 5 seconds
                    for _ in range(wait_time):
                        if self.stop_event and self.stop_event.is_set():
                            break
                        await asyncio.sleep(1)
                
            except Exception as e:
                self._log(f"❌ Error in execute_bet_loop: {e}")
        
        self._log("🛑 Execute bet loop stopped")
    
    async def place_bet_with_strategy(self) -> bool:
        """Place a bet using the current strategy."""
        try:
            current_round = self.current_round
            round_info = self.round_info
            
            if not current_round or not round_info:
                return False
            
            strategy = self.get_betting_strategy(current_round)
            is_bull = self.determine_bet_direction(round_info, strategy)
            bet_amount = await self.calculate_bet_amount(current_round, strategy)
            
            # Check if bet amount exceeds max
            if bet_amount > strategy.max_bet_amount:
                self.runtime_config.start_calc_rounds[current_round % 2] = current_round
                self._log("⚠️  Bet amount exceeds maximum, resetting calculation")
                return False
            
            # Check balance
            balance = await get_balance(self.client, self.wallet.pubkey())
            if balance < bet_amount + self.config['min_wallet_balance']:
                self.runtime_config.start_calc_rounds[current_round % 2] = current_round
                self._log(
                    f"⚠️  Insufficient balance. Current: {balance:.4f} SOL, "
                    f"Required: {(bet_amount + self.config['min_wallet_balance']):.4f} SOL"
                )
                return False
            
            # Place the bet
            self._log(f"🎲 Placing bet: {bet_amount:.4f} SOL on {'UP' if is_bull else 'DOWN'} for round {current_round}")
            
            # Signal that bet placement is starting
            if self.bet_placing_callback:
                self.bet_placing_callback(True)
            
            try:
                signature = await place_bet(
                    self.client,
                    self.wallet,
                    current_round,
                    is_bull,
                    bet_amount
                )
                
                if signature == "ALREADY_PLACED":
                    # Bet already exists for this round - this is normal
                    self._log(f"ℹ️  Bet already placed for round {current_round}")
                    return True
                elif signature and signature != "None":
                    new_balance = await get_balance(self.client, self.wallet.pubkey())
                    self._log(f"✅ Bet {bet_amount:.4f} SOL to {'UP' if is_bull else 'DOWN'} at Round {current_round}")
                    self._log(f"🔗 https://solscan.io/tx/{signature}")
                    self._log(f"💰 Current Balance: {new_balance:.4f} SOL")
                    
                    # Notify UI that bet was placed
                    direction_str = 'UP' if is_bull else 'DOWN'
                    if self.bet_placed_callback:
                        bet_data = {
                            'round_number': current_round,
                            'direction': direction_str,
                            'amount': bet_amount,
                            'signature': signature
                        }
                        print(f"[DEBUG] BettingService calling bet_placed_callback with: {bet_data}")
                        self.bet_placed_callback(bet_data)
                    else:
                        print("[DEBUG] BettingService: bet_placed_callback is None!")
                    
                    # Store bet details for round updates
                    self.current_bet_direction = direction_str
                    self.current_bet_amount = bet_amount
                    
                    # Clear direction override after successful bet
                    if self.runtime_config.direction:
                        self.runtime_config.direction = None
                    
                    return True
                elif signature is None:
                    self._log(f"❌ Failed to place bet - transaction returned None")
                    self._log(f"💡 Check console/terminal for detailed error message")
                    return False
                else:
                    self._log(f"⚠️  Unexpected response from place_bet: {signature}")
                    return False
            
            except Exception as bet_error:
                self._log(f"❌ Bet transaction error: {type(bet_error).__name__}")
                self._log(f"📄 Error: {str(bet_error)}")
                if hasattr(bet_error, 'args') and len(bet_error.args) > 0:
                    self._log(f"📋 Details: {bet_error.args[0] if bet_error.args else 'No details'}")
                return False
            finally:
                # Signal that bet placement is done
                if self.bet_placing_callback:
                    self.bet_placing_callback(False)
            
        except Exception as e:
            self._log(f"❌ Error in betting logic: {type(e).__name__}: {e}")
            return False
    
    async def _place_manual_bet(self, round_number: int, direction: str, amount: float) -> bool:
        """Place a manual bet immediately."""
        try:
            self._log(f"🎲 Placing manual bet: {amount:.4f} SOL on {direction} for round #{round_number}")
            
            # Check if bet already exists
            existing_bet = await get_bet(self.client, self.wallet.pubkey(), round_number)
            if existing_bet:
                # Extract and store bet details if not already stored
                if not self.current_bet_direction or not self.current_bet_amount:
                    bet_amount_lamports = existing_bet.get('amount', 0)
                    self.current_bet_amount = bet_amount_lamports / LAMPORTS_PER_SOL
                    self.current_bet_direction = 'UP' if existing_bet.get('predictBull', False) else 'DOWN'
                    self.bet_placed_for_round = round_number
                self._log(f"⚠️  Bet already placed for round #{round_number}")
                return False
            
            # Check balance
            balance = await get_balance(self.client, self.wallet.pubkey())
            if balance < amount + self.config['min_wallet_balance']:
                self._log(f"⚠️  Insufficient balance. Current: {balance:.4f} SOL, Required: {amount:.4f} SOL")
                return False
            
            # Convert direction to boolean
            is_bull = (direction == "UP")
            
            # Signal that bet placement is starting
            if self.bet_placing_callback:
                self.bet_placing_callback(True)
            
            # Place the bet
            signature = await place_bet(
                self.client,
                self.wallet,
                round_number,
                is_bull,
                amount
            )
            
            if signature == "ALREADY_PLACED":
                self._log(f"ℹ️  Bet already placed for round {round_number}")
                return True
            elif signature and signature != "None":
                new_balance = await get_balance(self.client, self.wallet.pubkey())
                self._log(f"✅ Manual bet placed: {amount:.4f} SOL to {direction} at Round {round_number}")
                self._log(f"🔗 https://solscan.io/tx/{signature}")
                self._log(f"💰 Current Balance: {new_balance:.4f} SOL")
                
                # Notify UI
                if self.bet_placed_callback:
                    bet_data = {
                        'round_number': round_number,
                        'direction': direction,
                        'amount': amount,
                        'signature': signature
                    }
                    print(f"[DEBUG] Manual bet - calling bet_placed_callback with: {bet_data}")
                    self.bet_placed_callback(bet_data)
                else:
                    print("[DEBUG] Manual bet - bet_placed_callback is None!")
                
                # Store bet details for round updates
                self.current_bet_direction = direction
                self.current_bet_amount = amount
                
                # Mark as placed
                self.bet_placed_for_round = round_number
                return True
            else:
                self._log(f"❌ Failed to place manual bet")
                return False
                
        except Exception as e:
            self._log(f"❌ Error placing manual bet: {type(e).__name__}: {e}")
            return False
        finally:
            # Signal that bet placement is done
            if self.bet_placing_callback:
                self.bet_placing_callback(False)
    
    async def start(self) -> None:
        """Start both betting loops concurrently."""
        await asyncio.gather(
            self.show_message_loop(),
            self.execute_bet_loop()
        )

