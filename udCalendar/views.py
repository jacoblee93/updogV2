from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from udCalendar.models import UpDogUser, Friendship, Event, Downtime
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

    current_user.add_friend(UpDogUser.objects.order_by('-user')[2])
    current_user.add_friend(UpDogUser.objects.order_by('-user')[3])
    current_user.add_friend(UpDogUser.objects.order_by('-user')[4])

    test_to_friendship = Friendship.objects.filter(to_user=UpDogUser.objects.order_by('-user')[4], from_user=current_user)[0]
    test_from_friendship = Friendship.objects.filter(from_user=UpDogUser.objects.order_by('-user')[4], to_user=current_user)[0]
    test_to_friendship.is_mutual= True
    test_from_friendship.is_mutual = True
    test_to_friendship.is_new = False
    test_from_friendship.is_new = False
    test_to_friendship.save()
    test_from_friendship.save()

    # Alex - friend request to build notifications bar
    #test_to_request = Friendship.objects.filter(to_user=UpDogUser.objects.order_by('-user')[2], from_user=current_user)[0]
    #test_from_request = Friendship.objects.filter(from_user=UpDogUser.objects.order_by('-user')[2], to_user=current_user)[0]
    #test_from_request.is_new = True
    #current_user.new_notifications = True
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
            if 'prev_repeated_event' in request.POST:
                prev_repeated_event = request.POST['prev_repeated_event']
            if 'next_repeated_event' in request.POST:
                next_repeated_event = request.POST['next_repeated_event']

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
            if int(repeating_event_length) != -1:
                # num_repeats is the number of repeating events to create
                num_repeats = 4
                #event.num_repeating_events = num_repeats
            repeating_events = [event,]

            # don't save the event if the end_date happens before the start_date
            if (start_datetime < end_datetime):
                event.save()
                event.owners.add(request.user.updoguser)

                # if we have repeating events, create and save them
                if int(repeating_event_length) != -1:
                    # the current and previous pk values (unique identifiers) for
                    # creating a linked list to model repeated events
                    current_pk = event.pk
                    prev_pk = -1
                    prev_event = event

                    for i in range(num_repeats):
                        print "here10!!"

                        start_datetime = start_datetime + timedelta(days=int(repeating_event_length))
                        end_datetime = end_datetime + timedelta(days=int(repeating_event_length))

                        event = Event(activity=activity, location=location,
                            start_time=start_datetime, end_time=end_datetime,
                            repeating_time_delta=repeating_event_length, prev_repeated_event=current_pk)#, num_repeating_events=num_repeats-i)
                        repeating_events.append(event)
                        event.save()
                        event.owners.add(request.user.updoguser)

                        prev_pk = current_pk
                        current_pk = event.pk

                        print "current_pk is below:"
                        print current_pk

                        prev_event.next_repeated_event = current_pk
                        prev_event.save()

                        prev_event = event
                        #print "event.prev_pk = " + prev_event.prev_repeated_event + ", event.next_pk" + prev_event.next_repeated_event
                    event.save()
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

            event.start_time = start_datetime
            event.end_time = end_datetime

          #  if (repeating_event_length not in request.POST) or (repeating_event_length == -1):
          #      event.prev_repeated_event = -1
          #      event.next_repeated_event = -1

            repeating_events = [event,]

          #############################JUST CHANGED THIS!!!  event.save()

            # don't save the edited event if the end_time happens before the start_time
            if (event.start_time < event.end_time):
                event.save()
                # if we have repeating events, create and save them
                if int(repeating_event_length) != -1:
                    # set up editting the repeating event; remove it
                    # from the linked list of repeating events
                    # and fix the linked list
                    makeRepeatingEventNonRepeating(event)
                 #   event.next_repeated_event = -1
                 #   event.prev_repeated_event = -1

                    print "event id, prev id, next id = "
                    print event.pk
                    print event.prev_repeated_event
                    print event.next_repeated_event

                    event.save()

                    # repeat 30 times
                #    for i in range(repeating_event_length):
                #        print repeating_event_length
                #        print start_datetime


                #        start_datetime = start_datetime + timedelta(days=int(repeating_event_length))
                #        end_datetime = end_datetime + timedelta(days=int(repeating_event_length))
                #        print "here4"
                #        event = Event(activity=event.activity, location=event.location, start_time=start_datetime, end_time=end_datetime, repeating_time_delta=repeating_event_length)
                #        repeating_events.append(event)
                #        print "here5"
                #        event.save()
                #        event.owners.add(request.user.updoguser)

                #        print start_datetime

            json_event = serializers.serialize("json", repeating_events)

            return HttpResponse(json_event)
    else: return HttpResponse("Failure!!!!")

@login_required
@csrf_exempt
def edit_repeating_events(request):
    if request.is_ajax():
        if request.method == 'POST':
            event = Event.objects.filter(pk=request.POST['pk'])[0]
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

            event.activity = activity
            event.location = location

            # arguments are datetime.date(year, month, day)
            start_date = datetime.date(int(start_date[6:]), int(start_date[:2]), int(start_date[3:5]))
            end_date = datetime.date(int(end_date[6:]), int(end_date[:2]), int(end_date[3:5]))

            # create time objects from start_time and end_time
            start_hour = get_hour(start_time)
            start_minute = get_minute(start_time)
            new_start_time = time(start_hour, start_minute)
            end_hour = get_hour(end_time)
            end_minute = get_minute(end_time)
            new_end_time = time(end_hour, end_minute)

            start_datetime = datetime.datetime.combine(start_date, new_start_time)
            end_datetime = datetime.datetime.combine(end_date, new_end_time)

            event.start_time = start_datetime
            event.end_time = end_datetime

            # if this is not the first repeating event, make sure
            # to disconnect it from the previous repeating event
            # in the linked list
            prev_pk = event.prev_repeated_event
            if prev_pk != -1:
                prev_event = Event.objects.filter(pk=prev_pk)[0]
                prev_event.next_repeated_event = -1;
                prev_event.save()
            # this first event to edit becomes the first event in a new set of repeating events
            event.prev_repeated_event = -1

            repeating_events = [event,]

      ################ JUST CHANGED THIS!!!!####### event.save()

            # don't save the edited event if the end_time happens before the start_time
            if (event.start_time < event.end_time):
                event.save()
                # if we have repeating events, create and save them
                if int(repeating_event_length) != -1:
                    # edit all future events (terminate when next_pk is -1)
                    while True:
                        next_pk = event.next_repeated_event
                        if next_pk != -1:

                            print "here1"

                            prev_pk = event.pk
                            event = Event.objects.filter(pk=next_pk)[0]

                            event.activity = activity
                            event.location = location

                            # if a repeating event has been changed in the middle of other
                            # repeating events, then the change in days won't line up perfectly,
                            # so we use the fact that repeated events are created all at once
                            # in order to find the change in days by using the change in pks
                            # between the current event and the previous event
                            day_change = event.pk - event.prev_repeated_event
                            start_datetime = start_datetime + timedelta(days=int(repeating_event_length)) * day_change
                            end_datetime = end_datetime + timedelta(days=int(repeating_event_length)) * day_change

                            event.start_time = start_datetime
                            event.end_time = end_datetime

                            event.prev_repeated_event = prev_pk

                            print "event.pk, prev.pk, next.pk start_datetime"
                            print event.pk
                            print event.prev_repeated_event
                            print event.next_repeated_event

                            event.save()
                            repeating_events.append(event)

                            print "here2"

                        else:
                            break

                        


                #        print start_datetime
                else:
                    return HttpResponse("Shouldn't ever get here because we should only call this function with a repeating event passed")

            json_event = serializers.serialize("json", repeating_events)

            print json_event

            return HttpResponse(json_event)
    else: return HttpResponse("Failure: request is not ajax")

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
            # make sure a changed event is no longer part of a linked list
            # of repeating events
            if event.prev_repeated_event != -1:
                prev_event = Event.objects.filter(pk = event.prev_repeated_event)[0]
                prev_event.next_repeated_event = event.next_repeated_event
                prev_event.save()
            if event.next_repeated_event != -1:
                next_event = Event.objects.filter(pk = event.next_repeated_event)[0]
                next_event.prev_repeated_event = event.prev_repeated_event
                next_event.save()
            event.repeating_time_delta = -1
            event.next_repeated_event = -1
            event.prev_repeated_event = -1

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
    else: return HttpResponse("Failure123")

@login_required
@csrf_exempt
def remove_event(request):
    if request.is_ajax():
        if request.method == 'POST':
            event = Event.objects.filter(pk=request.POST['pk'])[0]
            # set up removing an event; if that event is a repeating event,
            # remove it from the linked list of repeating events
            # and fix the linked list
            makeRepeatingEventNonRepeating(event);

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
                new_friend.new_notifications = True

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

                print to_friendship
                print from_friendship
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
            
            if not current_uduser.new_notifications:
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

# set up removing or editting an event; if that event is
# a repeating event, remove it from the linked list of
# repeating events and fix the linked list
def makeRepeatingEventNonRepeating(event):
    prev_pk = event.prev_repeated_event
    next_pk = event.next_repeated_event

    if prev_pk != -1:
        prev_event = Event.objects.filter(pk=prev_pk)[0]
    if next_pk != -1:
        next_event = Event.objects.filter(pk=next_pk)[0]

    if (prev_pk != -1):
        if (next_pk != -1):
            # if we are deleting an event between two repeated events, point those repeated events to each other
            prev_event.next_repeated_event = event.next_repeated_event;
            next_event.prev_repeated_event = event.prev_repeated_event;
            prev_event.save()
            next_event.save()
        else:
            # if we are deleting an event at the end of a list of repeated events, make the second to last event point to nothing (make it the last event)
            prev_event.next_repeated_event = -1;
            if prev_event.prev_repeated_event == -1:
                prev_event.repeating_time_delta = -1
            prev_event.save()
    elif (next_pk != -1):
        # if we are deleting the first event in a list of repeated events, make the second event have no previous event (make it the first event)
        next_event.prev_repeated_event = -1;
        if next_event.next_repeated_event == -1:
            next_event.repeating_time_delta = -1
        next_event.save()

    event.repeating_time_delta = -1
    event.prev_repeated_event = -1
    event.next_repeated_event = -1
    event.save()

@login_required
@csrf_exempt
def display(request):
    if request.is_ajax():
        if request.method == 'POST':
            current_user = request.user.updoguser
            display = parser.parse(request.POST['display_date'].strip("\""))
            print display
            json_events = gimme_events(current_user, display) + gimme_downtimes(current_user, display)
            return HttpResponse(serializers.serialize('json', json_events))
    else:
        return HttpResponse("request is not ajax")
