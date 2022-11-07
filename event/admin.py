from django.contrib import admin
from .models import UserLocation, UserEvent

# Register your models here.
admin.site.register(UserLocation)
admin.site.register(UserEvent)
