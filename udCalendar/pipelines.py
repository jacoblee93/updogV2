from models import UpDogUser
from urllib2 import urlopen
from social_auth.models import UserSocialAuth
import json

def get_fbid(backend, details, response, social_user, uid, user, *args, **kwargs):

    if not hasattr(user, 'updoguser'):

        new_uduser = UpDogUser(user=user)
        new_uduser.save()
    
    uduser = user.updoguser
    uduser.fbID = response['id']
    uduser.save()

def get_location(backend, details, response, social_user, uid, user, *args, **kwargs):

    if not hasattr(user, 'updoguser'):
        
        new_uduser = UpDogUser(user=user)
        new_uduser.save()
    
    uduser = user.updoguser

    data = urlopen('https://graph.facebook.com/%s?access_token=%s' % (response['id'], UserSocialAuth.objects.filter(provider='facebook', user=user).get().tokens['access_token']))
    data = data.read()
    
    uduser.location = json.loads(data)['location']['name']
    uduser.save()
