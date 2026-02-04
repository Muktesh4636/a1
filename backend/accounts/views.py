from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, parser_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from django.db import transaction as db_transaction
from django.utils import timezone
from django.conf import settings
from decimal import Decimal, InvalidOperation
import uuid
import re
import logging

logger = logging.getLogger('accounts')

try:
    import pytesseract
    from PIL import Image
    import io
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

from .models import User, Wallet, Transaction, DepositRequest, WithdrawRequest, PaymentMethod, UserBankDetail
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    WalletSerializer,
    TransactionSerializer,
    DepositRequestSerializer,
    DepositRequestAdminSerializer,
    WithdrawRequestSerializer,
    PaymentMethodSerializer,
    UserBankDetailSerializer,
)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])  # Disable authentication for registration
@permission_classes([AllowAny])
def register(request):
    """User registration"""
    logger.info(f"Registration attempt for username: {request.data.get('username')}")
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        logger.info(f"User registered successfully: {user.username} (ID: {user.id})")
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    logger.warning(f"Registration failed for username: {request.data.get('username')} - Errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])  # Disable authentication for login
@permission_classes([AllowAny])
def login(request):
    """User login"""
    try:
        # Safely get request data
        if hasattr(request, 'data'):
            username = request.data.get('username', '').strip()
            password = request.data.get('password', '').strip()
        else:
            # Fallback for non-DRF requests
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()

        logger.info(f"Login attempt for username: {username}")

        if not username or not password:
            logger.warning(f"Login failed: Missing credentials for username: {username}")
            return Response(
                {'error': 'Username and password required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Authenticate user
        try:
            user = authenticate(request=request, username=username, password=password)
        except Exception as auth_error:
            logger.exception(f"Authentication error for username {username}: {auth_error}")
            return Response(
                {'error': 'Authentication failed', 'detail': str(auth_error)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if not user:
            logger.warning(f"Login failed: Invalid credentials for username: {username}")
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login failed: Account disabled for user: {user.username} (ID: {user.id})")
            return Response(
                {'error': 'User account is disabled'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Generate JWT tokens
        try:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
        except Exception as token_error:
            logger.exception(f"Token generation error for user {user.username}: {token_error}")
            return Response(
                {'error': 'Failed to generate tokens', 'detail': str(token_error)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        logger.info(f"User logged in successfully: {user.username} (ID: {user.id})")
        # Serialize user data
        try:
            user_data = UserSerializer(user).data
        except Exception as serializer_error:
            logger.exception(f"User serialization error for user {user.username}: {serializer_error}")
            # Return minimal user data if serializer fails
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': getattr(user, 'email', ''),
                'is_staff': getattr(user, 'is_staff', False),
            }

        return Response({
            'user': user_data,
            'refresh': refresh_token,
            'access': access_token,
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Unexpected error during login: {e}")
        return Response({
            'error': 'Internal server error',
            'detail': str(e) if settings.DEBUG else 'An error occurred during login'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get user profile"""
    logger.info(f"Profile access for user: {request.user.username} (ID: {request.user.id})")
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet(request):
    """Get user wallet"""
    logger.info(f"Wallet balance check for user: {request.user.username} (ID: {request.user.id})")
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    serializer = WalletSerializer(wallet)
    return Response(serializer.data)


class TransactionList(generics.ListAPIView):
    """List user transactions"""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        logger.info(f"Transaction history access for user: {self.request.user.username} (ID: {self.request.user.id})")
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')


def _parse_amount(value):
    """Parse and validate amount value, ensuring it's a valid Decimal with max 2 decimal places"""
    if value is None:
        raise ValueError('Amount is required')
    
    try:
        # Convert to string first to handle various input types
        value_str = str(value).strip()
        if not value_str:
            raise ValueError('Amount cannot be empty')
        
        # Parse as Decimal
        amount = Decimal(value_str)
    except (InvalidOperation, TypeError, ValueError) as e:
        raise ValueError(f'Invalid amount value: {value}. Must be a valid number.')
    
    # Check for special values
    if amount.is_nan() or amount.is_infinite():
        raise ValueError('Amount cannot be NaN or infinite')
    
    if amount <= 0:
        raise ValueError('Amount must be greater than 0')
    
    # Quantize to 2 decimal places, rounding if necessary
    try:
        quantized = amount.quantize(Decimal('0.01'), rounding='ROUND_HALF_UP')
        return quantized
    except InvalidOperation:
        # If quantize fails, try rounding manually
        # This handles cases where the value has too many decimal places
        rounded = round(float(amount), 2)
        return Decimal(str(rounded)).quantize(Decimal('0.01'))


def notify_user(user, message):
    """Placeholder notification helper"""
    print(f"[NOTIFY] {user.username}: {message}")


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_deposit(request):
    """Generate a payment link for manual deposit"""
    amount_raw = request.data.get('amount')
    try:
        amount = _parse_amount(amount_raw)
    except ValueError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    payment_link = f"https://pay.example.com/{uuid.uuid4().hex}?amount={amount}"
    return Response({
        'amount': str(amount),
        'currency': 'INR',
        'payment_link': payment_link,
        'message': 'Complete the payment and upload the receipt.',
    })


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def extract_utr(request):
    """Analyze uploaded screenshot and extract UTR number"""
    if not TESSERACT_AVAILABLE:
        return Response({
            'success': False,
            'error': 'OCR functionality not available. Please install Tesseract OCR: brew install tesseract'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    screenshot = request.FILES.get('screenshot') or request.FILES.get('file') or request.FILES.get('image')

    if not screenshot:
        return Response({'error': 'Screenshot file is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Set tesseract path if provided in settings
        tesseract_cmd = getattr(settings, 'TESSERACT_CMD', '/opt/homebrew/bin/tesseract')
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            
        # Open image using Pillow
        img = Image.open(screenshot)
        # Convert to grayscale for better OCR
        img = img.convert('L')
        
        # Perform OCR
        # Note: requires tesseract binary installed on the system
        text = pytesseract.image_to_string(img)
        
        # Extract UTR using regex
        # Common UTR patterns: 12 digits, or starting with specific UPI patterns
        # Look for 12 consecutive digits (most common for UPI UTR)
        utr_match = re.search(r'\b\d{12}\b', text)
        
        # If not found, look for "UTR" or "Ref" keywords nearby
        if not utr_match:
            # Look for 10-16 alphanumeric characters after "UTR" or "Transaction ID"
            keyword_match = re.search(r'(?:UTR|Ref|Transaction ID|Ref No)[:\s]+([A-Z0-9]{10,16})', text, re.IGNORECASE)
            if keyword_match:
                utr_number = keyword_match.group(1)
            else:
                utr_number = None
        else:
            utr_number = utr_match.group(0)

        if not utr_number:
            return Response({
                'success': False,
                'message': 'Could not extract UTR automatically. Please enter it manually.',
                'raw_text': text[:500] if settings.DEBUG else None
            })

        return Response({
            'success': True,
            'utr': utr_number,
            'message': 'UTR extracted successfully'
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': f'Failed to process image: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def process_payment_screenshot(request):
    """
    Analyze uploaded screenshot, extract UTR number, and return with user_id and amount.
    Expects: screenshot (file), user_id (string/int), amount (decimal/string)
    """
    user_id = request.data.get('user_id')
    amount = request.data.get('amount')
    screenshot = request.FILES.get('screenshot') or request.FILES.get('file') or request.FILES.get('image')

    if not screenshot:
        return Response({'error': 'Screenshot file is required'}, status=status.HTTP_400_BAD_REQUEST)

    response_data = {
        'success': False,
        'user_id': user_id,
        'amount': amount,
        'utr': None
    }

    if not TESSERACT_AVAILABLE:
        response_data['error'] = 'OCR functionality not available'
        return Response(response_data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        # Set tesseract path
        tesseract_cmd = getattr(settings, 'TESSERACT_CMD', '/opt/homebrew/bin/tesseract')
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            
        img = Image.open(screenshot)
        # Convert to grayscale for better OCR
        img = img.convert('L')
        text = pytesseract.image_to_string(img)
        
        # Log extracted text for debugging (limited)
        print(f"Extracted Text: {text[:200]}...")
        
        # Extract UTR using regex
        utr_match = re.search(r'\b\d{12}\b', text)
        if not utr_match:
            keyword_match = re.search(r'(?:UTR|Ref|Transaction ID|Ref No)[:\s]+([A-Z0-9]{10,16})', text, re.IGNORECASE)
            utr_number = keyword_match.group(1) if keyword_match else None
        else:
            utr_number = utr_match.group(0)

        response_data['utr'] = utr_number
        if utr_number:
            response_data['success'] = True
            response_data['message'] = 'UTR extracted successfully'
        else:
            response_data['message'] = 'Could not extract UTR automatically'

        return Response(response_data)

    except Exception as e:
        response_data['error'] = f'Failed to process image: {str(e)}'
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_deposit_proof(request):
    """Create a deposit request with PENDING status - requires admin approval"""
    amount_raw = request.data.get('amount')
    logger.info(f"Deposit proof upload attempt for user {request.user.username} (ID: {request.user.id}), amount: {amount_raw}")
    
    # Try multiple possible field names for the file
    screenshot = request.FILES.get('screenshot') or request.FILES.get('file') or request.FILES.get('image')

    if not screenshot:
        available_files = list(request.FILES.keys()) if hasattr(request, 'FILES') and request.FILES else []
        error_msg = 'Screenshot file is required. '
        logger.warning(f"Deposit proof upload failed for user {request.user.username}: No file received. Available fields: {available_files}")
        if available_files:
            error_msg += f'Received file fields: {available_files}. Please use field name "screenshot".'
        else:
            error_msg += 'No files were received. Make sure to send the request as multipart/form-data.'
        return Response({'error': error_msg, 'received_files': available_files}, status=status.HTTP_400_BAD_REQUEST)

    try:
        amount = _parse_amount(amount_raw)
    except ValueError as exc:
        logger.warning(f"Deposit proof upload failed for user {request.user.username}: Invalid amount {amount_raw} - {exc}")
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    # Create deposit request with PENDING status - no wallet credit yet
    try:
        deposit = DepositRequest.objects.create(
            user=request.user,
            amount=amount,
            screenshot=screenshot,
            status='PENDING',
        )
        logger.info(f"Deposit request created: ID {deposit.id} for user {request.user.username}, amount: {amount}")
    except Exception as e:
        logger.exception(f"Unexpected error creating deposit request for user {request.user.username}: {e}")
        import traceback
        error_details = str(e)
        if hasattr(e, '__class__'):
            error_type = e.__class__.__name__
        else:
            error_type = 'UnknownError'
        
        # Return user-friendly error message
        if 'InvalidOperation' in error_type or 'decimal' in error_details.lower():
            return Response({
                'error': f'Invalid amount value: {amount_raw}. Please provide a valid number with up to 2 decimal places.',
                'details': error_details
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'Failed to create deposit request. Please check your input and try again.',
                'details': error_details
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    notify_user(request.user, f"Your deposit request of ₹{amount} has been submitted and is pending admin approval.")
    serializer = DepositRequestSerializer(deposit, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_deposit_requests(request):
    """List the authenticated user's deposit requests"""
    logger.info(f"Fetching deposit requests for user: {request.user.username} (ID: {request.user.id})")
    deposits = DepositRequest.objects.filter(user=request.user).order_by('-created_at')
    serializer = DepositRequestSerializer(deposits, many=True, context={'request': request})
    return Response(serializer.data)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAdminUser])
def pending_deposit_requests(request):
    """Admin: list all pending deposit requests"""
    logger.info(f"Admin {request.user.username} fetching all pending deposit requests")
    deposits = DepositRequest.objects.filter(status='PENDING').select_related('user').order_by('created_at')
    serializer = DepositRequestAdminSerializer(deposits, many=True, context={'request': request})
    return Response(serializer.data)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAdminUser])
def approve_deposit_request(request, pk):
    """Admin approves a pending deposit request"""
    note = request.data.get('note', '')
    logger.info(f"Admin {request.user.username} attempting to approve deposit {pk}")
    try:
        with db_transaction.atomic():
            deposit = DepositRequest.objects.select_for_update().get(pk=pk)
            if deposit.status != 'PENDING':
                logger.warning(f"Admin {request.user.username} failed to approve deposit {pk}: Already processed (Status: {deposit.status})")
                return Response({'error': 'Deposit request already processed'}, status=status.HTTP_400_BAD_REQUEST)

            wallet, _ = Wallet.objects.get_or_create(user=deposit.user)
            wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
            balance_before = wallet.balance
            wallet.balance = balance_before + deposit.amount
            wallet.save()

            Transaction.objects.create(
                user=deposit.user,
                transaction_type='DEPOSIT',
                amount=deposit.amount,
                balance_before=balance_before,
                balance_after=wallet.balance,
                description=f"Manual deposit #{deposit.id}",
            )

            deposit.status = 'APPROVED'
            deposit.admin_note = note
            deposit.processed_by = request.user
            deposit.processed_at = timezone.now()
            deposit.save()
            logger.info(f"Deposit {pk} approved by admin {request.user.username}. User: {deposit.user.username}, Amount: {deposit.amount}")
    except DepositRequest.DoesNotExist:
        logger.error(f"Admin {request.user.username} failed to approve deposit {pk}: Not found")
        return Response({'error': 'Deposit request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception(f"Unexpected error approving deposit {pk} by admin {request.user.username}: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    notify_user(deposit.user, f"Your deposit of ₹{deposit.amount} has been approved.")
    serializer = DepositRequestAdminSerializer(deposit, context={'request': request})
    return Response(serializer.data)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAdminUser])
def reject_deposit_request(request, pk):
    """Admin rejects a pending deposit request"""
    note = request.data.get('note', '')
    logger.info(f"Admin {request.user.username} attempting to reject deposit {pk}")
    try:
        with db_transaction.atomic():
            deposit = DepositRequest.objects.select_for_update().get(pk=pk)
            if deposit.status != 'PENDING':
                logger.warning(f"Admin {request.user.username} failed to reject deposit {pk}: Already processed (Status: {deposit.status})")
                return Response({'error': 'Deposit request already processed'}, status=status.HTTP_400_BAD_REQUEST)

            deposit.status = 'REJECTED'
            deposit.admin_note = note
            deposit.processed_by = request.user
            deposit.processed_at = timezone.now()
            deposit.save()
            logger.info(f"Deposit {pk} rejected by admin {request.user.username}. User: {deposit.user.username}, Amount: {deposit.amount}, Note: {note}")
    except DepositRequest.DoesNotExist:
        logger.error(f"Admin {request.user.username} failed to reject deposit {pk}: Not found")
        return Response({'error': 'Deposit request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception(f"Unexpected error rejecting deposit {pk} by admin {request.user.username}: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    notify_user(deposit.user, f"Your deposit of ₹{deposit.amount} was rejected. {note}".strip())
    serializer = DepositRequestAdminSerializer(deposit, context={'request': request})
    return Response(serializer.data)


# Withdraw functionality

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_withdraw(request):
    """Create a withdraw request with PENDING status - requires admin approval"""
    amount_raw = request.data.get('amount')
    withdrawal_method = request.data.get('withdrawal_method', '').strip()
    withdrawal_details = request.data.get('withdrawal_details', '').strip()

    logger.info(f"Withdrawal initiation attempt for user {request.user.username} (ID: {request.user.id}), amount: {amount_raw}, method: {withdrawal_method}")

    if not withdrawal_method:
        logger.warning(f"Withdrawal failed for user {request.user.username}: Missing method")
        return Response({'error': 'Withdrawal method is required'}, status=status.HTTP_400_BAD_REQUEST)

    if not withdrawal_details:
        logger.warning(f"Withdrawal failed for user {request.user.username}: Missing details")
        return Response({'error': 'Withdrawal details are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        amount = _parse_amount(amount_raw)
    except ValueError as exc:
        logger.warning(f"Withdrawal failed for user {request.user.username}: Invalid amount {amount_raw} - {exc}")
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    # Check if user has sufficient balance
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    if wallet.balance < amount:
        logger.warning(f"Withdrawal failed for user {request.user.username}: Insufficient balance (Balance: {wallet.balance}, Requested: {amount})")
        return Response({
            'error': f'Insufficient balance. You have ₹{wallet.balance}, but requested ₹{amount}'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check for existing pending withdraw request
    existing_pending = WithdrawRequest.objects.filter(
        user=request.user,
        status='PENDING'
    ).exists()

    if existing_pending:
        logger.warning(f"Withdrawal failed for user {request.user.username}: Already has a pending request")
        return Response({
            'error': 'You already have a pending withdraw request. Please wait for it to be processed.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Create withdraw request with PENDING status - no wallet debit yet
    try:
        withdraw = WithdrawRequest.objects.create(
            user=request.user,
            amount=amount,
            withdrawal_method=withdrawal_method,
            withdrawal_details=withdrawal_details,
            status='PENDING',
        )
        logger.info(f"Withdrawal request created: ID {withdraw.id} for user {request.user.username}, amount: {amount}")
    except Exception as e:
        logger.exception(f"Unexpected error creating withdrawal request for user {request.user.username}: {e}")
        import traceback
        error_details = str(e)
        if hasattr(e, '__class__'):
            error_type = e.__class__.__name__
        else:
            error_type = 'UnknownError'

        # Return user-friendly error message
        if 'InvalidOperation' in error_type or 'decimal' in error_details.lower():
            return Response({
                'error': f'Invalid amount value: {amount_raw}. Please provide a valid number with up to 2 decimal places.',
                'details': error_details
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'Failed to create withdraw request. Please check your input and try again.',
                'details': error_details
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    notify_user(request.user, f"Your withdraw request of ₹{amount} has been submitted and is pending admin approval.")
    serializer = WithdrawRequestSerializer(withdraw, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_withdraw_requests(request):
    """List the authenticated user's withdraw requests"""
    logger.info(f"Fetching withdrawal requests for user: {request.user.username} (ID: {request.user.id})")
    withdraws = WithdrawRequest.objects.filter(user=request.user).order_by('-created_at')
    serializer = WithdrawRequestSerializer(withdraws, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_payment_methods(request):
    """List active payment methods for deposits"""
    logger.info("Fetching active payment methods")
    methods = PaymentMethod.objects.filter(is_active=True)
    serializer = PaymentMethodSerializer(methods, many=True, context={'request': request})
    return Response(serializer.data)


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def my_bank_details(request):
    """Get or create user bank details"""
    if request.method == 'GET':
        logger.info(f"Fetching bank details for user: {request.user.username} (ID: {request.user.id})")
        details = UserBankDetail.objects.filter(user=request.user)
        serializer = UserBankDetailSerializer(details, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        logger.info(f"Creating bank detail for user: {request.user.username} (ID: {request.user.id})")
        serializer = UserBankDetailSerializer(data=request.data)
        if serializer.is_valid():
            # If setting as default, unset others
            if serializer.validated_data.get('is_default'):
                UserBankDetail.objects.filter(user=request.user).update(is_default=False)
            
            serializer.save(user=request.user)
            logger.info(f"Bank detail created successfully for user: {request.user.username}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning(f"Bank detail creation failed for user {request.user.username}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['DELETE', 'PUT'])
@permission_classes([IsAuthenticated])
def bank_detail_action(request, pk):
    """Update or delete a specific bank detail"""
    detail = get_object_or_404(UserBankDetail, pk=pk, user=request.user)
    
    if request.method == 'DELETE':
        logger.info(f"Deleting bank detail {pk} for user: {request.user.username}")
        detail.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    elif request.method == 'PUT':
        logger.info(f"Updating bank detail {pk} for user: {request.user.username}")
        serializer = UserBankDetailSerializer(detail, data=request.data, partial=True)
        if serializer.is_valid():
            if serializer.validated_data.get('is_default'):
                UserBankDetail.objects.filter(user=request.user).exclude(pk=pk).update(is_default=False)
            serializer.save()
            logger.info(f"Bank detail {pk} updated successfully for user: {request.user.username}")
            return Response(serializer.data)
        logger.warning(f"Bank detail {pk} update failed for user {request.user.username}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




