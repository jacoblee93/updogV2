from django.contrib import admin
from udCalendar.models import UpDogUser, Friendship, Pack, Downtime, Event

# Register your models here.
admin.site.register(UpDogUser)
admin.site.register(Friendship)
admin.site.register(Pack)
admin.site.register(Downtime)
admin.site.register(Event)
