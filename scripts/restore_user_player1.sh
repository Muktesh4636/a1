#!/bin/bash

# Script to restore/create player1 user with 10k balance
# This recreates the user if it was deleted

set -e

DEPLOY_DIR="${DEPLOY_DIR:-/opt/dice_game}"
cd "$DEPLOY_DIR" || exit 1

echo "👤 Restoring player1 user..."
echo "============================"
echo ""

# Create user via Django shell
docker compose exec -T web python manage.py shell << 'PYTHON_EOF'
from accounts.models import User, Wallet, Transaction
from decimal import Decimal

username = 'player1'
password = 'admin123'
initial_balance = Decimal('10000.00')

# Check if user already exists
if User.objects.filter(username=username).exists():
    user = User.objects.get(username=username)
    wallet = Wallet.objects.get(user=user)
    print(f'✅ User {username} already exists')
    print(f'   Current balance: ₹{wallet.balance}')
    
    # Update balance if needed
    if wallet.balance < initial_balance:
        old_balance = wallet.balance
        wallet.add(initial_balance - wallet.balance)
        Transaction.objects.create(
            user=user,
            transaction_type='DEPOSIT',
            amount=initial_balance - old_balance,
            balance_before=old_balance,
            balance_after=wallet.balance,
            description='Balance restored to 10,000 rupees'
        )
        print(f'✅ Balance updated: ₹{old_balance} → ₹{wallet.balance}')
    else:
        print(f'✅ Balance is already sufficient: ₹{wallet.balance}')
else:
    # Create new user
    user = User.objects.create_user(
        username=username,
        password=password,
        is_active=True
    )
    wallet = Wallet.objects.get(user=user)
    wallet.add(initial_balance)
    
    Transaction.objects.create(
        user=user,
        transaction_type='DEPOSIT',
        amount=initial_balance,
        balance_before=Decimal('0.00'),
        balance_after=wallet.balance,
        description='Initial deposit of 10,000 rupees'
    )
    
    print(f'✅ User {username} created successfully')
    print(f'   Password: {password}')
    print(f'   Balance: ₹{wallet.balance}')

print('')
print('✅ User restoration complete!')
PYTHON_EOF

echo ""
echo "✅ Done!"



