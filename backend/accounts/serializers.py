from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.validators import MinLengthValidator
from decimal import Decimal
from .models import User, Wallet, Transaction, DepositRequest, WithdrawRequest, PaymentMethod, UserBankDetail


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[MinLengthValidator(4, message="Password must be at least 4 characters long.")]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'phone_number')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        # Wallet is automatically created by signal (accounts.signals.create_user_wallet)
        # Using get_or_create as a safety measure in case signal doesn't fire
        Wallet.objects.get_or_create(user=user, defaults={'balance': Decimal('0.00')})
        return user


class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone_number', 'date_joined', 'is_staff')
        read_only_fields = ('id', 'date_joined')


class WalletSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Wallet
        fields = ('id', 'user', 'balance', 'created_at', 'updated_at')
        read_only_fields = ('id', 'balance', 'created_at', 'updated_at')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'transaction_type', 'amount', 'balance_before', 'balance_after', 'description', 'created_at')
        read_only_fields = ('id', 'created_at')


class DepositRequestSerializer(serializers.ModelSerializer):
    screenshot_url = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)

    class Meta:
        model = DepositRequest
        fields = (
            'id',
            'user',
            'amount',
            'status',
            'screenshot_url',
            'admin_note',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'status', 'created_at', 'updated_at', 'user', 'screenshot_url')

    def get_screenshot_url(self, obj):
        request = self.context.get('request')
        if obj.screenshot and hasattr(obj.screenshot, 'url'):
            if request:
                return request.build_absolute_uri(obj.screenshot.url)
            return obj.screenshot.url
        return None


class DepositRequestAdminSerializer(DepositRequestSerializer):
    class Meta(DepositRequestSerializer.Meta):
        fields = DepositRequestSerializer.Meta.fields + ('admin_note',)


class WithdrawRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    processed_by_name = serializers.ReadOnlyField(source='processed_by.username')

    class Meta:
        model = WithdrawRequest
        fields = (
            'id',
            'user',
            'amount',
            'status',
            'withdrawal_method',
            'withdrawal_details',
            'admin_note',
            'processed_by_name',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'status', 'created_at', 'updated_at', 'user', 'processed_by_name')


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'


class UserBankDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBankDetail
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')




