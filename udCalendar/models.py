from django.db import models
from django.contrib.auth.models import User
from time import gmtime, strftime

# Create your models here.
class UpDogUser(models.Model):

    user = models.OneToOneField(User)
    fbID = models.CharField(max_length=100, unique=True)
    visibleDowntimes = models.ManyToManyField('Downtime')
    events = models.ManyToManyField('Event')
    packs = models.ManyToManyField('Pack')

    def __unicode__(self):
        return self.user.username

class UpDogFriend(models.Model):

    friend = models.ForeignKey(UpDogUser)
    person = models.OneToOneField(User)
    dateLastSeen = models.DateField(auto_now=True)
    meetingCount = models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.person.username
        
class Pack(models.Model):
    
    name = models.CharField(max_length=100)
    dateLastSeen = models.DateField(auto_now=True)
    meetingCount = models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.name
    
class Downtime(models.Model):

    user = models.ForeignKey(UpDogUser)
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()
    preferredActivity = models.CharField(max_length=100, null=True, blank=True)

    def __unicode(self):
        return self.startTime.strftime("%Y-%m-%d %H:%M:%S")

class Event(models.Model):

    startTime = models.DateTimeField()
    endTime = models.DateTimeField()
    activity = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return self.startTime.strftime("%Y-%m-%d %H:%M:%S")
