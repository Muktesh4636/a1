import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class AdminPasswordValidator:
    """
    Custom password validator for admin and super admin accounts.
    Requires: uppercase, lowercase, digit, special character, minimum 8 chars
    """

    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Password must be at least %(min_length)d characters long."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Password must contain at least one uppercase letter (A-Z)."),
                code='password_no_upper',
            )

        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("Password must contain at least one lowercase letter (a-z)."),
                code='password_no_lower',
            )

        # Check for at least one digit
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("Password must contain at least one digit (0-9)."),
                code='password_no_digit',
            )

        # Check for at least one special character
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            raise ValidationError(
                _("Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Password must be at least %(min_length)d characters long and contain at least "
            "one uppercase letter, one lowercase letter, one digit, and one special character."
        ) % {'min_length': self.min_length}


# Create an instance for use in forms/admin
admin_password_validator = AdminPasswordValidator()