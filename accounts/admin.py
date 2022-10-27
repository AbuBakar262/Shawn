from django.contrib import admin
from .models import User, VerificationCode

# Register your models here.
admin.site.register(User)
admin.site.register(VerificationCode)