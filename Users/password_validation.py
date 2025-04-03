import re
from difflib import SequenceMatcher
from django.contrib.auth.password_validation import exceeds_maximum_length_ratio
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.utils.translation import gettext_lazy as _


class UserAttributeSimilarityValidator:
    """
    Validate that the password is sufficiently different from the user's
    attributres (currently only email).
    """

    DEFAULT_USER_ATTRIBUTES = ("email",)

    def __init__(self, user_attributes=DEFAULT_USER_ATTRIBUTES, max_similarity=0.7):
        self.user_atttributes = user_attributes
        if max_similarity <= 0.1:
            raise ValueError("max_similarity must be at least 0.1")
        self.max_similarity = max_similarity

    def validate(self, password, user=None):
        if not user:
            return

        password = password.lower()
        for attribute_name in self.user_atttributes:
            value = getattr(user, attribute_name, None)
            if not value or not isinstance(value, str):
                continue
            value_lower = value.lower()
            value_parts = re.split(r"\W+", value_lower) + [value_lower]
            for value_part in value_parts:
                if exceeds_maximum_length_ratio(
                    password, self.max_similarity, value_part
                ):
                    continue
                if (
                    SequenceMatcher(a=password, b=value_part).quick_ratio()
                    >= self.max_similarity
                ):
                    try:
                        verbose_name = str(
                            user._meta.get_field(attribute_name).verbose_name
                        )
                    except FieldDoesNotExist:
                        verbose_name = attribute_name
                    raise ValidationError(
                        _("The password is too similar to the %(verbose_name)s"),
                        code="password_too_similar",
                        params={"verbose_name": verbose_name},
                    )

    def get_help_text(self):
        return _("Your password can’t be too similar to your email.")


class NumberAndSymbolPasswordValidator:
    symbols_pattern = r"[!@#$%^&*()\-_=+{};:,<.>\\|/?~]"

    def validate(self, password, user=None):
        if not re.search(self.symbols_pattern, password) and not any(
            char.isdigit() for char in password
        ):
            raise ValidationError(
                _("The password must contain at least one number or symbol."),
                code="password_no_number_or_symbol",
            )

    def get_help_text(self):
        return _("Your password must contain at least one number or symbol.")


class LowerCaseAndUpperCaseLettersPasswordValidator:
    def validate(self, password, user=None):
        if not any(char.islower() for char in password) or not any(
            char.isupper() for char in password
        ):
            raise ValidationError(
                _("The password must contain both lowercase and uppercase letters."),
                code="password_no_uppercase_or_lowercase",
            )

    def get_help_text(self):
        return _("Your password must contain both lowercase and uppercase letters.")
 