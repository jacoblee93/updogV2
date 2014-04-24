from django.db import models
from django.contrib.auth.models import User
from time import gmtime, strftime

# Create your models here.
class UpDogUser(models.Model):

    user = models.OneToOneField(User)
    fbID = models.CharField(max_length=100, unique=True)
    visible_downtimes = models.ManyToManyField('Downtime', related_name='seeing_users')
    events = models.ManyToManyField('Event', related_name='owners')
    packs = models.ManyToManyField('Pack')
    friends = models.ManyToManyField('self', through='Friendship', symmetrical=False, related_name='friend_to+')
    location = models.CharField(max_length=100)
    new_notifications = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.username

    def add_friend(self, person, symm=True):
        friendship, created = Friendship.objects.get_or_create(
            from_user=self,
            to_user=person)

        if symm:
            person.add_friend(self, False)

        return friendship

    def remove_friend(self, person, symm=True):
        Friendship.objects.filter(
            from_user=self,
            to_user=person).delete()
        if symm:
            person.remove_friend(self, False)
        return

    def get_friends(self):
        return Friendship.objects.filter(from_user=self, is_mutual=True)

    def get_downtimes_on_day(self, date):
        return self.downtime_set.filter(
            start_time__day=date.day, start_time__month=date.month, start_time__year=date.year)

    def get_events_on_day(self, date):
        return self.events.filter(
            start_time__day=date.day, start_time__month=date.month, start_time__year=date.year)
   
class Friendship(models.Model):

    to_user = models.ForeignKey(UpDogUser, related_name='friend_to')
    from_user = models.ForeignKey(UpDogUser, related_name='friend_of')
    date_last_seen = models.DateField(auto_now=True)
    meeting_count = models.IntegerField(default=0)
    is_mutual = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    
    def __unicode__(self):
        return "From %s to %s" % (self.from_user, self.to_user)
        
class Pack(models.Model):
    
    name = models.CharField(max_length=100)
    date_last_seen = models.DateField(auto_now=True)
    meeting_count = models.IntegerField(default=0)
    
    def add_user(self, user):
        return self.updoguser_set.add(user)

    def remove_user(self, user):
        return self.updoguser_set.remove(user)

    def get_users(self):
        return self.updoguser_set.all()

    def __unicode__(self):
        return self.name
    
class Downtime(models.Model):

    owner = models.ForeignKey(UpDogUser)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    preferred_activity = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return self.start_time.strftime("%Y-%m-%d %H:%M:%S")

class Event(models.Model):

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    activity = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    is_confirmed = models.BooleanField(default=True)

    def add_user(self, user):
        return self.owners.add(user)

    def remove_user(self, user):
        return self.updoguser_set.remove(user)

    def get_users(self):
        return self.updoguser_set.all()

    def __unicode__(self):
        return self.start_time.strftime("%Y-%m-%d %H:%M:%S")
