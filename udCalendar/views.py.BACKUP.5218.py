from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from udCalendar.models import UpDogUser, Friendship, Event
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from datetime import timedelta
from django.utils.timezone import utc

# TESTING JSON STUFF
from django.utils import simplejson
from django.core import serializers
import json

@login_required
# A view in which to test graphics
def test(request):
    context = RequestContext(request)
    #user = UpDogUser.objects.order_by('-user')[4]
    user = request.user.updoguser

    ships_list = user.get_friends()
    ordered_ships_list = ships_list.order_by('-meeting_count')
    friends_list = []
    for ship in ordered_ships_list:
        friends_list.append(ship.to_user.user)
    context_dict = {'friends_list': friends_list}

    return render_to_response('updog/base.html', context_dict, context)

@login_required
# The calendar view  
def calendar(request):
    context = RequestContext(request)

    ## sort user's friendships from by decr. meet count
<<<<<<< HEAD
    user.add_friend(UpDogUser.objects.order_by('-user')[2])
    ships_list = user.get_friends()
=======
    ships_list = request.user.updoguser.get_friends()

>>>>>>> 67f2c06bca5397cab3b05495a13da47e83aeeed3
    ordered_ships_list = ships_list.order_by('-meeting_count')
    friends_list = []
    for ship in ordered_ships_list:
        friends_list.append(ship.to_user.user)

<<<<<<< HEAD
    user.remove_friend(UpDogUser.objects.order_by('-user')[2])
    #json_friends = serializers.serialize("json", friends_list)
=======
>>>>>>> 67f2c06bca5397cab3b05495a13da47e83aeeed3
    context_dict = {'friends_list': friends_list}#json_friends}
    
    ## events for 60 days, starting today
    i = 0
    start_date = datetime.datetime.utcnow().replace(tzinfo=utc) # shouldn't start on today
    events_list = []
    while i < 60:
        days_events = request.user.updoguser.get_events_on_day(start_date)
        for event in days_events:
            events_list.append(event)
            print event

        start_date = start_date + datetime.timedelta(days=1)
        i = i + 1

    json_events = serializers.serialize("json", events_list)
    context_dict['events_list'] = json_events

    return render_to_response('updog/calendar.html', context_dict, context)

# TESTING AJAX STUFF
def test_ajax(request):

    context = RequestContext(request)

  #  if request.is_ajax():
   #     message = "Yes, AJAX!"
   # else:
  #      message = "Not Ajax"

    #user = UpDogUser.objects.order_by('-user')[1]

    ## sort user's friendships from by decr. meet count
    #ships_list = user.get_friends()
#    ordered_ships_list = ships_list.order_by('-meeting_count')
 #   friends_list = []
  #  for ship in ordered_ships_list:
   #     friends_list.append(ship.to_user.user)

   # context_dict = {'friends_list': friends_list}
    
    ## events for 35 days, starting today
   # i = 0
   # start_date = datetime.datetime.utcnow().replace(tzinfo=utc) # shouldn't start on today
   # events_list = []
   # while i < 35:
   #     days_events = user.get_events_on_day(start_date)
   #     for event in days_events:
   #         events_list.append(event)
   #     start_date = start_date - datetime.timedelta(days=1)
   #     i = i + 1

    #json_events = serializers.serialize("json", events_list)
    #context_dict['events_list'] = json_events

    #return HttpResponse(simplejson.dumps(context_dict))
    #return render_to_response('updog/test_ajax.html', context_dict, context)
    return render_to_response('updog/test_ajax.html', {}, context)

def login(request):
    context = RequestContext(request)
    return render_to_response('updog/login.html', {}, context)

@login_required
def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/calendar/login/')


@login_required
def add_event(request):
    if request.is_ajax():
        if request.method == 'POST':
            if 'activity' in request.POST:
                activity = request.POST['activity']

            if 'location' in request.POST:
                location = request.POST['location']

            event = Event(activity=activity, location=location, start_time=timezone.now() + timedelta(hours=47), end_time=(timezone.now() + timedelta(hours=48)))

            event.save()

            event.owners.add(request.user.updoguser)

            return HttpResponse("Success!!!!!")
    else: return HttpResponse("Failure!!!!")

@login_required
def edit_event(request):
    if request.is_ajax():
        if request.method == 'POST':
            event = Event.objects.filter(pk=request.POST['pk'])[0]
            if 'activity' in request.POST:
                event.activity = request.POST['activity']
            if 'location' in request.POST:
                event.location = request.POST['location']
            event.save()

            return HttpResponse("Success here!!!!!")
    else: return HttpResponse("Failure here!!!!")

@login_required
def change_event(request):
    if request.is_ajax():
        if request.method == 'POST':            
            event = Event.objects.filter(pk=request.POST['pk'])[0]
            time_changes = timedelta(days = int(request.POST['day_delta']), 
                minutes = int(request.POST['minute_delta']))

            event.end_time = event.end_time + time_changes

            if request.POST['resize'] == "false":
                event.start_time = event.start_time + time_changes

            event.save()

        return HttpResponse("Success123")

    else: return HttpResponse("Failure123")











