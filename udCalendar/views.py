from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from udCalendar.models import UpDogUser, Friendship
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from django.utils.timezone import utc
import json

# A view in which to test graphics
def test(request):
    context = RequestContext(request)

    user = UpDogUser.objects.order_by('-user')[0]

    ## sort user's friendships from by decr. meet count                                         
    ships_list = user.get_friends()
    ordered_ships_list = ships_list.order_by('-meeting_count')
    friends_list = []
    for ship in ordered_ships_list:
        friends_list.append(ship.to_user.user)
    context_dict = {'friends_list': friends_list}

    return render_to_response('updog/base.html', {}, context)

# The calendar view  
def calendar(request):
    context = RequestContext(request)
    user = UpDogUser.objects.order_by('-user')[4]
    
    ## sort user's friendships from by decr. meet count
    ships_list = user.get_friends()
    ordered_ships_list = ships_list.order_by('-meeting_count')
    friends_list = []
    for ship in ordered_ships_list:
        friends_list.append(ship.to_user.user)
    context_dict = {'friends_list': friends_list}
    
    ## events for 35 days, starting today
    i = 0
    start_date = datetime.datetime.utcnow().replace(tzinfo=utc) # shouldn't start on today
    events_list = []
    while i < 35:
        days_events = user.get_events_on_day(start_date)
        for event in days_events:
            events_list.append(event)
        start_date = start_date + datetime.timedelta(days=1)
        i = i + 1

    context_dict['events_list'] = events_list
    return render_to_response('updog/calendar.html', context_dict, context)
