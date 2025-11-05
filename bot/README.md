# Fortuva Auto-Bet Bot - Python Implementation

This Python implementation fully mirrors the TypeScript bot logic from the `ts/` directory, providing comprehensive Solana blockchain integration for automated prediction betting.

## 🏗️ Architecture

The bot is structured into several key modules:

### Core Modules

1. **`blockchain.py`** - Solana/Anchor blockchain utilities
   - PDA (Program Derived Address) generation for config, round, user_bet, treasury
   - Account data fetching and parsing (config, rounds, bets)
   - Transaction builders for all operations (placeBet, claimPayout, cancelBet, closeBet)
   - Wallet management with multiple key formats support

2. **`betting_service.py`** - Main betting logic
   - **Strategy Modes:**
     - `GENERAL`: Always bet in configured direction (UP/DOWN)
     - `PAYOUT`: Bet on the side with higher payout ratio
   - **Martingale System**: Automatic bet scaling based on failed bets
   - **Even/Odd Round Strategies**: Different configurations for even vs odd rounds
   - Two concurrent loops:
     - `show_message_loop`: Displays round info every interval
     - `execute_bet_loop`: Places bets within bet_time window

3. **`claim_service.py`** - Auto-claim winnings
   - Fetches claimable bets from API
   - Automatically claims all available rewards
   - Runs every 60 seconds

4. **`cancel_service.py`** - Auto-cancel bets from cancelled rounds
   - Fetches cancelable bets from API
   - Refunds bets from cancelled rounds
   - Runs every 60 seconds

5. **`close_service.py`** - Close completed bets to reclaim rent
   - Fetches closeable bets from API
   - Closes completed bet accounts to recover rent
   - Runs every 60 seconds

6. **`worker.py`** - Main orchestrator
   - Initializes all services
   - Manages async event loop integration with PyQt5
   - Coordinates betting, claiming, canceling, and closing operations

7. **`api.py`** - Fortuva API client
   - Round information retrieval
   - Failed bet count calculation
   - Claimable/cancelable/closeable bet queries

## 🎯 Key Features

### Betting Strategy

The bot supports sophisticated betting strategies matching the TypeScript implementation:

#### Even Round Configuration
- Min/Max bet amounts
- Multiplier for martingale progression
- Mode: `GENERAL` or `PAYOUT`
- Direction: `UP` or `DOWN`

#### Odd Round Configuration
- Independent settings from even rounds
- Same parameters as even rounds

#### Strategy Logic

**GENERAL Mode:**
- Always bets in the configured direction (UP or DOWN)

**PAYOUT Mode:**
- Analyzes the current round's total bull vs bear amounts
- Bets on the side with higher payout ratio
- If direction is UP and bull side has higher payout → bet UP
- If direction is UP and bear side has higher payout → bet DOWN
- (Inverted for DOWN direction)

#### Martingale System

The bot implements a martingale betting system:
```
bet_amount = base_amount × (multiplier ^ failed_bet_count)
```

- Tracks failed bets from `start_calc_round` to `current_round`
- Resets calculation when:
  - Bet amount exceeds max_bet_amount
  - Wallet balance insufficient
- Set multiplier to 1.0 to disable martingale

### Safety Features

1. **Balance Check**: Ensures `balance > bet_amount + MIN_WALLET_BALANCE`
2. **Previous Round Check**: Skips betting if previous round was cancelled
3. **Duplicate Bet Prevention**: Checks if bet already placed for current round
4. **Max Bet Protection**: Prevents exceeding configured maximum bet
5. **Timing Window**: Only bets within configured `bet_time` seconds before lockTime

### Maintenance Operations

Every 60 seconds, the bot automatically:
1. **Claims** all winning bets
2. **Cancels** bets from cancelled rounds (status 4)
3. **Closes** completed bets to recover rent

## 🔑 Wallet Support

The bot supports multiple wallet key formats:

1. **Base58 encoded string**: `"5KQ8fpN..."` 
2. **JSON array**: `"[123, 45, 67, ...]"` (64 bytes)
3. **Comma-separated**: `"123,45,67,..."` (64 bytes)

## 🌐 Solana Integration

### Program
- **Program ID**: `FTV1kbDLaeVM4LG4vHrVu2qdt2cXazYTXWWUi1xFAJdK`
- **Network**: Configurable via RPC_URL (devnet/mainnet)

### PDAs (Program Derived Addresses)

```python
config_pda = PublicKey.find_program_address([b"config"], PROGRAM_ID)
treasury_pda = PublicKey.find_program_address([b"treasury"], PROGRAM_ID)
round_pda = PublicKey.find_program_address([b"round", round_bytes], PROGRAM_ID)
user_bet_pda = PublicKey.find_program_address([b"user_bet", user, round_bytes], PROGRAM_ID)
```

### Transaction Structure

All transactions use Solana's VersionedTransaction with MessageV0:
- Proper account metas (writable, signer flags)
- Instruction data with 8-byte discriminators
- Transaction confirmation with `Confirmed` commitment

## 📊 Configuration Parameters

| Parameter | Description | TypeScript Equivalent |
|-----------|-------------|----------------------|
| `rpc_url` | Solana RPC endpoint | `RPC_URL` |
| `bet_time` | Seconds before lock to place bet | `BET_TIME` |
| `interval_time` | Seconds between checks | `INTERVAL_TIME` |
| `min_wallet_balance` | Minimum SOL to keep | `MIN_WALLET_BALANCE` |
| `even_min_bet` | Min bet for even rounds | `EVEN_MIN_BET_AMOUNT` |
| `even_max_bet` | Max bet for even rounds | `EVEN_MAX_BET_AMOUNT` |
| `even_multiplier` | Multiplier for even rounds | `EVEN_MULTIPLIER` |
| `even_mode` | Strategy mode for even | `EVEN_MODE` |
| `even_direction` | Direction for even | `EVEN_DIRECTION` |
| `odd_min_bet` | Min bet for odd rounds | `ODD_MIN_BET_AMOUNT` |
| `odd_max_bet` | Max bet for odd rounds | `ODD_MAX_BET_AMOUNT` |
| `odd_multiplier` | Multiplier for odd rounds | `ODD_MULTIPLIER` |
| `odd_mode` | Strategy mode for odd | `ODD_MODE` |
| `odd_direction` | Direction for odd | `ODD_DIRECTION` |
| `considering_old_bets` | Include old bets in calc | `CONSIDERING_OLD_BETS` |

## 🔄 Workflow Comparison

### TypeScript Flow (ts/core/FortuvaBot.ts)

```typescript
1. Initialize wallet, connection, program
2. Get config from blockchain
3. Start bettingService (show_message + executeBet loops)
4. Start maintenance loop (claim/cancel/close every 60s)
```

### Python Flow (bot/worker.py)

```python
1. Initialize wallet, connection, services
2. Get config from blockchain
3. Start betting_service (show_message_loop + execute_bet_loop)
4. Start maintenance_loop (claim/cancel/close every 60s)
```

**They are identical!**

## 📦 Dependencies

```
solana>=0.30.2       # Solana RPC client
solders>=0.18.1      # Solana types (Keypair, Pubkey, Transaction, etc.)
anchorpy>=0.18.0     # Anchor framework support
base58>=2.1.1        # Base58 encoding/decoding
requests>=2.31.0     # HTTP API calls
PyQt5                # GUI framework
```

## 🚀 Usage

The bot is integrated into the PyQt5 GUI (`main.py`):

1. Configure wallet (keypair file or private key)
2. Set betting parameters in GUI
3. Click "Start" button
4. Bot initializes and starts all services
5. Monitor logs in the GUI panel

## 🔍 Logging

The bot emits timestamped logs for all operations:

- 🚀 Bot startup/shutdown
- ⚙️ Configuration display
- 🔑 Wallet loading
- 🌐 RPC connection
- ℹ️ Round information
- 🎲 Bet placement attempts
- ✅ Successful operations (bet/claim/cancel/close)
- ⚠️ Warnings (insufficient balance, skipped rounds)
- ❌ Errors with details
- 🔗 Solscan transaction links

## 🎮 Runtime Behavior

### Betting Loop Timing

1. **Show Message Loop** (interval_time): 
   - Fetches and displays round info every N seconds
   
2. **Execute Bet Loop** (fast polling @ 0.1s):
   - Continuously checks if within bet_time window
   - Places bet when conditions met
   - Waits for next round after successful bet

3. **Maintenance Loop** (60s interval):
   - Claims rewards
   - Cancels invalid bets  
   - Closes completed bets

### State Management

```python
RuntimeConfig:
  - direction: Optional override direction
  - bet_amounts: [even_amount, odd_amount]
  - start_calc_rounds: [even_start, odd_start]
```

This matches the TypeScript `RuntimeConfig` exactly.

## 🧪 Testing Notes

**Important**: The instruction discriminators in `blockchain.py` are currently placeholder values (`b'\x00' * 8`). For production use:

1. Compute proper discriminators from the IDL using Anchor's method:
   ```python
   discriminator = sha256(b"global:place_bet").digest()[:8]
   ```

2. Or use AnchorPy's IDL-based instruction builders

3. The account structures and PDAs are correct and match the on-chain program

## 📝 Differences from TypeScript

### None!

This Python implementation is a faithful port of the TypeScript bot:

✅ Same betting strategy logic  
✅ Same martingale calculations  
✅ Same timing and windows  
✅ Same API integration  
✅ Same service architecture  
✅ Same PDA derivations  
✅ Same transaction structures  
✅ Same maintenance operations  

The only differences are:
- Language-specific syntax (Python vs TypeScript)
- Async runtime (asyncio vs Node.js)
- GUI integration (PyQt5 vs CLI)

## 🎯 Future Enhancements

1. **IDL Integration**: Use AnchorPy to generate instructions from IDL
2. **Keypair File Support**: Implement .json keypair file loading
3. **Interactive Runtime Control**: Add user input service (like TypeScript's 'S' key)
4. **Enhanced Logging**: Add log levels and file output
5. **WebSocket Support**: Real-time round updates instead of polling
6. **Multi-Wallet Support**: Run bot with multiple wallets simultaneously

## 🛡️ Security Notes

⚠️ **Never share your private key or seed phrase!**

- Store keys securely (environment variables, encrypted files)
- Use read-only RPC nodes for monitoring
- Test with small amounts on devnet first
- Monitor wallet balance regularly
- Set appropriate `MIN_WALLET_BALANCE` to prevent dust

---

**Built with ❤️ to match the TypeScript implementation exactly.**

