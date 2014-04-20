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
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

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

    current_user = request.user.updoguser
    #current_user = UpDogUser.objects.order_by('-user')[2]
    ## sort user's friendships from by decr. meet count
    # Alex - for local use when redesigning friends tab
    #current_user.add_friend(UpDogUser.objects.order_by('-user')[5])
    current_user.add_friend(UpDogUser.objects.order_by('-user')[2])
    current_user.add_friend(UpDogUser.objects.order_by('-user')[3])
    current_user.add_friend(UpDogUser.objects.order_by('-user')[4])

    ships_list = current_user.get_friends()
    #ships_list = request.user.updoguser.get_friends()

    ordered_ships_list = ships_list.order_by('-meeting_count')
    friends_list = []
    for ship in ordered_ships_list:
        friends_list.append(ship.to_user.user)

    # Alex - for local use when rediesigning friends tab 
    current_user.remove_friend(UpDogUser.objects.order_by('-user')[1])
    current_user.remove_friend(UpDogUser.objects.order_by('-user')[2])
    current_user.remove_friend(UpDogUser.objects.order_by('-user')[3])
    current_user.remove_friend(UpDogUser.objects.order_by('-user')[4])
    #json_friends = serializers.serialize("json", friends_list)

    context_dict = {'friends_list': friends_list}#json_friends}

    json_events = serializers.serialize("json", gimme_events(current_user))
    context_dict['events_list'] = json_events
    context_dict['username'] = request.user.username;

    return render_to_response('updog/calendar.html', context_dict, context)

def gimme_events(current_user):
    ## events for 60 days, starting today
    i = 0
    start_date = datetime.datetime.utcnow().replace(tzinfo=utc) # shouldn't start on today
    events_list = []
    while i < 30:
        days_events = current_user.get_events_on_day(start_date)
        for event in days_events:
            events_list.append(event)

        start_date = start_date + datetime.timedelta(days=1)
        i = i + 1
    i = 0
    start_date = datetime.datetime.utcnow().replace(tzinfo=utc) # shouldn't start on today
    start_date = start_date - datetime.timedelta(days=1)
    while i < 30:
        days_events = current_user.get_events_on_day(start_date)
        for event in days_events:
            events_list.append(event)

        start_date = start_date - datetime.timedelta(days=1)
        i = i + 1

    return events_list

def gimme_downtimes(current_user):
    ## downtimes for 60 days, surrounding today
    i = 0
    start_date = datetime.datetime.utcnow().replace(tzinfo=utc)
    dts_list = []
    while i < 30:
        days_dts = current_user.get_downtimes_on_day(start_date)
        for dt in days_dts:
            dts_list.append(dt)

        start_date = start_date + datetime.timedelta(days=1)
        i = i + 1
    i = 0
    start_date = datetime.datetime.utcnow().replace(tzinfo=utc)
    start_date = start_date - datetime.timedelta(days=1)
    while i < 30:
        days_dts = current_user.get_downtimes_on_day(start_date)
        for dt in days_dts:
            dts_list.append(dt)

        start_date = start_date - datetime.timedelta(days=1)
        i = i + 1

    return dts_list

#### TRYING TO have FRONT END REQUEST A FRIENDS EVENTS::::: WE DON:T ACTUALLY NEED THIS *SWITCH TO DOWNTIMES*
@login_required
@csrf_exempt ## DELETE_ME
def get_friends_events(request):
    if request.is_ajax():
        if request.method == 'POST':
            if 'friend' in request.POST:
                friend = request.POST['friend']
                friend = User.objects.filter(username=friend)[0]
                if friend:
                    friend_events = gimme_events(friend.updoguser)
                    json_events = serializers.serialize("json", friend_events)

                    return HttpResponse(json_events)

                else: return HttpResponse("Failure!")
    else: 
        return HttpResponse("Failure!!!!")

@login_required
@csrf_exempt ## DELETE_ME
def get_friends_downtimes(request):
    if request.is_ajax():
        if request.method == 'POST':
            if 'friend' in request.POST:
                friend = request.POST['friend']
                friend = User.objects.filter(username=friend)[0]
                if friend:
                    friend_downtimes = gimme_downtimes(friend.updoguser)
                    json_downtimes = serializers.serialize("json", friend_downtimes)

                    return HttpResponse(json_downtimes)

                else: return HttpResponse("Failure!")
    else: 
        return HttpResponse("Failure!!!!")


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
@csrf_exempt ## DELETE_ME
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
@csrf_exempt ## DELETE_ME
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
@csrf_exempt ## DELETE_ME
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

@login_required
@csrf_exempt ## DELETE_ME
def find_friends(request):
    if request.is_ajax():
        if request.method == 'GET':
            l = len(request.GET["search"])
            # problems: only matches full string, is also case sensitive
            friends_list = UpDogUser.objects.filter(Q(user__first_name=request.GET["search"]) | Q(user__last_name=request.GET["search"]) | Q(user__username=request.GET["search"]))
            fl = len(friends_list)
            user_list = []

            for i in xrange(0,fl):
                user_list.append(friends_list[i].user)
            user_list = serializers.serialize('json', user_list)
            return HttpResponse(user_list)

    return HttpResponse("Uh-Oh")











