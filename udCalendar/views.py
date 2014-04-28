from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from udCalendar.models import UpDogUser, Friendship, Event, Downtime, EventNotification
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from datetime import date, time, timedelta
from django.utils.timezone import utc
from django.db.models import Q
from dateutil import parser
import random

from django.views.decorators.csrf import csrf_exempt

# TESTING JSON STUFF
from django.utils import simplejson
from django.core import serializers
import json

@login_required
@csrf_exempt
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
@csrf_exempt
# The calendar view  
def calendar(request):
    context = RequestContext(request)
    current_user = request.user.updoguser
    #current_user = UpDogUser.objects.order_by('-user')[2]
    ## sort user's friendships from by decr. meet count
    # Alex - for local use when redesigning friends tab

    #current_user.add_friend(UpDogUser.objects.order_by('-user')[2])

    current_user.add_friend(UpDogUser.objects.order_by('-user')[1])
    current_user.add_friend(UpDogUser.objects.order_by('-user')[2])
    current_user.add_friend(UpDogUser.objects.order_by('-user')[3])
    current_user.add_friend(UpDogUser.objects.order_by('-user')[4])
    current_user.add_friend(UpDogUser.objects.order_by('-user')[5])

    test_to_friendship = Friendship.objects.filter(to_user=UpDogUser.objects.order_by('-user')[4], from_user=current_user)[0]
    test_from_friendship = Friendship.objects.filter(from_user=UpDogUser.objects.order_by('-user')[4], to_user=current_user)[0]
    test_to_friendship.is_mutual= True
    test_from_friendship.is_mutual = True
    test_to_friendship.is_new = False
    test_from_friendship.is_new = False
    test_to_friendship.save()
    test_from_friendship.save()

    test_to_friendship3 = Friendship.objects.filter(to_user=UpDogUser.objects.order_by('-user')[3], from_user=current_user)[0]
    test_from_friendship3 = Friendship.objects.filter(from_user=UpDogUser.objects.order_by('-user')[3], to_user=current_user)[0]
    test_to_friendship3.is_mutual = True
    test_from_friendship3.is_mutual = True
    test_to_friendship3.is_new = False
    test_from_friendship3.is_new = False
    test_to_friendship3.save()
    test_from_friendship3.save()

    test_to_friendship2 = Friendship.objects.filter(to_user=UpDogUser.objects.order_by('-user')[2], from_user=current_user)[0]
    test_from_friendship2 = Friendship.objects.filter(from_user=UpDogUser.objects.order_by('-user')[2], to_user=current_user)[0]
    test_to_friendship2.is_mutual = True
    test_from_friendship2.is_mutual = True
    test_to_friendship2.is_new = False
    test_from_friendship2.is_new = False
    test_to_friendship2.save()
    test_from_friendship2.save()

    test_to_friendship1 = Friendship.objects.filter(to_user=UpDogUser.objects.order_by('-user')[1], from_user=current_user)[0]
    test_from_friendship1 = Friendship.objects.filter(from_user=UpDogUser.objects.order_by('-user')[1], to_user=current_user)[0]
    test_to_friendship1.is_mutual = True
    test_from_friendship1.is_mutual = True
    test_to_friendship1.is_new = False
    test_from_friendship1.is_new = False
    test_to_friendship1.save()
    test_from_friendship1.save()

    test_to_friendship5 = Friendship.objects.filter(to_user=UpDogUser.objects.order_by('-user')[5], from_user=current_user)[0]
    test_from_friendship5 = Friendship.objects.filter(from_user=UpDogUser.objects.order_by('-user')[5], to_user=current_user)[0]
    test_to_friendship5.is_mutual = True
    test_from_friendship5.is_mutual = True
    test_to_friendship5.is_new = False
    test_from_friendship5.is_new = False
    test_to_friendship5.save()
    test_from_friendship5.save()

    # Alex - friend request to build notifications bar
    #test_to_request = Friendship.objects.filter(to_user=UpDogUser.objects.order_by('-user')[2], from_user=current_user)[0]
    #test_from_request = Friendship.objects.filter(from_user=UpDogUser.objects.order_by('-user')[2], to_user=current_user)[0]
    #test_from_request.is_new = True
    #current_user.new_friend_requests = True
    #test_to_request.is_new = False
    #test_to_request.is_mutual = False
    #test_from_request.is_mutual = False
    #test_from_request.save()
    #test_to_request.save()
    #current_user.save()

    
    ships_list = current_user.get_friends()

    ordered_ships_list = ships_list.order_by('-meeting_count')
    friends_list = []
    for ship in ordered_ships_list:
        friends_list.append(ship.to_user.user)

    # Alex - for local use when rediesigning friends tab 
    #json_friends = serializers.serialize("json", friends_list)

    context_dict = {'friends_list': friends_list}#json_friends}

    #display = parser.parse(request.POST['display_date'].strip("\""))
    display = datetime.datetime.utcnow().replace(tzinfo=utc)

    json_events = serializers.serialize("json", gimme_events(current_user, display))
    json_downtimes = serializers.serialize("json", gimme_downtimes(current_user, display))
    context_dict['events_list'] = json_events
    context_dict['downtimes'] = json_downtimes
    context_dict['username'] = request.user.username;

    return render_to_response('updog/calendar.html', context_dict, context)

def gimme_events(current_user, date):
    ## events for 60 days, surrounding date
    i = 0
    start_date = date
    events_list = []
    while i < 30:
        days_events = current_user.get_events_on_day(start_date)
        for event in days_events:
            events_list.append(event)

        start_date = start_date + datetime.timedelta(days=1)
        i = i + 1
    i = 0
    start_date = date
    start_date = start_date - datetime.timedelta(days=1)
    while i < 30:
        days_events = current_user.get_events_on_day(start_date)
        for event in days_events:
            events_list.append(event)

        start_date = start_date - datetime.timedelta(days=1)
        i = i + 1

    return events_list

def gimme_downtimes(current_user, date):
    ## downtimes for 60 days, surrounding today
    i = 0
    start_date = date
    dts_list = []
    while i < 30:
        days_dts = current_user.get_downtimes_on_day(start_date)
        for dt in days_dts:
            dts_list.append(dt)

        start_date = start_date + datetime.timedelta(days=1)
        i = i + 1
    i = 0
    start_date = date

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
@csrf_exempt
def get_friends_events(request):
    if request.is_ajax():
        if request.method == 'POST':
            if 'friend' in request.POST:
                friend = request.POST['friend']
                friend = User.objects.filter(username=friend)[0]
                if friend:
                    display = parser.parse(request.POST['display_date'].strip("\""))

                    friend_events = gimme_events(friend.updoguser, display)
                    json_events = serializers.serialize("json", friend_events)

                    return HttpResponse(json_events)

                else: return HttpResponse("Failure!")
    else: 
        return HttpResponse("Failure!!!!")

@login_required
@csrf_exempt
def get_friends_downtimes(request):
    if request.is_ajax():
        if request.method == 'POST':
            if 'friend' in request.POST:
                friend = request.POST['friend']
                friend = User.objects.filter(username=friend)[0]
                if friend:
                    display = parser.parse(request.POST['display_date'].strip("\""))

                    friend_downtimes = gimme_downtimes(friend.updoguser, display)
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
@csrf_exempt
def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/calendar/login/')

@login_required
@csrf_exempt
def add_downtime(request):
    if request.is_ajax():
        if request.method == 'POST':
            startDate = None
            endDate = None
            if 'startDate' in request.POST:
                startDate = request.POST['startDate']
            else: return HttpResponse("Error! No startDate provided")
            if 'endDate' in request.POST:
                endDate = request.POST['endDate']
            else: return HttpResponse("Error! No endDate provided")

            startDate = startDate.strip("\"")
            startDate = parser.parse(startDate)
            endDate = endDate.strip("\"")
            endDate = parser.parse(endDate)

            me = request.user.updoguser
            
            existing_dt = me.downtime_set.filter(start_time__gte=startDate, 
                start_time__lte=endDate) | me.downtime_set.filter(end_time__gte=startDate,
                end_time__lte=endDate) | me.downtime_set.filter(start_time__lte=startDate,
                end_time__gte=endDate)

            existing_dt = existing_dt.exclude(start_time=endDate)
            existing_dt = existing_dt.exclude(end_time=startDate)
            merged = False
            if len(existing_dt) == 0:
                new_downtime = Downtime.objects.get_or_create(owner=me, start_time=startDate, end_time=endDate)[0]
                response = serializers.serialize('json',[new_downtime, ])
            else:
                min_startDate = startDate
                max_endDate = endDate
                remove_me = []

                for dt in existing_dt:
                    if dt.preferred_activity == None:
                        if not (dt.start_time <= startDate and dt.end_time >= endDate):
                            min_startDate = min(min_startDate, dt.start_time)
                            max_endDate = max(max_endDate, dt.end_time)
                            remove_me.append(dt)
                        else:
                            return HttpResponse(serializers.serialize('json',[]))
                        merged = True
                        
                if not merged:
                    new_downtime = Downtime.objects.get_or_create(owner=me, start_time=startDate, end_time=endDate)[0]
                    response = serializers.serialize('json',[new_downtime, ])

                else:
                    
                    new_downtime=Downtime.objects.get_or_create(owner=me, start_time=min_startDate, 
                        end_time=max_endDate)[0]
                    remove_me.insert(0, new_downtime)
                    response = serializers.serialize('json',remove_me)
                    for dt in remove_me:
                        if dt != new_downtime:
                            dt.delete()
                    
            return HttpResponse(response)

    return HttpResponse("Error!")

@login_required
@csrf_exempt
def add_event(request):
    if request.is_ajax():
        if request.method == 'POST':
            context = RequestContext(request)

            if 'activity' in request.POST:
                activity = request.POST['activity']
            if 'location' in request.POST:
                location = request.POST['location']
            if 'start_date' in request.POST:
                start_date = request.POST['start_date']
            if 'end_date' in request.POST:
                end_date = request.POST['end_date']
            if 'start_time' in request.POST:
                start_time = request.POST['start_time']
            if 'end_time' in request.POST:
                end_time = request.POST['end_time']
            if 'repeating_event_length' in request.POST:
                repeating_event_length = request.POST['repeating_event_length']

            start_date = datetime.date(int(start_date[6:]), int(start_date[:2]), int(start_date[3:5]))
            end_date = datetime.date(int(end_date[6:]), int(end_date[:2]), int(end_date[3:5]))

            # create time objects from start_time and end_time
            start_hour = get_hour(start_time)
            start_minute = get_minute(start_time)
            start_time = time(start_hour, start_minute)
            end_hour = get_hour(end_time)
            end_minute = get_minute(end_time)
            end_time = time(end_hour, end_minute)

            start_datetime = datetime.datetime.combine(start_date, start_time)
            end_datetime = datetime.datetime.combine(end_date, end_time)

            event = Event(activity=activity, location=location, start_time=start_datetime, end_time=end_datetime, repeating_time_delta=repeating_event_length)
            repeating_events = [event,]

            # don't save the event if the end_date happens before the start_date
            if (start_datetime < end_datetime):
                event.save()
                event.owners.add(request.user.updoguser)
                
                # if we have repeating events, create and save them
                if int(repeating_event_length) != -1:
                    for i in range(100):
                        start_datetime = start_datetime + timedelta(days=int(repeating_event_length))
                        end_datetime = end_datetime + timedelta(days=int(repeating_event_length))
                        event = Event(activity=activity, location=location, start_time=start_datetime, end_time=end_datetime, repeating_time_delta=repeating_event_length)
                        repeating_events.append(event)
                        event.save()
                        event.owners.add(request.user.updoguser)

            json_event = serializers.serialize("json", repeating_events)

            return HttpResponse(json_event)
    else: return HttpResponse("Failure!!!!")

@login_required
@csrf_exempt
def edit_event(request):
    if request.is_ajax():
        if request.method == 'POST':
            event = Event.objects.filter(pk=request.POST['pk'])[0]
            if 'activity' in request.POST:
                event.activity = request.POST['activity']
            if 'location' in request.POST:
                event.location = request.POST['location']
            if 'start_date' in request.POST:
                start_date = request.POST['start_date']
            if 'end_date' in request.POST:
                end_date = request.POST['end_date']
            if 'start_time' in request.POST:
                start_time = request.POST['start_time']
            if 'end_time' in request.POST:
                end_time = request.POST['end_time']
            if 'repeating_event_length' in request.POST:
                repeating_event_length = request.POST['repeating_event_length']

            start_date = datetime.date(int(start_date[6:]), int(start_date[:2]), int(start_date[3:5]))
            end_date = datetime.date(int(end_date[6:]), int(end_date[:2]), int(end_date[3:5]))
            
            # create time objects from start_time and end_time
            start_hour = get_hour(start_time)
            start_minute = get_minute(start_time)
            start_time = time(start_hour, start_minute)
            end_hour = get_hour(end_time)
            end_minute = get_minute(end_time)
            end_time = time(end_hour, end_minute)

            start_datetime = datetime.datetime.combine(start_date, start_time)
            end_datetime = datetime.datetime.combine(end_date, end_time)

            event.start_time = datetime.datetime.combine(start_date, start_time)
            event.end_time = datetime.datetime.combine(end_date, end_time)

            repeating_events = [event,]

            # don't save the edited event if the end_time happens before the start_time
            if (event.start_time < event.end_time):
                event.save()
                # if we have repeating events, create and save them
                if int(repeating_event_length) != -1:
                    # repeat 30 times
                    for i in range(30):
                        print repeating_event_length
                        print start_datetime


                        start_datetime = start_datetime + timedelta(days=int(repeating_event_length))
                        end_datetime = end_datetime + timedelta(days=int(repeating_event_length))
                        print "here4"
                        event = Event(activity=event.activity, location=event.location, start_time=start_datetime, end_time=end_datetime, repeating_time_delta=repeating_event_length)
                        repeating_events.append(event)
                        print "here5"
                        event.save()
                        event.owners.add(request.user.updoguser)

                        print start_datetime

            json_event = serializers.serialize("json", repeating_events)

            return HttpResponse(json_event)
    else: return HttpResponse("Failure!!!!")

@login_required
@csrf_exempt
def edit_downtime(request):
    if request.is_ajax():
        if request.method == 'POST':
            downtime = Downtime.objects.filter(pk=request.POST['pk'])[0]
            if 'activity' in request.POST:
                downtime.preferred_activity = request.POST['activity']
                if len(request.POST['activity']) == 0:
                    downtime.preferred_activity = None
            downtime.save()

            me = request.user.updoguser
            
            existing_dt = me.downtime_set.filter(start_time__gte=downtime.start_time, 
                start_time__lte=downtime.end_time) | me.downtime_set.filter(end_time__gte=downtime.start_time,
                end_time__lte=downtime.end_time) | me.downtime_set.filter(start_time__lte=downtime.start_time,
                end_time__gte=downtime.end_time)
            existing_dt = existing_dt.exclude(start_time=downtime.end_time)
            existing_dt = existing_dt.exclude(end_time=downtime.start_time)
            existing_dt = existing_dt.exclude(pk=downtime.pk)
            existing_dt = existing_dt.filter(preferred_activity=downtime.preferred_activity)
            merged = False
            if len(existing_dt) == 0:
                return HttpResponse(serializers.serialize('json',[]))
            else:
                min_startDate = downtime.start_time
                max_endDate = downtime.end_time
                remove_me = []

                for dt in existing_dt:
                    if (dt.preferred_activity == downtime.preferred_activity): # only merge if they have the same pref activity
                        if not (dt.start_time <= downtime.start_time and dt.end_time >= downtime.end_time):
                            min_startDate = min(min_startDate, dt.start_time)
                            max_endDate = max(max_endDate, dt.end_time)
                            remove_me.append(dt)
                        else:
                            response = serializers.serialize('json', [downtime, ])
                            downtime.delete()
                            return HttpResponse(response)
                        merged = True
                        
                if not merged:
    
                    return HttpResponse(serializers.serialize('json',[]))
                else:
                    downtime.start_time = min_startDate
                    downtime.end_time = max_endDate
                    downtime.save()
                    remove_me.insert(0, downtime)
                    response = serializers.serialize('json',remove_me)
                    for dt in remove_me:
                        if dt != downtime:
                            dt.delete()
                    
            return HttpResponse(response)

    return HttpResponse("Invalid request")

@login_required
@csrf_exempt
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
@csrf_exempt
def change_downtime(request):
    if request.is_ajax():
        if request.method == 'POST':
            downtime = Downtime.objects.filter(pk=request.POST['pk'])[0]
            time_changes = timedelta(days = int(request.POST['day_delta']), 
                minutes = int(request.POST['minute_delta']))

            endDate = downtime.end_time + time_changes

            if request.POST['resize'] == "false":
                startDate = downtime.start_time + time_changes
            else:
                startDate = downtime.start_time

            ##=============================
            me = request.user.updoguser
            
            existing_dt = me.downtime_set.filter(start_time__gte=startDate, 
                start_time__lte=endDate) | me.downtime_set.filter(end_time__gte=startDate,
                end_time__lte=endDate) | me.downtime_set.filter(start_time__lte=startDate,
                end_time__gte=endDate)

            existing_dt = existing_dt.exclude(start_time=endDate)
            existing_dt = existing_dt.exclude(end_time=startDate)
            existing_dt = existing_dt.exclude(pk=downtime.pk)

            merged = False
            if len(existing_dt) == 0:
                downtime.start_time = startDate
                downtime.end_time = endDate
                downtime.save()
                return HttpResponse(serializers.serialize('json',[]))
            else:
                min_startDate = startDate
                max_endDate = endDate
                remove_me = []

                for dt in existing_dt:
                    if dt.preferred_activity == downtime.preferred_activity: # only merge if they have the same pref activity
                        if not (dt.start_time <= startDate and dt.end_time >= endDate):
                            min_startDate = min(min_startDate, dt.start_time)
                            max_endDate = max(max_endDate, dt.end_time)
                            remove_me.append(dt)
                        else:
                            response = serializers.serialize('json', [downtime, ])
                            downtime.delete()
                            return HttpResponse(response)
                        merged = True
                        
                if not merged:
                    downtime.start_time = startDate
                    downtime.end_time = endDate
                    downtime.save()
                    return HttpResponse(serializers.serialize('json',[]))
                else:
                    downtime.start_time = min_startDate
                    downtime.end_time = max_endDate
                    downtime.save()
                    remove_me.insert(0, downtime)
                    response = serializers.serialize('json',remove_me)
                    for dt in remove_me:
                        if dt != downtime:
                            dt.delete()
                    
            return HttpResponse(response)
            ##======================================

    else: return HttpResponse("Failure123")

@login_required
@csrf_exempt
def remove_event(request):
    if request.is_ajax():
        if request.method == 'POST':
            event = Event.objects.filter(pk=request.POST['pk'])[0]
            event.owners.remove(request.user.updoguser)
            if not event.owners:
                event.delete()

            return HttpResponse("Success here!!!!!")
    else: return HttpResponse("Failure here!!!!")

@login_required
@csrf_exempt
def remove_downtime(request):
    if request.is_ajax():
        if request.method == 'POST':
            downtime = Downtime.objects.filter(pk=request.POST['pk'])[0]
            downtime.delete()

            return HttpResponse("Successfully deleted downtime")

    return HttpResponse("Invalid request")

@login_required
def get_friends(request):
    if request.is_ajax():
        if request.method == "GET":
            current_user = request.GET["user"]
            user = UpDogUser.objects.filter(user__username = current_user)[0]
            friendships_list = Friendship.objects.filter(to_user = user, is_mutual = True)

            fl = len(friendships_list)
            friends = []

            for i in xrange(0, fl):
                friends.append(friendships_list[i].from_user.user)
            friends = serializers.serialize('json', friends)
            return HttpResponse(friends)

    return HttpResponse("Uh-Oh")

@login_required
@csrf_exempt
def find_friends(request):
    if request.is_ajax():
        if request.method == 'GET':
            l = len(request.GET["search"])

            friends_list = UpDogUser.objects.filter(Q(user__first_name__iexact=request.GET["search"]) | Q(user__last_name__iexact=request.GET["search"]) | Q(user__username__iexact=request.GET["search"]) | Q(user__first_name__startswith=request.GET["search"]) | Q(user__last_name__startswith=request.GET["search"]) | Q(user__username__startswith=request.GET["search"]))
            fl = len(friends_list)
            user_list = []
            

            for i in xrange(0,fl):
                user_list.append(friends_list[i].user)
            user_list = serializers.serialize('json', user_list)
            return HttpResponse(user_list)

    return HttpResponse("Uh-Oh")

@login_required
@csrf_exempt
def invite_search(request):
    if request.is_ajax():
        if request.method == 'GET':
            l = len(request.GET["search"])
            friends_list = UpDogUser.objects.filter(Q(user__first_name__iexact=request.GET["search"]) | Q(user__last_name__iexact=request.GET["search"]) | Q(user__username__iexact=request.GET["search"]) | Q(user__first_name__startswith=request.GET["search"]) | Q(user__last_name__startswith=request.GET["search"]) | Q(user__username__startswith=request.GET["search"]))
            friends_list = friends_list.exclude(user__username = request.user.username);
            fl = len(friends_list)
            user_list = []

            for i in xrange(0,fl):
                if Friendship.objects.filter(to_user=request.user.updoguser, from_user=friends_list[i], is_mutual=True):
                    user_list.append(friends_list[i].user)
            user_list = serializers.serialize('json', user_list)
            return HttpResponse(user_list)

    return HttpResponse("Uh-Oh")

@login_required
@csrf_exempt
def send_friend_request(request):
    if request.is_ajax():
        if request.method == 'POST':

            if 'new_friend' in request.POST and 'i' in request.POST:
                i = request.POST['i']
                new_friend = UpDogUser.objects.filter(user__username=request.POST['new_friend'])[0]
                current_user = request.user.updoguser

                to_friendship = Friendship.objects.filter(to_user=new_friend, from_user=current_user)

                if to_friendship:
                    return HttpResponse("Request Pending," + i)

                current_user.add_friend(new_friend)

                to_friendship = Friendship.objects.filter(to_user=new_friend, from_user=current_user)[0]
                from_friendship = Friendship.objects.filter(to_user=current_user, from_user=new_friend)[0]

                to_friendship.is_new = True
                new_friend.new_friend_requests = True

                to_friendship.save()
                new_friend.save()

                return HttpResponse("Success," + i)

    return HttpResponse("Failure!")

@login_required
@csrf_exempt
def accept_friend_request(request):
    if request.is_ajax():
        if request.method == 'POST':
            if 'new_friend' in request.POST:
                new_friend = UpDogUser.objects.filter(user__username=request.POST['new_friend'])[0]
                current_user = request.user.updoguser

                to_friendship = Friendship.objects.filter(to_user=new_friend, from_user=current_user)[0]
                from_friendship = Friendship.objects.filter(to_user=current_user, from_user=new_friend)[0]

                to_friendship.is_mutual = True
                from_friendship.is_mutual = True

                to_friendship.is_new = False
                from_friendship.is_new = False

                to_friendship.save()
                from_friendship.save()

                return HttpResponse("Success!")

    return HttpResponse("Failure!")

@login_required
@csrf_exempt
def reject_friend_request(request):
    if request.is_ajax():
        if request.method == 'POST':
            if 'new_friend' in request.POST:
                new_friend = UpDogUser.objects.filter(user__username=request.POST['new_friend'])[0]
                current_user = request.user.updoguser

                to_friendship = Friendship.objects.filter(to_user=new_friend, from_user=current_user)[0]
                from_friendship = Friendship.objects.filter(to_user=current_user, from_user=new_friend)[0]

                to_friendship.is_new = False
                from_friendship.is_new = False
                to_friendship.save()
                from_friendship.save()

                return HttpResponse("Success!")

    return HttpResponse("Failure!")

@login_required
@csrf_exempt
def suggest(request):
    if request.is_ajax():
        if request.method == 'GET':
            current_user = request.user.updoguser

            if 'pk' in request.GET:
                my_dt = Downtime.objects.filter(pk=request.GET['pk'])[0]
            else:
                start_date = datetime.datetime.utcnow().replace(tzinfo=utc)
                after_today = current_user.downtime_set.filter(start_time__gte=start_date)
                ordered = after_today.order_by('start_time')
                if len(ordered) == 0:
                    return HttpResponse(None)
                my_dt = ordered[0]

            my_friends = current_user.get_friends()
            if len(my_friends) == 0:
                return HttpResponse("NoFriends")
            my_friends_ord = my_friends.order_by('-date_last_seen')
            minscore = 0

            options = []

            while len(options) == 0:
                maxscore = len(my_friends_ord)-1
                amigo = my_friends_ord[int(minscore+(maxscore-minscore)*random.random()**2)].to_user
                options = amigo.downtime_set.filter(start_time__gte=my_dt.start_time, 
                    start_time__lte=my_dt.end_time) | amigo.downtime_set.filter(end_time__gte=my_dt.start_time,
                     end_time__lte=my_dt.end_time) | amigo.downtime_set.filter(start_time__lte=my_dt.start_time,
                      end_time__gte=my_dt.end_time)

                options = options.exclude(start_time=my_dt.end_time)
                options = options.exclude(end_time=my_dt.start_time)

                my_friends_ord = my_friends_ord.exclude(to_user = amigo)
                if len(my_friends_ord) == 0 and len(options) == 0:
                    return HttpResponse("NoMatch")

            choose = options.order_by('start_time')[0]
            single = []
            single.append(get_overlap(my_dt, choose))
            single.append(amigo)
            json_me = serializers.serialize('json',single)
            return HttpResponse(json_me)
    else:
        return HttpResponse("You fuckup!!?!?!?")

def get_overlap(one, two):

    if one.start_time >= two.end_time or one.end_time <= two.start_time:
        return None
    if one.start_time < two.start_time:
        if one.end_time < two.end_time:
            overlap = Event.objects.get_or_create(start_time=two.start_time, end_time=one.end_time,
             is_confirmed = False)[0]
        else:
            overlap = Event.objects.get_or_create(start_time=two.start_time, end_time=two.end_time,
             is_confirmed = False)[0]
    else:
        if one.end_time >= two.end_time:
            overlap = Event.objects.get_or_create(start_time=one.start_time, end_time=two.end_time,
             is_confirmed = False)[0]
        else:
            overlap = Event.objects.get_or_create(start_time=one.start_time, end_time=one.end_time, 
                is_confirmed = False)[0]
    overlap.add_user(one.owner)
    #overlap.add_user(two.owner)
    return overlap

@login_required
def display_friend_requests(request):
    if request.is_ajax():
        if request.method == 'GET':

            current_uduser = request.user.updoguser
            
            if not current_uduser.new_friend_requests:
                return HttpResponse("No new notifications")

            else:
                requests = Friendship.objects.filter(to_user=current_uduser, is_new = True)
                print requests
                rl = len(requests)
                request_list = []

                for i in xrange(0,rl):
                    request_list.append(requests[i].from_user.user)
                requests_out = serializers.serialize('json', request_list)

                return HttpResponse(requests_out)

    return HttpResponse("Failure")

@login_required
def get_notifications(request):
    #test_notif = EventNotification(to_user=request.user.updoguser, from_user=UpDogUser.objects.order_by('-user')[2], event=Event.objects.all()[0], is_reply=True)
    #test_notif.save()
    if request.is_ajax():
        if request.method == 'GET':

            current_uduser = request.user.updoguser
            event_notifications = EventNotification.objects.filter(to_user=current_uduser) 
            if event_notifications:
                event_notifications = serializers.serialize('json', event_notifications)


            else: 
                event_notifications = []

            return HttpResponse(event_notifications)

    return HttpResponse("Failure")

@login_required
def send_event_notifications(request):
    if request.is_ajax():
        if request.method == 'POST':

            current_uduser = request.user.updoguser

            if 'event' in request.POST:
                event = Event.objects.filter(pk=request.POST['event'])[0]
                if 'to_users' in request.POST:
                    to_users = json.loads(request.POST['to_users'])

                    if 'data_type' in request.POST:

                        if request.POST['data_type'] == 'pk':

                            for key in to_users:
                                recipient = UpDogUser.objects.filter(pk=key)[0]
                                event_notification = EventNotification(to_user=recipient, from_user=current_uduser, event=event)
                                event_notification.save()

                        elif request.POST['data_type'] == 'username':

                            for username in to_users:
                                recipient = UpDogUser.objects.filter(user__username=username)[0]
                                event_notification = EventNotification(to_user=recipient, from_user=current_uduser, event=event)
                                event_notification.save()


                return HttpResponse("Success")


    return HttpResponse("Failure")

@login_required
def respond_to_event_notification(request):
    if request.is_ajax():
        if request.method == 'POST':

            current_uduser = request.user.updoguser

            if 'notification' in request.POST:
                notification = EventNotification.objects.filter(pk=request.POST['notification'])[0]

                if 'response' in request.POST:
                    response = request.POST['response']

                    if response == 'accept':
                        notification.event.add_user(current_uduser)
                        notification.event.save()
                        reply_notification = EventNotification(to_user=notification.from_user, from_user=current_uduser, event=notification.event, is_reply=True)

                    return HttpResponse("Success")

    return HttpResponse("Failure")


# return the hour of the time variable, where the time variable
# is formatted as H:MM AP or HH:MM AP, where AP is either AM or
# PM, and we don't include to digits for the hour if it's
# less than 10
def get_hour(time):
    # the index of the colon in time
    col_index = int(time.find(':'))
    # the index of the space in time
    space_index = int(time.find(' '))

    # error messages to help with future potential bugs
    if col_index == -1:
        print "In get_minute method: time is in incorrect format"
    if space_index == -1:
        print "In get_minute method: time is in incorrect format"
    # the hour of the start date
    hour = int(time[:col_index])
    
    if time[space_index+1:] == "AM":
        am_pm = "AM"
    else: am_pm = "PM"
    
    if (hour == 12) and (am_pm == "AM"):
        hour = 0
    elif am_pm == "PM":
        # we don't change 12:00 PM to 24:00 for military time
        if hour != 12:
            # use military time (add 12 to hours after 12:00PM)
            hour = hour + 12

    return hour

# return the minute of the time variable, where the time variable
# is formatted as H:MM AP or HH:MM AP, where AP is either AM or
# PM, and we don't include to digits for the hour if it's
# less than 10
def get_minute(time):
    col_index = int(time.find(':'))
    space_index = int(time.find(' '))

    # error messages to help with future potential bugs
    if col_index == -1:
        print "In get_minute method: time is in incorrect format"
    if space_index == -1:
        print "In get_minute method: time is in incorrect format"

    return int(time[col_index+1:space_index])

@login_required
@csrf_exempt
def display(request):
    if request.is_ajax():
        if request.method == 'POST':
            current_user = request.user.updoguser
            display = parser.parse(request.POST['display_date'].strip("\""))
            json_events = gimme_events(current_user, display) + gimme_downtimes(current_user, display)
            return HttpResponse(serializers.serialize('json', json_events))
    else:
        return HttpResponse("You fuckup!!?!?!?")

@login_required
@csrf_exempt
def get_event_owners(request):
    if request.is_ajax():
        if request.method == 'GET':
            if 'type' in request.GET:
                # if this is an event
                if request.GET['type'] == "true":
                    if 'pk' in request.GET:
                        event = Event.objects.filter(pk=request.GET['pk'])[0]
                        event_owners = []
                        owners =  event.owners.all()
                        for owner in owners:
                            event_owners.append(owner.user)
                        
                        return HttpResponse(serializers.serialize('json', event_owners))
                # else this is a downtime
                else:
                    if 'pk' in request.GET:
                        downtime = Downtime.objects.filter(pk=request.GET['pk'])[0]
                        return HttpResponse(serializers.serialize('json', [downtime.owner.user]))
    else:
        return HttpResponse("Failure.")




