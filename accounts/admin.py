from django.contrib import admin
from .models import User, FireBaseNotification, BlockUser

# Register your models here.
admin.site.register(User)
admin.site.register(FireBaseNotification)
admin.site.register(BlockUser)