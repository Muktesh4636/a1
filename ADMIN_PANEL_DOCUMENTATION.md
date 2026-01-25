# Admin Panel Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Access & Authentication](#access--authentication)
3. [User Roles & Permissions](#user-roles--permissions)
4. [Admin Pages & Features](#admin-pages--features)
5. [Game Logic & Round Management](#game-logic--round-management)
6. [Dice Control System](#dice-control-system)
7. [User Management](#user-management)
8. [Financial Operations](#financial-operations)
9. [Settings Management](#settings-management)
10. [Technical Implementation](#technical-implementation)

---

## Overview

The Admin Panel is a comprehensive management interface for the Dice Betting Game. It provides full control over game rounds, dice results, user management, financial operations, and system settings.

**Base URL:** `http://159.198.46.36:8232/game-admin/`

**Main Features:**
- Real-time game monitoring and control
- Dice result management (manual and random modes)
- User and wallet management
- Deposit request approval/rejection
- Transaction history tracking
- Game settings configuration
- Admin user management with granular permissions

---

## Access & Authentication

### Login Page
**URL:** `/game-admin/login/`

**Authentication Logic:**
1. User must be authenticated via Django's authentication system
2. User must have admin privileges (`is_staff=True` or `is_superuser=True`)
3. Login uses Django's `authenticate()` and `login()` functions
4. After successful login, redirects to dashboard

**Login Process:**
```python
# From admin_views.py - admin_login()
1. Check if user is already authenticated and is admin → redirect to dashboard
2. On POST:
   - Get username and password from form
   - Authenticate user with Django's authenticate()
   - Check if user is admin using is_admin() helper
   - If admin: login user and redirect to dashboard
   - If not admin: show "no permission" error
   - If invalid credentials: show "invalid username or password" error
```

**Logout:**
- **URL:** `/game-admin/logout/`
- Uses Django's `logout()` function
- Clears session and redirects to login page

---

## User Roles & Permissions

### Role Types

#### 1. Super Admin
- **Check:** `user.is_superuser == True`
- **Access:** Full access to all features
- **Permissions:** All permissions automatically granted
- **Special Access:**
  - Game Settings (only super admins)
  - Admin Management (only super admins)
  - Django Admin panel link

#### 2. Regular Admin (Staff)
- **Check:** `user.is_staff == True`
- **Access:** Controlled by `AdminPermissions` model
- **Permissions:** Granular permission system

### Permission System

**Model:** `AdminPermissions` (One-to-One with User)

**Available Permissions:**
```python
can_view_dashboard = True          # View main dashboard
can_control_dice = True            # Control dice results
can_view_recent_rounds = True      # View recent rounds
can_view_all_bets = True          # View all bets
can_view_wallets = True           # View wallets
can_view_players = True           # View players/users
can_view_deposit_requests = True  # View deposit requests
can_view_transactions = True      # View transactions
can_view_game_settings = False     # Game settings (super admin only)
can_view_admin_management = False  # Admin management (super admin only)
```

**Permission Logic:**
```python
# From admin_utils.py
def is_admin(user):
    - Must be authenticated
    - Must be superuser OR staff
    - If AdminProfile exists, must be active

def has_menu_permission(user, permission_name):
    - Super admins: Always True
    - Regular admins: Check AdminPermissions model
    - Maps permission names to model fields
```

**Permission Checking:**
- Each admin page uses `@admin_required` decorator
- Menu items check permissions before displaying
- Super admin pages use `@super_admin_required` decorator

---

## Admin Pages & Features

### 1. Dashboard (`/game-admin/dashboard/`)

**Purpose:** Main overview of game status and statistics

**Features:**
- Current round information (round ID, status, timer)
- Real-time round data updates (via AJAX polling)
- Overall statistics:
  - Total bets count
  - Total bet amount (₹)
- Game timing settings display:
  - Betting Close Time (default: 30s)
  - Dice Result Time (default: 51s)
  - Round End Time (default: 70s)
- Round status indicators
- Quick access links

**Logic:**
```python
# From admin_views.py - admin_dashboard()
1. Get current round (latest by start_time)
2. Calculate total bets count
3. Calculate total bet amount (sum of all chip_amount)
4. Get game timing settings from database
5. Display round status and timer
6. Real-time updates via admin_dashboard_data endpoint
```

**Real-time Updates:**
- **Endpoint:** `/game-admin/dashboard-data/`
- **Method:** GET
- **Returns:** JSON with current round data, timer, status
- **Polling:** Frontend polls every 2-3 seconds

**Required Permission:** `can_view_dashboard`

---

### 2. Dice Control (`/game-admin/dice-control/`)

**Purpose:** Control dice results for current round

**Features:**
- View current round information
- Set individual dice values (Dice 1-6)
- Set all dice to same value (legacy mode)
- Manual Adjust mode (bypasses time restrictions)
- Toggle between Manual and Random dice modes
- View current round bets by number
- Real-time bet statistics

**Dice Setting Methods:**

#### Method 1: Individual Dice Values
**Endpoint:** `/game-admin/set-individual-dice/`
**Logic:**
```python
1. Get current round from Redis or database
2. Check timer restriction (unless Manual Adjust mode)
3. Collect dice values from POST (dice_1 through dice_6)
4. Validate each value (1-6)
5. Calculate winning number using determine_winning_number():
   - Count frequency of each number (1-6)
   - Find most frequent number(s)
   - If tie: return highest number
6. Update round object with dice values
7. Set dice_result to calculated winning number
8. Update status to 'RESULT'
9. Save to database
10. Update Redis cache
11. Calculate payouts for all bets
12. Broadcast dice_result via WebSocket
```

#### Method 2: Set All Dice to Same Value (Legacy)
**Endpoint:** `/game-admin/set-dice/`
**Logic:**
```python
1. Get single result value (1-6)
2. Set all 6 dice to same value
3. Set dice_result to that value
4. Calculate payouts
5. Broadcast result
```

**Manual Adjust Mode:**
- **Purpose:** Allows setting dice values even after dice_result_time
- **Use Case:** Corrections, testing, manual overrides
- **Logic:** Bypasses timer restrictions, allows partial updates

**Dice Mode Toggle:**
- **Endpoint:** `/game-admin/toggle-dice-mode/`
- **Modes:** `manual` or `random`
- **Storage:** `GameSettings` model with key `dice_mode`
- **Effect:** Controls whether dice auto-roll or require manual setting

**Timer Restrictions:**
- Normal mode: Can only set dice before `DICE_RESULT_TIME` (default: 51s)
- Manual Adjust mode: Can set dice at any time
- Timer calculated from round start_time

**Required Permission:** `can_control_dice`

---

### 3. Recent Rounds (`/game-admin/recent-rounds/`)

**Purpose:** View history of completed rounds

**Features:**
- List of recent rounds (paginated)
- Round details:
  - Round ID
  - Status
  - Start time, result time, end time
  - Dice result (winning number)
  - Individual dice values (Dice 1-6)
  - Total bet amount
  - Total payouts
- Click round to view details
- Search and filter options

**Logic:**
```python
# From admin_views.py - recent_rounds()
1. Get rounds ordered by -start_time (newest first)
2. Paginate results (default: 20 per page)
3. Calculate stats for each round:
   - Total bets count
   - Total bet amount
   - Total payouts
4. Display round list with summary
```

**Round Details Page:**
- **URL:** `/game-admin/round/<round_id>/`
- Shows complete round information
- Lists all bets for that round
- Shows bet statistics by number
- Displays transaction history

**Required Permission:** `can_view_recent_rounds`

---

### 4. All Bets (`/game-admin/all-bets/`)

**Purpose:** View all bets across all rounds

**Features:**
- List of all bets (latest 100)
- Bet information:
  - User username
  - Round ID
  - Number bet on (1-6)
  - Bet amount (₹)
  - Payout amount (₹)
  - Win/Loss status
  - Created timestamp
- Statistics:
  - Total bets count
  - Total bets amount (₹)
  - Total payouts (₹)
  - Total winners count

**Logic:**
```python
# From admin_views.py - all_bets()
1. Get all bets with select_related('user', 'round')
2. Limit to 100 most recent
3. Calculate aggregate statistics:
   - Total count
   - Sum of chip_amount
   - Sum of payout_amount
   - Count of winners (is_winner=True)
```

**Required Permission:** `can_view_all_bets`

---

### 5. Wallets (`/game-admin/wallets/`)

**Purpose:** Manage and view user wallets

**Features:**
- List of all user wallets
- Wallet information:
  - Username
  - Phone number
  - Balance (₹)
  - Last transaction date
- Filters:
  - All wallets
  - Wallets with balance (> 0)
  - Zero balance wallets
- Search by username or phone number
- Sort options:
  - Balance (high to low / low to high)
  - Username (A-Z / Z-A)
- Statistics:
  - Total wallets
  - Total balance across all wallets
  - Active wallets count
  - Zero balance wallets count

**Logic:**
```python
# From admin_views.py - wallets()
1. Get filter parameters (balance_filter, search_query, sort_by)
2. Build query with filters:
   - Balance filter: all/has_balance/zero
   - Search: username or phone_number contains query
   - Sort: by balance or username
3. Calculate statistics before filtering
4. Return filtered wallets
```

**Required Permission:** `can_view_wallets`

---

### 6. Players (`/game-admin/players/`)

**Purpose:** Manage users/players

**Features:**
- List of all users
- User information:
  - Username
  - Email
  - Phone number
  - Registration date
  - Account status (Active/Inactive)
  - Wallet balance
- Filters:
  - Active users (default)
  - Inactive users
  - All users
- Search by username, email, or phone
- Pagination
- Click user to view details

**User Details Page:**
- **URL:** `/game-admin/user/<user_id>/`
- Complete user profile
- Wallet balance and transaction history
- Betting history
- Deposit history
- Statistics:
  - Total bet amount
  - Total payouts
  - Net profit/loss

**Logic:**
```python
# From admin_views.py - players()
1. Get status filter (default: 'active')
2. Get search query
3. Get page number for pagination
4. Build query:
   - Filter by is_active status
   - Search in username, email, phone_number
5. Paginate results (20 per page)
6. Calculate total counts
```

**Required Permission:** `can_view_players`

---

### 7. Deposit Requests (`/game-admin/deposit-requests/`)

**Purpose:** Approve or reject user deposit requests

**Features:**
- List of all deposit requests
- Request information:
  - User
  - Amount (₹)
  - Payment link
  - Payment reference
  - Screenshot
  - Status (PENDING/APPROVED/REJECTED)
  - Created date
  - Processed date and admin
- Statistics:
  - Total requests
  - Pending requests
  - Approved requests
  - Rejected requests
  - Total amount (₹)
  - Pending amount (₹)
- Actions:
  - Approve deposit
  - Reject deposit (with reason)

**Approve Deposit Logic:**
```python
# From admin_views.py - approve_deposit()
1. Get deposit request by ID
2. Check if already processed
3. Update status to 'APPROVED'
4. Set processed_at = now
5. Set processed_by = current admin user
6. Credit user's wallet:
   - Get user's wallet
   - Add deposit amount to balance
   - Create Transaction record:
     - Type: 'DEPOSIT'
     - Amount: deposit amount
     - Balance before/after
7. Save deposit request
8. Show success message
```

**Reject Deposit Logic:**
```python
# From admin_views.py - reject_deposit()
1. Get deposit request by ID
2. Get rejection reason from form
3. Update status to 'REJECTED'
4. Set processed_at = now
5. Set processed_by = current admin user
6. Set rejection_note (if provided)
7. Save deposit request
8. Show success message
```

**Required Permission:** `can_view_deposit_requests`

---

### 8. Transactions (`/game-admin/transactions/`)

**Purpose:** View all financial transactions

**Features:**
- List of all transactions
- Transaction information:
  - User
  - Type (DEPOSIT/WITHDRAW/BET/WIN)
  - Amount (₹)
  - Balance before transaction
  - Balance after transaction
  - Timestamp
- Statistics:
  - Total deposits (₹)
  - Total withdrawals (₹)
  - Total bets (₹)
  - Total wins/payouts (₹)
- Filter by transaction type
- Search by username

**Transaction Types:**
- **DEPOSIT:** User adds money to wallet
- **WITHDRAW:** User withdraws money (if implemented)
- **BET:** User places a bet (deducted from wallet)
- **WIN:** User wins a bet (added to wallet)

**Logic:**
```python
# From admin_views.py - transactions()
1. Get transaction type filter
2. Get search query
3. Build query with filters
4. Calculate statistics:
   - Sum deposits (type='DEPOSIT')
   - Sum withdrawals (type='WITHDRAW')
   - Sum bets (type='BET')
   - Sum wins (type='WIN')
5. Return filtered transactions
```

**Required Permission:** `can_view_transactions`

---

### 9. Game Settings (`/game-admin/game-settings/`)

**Purpose:** Configure game timing and behavior (Super Admin only)

**Features:**
- Edit game timing settings:
  - **BETTING_CLOSE_TIME:** When betting closes (default: 30 seconds)
  - **DICE_ROLL_TIME:** When dice roll animation starts (default: 19 seconds)
  - **DICE_RESULT_TIME:** When dice result is announced (default: 51 seconds)
  - **ROUND_END_TIME:** Total round duration (default: 70 seconds)
- Settings are stored in `GameSettings` model
- Changes take effect immediately (no restart required)
- Settings are read dynamically on each round iteration

**Settings Logic:**
```python
# From admin_views.py - game_settings()
1. Get all settings from database
2. Display current values in form
3. On POST:
   - Update or create GameSettings records
   - Save to database
   - Settings are read fresh on each game timer iteration
```

**How Settings Work:**
- Settings stored in `GameSettings` model (key-value pairs)
- Read using `get_game_setting(key, default)` function
- Function always reads fresh from database (no caching)
- Game timer reads settings on each iteration
- Changes apply to next round automatically

**Round Timing Flow:**
```
0s - ROUND_START (BETTING status)
↓
BETTING_CLOSE_TIME (30s) - Betting closes (CLOSED status)
↓
DICE_ROLL_TIME (19s) - Dice roll animation starts
↓
DICE_RESULT_TIME (51s) - Dice result announced (RESULT status)
↓
ROUND_END_TIME (70s) - Round ends, new round starts
```

**Required Permission:** `can_view_game_settings` (Super Admin only)

---

### 10. Admin Management (`/game-admin/admin-management/`)

**Purpose:** Create and manage admin users with permissions (Super Admin only)

**Features:**
- List of all admin users (staff users)
- Admin information:
  - Username
  - Email
  - Superuser status
  - Permissions granted
  - Date joined
- Actions:
  - Create new admin
  - Edit admin permissions
  - Delete admin

**Create Admin Logic:**
```python
# From admin_views.py - create_admin()
1. On POST:
   - Get username, email, password
   - Create User with is_staff=True
   - Create AdminPermissions record
   - Set permissions from form checkboxes
   - Save user and permissions
2. Redirect to admin management page
```

**Edit Admin Logic:**
```python
# From admin_views.py - edit_admin()
1. Get admin user by ID
2. Get or create AdminPermissions
3. On POST:
   - Update user info (username, email, password if provided)
   - Update permissions from checkboxes
   - Save changes
4. Display edit form with current values
```

**Delete Admin Logic:**
```python
# From admin_views.py - delete_admin()
1. Get admin user by ID
2. Prevent deleting superuser
3. Delete AdminPermissions record
4. Set user.is_staff = False (don't delete user)
5. Save user
6. Show success message
```

**Required Permission:** `can_view_admin_management` (Super Admin only)

---

## Game Logic & Round Management

### Round Lifecycle

**Round States:**
1. **WAITING:** Round created but not started
2. **BETTING:** Betting is open (0 to BETTING_CLOSE_TIME seconds)
3. **CLOSED:** Betting closed, waiting for result (BETTING_CLOSE_TIME to DICE_RESULT_TIME)
4. **RESULT:** Result announced (DICE_RESULT_TIME to ROUND_END_TIME)
5. **COMPLETED:** Round ended, new round can start

**Round Creation:**
- Created automatically by game timer
- Round ID format: `R{timestamp}` (e.g., R1705123456)
- Status starts as 'BETTING'
- Timer starts at 1 second

**Round Completion:**
- When timer reaches ROUND_END_TIME
- Status changes to 'COMPLETED'
- end_time is set
- New round is created automatically

### Winning Number Calculation

**Logic:**
```python
# From utils.py - determine_winning_number()
1. Count frequency of each number (1-6) in dice values
2. Find maximum frequency
3. Get all numbers with max frequency (ties)
4. Return highest number among ties

Example:
- Dice: [1, 2, 2, 3, 3, 3]
- Frequencies: {1:1, 2:2, 3:3}
- Max frequency: 3
- Winning number: 3

Example with tie:
- Dice: [1, 1, 2, 2, 3, 4]
- Frequencies: {1:2, 2:2, 3:1, 4:1}
- Max frequency: 2
- Tied numbers: [1, 2]
- Winning number: 2 (highest)
```

### Payout Calculation

**Logic:**
```python
# From views.py - calculate_payouts()
1. Get all bets for the round
2. Count frequency of each number in dice values
3. Determine winning number (most frequent, highest on tie)
4. For each bet:
   - If bet.number == winning_number:
     - Count how many times winning_number appears in dice
     - Calculate payout based on frequency:
       - 1 occurrence: 2x bet amount
       - 2 occurrences: 3x bet amount
       - 3 occurrences: 4x bet amount
       - 4 occurrences: 5x bet amount
       - 5 occurrences: 6x bet amount
       - 6 occurrences: 7x bet amount
     - Set is_winner = True
     - Set payout_amount = calculated payout
     - Credit user's wallet with payout
     - Create WIN transaction
   - Else:
     - Set is_winner = False
     - Set payout_amount = 0
5. Save all bets
```

**Payout Ratios:**
- Based on frequency of winning number in dice
- Higher frequency = higher payout multiplier
- Stored in settings as `PAYOUT_RATIOS`

---

## Dice Control System

### Dice Modes

#### Manual Mode
- Admin must manually set dice values
- Dice values set via Dice Control page
- No automatic rolling
- Full control over results

#### Random Mode
- Dice values generated automatically
- Uses `generate_random_dice_values()` function
- Random values for each of 6 dice
- Winning number calculated from random values

**Mode Toggle:**
- Stored in `GameSettings` with key `dice_mode`
- Values: `'manual'` or `'random'`
- Can be toggled from Dice Control page

### Setting Dice Values

**Individual Dice Setting:**
- Set each of 6 dice independently (1-6)
- Values can be different
- Winning number calculated from all 6 dice
- Supports partial updates in Manual Adjust mode

**All Dice Same Value (Legacy):**
- Set all 6 dice to same number
- Used for simple testing
- Still supported for backward compatibility

**Time Restrictions:**
- Normal mode: Can only set before DICE_RESULT_TIME
- Manual Adjust mode: Can set at any time
- Timer checked from round start_time

**Validation:**
- Each dice value must be 1-6
- All 6 values required (unless Manual Adjust mode)
- Invalid values show error message

---

## User Management

### User Model
- Extends Django's User model
- Fields: username, email, password, phone_number
- Related models: Wallet, Bet, Transaction, DepositRequest

### Wallet Management
- Each user has one Wallet
- Wallet created automatically via signal
- Balance stored as Decimal (2 decimal places)
- Balance updated on:
  - Deposit approval
  - Bet placement
  - Bet win (payout)

### User Status
- **Active:** User can login and play
- **Inactive:** User account disabled
- Controlled by `user.is_active` field

### User Actions
- View user details
- View betting history
- View transaction history
- View wallet balance
- View deposit requests

---

## Financial Operations

### Wallet Operations

**Balance Updates:**
- Deposits: Added when deposit approved
- Bets: Deducted when bet placed
- Wins: Added when bet wins
- All changes create Transaction records

**Transaction Types:**
- **DEPOSIT:** Money added to wallet
- **WITHDRAW:** Money removed (if implemented)
- **BET:** Money deducted for bet
- **WIN:** Money added from winning bet

**Transaction Record:**
```python
Transaction model:
- user: ForeignKey to User
- transaction_type: CharField (DEPOSIT/WITHDRAW/BET/WIN)
- amount: DecimalField
- balance_before: DecimalField
- balance_after: DecimalField
- created_at: DateTimeField
- related_object: GenericForeignKey (to Bet or DepositRequest)
```

### Deposit Request Flow

1. **User Submits Deposit:**
   - User uploads screenshot
   - Provides payment link and reference
   - Amount specified
   - Status: PENDING

2. **Admin Reviews:**
   - View deposit request
   - See screenshot, amount, payment details

3. **Admin Approves:**
   - Status changes to APPROVED
   - User's wallet credited
   - Transaction record created
   - processed_by set to admin user

4. **Admin Rejects:**
   - Status changes to REJECTED
   - Rejection note can be added
   - No wallet credit
   - Transaction record created (optional)

---

## Settings Management

### Game Settings Model
- Key-value storage
- Settings stored in database
- Can be updated via admin panel
- Read dynamically (no caching)

### Available Settings

**Timing Settings:**
- `BETTING_CLOSE_TIME`: Seconds when betting closes (default: 30)
- `DICE_ROLL_TIME`: Seconds when dice roll starts (default: 19)
- `DICE_RESULT_TIME`: Seconds when result announced (default: 51)
- `ROUND_END_TIME`: Total round duration (default: 70)

**Mode Settings:**
- `dice_mode`: 'manual' or 'random'

**Payout Settings:**
- `PAYOUT_RATIOS`: Dictionary mapping frequency to multiplier
  - Stored in settings.py (not in database)

### Settings Reading Logic

```python
# From utils.py - get_game_setting()
1. Query GameSettings model for key
2. If found: return value (convert to int if numeric)
3. If not found: fallback to settings.py GAME_SETTINGS dict
4. Always reads fresh (no caching)
```

**Why No Caching:**
- Settings can change during runtime
- Game timer reads settings on each iteration
- Changes should apply immediately
- No server restart needed

---

## Technical Implementation

### Architecture

**Backend:**
- Django framework
- Django REST Framework for APIs
- Django Channels for WebSocket
- Redis for caching and channel layer
- PostgreSQL/SQLite database

**Frontend:**
- Server-side rendered HTML templates
- JavaScript for real-time updates
- AJAX polling for dashboard updates
- WebSocket for game events

### Database Models

**GameRound:**
- Stores round information
- Fields: round_id, status, dice_result, dice_1-6, timestamps
- Related: Bet, DiceResult

**Bet:**
- Stores user bets
- Fields: user, round, number, chip_amount, payout_amount, is_winner
- Unique constraint: (user, round, number)

**AdminPermissions:**
- Stores admin user permissions
- One-to-One with User
- Boolean fields for each permission

**GameSettings:**
- Key-value storage for settings
- Fields: key, value, description

**Transaction:**
- Financial transaction history
- Fields: user, type, amount, balance_before, balance_after

**DepositRequest:**
- User deposit requests
- Fields: user, amount, screenshot, status, processed_by

### Redis Integration

**Usage:**
- Store current round data
- Store round timer
- Channel layer for WebSocket
- Fast read/write for real-time updates

**Round Data Structure:**
```json
{
  "round_id": "R1705123456",
  "status": "BETTING",
  "start_time": "2025-01-12T10:30:00Z",
  "timer": 25,
  "dice_result": null,
  "dice_1": null,
  "dice_2": null,
  ...
}
```

**Sync Logic:**
- Database is source of truth
- Redis synced from database
- Timer calculated from start_time
- Updates happen in both places

### WebSocket Broadcasting

**Channel Group:** `game_room`

**Message Types:**
- `game_start`: New round started
- `game_timer`: Timer update
- `dice_roll`: Dice roll animation start
- `dice_result`: Dice result announced
- `game_end`: Round ended

**Broadcasting Logic:**
```python
# From admin_views.py and start_game_timer.py
1. Get channel layer
2. Send message to 'game_room' group
3. All connected clients receive update
4. Frontend updates UI accordingly
```

### Security

**Authentication:**
- Django session-based authentication
- CSRF protection enabled
- Login required for all admin pages

**Authorization:**
- Permission checks on every page
- Decorators: `@admin_required`, `@super_admin_required`
- Menu items hidden based on permissions

**Data Protection:**
- User passwords hashed (Django's password hashers)
- Sensitive operations logged
- Admin actions tracked (processed_by fields)

### Error Handling

**Common Errors:**
- Invalid dice values: Shows error, redirects back
- Timer restrictions: Shows error with time limit
- No active round: Shows error message
- Permission denied: Redirects to login or shows error

**Error Messages:**
- Displayed via Django messages framework
- Shown at top of page
- Auto-dismiss after few seconds (via JavaScript)

---

## API Endpoints

### Admin Endpoints

**Authentication:**
- `POST /game-admin/login/` - Admin login
- `GET /game-admin/logout/` - Admin logout

**Dashboard:**
- `GET /game-admin/dashboard/` - Main dashboard
- `GET /game-admin/dashboard-data/` - Real-time data (JSON)

**Dice Control:**
- `GET /game-admin/dice-control/` - Dice control page
- `POST /game-admin/set-dice/` - Set all dice to same value
- `POST /game-admin/set-individual-dice/` - Set individual dice
- `POST /game-admin/toggle-dice-mode/` - Toggle manual/random mode

**Rounds:**
- `GET /game-admin/recent-rounds/` - List recent rounds
- `GET /game-admin/round/<round_id>/` - Round details

**Users:**
- `GET /game-admin/players/` - List players
- `GET /game-admin/user/<user_id>/` - User details

**Financial:**
- `GET /game-admin/wallets/` - List wallets
- `GET /game-admin/deposit-requests/` - List deposit requests
- `POST /game-admin/deposit-requests/<id>/approve/` - Approve deposit
- `POST /game-admin/deposit-requests/<id>/reject/` - Reject deposit
- `GET /game-admin/transactions/` - List transactions
- `GET /game-admin/all-bets/` - List all bets

**Settings:**
- `GET /game-admin/game-settings/` - Game settings page
- `POST /game-admin/game-settings/` - Update settings

**Admin Management:**
- `GET /game-admin/admin-management/` - List admins
- `GET /game-admin/admin-management/create/` - Create admin form
- `POST /game-admin/admin-management/create/` - Create admin
- `GET /game-admin/admin-management/edit/<id>/` - Edit admin form
- `POST /game-admin/admin-management/edit/<id>/` - Update admin
- `POST /game-admin/admin-management/delete/<id>/` - Delete admin

---

## Common Workflows

### Workflow 1: Setting Dice Result (Manual Mode)

1. Navigate to Dice Control page
2. View current round timer and status
3. If timer < DICE_RESULT_TIME:
   - Set individual dice values (1-6 for each)
   - Click "Set Dice Values"
4. System calculates winning number from dice values
5. Payouts calculated automatically
6. Result broadcasted via WebSocket
7. Users see result and receive payouts

### Workflow 2: Approving Deposit

1. Navigate to Deposit Requests page
2. View pending requests
3. Review screenshot and payment details
4. Click "Approve" on request
5. System:
   - Updates request status to APPROVED
   - Credits user's wallet
   - Creates DEPOSIT transaction
   - Records admin who approved
6. User's balance updated immediately

### Workflow 3: Creating New Admin

1. Navigate to Admin Management (Super Admin only)
2. Click "Create Admin"
3. Fill form:
   - Username
   - Email
   - Password
   - Select permissions
4. Submit form
5. System:
   - Creates User with is_staff=True
   - Creates AdminPermissions record
   - Sets selected permissions
6. New admin can login immediately

### Workflow 4: Changing Game Timing

1. Navigate to Game Settings (Super Admin only)
2. View current timing values
3. Update values (e.g., change BETTING_CLOSE_TIME to 35s)
4. Save settings
5. Settings stored in database
6. Game timer reads new values on next iteration
7. Changes apply to next round automatically

---

## Best Practices

### Admin Operations

1. **Dice Control:**
   - Set dice values before DICE_RESULT_TIME
   - Use Manual Adjust mode only when necessary
   - Verify dice values before confirming

2. **Deposit Approval:**
   - Always verify screenshot matches amount
   - Check payment reference
   - Approve only verified deposits

3. **User Management:**
   - Grant minimal necessary permissions
   - Regularly review admin users
   - Deactivate unused admin accounts

4. **Settings:**
   - Test timing changes in staging first
   - Ensure ROUND_END_TIME > DICE_RESULT_TIME > BETTING_CLOSE_TIME
   - Document any custom settings

### Security

1. **Access Control:**
   - Use strong passwords for admin accounts
   - Regularly rotate admin passwords
   - Grant permissions based on role

2. **Data Protection:**
   - Never share admin credentials
   - Log out after session
   - Monitor admin actions

3. **Backup:**
   - Regular database backups
   - Backup before major changes
   - Test restore procedures

---

## Troubleshooting

### Common Issues

**Issue: Cannot set dice values**
- **Cause:** Timer exceeded DICE_RESULT_TIME
- **Solution:** Use Manual Adjust mode or wait for next round

**Issue: Settings not applying**
- **Cause:** Settings cached or not saved
- **Solution:** Verify settings saved in database, check game timer is reading fresh

**Issue: Permissions not working**
- **Cause:** AdminPermissions not created
- **Solution:** Edit admin user, permissions will be created automatically

**Issue: WebSocket not updating**
- **Cause:** Channel layer not configured or Redis down
- **Solution:** Check Redis connection, verify channel layer settings

**Issue: Payouts not calculated**
- **Cause:** Dice values not set or incomplete
- **Solution:** Ensure all 6 dice values are set before DICE_RESULT_TIME

---

## Conclusion

This admin panel provides comprehensive control over the dice betting game. All features are designed with security, usability, and real-time updates in mind. The permission system allows fine-grained access control, while the game logic ensures fair and accurate payouts.

For technical support or questions, refer to the codebase or contact the development team.

