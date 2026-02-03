# Gundu ata Project - Complete Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Setup & Installation](#setup--installation)
6. [Configuration](#configuration)
7. [API Documentation](#api-documentation)
8. [Admin Panel](#admin-panel)
9. [Frontend](#frontend)
10. [WebSocket Communication](#websocket-communication)
11. [Game Logic](#game-logic)
12. [Database Models](#database-models)
13. [Deployment](#deployment)
14. [Development Guidelines](#development-guidelines)
15. [Troubleshooting](#troubleshooting)
16. [Security](#security)

---

## Project Overview

### Description
A real-time multiplayer dice betting game platform where users can place bets on dice outcomes. The system includes a comprehensive admin panel for game management, user administration, and financial operations.

### Key Features
- **Real-time Game Rounds**: Automated game rounds with betting windows
- **Dice Control**: Manual or random dice result generation
- **User Management**: Registration, authentication, wallet management
- **Deposit System**: Deposit requests with proof upload and admin approval
- **Admin Panel**: Comprehensive management interface with granular permissions
- **WebSocket Support**: Real-time updates for game state and results
- **Transaction History**: Complete audit trail of all financial operations

### Production URL
- **Backend API**: `http://72.61.254.71:8232/`
- **Admin Panel**: `http://72.61.254.71:8232/game-admin/`
- **Frontend**: Configured separately

---

## Architecture

### System Architecture

```
┌─────────────────┐
│   Frontend      │  React + Vite
│   (React)       │  WebSocket Client
└────────┬────────┘
         │
         │ HTTP/WebSocket
         │
┌────────▼─────────────────────────┐
│   Django Backend (Daphne)       │
│   ┌───────────────────────────┐ │
│   │ REST API                  │ │
│   │ - Authentication          │ │
│   │ - Game Operations         │ │
│   │ - User Management         │ │
│   └───────────────────────────┘ │
│   ┌───────────────────────────┐ │
│   │ WebSocket (Channels)      │ │
│   │ - Real-time Updates       │ │
│   │ - Game State Broadcast    │ │
│   └───────────────────────────┘ │
│   ┌───────────────────────────┐ │
│   │ Game Timer Service         │ │
│   │ - Round Management         │ │
│   │ - Status Transitions       │ │
│   └───────────────────────────┘ │
└────────┬─────────────────────────┘
         │
    ┌────┴────┬──────────────┐
    │         │              │
┌───▼───┐ ┌──▼────┐  ┌──────▼────┐
│Redis  │ │PostgreSQL│ │  Media   │
│Cache  │ │Database  │ │  Files   │
└───────┘ └─────────┘ └──────────┘
```

### Component Overview

1. **Django Backend**: Main application server using Daphne (ASGI)
2. **Game Timer Service**: Separate service managing game rounds and timing
3. **Redis**: Channel layer for WebSocket communication and caching
4. **PostgreSQL**: Primary database (SQLite for development)
5. **Frontend**: React application with WebSocket client

---

## Technology Stack

### Backend
- **Framework**: Django 4.2.7
- **ASGI Server**: Daphne 4.0.0
- **API**: Django REST Framework 3.14.0
- **Authentication**: JWT (djangorestframework-simplejwt 5.3.1)
- **WebSocket**: Django Channels 4.0.0
- **Channel Layer**: channels-redis 4.1.0
- **Database**: PostgreSQL 15 (production), SQLite (development)
- **Cache**: Redis 7
- **Image Processing**: Pillow 10.1.0
- **Environment**: python-dotenv 1.0.0

### Frontend
- **Framework**: React 18.2.0
- **Build Tool**: Vite 5.0.8
- **Styling**: Tailwind CSS 3.4.0
- **Animations**: Framer Motion 10.16.16
- **WebSocket**: Native WebSocket API
- **HTTP Client**: Fetch API

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions (optional)
- **Server**: Linux VPS

---

## Project Structure

```
Ata3/
├── backend/                    # Django backend application
│   ├── accounts/               # User account management
│   │   ├── models.py          # User, Wallet, DepositRequest models
│   │   ├── views.py            # Auth & deposit endpoints
│   │   ├── serializers.py      # DRF serializers
│   │   └── signals.py          # Post-save signals
│   ├── game/                   # Game logic
│   │   ├── models.py           # GameRound, Bet, DiceResult models
│   │   ├── views.py            # Game API endpoints
│   │   ├── admin_views.py      # Admin panel views
│   │   ├── consumers.py        # WebSocket consumers
│   │   ├── routing.py          # WebSocket routing
│   │   ├── utils.py            # Game utilities
│   │   ├── management/         # Django management commands
│   │   │   └── commands/
│   │   │       ├── start_game_timer.py
│   │   │       └── protect_users.py
│   │   └── templates/admin/    # Admin panel templates
│   ├── dice_game/              # Django project settings
│   │   ├── settings.py         # Main settings
│   │   ├── urls.py             # URL routing
│   │   ├── asgi.py             # ASGI configuration
│   │   └── wsgi.py             # WSGI configuration
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile             # Docker image definition
│   └── env.example            # Environment variables template
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── services/           # API & WebSocket services
│   │   └── main.jsx            # Entry point
│   ├── package.json            # Node dependencies
│   └── vite.config.js          # Vite configuration
├── scripts/                    # Utility scripts
│   ├── deploy_to_server.sh     # Deployment script
│   ├── create_database.sh      # Database setup
│   └── ...
├── docker-compose.yml          # Docker Compose configuration
├── ADMIN_PANEL_DOCUMENTATION.md  # Admin panel docs
├── docs/
│   └── GAME_RULES.md          # Game rules documentation
└── PROJECT_DOCUMENTATION.md    # This file
```

---

## Setup & Installation

### Prerequisites
- Docker & Docker Compose
- Git
- (Optional) Python 3.12+ for local development
- (Optional) Node.js 18+ for frontend development

### Quick Start with Docker

1. **Clone the repository**
```bash
git clone <repository-url>
cd Ata3
```

2. **Configure environment variables**
```bash
cp backend/env.example backend/.env
# Edit backend/.env with your settings
```

3. **Start services**
```bash
docker compose up -d
```

4. **Run migrations**
```bash
docker compose exec web python manage.py migrate
```

5. **Create superuser**
```bash
docker compose exec web python manage.py createsuperuser
```

6. **Start game timer**
```bash
docker compose exec game_timer python manage.py start_game_timer
```

### Local Development Setup

#### Backend

1. **Create virtual environment**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp env.example .env
# Edit .env file
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Start development server**
```bash
python manage.py runserver
```

7. **Start game timer** (in separate terminal)
```bash
python manage.py start_game_timer
```

#### Frontend

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Start development server**
```bash
npm run dev
```

3. **Build for production**
```bash
npm run build
```

---

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=72.61.254.71,localhost,127.0.0.1

# Database
USE_SQLITE=False  # Set True for SQLite, False for PostgreSQL
DB_NAME=dice_game
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=db  # Use 'localhost' for local development
DB_PORT=5432

# Redis
REDIS_HOST=redis  # Use 'localhost' for local development
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your-redis-password
REDIS_POOL_SIZE=100

# JWT Settings (optional, defaults provided)
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_LIFETIME=3600  # 1 hour
JWT_REFRESH_TOKEN_LIFETIME=86400  # 24 hours
```

### Game Settings

Game settings are stored in the `GameSettings` model and can be configured via the admin panel:

- `BETTING_TIME`: Time in seconds for betting phase (default: 30)
- `DICE_RESULT_TIME`: Time in seconds before dice result is shown (default: 5)
- `RESULT_DISPLAY_TIME`: Time in seconds to display result (default: 10)
- `DICE_MODE`: `manual` or `random` (default: `manual`)

### Docker Compose Configuration

Key services:
- **web**: Django application (port 8232)
- **game_timer**: Game timer service
- **db**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)

---

## API Documentation

### Base URL
```
http://72.61.254.71:8232/api/
```

### Authentication

All API endpoints (except register/login) require JWT authentication:

```
Authorization: Bearer <access_token>
```

### Authentication Endpoints

#### Register
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "player1",
  "email": "player1@example.com",
  "password": "securepassword",
  "password2": "securepassword"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "player1",
    "email": "player1@example.com"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "player1",
  "password": "securepassword"
}
```

**Response:** Same as register

#### Get Profile
```http
GET /api/auth/profile/
Authorization: Bearer <token>
```

#### Get Wallet
```http
GET /api/auth/wallet/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "balance": "1000.00",
  "currency": "INR"
}
```

### Game Endpoints

#### Get Current Round
```http
GET /api/game/round/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "round_id": "ROUND_20250101_001",
  "status": "BETTING",
  "dice_result": null,
  "time_remaining": 25,
  "total_bets": 15,
  "total_amount": "5000.00"
}
```

#### Place Bet
```http
POST /api/game/bet/
Authorization: Bearer <token>
Content-Type: application/json

{
  "number": 3,
  "chip_amount": "100.00"
}
```

#### Remove Bet
```http
DELETE /api/game/bet/3/
Authorization: Bearer <token>
```

#### Get My Bets
```http
GET /api/game/bets/
Authorization: Bearer <token>
```

#### Get Round Results
```http
GET /api/game/results/
Authorization: Bearer <token>
```

#### Get Winning Results
```http
GET /api/game/winning-results/
Authorization: Bearer <token>
```

### Deposit Endpoints

#### Initiate Deposit
```http
POST /api/auth/deposits/initiate/
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount": "500.00",
  "payment_method": "UPI",
  "transaction_id": "TXN123456"
}
```

#### Upload Deposit Proof
```http
POST /api/auth/deposits/upload-proof/
Authorization: Bearer <token>
Content-Type: multipart/form-data

{
  "deposit_request_id": 1,
  "proof_image": <file>
}
```

#### Get My Deposit Requests
```http
GET /api/auth/deposits/mine/
Authorization: Bearer <token>
```

### Transaction Endpoints

#### Get Transactions
```http
GET /api/auth/transactions/
Authorization: Bearer <token>
```

**Query Parameters:**
- `type`: Filter by type (`deposit`, `withdrawal`, `bet`, `payout`)
- `limit`: Number of results (default: 50)
- `offset`: Pagination offset

---

## Admin Panel

### Access
- **URL**: `http://72.61.254.71:8232/game-admin/`
- **Login**: `/game-admin/login/`

### Features

1. **Dashboard**: Real-time game monitoring
2. **Dice Control**: Manual/random dice result management
3. **Recent Rounds**: View and manage game rounds
4. **All Bets**: View all bets across rounds
5. **Wallets**: User wallet management
6. **Players**: User management
7. **Deposit Requests**: Approve/reject deposits
8. **Transactions**: Complete transaction history
9. **Game Settings**: Configure game parameters
10. **Admin Management**: Manage admin users and permissions

### Permissions

Admin users have granular permissions:
- `can_view_dashboard`
- `can_control_dice`
- `can_view_recent_rounds`
- `can_view_all_bets`
- `can_view_wallets`
- `can_view_players`
- `can_view_deposit_requests`
- `can_view_transactions`
- `can_view_game_settings` (Super Admin only)
- `can_view_admin_management` (Super Admin only)

For detailed admin panel documentation, see `ADMIN_PANEL_DOCUMENTATION.md`.

---

## Frontend

### Structure

```
frontend/
├── src/
│   ├── components/        # React components
│   │   ├── Game.jsx       # Main game component
│   │   ├── Login.jsx      # Login component
│   │   └── ...
│   ├── services/
│   │   ├── api.js         # REST API service
│   │   └── diceService.js # WebSocket service
│   ├── App.jsx            # Main app component
│   └── main.jsx           # Entry point
```

### Key Components

- **Game.jsx**: Main game interface with betting controls
- **Login.jsx**: User authentication
- **Dashboard**: User dashboard (if implemented)

### WebSocket Integration

The frontend connects to WebSocket for real-time updates:

```javascript
const ws = new WebSocket('ws://72.61.254.71:8232/ws/game/');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle game state updates
};
```

---

## WebSocket Communication

### Connection
```
ws://72.61.254.71:8232/ws/game/
```

### Message Types

#### Client → Server

**Join Game Room**
```json
{
  "type": "join_game"
}
```

**Place Bet**
```json
{
  "type": "place_bet",
  "number": 3,
  "chip_amount": "100.00"
}
```

#### Server → Client

**Game State Update**
```json
{
  "type": "game_state",
  "round_id": "ROUND_20250101_001",
  "status": "BETTING",
  "time_remaining": 25,
  "dice_result": null
}
```

**Dice Roll**
```json
{
  "type": "dice_roll",
  "round_id": "ROUND_20250101_001",
  "dice_result": 3,
  "dice_values": [3, 3, 2, 4, 3, 1]
}
```

**Round Complete**
```json
{
  "type": "round_complete",
  "round_id": "ROUND_20250101_001",
  "dice_result": 3,
  "winners": [...]
}
```

---

## Game Logic

### Round States

1. **WAITING**: Round created, waiting to start
2. **BETTING**: Users can place bets
3. **CLOSED**: Betting closed, waiting for result
4. **RESULT**: Result announced
5. **COMPLETED**: Round finished, payouts distributed

### Round Flow

```
WAITING → BETTING → CLOSED → RESULT → COMPLETED
```

### Dice Result Calculation

- **Manual Mode**: Admin sets dice values manually
- **Random Mode**: System generates random dice values

Winning number is the **most common** number across all 6 dice.

### Payout Calculation

- Users bet on numbers (1-6)
- If their bet matches the winning number, they win
- Payout = `bet_amount * (total_amount_on_winning_number / total_amount_on_other_numbers)`

### Betting Rules

- One bet per number per round per user
- Minimum bet amount: Configurable
- Maximum bet amount: Based on wallet balance
- Bets can be removed before betting closes

---

## Database Models

### User (Django Auth)
- Standard Django User model
- Extended with Wallet and AdminPermissions

### Wallet
- `user`: OneToOne with User
- `balance`: DecimalField
- `currency`: CharField (default: "INR")

### GameRound
- `round_id`: Unique identifier
- `status`: Round state
- `dice_result`: Most common number (1-6)
- `dice_1` through `dice_6`: Individual dice values
- `total_bets`: Total number of bets
- `total_amount`: Total bet amount
- Timestamps: `start_time`, `betting_close_time`, `result_time`, `end_time`

### Bet
- `user`: ForeignKey to User
- `round`: ForeignKey to GameRound
- `number`: Bet number (1-6)
- `chip_amount`: Bet amount
- `payout_amount`: Calculated payout
- `is_winner`: Boolean

### DepositRequest
- `user`: ForeignKey to User
- `amount`: Requested amount
- `status`: `pending`, `approved`, `rejected`
- `proof_image`: Uploaded proof
- `approved_by`: Admin who approved
- Timestamps: `created_at`, `approved_at`

### Transaction
- `user`: ForeignKey to User
- `transaction_type`: `deposit`, `withdrawal`, `bet`, `payout`
- `amount`: Transaction amount
- `description`: Transaction details
- `created_at`: Timestamp

### AdminPermissions
- `user`: OneToOne with User
- Boolean fields for each permission

### GameSettings
- `key`: Setting key
- `value`: Setting value (stored as text)
- `description`: Setting description

---

## Deployment

### Production Deployment

1. **Server Setup**
   - Linux VPS (Ubuntu/Debian recommended)
   - Docker & Docker Compose installed
   - Domain name configured (optional)

2. **Clone Repository**
```bash
git clone <repository-url>
cd Ata3
```

3. **Configure Environment**
```bash
cp backend/env.example backend/.env
nano backend/.env  # Edit with production values
```

4. **Start Services**
```bash
docker compose up -d
```

5. **Run Migrations**
```bash
docker compose exec web python manage.py migrate
```

6. **Collect Static Files**
```bash
docker compose exec web python manage.py collectstatic --noinput
```

7. **Create Admin User**
```bash
docker compose exec web python manage.py createsuperuser
```

8. **Verify Services**
```bash
docker compose ps
docker compose logs web
docker compose logs game_timer
```

### Deployment Scripts

- `scripts/deploy_to_server.sh`: Automated deployment
- `scripts/verify_deployment.sh`: Verify deployment health
- `scripts/monitor_deployment.sh`: Monitor service status

### CI/CD (GitHub Actions)

See `.github/workflows/deploy.yml` for automated deployment configuration.

### Backup

- Database: PostgreSQL volumes persist automatically
- Media files: Stored in Docker volumes
- Manual backup script: `scripts/automated_backup.sh`

---

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8
- **JavaScript**: Use ES6+ syntax
- **React**: Functional components with hooks

### Git Workflow

1. Create feature branch
2. Make changes
3. Test locally
4. Commit with descriptive messages
5. Push to remote
6. Create pull request

### Testing

- Test API endpoints with Postman/curl
- Test WebSocket connections
- Test admin panel functionality
- Test game timer service

### Logging

- Django logs: `backend/logs/django_server.log`
- Game timer logs: `backend/logs/game_timer.log`
- Error logs: `backend/logs/django_error.log`

### Debugging

- Set `DEBUG=True` in `.env` for development
- Check Docker logs: `docker compose logs <service>`
- Use Django debug toolbar (if installed)
- Check Redis/PostgreSQL connections

---

## Troubleshooting

### Common Issues

#### 1. Services Won't Start
```bash
# Check Docker status
docker compose ps

# View logs
docker compose logs web
docker compose logs game_timer

# Restart services
docker compose restart
```

#### 2. Database Connection Errors
- Verify PostgreSQL is running: `docker compose ps db`
- Check database credentials in `.env`
- Verify network connectivity

#### 3. Redis Connection Errors
- Verify Redis is running: `docker compose ps redis`
- Check Redis password in `.env`
- Test connection: `docker compose exec redis redis-cli ping`

#### 4. Game Timer Not Working
- Check if timer service is running: `docker compose ps game_timer`
- View timer logs: `docker compose logs game_timer`
- Restart timer: `docker compose restart game_timer`

#### 5. WebSocket Connection Failed
- Verify Daphne is running
- Check WebSocket URL in frontend
- Verify CORS settings
- Check firewall/port settings

#### 6. Admin Login Issues
- Verify user exists: `docker compose exec web python manage.py shell`
- Check user is staff: `user.is_staff` and `user.is_superuser`
- Reset password: `python manage.py changepassword <username>`

#### 7. Static Files Not Loading
```bash
# Collect static files
docker compose exec web python manage.py collectstatic --noinput

# Check static files volume
docker volume ls
```

### Performance Issues

- Check Redis connection pool size
- Monitor database query performance
- Check WebSocket connection limits
- Review game timer execution time

### Database Issues

```bash
# Access database shell
docker compose exec db psql -U postgres -d dice_game

# Reset database (WARNING: Deletes all data)
docker compose down -v
docker compose up -d
docker compose exec web python manage.py migrate
```

---

## Security

### Best Practices

1. **Environment Variables**: Never commit `.env` files
2. **Secret Keys**: Use strong, random secret keys
3. **Database Passwords**: Use strong passwords
4. **CORS**: Configure allowed origins properly
5. **HTTPS**: Use HTTPS in production (configure reverse proxy)
6. **Firewall**: Restrict access to necessary ports only
7. **User Permissions**: Use granular admin permissions
8. **SQL Injection**: Django ORM prevents SQL injection
9. **XSS**: Django templates escape by default
10. **CSRF**: Django CSRF protection enabled

### Security Checklist

- [ ] Strong `SECRET_KEY` set
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` configured
- [ ] Database passwords are strong
- [ ] Redis password set
- [ ] Admin users have strong passwords
- [ ] HTTPS configured (via reverse proxy)
- [ ] Regular backups scheduled
- [ ] Logs monitored for suspicious activity

---

## Additional Resources

- **Admin Panel Documentation**: `ADMIN_PANEL_DOCUMENTATION.md`
- **Game Rules**: `docs/GAME_RULES.md`
- **Django Documentation**: https://docs.djangoproject.com/
- **React Documentation**: https://react.dev/
- **Django Channels**: https://channels.readthedocs.io/

---

## Support & Maintenance

### Regular Maintenance Tasks

1. **Daily**
   - Monitor service logs
   - Check for errors
   - Verify game timer is running

2. **Weekly**
   - Review transaction logs
   - Check database size
   - Verify backups

3. **Monthly**
   - Update dependencies
   - Review security logs
   - Performance optimization

### Contact

For issues or questions, refer to the project repository or contact the development team.

---

**Last Updated**: January 2025
**Version**: 1.0

