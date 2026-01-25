# Game Rules - Complete Guide

## Overview
This is a 6-dice probability-based betting game. Players place bets on one or more numbers (1–6). After placing bets, six dice are rolled simultaneously. Winnings depend on how many times a chosen number appears.

---

## Game Mechanics

### Dice System
- **Number of Dice**: 6 dice are rolled per round
- **Dice Values**: Each die shows a number from 1 to 6
- **Winning Number**: Determined by the number(s) that appear most frequently across all 6 dice. If multiple numbers have the same highest frequency, all of them are winners.

**Example:**
- Dice results: [1, 1, 1, 2, 3, 4] → Winning number: **1** (appears 3 times)
- Dice results: [2, 2, 3, 3, 4, 4] → Winning number: **4** (all appear twice, highest wins)
- Dice results: [5, 5, 5, 6, 6, 6] → Winning number: **6** (both appear 3 times, highest wins)

### Round Structure
Each round follows a timed sequence:

1. **Betting Phase** (0-30 seconds)
   - Players can place, modify, or remove bets
   - All bets must be placed before this window closes
   - Wallet balance is deducted immediately when placing bets

2. **Closed Phase** (30-51 seconds)
   - Betting is closed
   - No bets can be placed, modified, or removed
   - Round is being processed

3. **Result Phase** (51-70 seconds)
   - Dice results are revealed
   - Winning bets are calculated and paid out
   - Players can view round results

4. **Round End** (70 seconds)
   - Round completes
   - New round automatically starts

### Default Timing (Configurable)
- **Betting Close Time**: 30 seconds
- **Dice Roll Time**: 51 seconds
- **Round End Time**: 70 seconds

---

## Betting Rules

### Available Numbers
Players can bet on any number from **1 to 6**.

### Placing Bets
- Each player can bet on **one or multiple numbers** (1 to 6)
- Each bet has a **fixed stake amount**
- Bets must be placed **before the dice roll**
- Once the roll starts, **no bet can be modified**

### Betting Window
- Bets can only be placed during the **Betting Phase** (0-30 seconds)
- After 30 seconds, no new bets are accepted
- Existing bets can be removed (refunded) only during the Betting Phase

### Removing Bets
- Players can remove their bet on any number before the betting window closes
- When a bet is removed, the full bet amount is refunded to the wallet
- Refunds are processed immediately
- After betting closes, bets cannot be removed

---

## Winning Conditions

### How to Win
A player wins only if their selected number appears **at least 2 times** in the 6 dice roll.

### Winning Conditions Table
| Occurrences of Selected Number | Result |
|--------------------------------|--------|
| 0 times | Loss |
| 1 time | Loss |
| 2 times | Win (2× payout) |
| 3 times | Win (3× payout) |
| 4 times | Win (4× payout) |
| 5 times | Win (5× payout) |
| 6 times | Win (6× payout) |

### Payout Calculation
**Payout Formula:**
```
Total Return = Bet Amount × Number of Occurrences
Player Receives = Total Return × 0.90 (after 10% commission)
```

**Examples:**
- **6 of a kind** (all 6 dice show the same number):
  - Bet ₹100 → Total Return ₹600 → Player receives ₹540 (after 10% commission)

- **5 of a kind**:
  - Bet ₹100 → Total Return ₹500 → Player receives ₹450 (after 10% commission)

- **4 of a kind**:
  - Bet ₹100 → Total Return ₹400 → Player receives ₹360 (after 10% commission)

- **3 of a kind**:
  - Bet ₹100 → Total Return ₹300 → Player receives ₹270 (after 10% commission)

- **2 of a kind**:
  - Bet ₹100 → Total Return ₹200 → Player receives ₹180 (after 10% commission)

**Important Notes:**
- You **must have at least 2 occurrences** of your selected number to win
- If your number appears 0 or 1 time, you lose your bet amount
- Higher occurrences = Higher payout multiplier
- The multiplier equals the exact number of times your number appears

### Multiple Number Betting
Players may bet on multiple numbers in the same round.

**Example:**
A player bets:
- ₹100 on 3
- ₹100 on 5
- ₹100 on 6

If results are:
- 3 appears twice → wins ₹200
- 5 appears twice → wins ₹200
- 6 appears twice → wins ₹200

**Total return = ₹600**

### Commission (10%)
- From each total payout, **10% commission** is deducted
- **90%** goes to the player, **10%** is retained by the house
- Example: ₹200 total payout → Player receives ₹180, Commission: ₹20
- The commission is deducted from the payout amount, not the original bet

### Losing Bets
- If a player's bet number does not match the winning number, the bet loses
- The bet amount is not refunded
- Players lose the full bet amount

---

## Wallet & Transactions

### Wallet Balance
- Each player has a wallet with a balance
- Balance is displayed in real-time
- Balance is deducted when placing bets
- Balance increases when receiving payouts or refunds

### Transaction Types
1. **BET**: Money deducted when placing a bet
2. **WIN**: Money added when winning a bet
3. **REFUND**: Money added when removing a bet
4. **DEPOSIT**: Money added through deposits
5. **WITHDRAW**: Money deducted through withdrawals

### Minimum Balance
- Players must have sufficient balance to place bets
- If balance is insufficient, bets cannot be placed
- Players can deposit funds to increase their balance

---

## Round Information

### Round ID
Each round has a unique ID (format: R{timestamp})

### Round Status
- **BETTING**: Betting window is open
- **CLOSED**: Betting window is closed, awaiting results
- **RESULT**: Results are available
- **COMPLETED**: Round has ended

### Round Statistics
- Total number of bets placed
- Total amount wagered
- Number of winners
- Total payouts

---

## Player Actions

### During Betting Phase
- ✅ Place bets on numbers (1-6)
- ✅ Increase bet amount on existing bets
- ✅ Remove bets (get refund)
- ✅ View current round information
- ✅ View wallet balance

### During Closed/Result Phase
- ❌ Cannot place new bets
- ❌ Cannot remove bets
- ✅ View round results
- ✅ View winning numbers
- ✅ View payout information
- ✅ View transaction history

---

## Fair Play Rules

### Betting Restrictions
- One bet per number per round per player
- Bets must be placed during the betting window
- Insufficient balance prevents betting
- Cannot bet after the betting window closes

### Result Fairness
- Dice results are determined fairly
- Winning number is calculated based on actual dice frequencies
- All players see the same results for each round
- Payouts are calculated automatically based on the rules

### Account Security
- Players must be logged in to place bets
- Each player can only see and manage their own bets
- Transaction history is private to each player

---

## Admin Controls

Administrators can:
- Set dice results manually (if manual mode is enabled)
- View all bets placed
- View all players and their balances
- Approve/reject deposit requests
- Manage game settings (timing, payout ratios)
- View transaction history

---

## Tips for Players

1. **Manage Your Bankroll**: Don't bet more than you can afford to lose
2. **Understand the Odds**: The winning number is determined by frequency, not probability
3. **Time Your Bets**: Place bets early in the betting window to avoid missing the deadline
4. **Diversify**: You can bet on multiple numbers to increase your chances of winning
5. **Check Results**: Always check round results to understand your wins/losses
6. **Monitor Your Balance**: Keep track of your wallet balance and transactions

---

## Configuration

All game settings can be configured by administrators:
- Betting window duration
- Round duration
- Payout ratios
- Minimum bet amounts
- Dice roll timing

These settings may be adjusted to change game dynamics.

---

## Support

For questions or issues:
- Contact support through the platform
- Check your transaction history for bet details
- Review round results for payout information
- Contact administrators for account-related issues

---

**Last Updated**: January 2025

