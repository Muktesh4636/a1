from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, parser_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from django.db import transaction as db_transaction
from django.utils import timezone
from django.conf import settings
from decimal import Decimal, InvalidOperation
import uuid
import re
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


@api_view(['POST'])
@authentication_classes([])  # Disable authentication for registration
@permission_classes([AllowAny])
def register(request):
    """User registration"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([])  # Disable authentication for login
@permission_classes([AllowAny])
def login(request):
    """User login"""
    import traceback
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Safely get request data
        if hasattr(request, 'data'):
            username = request.data.get('username', '').strip()
            password = request.data.get('password', '').strip()
        else:
            # Fallback for non-DRF requests
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()

        if not username or not password:
            return Response(
                {'error': 'Username and password required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Authenticate user
        try:
            user = authenticate(request=request, username=username, password=password)
        except Exception as auth_error:
            logger.error(f"Authentication error: {auth_error}")
            traceback.print_exc()
            return Response(
                {'error': 'Authentication failed', 'detail': str(auth_error)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if not user:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if user is active
        if not user.is_active:
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
            logger.error(f"Token generation error: {token_error}")
            traceback.print_exc()
            return Response(
                {'error': 'Failed to generate tokens', 'detail': str(token_error)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Serialize user data
        try:
            user_data = UserSerializer(user).data
        except Exception as serializer_error:
            logger.error(f"User serialization error: {serializer_error}")
            traceback.print_exc()
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
        logger.error(f"Login API error: {e}")
        traceback.print_exc()
        return Response({
            'error': 'Internal server error',
            'detail': str(e) if settings.DEBUG else 'An error occurred during login'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get user profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet(request):
    """Get user wallet"""
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    serializer = WalletSerializer(wallet)
    return Response(serializer.data)


class TransactionList(generics.ListAPIView):
    """List user transactions"""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_deposit_proof(request):
    """Create a deposit request with PENDING status - requires admin approval"""
    amount_raw = request.data.get('amount')
    
    # Try multiple possible field names for the file
    screenshot = request.FILES.get('screenshot') or request.FILES.get('file') or request.FILES.get('image')

    if not screenshot:
        available_files = list(request.FILES.keys()) if hasattr(request, 'FILES') and request.FILES else []
        error_msg = 'Screenshot file is required. '
        if available_files:
            error_msg += f'Received file fields: {available_files}. Please use field name "screenshot".'
        else:
            error_msg += 'No files were received. Make sure to send the request as multipart/form-data.'
        return Response({'error': error_msg, 'received_files': available_files}, status=status.HTTP_400_BAD_REQUEST)

    try:
        amount = _parse_amount(amount_raw)
    except ValueError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    # Create deposit request with PENDING status - no wallet credit yet
    try:
        deposit = DepositRequest.objects.create(
            user=request.user,
            amount=amount,
            screenshot=screenshot,
            status='PENDING',
        )
    except Exception as e:
        # Catch any database or validation errors and return JSON response
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_deposit_requests(request):
    """List the authenticated user's deposit requests"""
    deposits = DepositRequest.objects.filter(user=request.user)
    serializer = DepositRequestSerializer(deposits, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def pending_deposit_requests(request):
    """Admin: list all pending deposit requests"""
    deposits = DepositRequest.objects.filter(status='PENDING').select_related('user')
    serializer = DepositRequestAdminSerializer(deposits, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def approve_deposit_request(request, pk):
    """Admin approves a pending deposit request"""
    note = request.data.get('note', '')
    try:
        with db_transaction.atomic():
            deposit = DepositRequest.objects.select_for_update().get(pk=pk)
            if deposit.status != 'PENDING':
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
    except DepositRequest.DoesNotExist:
        return Response({'error': 'Deposit request not found'}, status=status.HTTP_404_NOT_FOUND)

    notify_user(deposit.user, f"Your deposit of ₹{deposit.amount} has been approved.")
    serializer = DepositRequestAdminSerializer(deposit, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def reject_deposit_request(request, pk):
    """Admin rejects a pending deposit request"""
    note = request.data.get('note', '')
    try:
        with db_transaction.atomic():
            deposit = DepositRequest.objects.select_for_update().get(pk=pk)
            if deposit.status != 'PENDING':
                return Response({'error': 'Deposit request already processed'}, status=status.HTTP_400_BAD_REQUEST)

            deposit.status = 'REJECTED'
            deposit.admin_note = note
            deposit.processed_by = request.user
            deposit.processed_at = timezone.now()
            deposit.save()
    except DepositRequest.DoesNotExist:
        return Response({'error': 'Deposit request not found'}, status=status.HTTP_404_NOT_FOUND)

    notify_user(deposit.user, f"Your deposit of ₹{deposit.amount} was rejected. {note}".strip())
    serializer = DepositRequestAdminSerializer(deposit, context={'request': request})
    return Response(serializer.data)


# Withdraw functionality

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_withdraw(request):
    """Create a withdraw request with PENDING status - requires admin approval"""
    amount_raw = request.data.get('amount')
    withdrawal_method = request.data.get('withdrawal_method', '').strip()
    withdrawal_details = request.data.get('withdrawal_details', '').strip()

    if not withdrawal_method:
        return Response({'error': 'Withdrawal method is required'}, status=status.HTTP_400_BAD_REQUEST)

    if not withdrawal_details:
        return Response({'error': 'Withdrawal details are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        amount = _parse_amount(amount_raw)
    except ValueError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    # Check if user has sufficient balance
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    if wallet.balance < amount:
        return Response({
            'error': f'Insufficient balance. You have ₹{wallet.balance}, but requested ₹{amount}'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check for existing pending withdraw request
    existing_pending = WithdrawRequest.objects.filter(
        user=request.user,
        status='PENDING'
    ).exists()

    if existing_pending:
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
    except Exception as e:
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_withdraw_requests(request):
    """List the authenticated user's withdraw requests"""
    withdraws = WithdrawRequest.objects.filter(user=request.user)
    serializer = WithdrawRequestSerializer(withdraws, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_payment_methods(request):
    """List active payment methods for deposits"""
    methods = PaymentMethod.objects.filter(is_active=True)
    serializer = PaymentMethodSerializer(methods, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def my_bank_details(request):
    """Get or create user bank details"""
    if request.method == 'GET':
        details = UserBankDetail.objects.filter(user=request.user)
        serializer = UserBankDetailSerializer(details, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = UserBankDetailSerializer(data=request.data)
        if serializer.is_valid():
            # If setting as default, unset others
            if serializer.validated_data.get('is_default'):
                UserBankDetail.objects.filter(user=request.user).update(is_default=False)
            
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', 'PUT'])
@permission_classes([IsAuthenticated])
def bank_detail_action(request, pk):
    """Update or delete a specific bank detail"""
    detail = get_object_or_404(UserBankDetail, pk=pk, user=request.user)
    
    if request.method == 'DELETE':
        detail.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    elif request.method == 'PUT':
        serializer = UserBankDetailSerializer(detail, data=request.data, partial=True)
        if serializer.is_valid():
            if serializer.validated_data.get('is_default'):
                UserBankDetail.objects.filter(user=request.user).exclude(pk=pk).update(is_default=False)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




