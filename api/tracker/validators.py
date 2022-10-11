from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible


@deconstructible
class NegativeValidator:
    def __init__(self, validator, message):
        self.validator = validator
        self.message = message

    def __call__(self, value):
        try:
            self.validator(value)

        except ValidationError:
            return

        raise ValidationError(
            _(self.message)
        )

    def __eq__(self, other):
        if not hasattr(other, 'validator') or (self.validator != other.validator):
            return False

        elif not hasattr(other, 'message') or (self.message != other.message):
            return False

        return True
