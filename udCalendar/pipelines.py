from models import UpDogUser
from urllib2 import urlopen
from social_auth.models import UserSocialAuth
import json
from requests import request, HTTPError
from django.core.files.base import ContentFile
from django.template.defaultfilters import slugify

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

    try:
        data = urlopen('https://graph.facebook.com/%s?access_token=%s' % (response['id'], UserSocialAuth.objects.filter(provider='facebook', user=user).get().tokens['access_token']))
        data = data.read()
    
        json_data = json.loads(data)
        if json_data.has_key('location'):
            if json_data['location'].has_key('name'):
                uduser.location= json_data['location']['name']

        uduser.save()

    except HTTPError:
        pass

def save_profile_picture(backend, details, response, social_user, uid, user, *args,**kwargs):

    if not hasattr(user, 'updoguser'):
        new_uduser = UpDogUser(user=user)
        new_uduser.save()

    uduser = user.updoguser

    if uduser.profile_picture:
        return

    url = 'http://graph.facebook.com/{0}/picture'.format(response['id'])

    try:

        picture = urlopen(url)

        uduser.profile_picture.save(user.username + '-social.jpg', ContentFile(picture.read()))

        uduser.save()

    except HTTPError:
        pass







