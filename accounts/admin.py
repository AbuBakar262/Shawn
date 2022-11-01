from django.contrib import admin
from .models import User, VerificationCode, FriendRequest, Friend, BlockUser

# Register your models here.
admin.site.register(User)
admin.site.register(VerificationCode)
admin.site.register(FriendRequest)
admin.site.register(Friend)
admin.site.register(BlockUser)