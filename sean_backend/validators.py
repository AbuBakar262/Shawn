import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


class NumberValidator(object):
    def __init__(self, min_digits=0):
        self.min_digits = min_digits

    def validate(self, password, user=None):
        if not re.findall('\d', password) or not re.findall('[A-Z]', password) or not re.findall('[a-z]', password) \
                or not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password) or len(password) < 8 or len(password) == 0:
            raise ValidationError(
                _("Password contains minimum 8 characters, upper and lower case alphabets, at least one digit and one special character"),
                code='password_no_number',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 digit, 0-9."
        )


# class UppercaseValidator(object):
#     def validate(self, password, user=None):
#         if not re.findall('[A-Z]', password):
#             raise ValidationError(
#                 _("Password contains minimum 8 characters, upper and lower case alphabets, at least one digit and one special character"),
#                 code='password_no_upper',
#             )
#
#     def get_help_text(self):
#         return _(
#             "Password contains minimum 8 characters, upper and lower case alphabets, at least one digit and one special character"
#         )


# class LowercaseValidator(object):
#     def validate(self, password, user=None):
#         if not re.findall('[a-z]', password):
#             raise ValidationError(
#                 _("Password contains minimum 8 characters, upper and lower case alphabets, at least one digit and one special character"),
#                 code='password_no_lower',
#             )
#
#     def get_help_text(self):
#         return _(
#             "Password contains minimum 8 characters, upper and lower case alphabets, at least one digit and one special character"
#         )


# class SymbolValidator(object):
#     def validate(self, password, user=None):
#         if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
#             raise ValidationError(
#                 _("Password contains minimum 8 characters, upper and lower case alphabets, at least one digit and one special character"),
#                 code='password_no_symbol',
#             )
#
#     def get_help_text(self):
#         return _(
#             "Password contains minimum 8 characters, upper and lower case alphabets, at least one digit and one special character"
#         )