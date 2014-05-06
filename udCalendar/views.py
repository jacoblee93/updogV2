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
#from datetime import datetime
from django.utils.timezone import utc

from django.db.models import Q
from dateutil import parser
from operator import attrgetter
import random
from django.views.decorators.csrf import csrf_exempt

# TESTING JSON STUFF
from django.utils import simplejson
from django.core import serializers
import json

import os

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
    try:
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
        else: 
            return HttpResponse("Failure!!!!")
    except Exception as e:
        print e

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

            ### comment these two back out
            #existing_dt = existing_dt.exclude(start_time=endDate)
            #existing_dt = existing_dt.exclude(end_time=startDate)
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
            if 'num_repeating_events' in request.POST:
                num_repeating_events = int(request.POST['num_repeating_events'])

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
                    # the current and previous pk values (unique identifiers) for
                    # creating a linked list to model repeated events
                    current_pk = event.pk
                    prev_pk = -1
                    prev_event = event

                    # num_repeating_events - 1 makes it so that we have a total of
                    # num_repeating_events events because we've already added an
                    # event by the time we get to this loop
                    for i in range(num_repeating_events-1):
                        start_datetime = start_datetime + timedelta(days=int(repeating_event_length))
                        end_datetime = end_datetime + timedelta(days=int(repeating_event_length))

                        event = Event(activity=activity, location=location,
                            start_time=start_datetime, end_time=end_datetime,
                            repeating_time_delta=repeating_event_length, prev_repeated_event=current_pk)
                        repeating_events.append(event)
                        event.save()
                        event.owners.add(request.user.updoguser)

                        prev_pk = current_pk
                        current_pk = event.pk

                        prev_event.next_repeated_event = current_pk
                        prev_event.save()

                        prev_event = event
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
                    event.save()

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
                            event.save()
                            repeating_events.append(event)

                        else:
                            break
                else:
                    return HttpResponse("Shouldn't ever get here because we should only call this function with a repeating event passed")

            json_event = serializers.serialize("json", repeating_events)

            return HttpResponse(json_event)
    else: return HttpResponse("Failure: request is not ajax")

@login_required
@csrf_exempt
def edit_downtime(request):
    if request.is_ajax():
        if request.method == 'POST':
            downtime = Downtime.objects.filter(pk=parse_downtime_id(request.POST['pk']))[0]
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
            #existing_dt = existing_dt.exclude(start_time=downtime.end_time)
            #existing_dt = existing_dt.exclude(end_time=downtime.start_time)
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
def resolve_repeating_conflicts(request):
    if request.is_ajax():
        if request.method == 'POST':
            try:
                uduser = request.user.updoguser

                event = Event.objects.filter(pk=request.POST['pk'])[0]

                startDate = event.start_time
                endDate = event.end_time

                # this event's updog user
                # uduser = request.user.updoguser

                # get all downtimes overlapping with this event
                overlapping_downtimes = uduser.downtime_set.filter(start_time__gte=startDate, 
                    start_time__lte=endDate) | uduser.downtime_set.filter(end_time__gte=startDate,
                    end_time__lte=endDate) | uduser.downtime_set.filter(start_time__lte=startDate,
                    end_time__gte=endDate)

                list_of_new_downtimes = []

                # store all the downtimes that overlap with the changed event
                for downtime in overlapping_downtimes:
                    new_downtimes = handle_overlap(event, downtime)
                    if new_downtimes:
                        for new_downtime in new_downtimes:
                            list_of_new_downtimes.append(new_downtime)

                json_downtimes = serializers.serialize("json", list_of_new_downtimes)

            except Exception as e:
                print e

            return HttpResponse(json_downtimes);
        else: return HttpResponse("Didn't sent a POST request to resolve_repeating_conflicts");
    else: return HttpResponse("Failed function resolve_repeating_conflicts");

@login_required
@csrf_exempt
def change_event(request):
    if request.is_ajax():
        if request.method == 'POST':    
            try:        
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

                if 'activity' in request.POST:
                    event.activity = request.POST['activity']

                event.save()

                startDate = event.start_time
                endDate = event.end_time

                # this event's updog user
                uduser = request.user.updoguser

                # get all downtimes overlapping with this event
                overlapping_downtimes = uduser.downtime_set.filter(start_time__gte=startDate, 
                    start_time__lte=endDate) | uduser.downtime_set.filter(end_time__gte=startDate,
                    end_time__lte=endDate) | uduser.downtime_set.filter(start_time__lte=startDate,
                    end_time__gte=endDate)

                list_of_new_downtimes = []

                # store all the downtimes that overlap with the changed event
                for downtime in overlapping_downtimes:
                    new_downtimes = handle_overlap(event, downtime)
                    if new_downtimes:
                        for new_downtime in new_downtimes:
                            list_of_new_downtimes.append(new_downtime)

                json_downtimes = serializers.serialize("json", list_of_new_downtimes)


            except Exception as e:
                print e

        # return all the downtimes that overlap with the changed event
        return HttpResponse(json_downtimes)

    else: return HttpResponse("Failure123")

def parse_downtime_id(front_id):
    return str(-int(front_id))

@login_required
@csrf_exempt
def change_downtime(request):
    if request.is_ajax():
        if request.method == 'POST':
            downtime = Downtime.objects.filter(pk=parse_downtime_id(request.POST['pk']))[0]
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


            #############comment back out
            #existing_dt = existing_dt.exclude(start_time=endDate)
            #existing_dt = existing_dt.exclude(end_time=startDate)
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

# this view checks if a changed downtime conflicts with any existing events
# and if there are conflicts, it returns a list of the newly changed downtimes
@login_required
@csrf_exempt
def event_conflicts(request):
    if request.is_ajax():
        if request.method == 'POST':

            if 'pk' in request.POST:
                downtime = Downtime.objects.filter(pk=request.POST['pk'])[0]

            # this event's updog user
            uduser = request.user.updoguser

            startDate = downtime.start_time
            endDate = downtime.end_time

        

            # get all events overlapping with this event
            overlapping_events = uduser.events.filter(start_time__gte=startDate, 
                start_time__lte=endDate) | uduser.events.filter(end_time__gte=startDate,
                end_time__lte=endDate) | uduser.events.filter(start_time__lte=startDate,
                end_time__gte=endDate)

            list_of_new_downtimes = []

            num_overlapping_events = len(overlapping_events)
            if num_overlapping_events == 1:
                new_downtimes = handle_overlap(overlapping_events[0], downtime)
                if new_downtimes:
                    for new_downtime in new_downtimes:
                        list_of_new_downtimes.append(new_downtime)
            elif num_overlapping_events != 0:
                new_downtimes = handle_multiple_overlaps(overlapping_events, downtime)
                if new_downtimes:
                    for new_downtime in new_downtimes:
                        list_of_new_downtimes.append(new_downtime)

            json_downtimes = serializers.serialize("json", list_of_new_downtimes)

            # return all the downtimes that overlap with the changed event
            return HttpResponse(json_downtimes)
        else: return HttpResponse("event_conflicts got a non-post ajax call")
    else: return HttpResponse("failed event_conflicts")

# this function will return the earliest available
# downtime, or it will return None
def earliest_downtime(downtimes):
    if downtimes:
        earliest_downtime = downtimes[0]
    else: return None

    for downtime in downtimes:
        if downtime.start_time < earliest_downtime.start_time:
            earliest_downtime = downtime
    return earliest_downtime

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
            downtime = Downtime.objects.filter(pk=parse_downtime_id(request.POST['pk']))[0]
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
            friendships_list = friendships_list.order_by('-meeting_count')
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
    try:
        if request.is_ajax():
            if request.method == 'GET':

                friendships_list = Friendship.objects.filter(to_user = request.user.updoguser)
                friendships_list = friendships_list.order_by('-is_mutual')

                friends_list = UpDogUser.objects.filter(Q(user__first_name__istartswith=request.GET["search"]) | Q(user__last_name__istartswith=request.GET["search"]) | Q(user__username__istartswith=request.GET["search"]))
                friends_list = friends_list.exclude(user__username = request.user.username)

                users = []

                
                fl = len(friendships_list)
                f2 = len(friends_list)
                user_list = []
                friend_status = []

                for i in xrange(0,fl):
                    if friendships_list[i].is_mutual == True:
                        users.append(friendships_list[i].from_user)

                ul = len(users)

                for i in xrange(0,ul):
                    if (users[i] in friends_list):
                        if friendships_list[i].is_mutual:
                            user_list.append(users[i].user)
                            friend_status.append(1)

                for i in xrange(0,f2):
                    if (friends_list[i] in users):
                        i = i
                    else:
                        check = Friendship.objects.filter(to_user = request.user.updoguser, from_user = friends_list[i].user, is_mutual = False)
                        if not check:   
                            user_list.append(friends_list[i].user)
                            friend_status.append(0)

                if user_list:
                    user_list = serializers.serialize('json', user_list)
                    json_stuff = simplejson.dumps([user_list, friend_status])
                    return HttpResponse(json_stuff, content_type ="application/json")

                else:
                    console.log
                    return HttpResponse("no friends")

    except Exception as e:
        print e

    return HttpResponse("Uh-Oh")

@login_required
def search_friends(request):
    if request.is_ajax():
        if request.method == 'GET':
            l = len(request.GET["search"])

            friends_list = UpDogUser.objects.filter(Q(user__first_name__istartswith=request.GET["search"]) | Q(user__last_name__istartswith=request.GET["search"]) | Q(user__username__istartswith=request.GET["search"])) 
            fl = len(friends_list)
            user_list = []

            for i in xrange(0,fl):
                friendship = Friendship.objects.filter(to_user = request.user.updoguser, from_user = friends_list[i], is_mutual = True)
                if friendship:
                    user_list.append(friends_list[i].user)
            user_list = serializers.serialize('json', user_list)
            return HttpResponse(user_list)

    return HttpResponse("Uh-Oh")

@login_required
@csrf_exempt
def invite_search(request):
    if request.is_ajax():
        if request.method == 'GET':
            if 'search' in request.GET:
                if 'event' in request.GET:
                    event = Event.objects.filter(pk=request.GET['event'])[0]
                    l = len(request.GET["search"])
                    friends_list = UpDogUser.objects.filter(Q(user__first_name__istartswith=request.GET["search"]) | Q(user__last_name__istartswith=request.GET["search"]) | Q(user__username__istartswith=request.GET["search"]))
                    friends_list = friends_list.exclude(user__username = request.user.username);
                    fl = len(friends_list)
                    user_list = []

                    for i in xrange(0,fl):
                        if Friendship.objects.filter(to_user=request.user.updoguser, from_user=friends_list[i], is_mutual=True):
                            if len(EventNotification.objects.filter(event=event,to_user=friends_list[i])) == 0:
                                user_list.append(friends_list[i].user)
                    user_list = serializers.serialize('json', user_list)
                    return HttpResponse(user_list)

    return HttpResponse("Uh-Oh")

@login_required
@csrf_exempt
def suggest_search(request):
    if request.is_ajax():
        if request.method == 'GET':
            if 'search' in request.GET:
                l = len(request.GET["search"])
                friends_list = UpDogUser.objects.filter(Q(user__first_name__istartswith=request.GET["search"]) | Q(user__last_name__istartswith=request.GET["search"]) | Q(user__username__istartswith=request.GET["search"]))
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
def multi_suggest(request):
    try:
        if request.is_ajax():
            if request.method == 'GET':
                if 'suggest_list' in request.GET:
                    exclude_list = []
                    if 'exclude' in request.GET:
                        exclude = json.loads(request.GET['exclude'])
                        for exclude_me in exclude:
                            exclude_list.append(Event.objects.filter(pk=exclude_me)[0])

                    if 'hours' in request.GET:
                        hours = request.GET['hours']
                        if hours == "NaN":
                            hours = 0;
                        else:
                            hours = int(hours)
                    else: hours = 0
                    if 'minutes' in request.GET:
                        minutes = request.GET['minutes']
                        if minutes == "NaN":
                            minutes = 0;
                        else:
                            minutes = int(minutes)
                    else: minutes = 0
                    if hours == 0 and minutes == 0:
                        is_specified = False
                    else:
                        is_specified = True

                    delta = timedelta(hours=hours,minutes=minutes)
                    single = []
                    users = json.loads(request.GET['suggest_list'])
                    #print users
                    current_user = request.user.updoguser
                    ## fix this if we have time!
                    start_date = datetime.datetime.utcnow().replace(tzinfo=utc) - timedelta(hours=4)
                    after_today = current_user.downtime_set.filter(end_time__gte=start_date)

                    ordered = after_today.order_by('start_time')
                    if len(ordered) == 0:
                        return HttpResponse(None)
                    
                    if len(users) == 0:
                        return HttpResponse("NoFriends")


                    for my_dt in ordered: # cycle through logged in users downtimes

                        amigo_dts = [] # list of lists of downtimes
                        for user in users:

                            amigo = UpDogUser.objects.filter(user__username=user)[0]
                            if amigo.user not in single:
                                single.append(amigo.user)
                            options = amigo.downtime_set.filter(start_time__gte=my_dt.start_time, 
                                start_time__lte=my_dt.end_time) | amigo.downtime_set.filter(end_time__gte=my_dt.start_time,
                                 end_time__lte=my_dt.end_time) | amigo.downtime_set.filter(start_time__lte=my_dt.start_time,
                                  end_time__gte=my_dt.end_time)

                            options = options.exclude(start_time=my_dt.end_time)
                            options = options.exclude(end_time=my_dt.start_time)

                            if len(options) == 0:
                                ordered.exclude(pk=my_dt.pk)
                                if len(ordered) == 0:
                                    return HttpResponse("NoMatch")
                                break
                                ####continue to next my_dt
                            else:
                                amigo_dts.append(options)

                        if len(amigo_dts) != len(users):
                            continue
                        newb = multi_get_overlap(my_dt, amigo_dts, delta, is_specified, exclude_list)
                        if newb:
                            added = Event.objects.get_or_create(start_time=newb[0], end_time=newb[1])[0]
                            added.add_user(my_dt.owner)
                            single.insert(0, added)
                            json_me = serializers.serialize('json',single)
                            return HttpResponse(json_me)
                    return HttpResponse("NoMatch")
                    
        else:
            return HttpResponse("You messup!!?!?!?")
    except Exception as e:
        print e

def multi_get_overlap(mine, yalls, delta, is_specified, exclude_list):
    try:
        ## walls overlap is a list of overlaps (each overlap consists of a start and end time)
        ## that work for all users that have been checked so far
        ## fix this if we have time!
        start_date = datetime.datetime.utcnow().replace(tzinfo=utc) - timedelta(hours=4)
        real_time = max(mine.start_time, start_date)
        walls_overlap = [[real_time, mine.end_time]]
        ## for each friend in the suggests list, update the overlaps list to reflect thier freetimes
        for yall in yalls: # yalls is a list of a list of downtimes      
            ## for each overlap possibility that has worked for everyone else so far...
            for overlap in walls_overlap:
                walls_overlap.remove(overlap)
                for yall_dt in yall: # yall is a list of a single friends downtimes
                    burlap = get_overlap(yall_dt, overlap)

                    if burlap:
                        walls_overlap.append(burlap)

        if len(exclude_list) > 0:
            for excluded_event in exclude_list:
                for overlap in walls_overlap:
                    if (overlap[0]>=excluded_event.start_time and overlap[0] <=excluded_event.end_time) or (overlap[1]>=excluded_event.start_time and overlap[1]<=excluded_event.end_time) or (overlap[0]<=excluded_event.start_time and overlap[1]>=excluded_event.end_time):
                      if not overlap[0] == excluded_event.end_time and not overlap[1] == excluded_event.start_time:
                        # they overlap~
                        # split walls overlap by the excluded event
                        walls_overlap.remove(overlap)

                        exclusions = get_exclusions(overlap, [excluded_event.start_time, excluded_event.end_time])
                        if exclusions:
                            for exclusion in exclusions:
                                walls_overlap.append(exclusion)

        # return the first thing in the overlaps list
        if len(walls_overlap) == 0:
            return None
        else:
            if is_specified:

                acceptable_overlaps = []
                unacceptable_overlaps = []
                for wall in walls_overlap:
                    if wall[1]-wall[0] > delta:
                        acceptable_overlaps.append(wall)
                    else:
                        unacceptable_overlaps.append(wall)
                if len(acceptable_overlaps) == 0:
                    longest_overlap = unacceptable_overlaps[0]
                    for overlap in unacceptable_overlaps:
                        if overlap[1]-overlap[0] > longest_overlap[1]-longest_overlap[0]:
                            longest_overlap = overlap
                    return longest_overlap

                else:
                    earliest_overlap = acceptable_overlaps[0] # initialize
                    for overlap in acceptable_overlaps:
                        if overlap[0] < earliest_overlap[0]:
                            earliest_overlap = overlap
                    return [earliest_overlap[0], earliest_overlap[0] + delta]
            else:
                earliest_overlap = walls_overlap[0]
                for overlap in walls_overlap:
                    if overlap[0] < earliest_overlap[0]:
                        earliest_overlap = overlap
                return earliest_overlap
    except Exception as e:
        print e
    return "failure"

# this function returns the overlapped time between one and two as
# an event
def get_overlap(one, two):
    if type(one) is Downtime:
        one_start_time = one.start_time
        one_end_time = one.end_time
    else:
        one_start_time = one[0]
        one_end_time = one[1]

    if type(two) is Downtime:
        two_start_time = two.start_time
        two_end_time = two.end_time
    else:
        two_start_time = two[0]
        two_end_time = two[1]

    if one_start_time >= two_end_time or one_end_time <= two_start_time:
        return None
    if one_start_time < two_start_time:
        if one_end_time < two_end_time:
            overlap = [two_start_time, one_end_time]
        else:
            overlap = [two_start_time, two_end_time]
    else:
        if one_end_time >= two_end_time:
            overlap = [one_start_time, two_end_time]
        else:
            overlap = [one_start_time, one_end_time]

    start_date = datetime.datetime.utcnow().replace(tzinfo=utc) - timedelta(hours=4)

    if overlap[1] < start_date:
        return None
    if overlap[0] < start_date:
        return [start_date, overlap[1]]
    return overlap

@login_required
@csrf_exempt
def suggest(request):
    try:
        if request.is_ajax():
            if request.method == 'GET':
                exclude_list = []

                if 'exclude' in request.GET:
                    exclude = json.loads(request.GET['exclude'])
                    for exclude_me in exclude:
                        exclude_list.append(Event.objects.filter(pk=exclude_me)[0])

                # each friend in this list corresponds to an event in exclude_list
                # so that we don't suggest the same event with the same person
                exclude_friends_list = []
                if 'exclude_friends' in request.GET:
                    exclude_friends = json.loads(request.GET['exclude_friends'])
                    for excluded_friend in exclude_friends:
                        exclude_friends_list.append(UpDogUser.objects.filter(pk=excluded_friend)[0])

                single = []
                current_user = request.user.updoguser

                if 'hours' in request.GET:
                    hours = request.GET['hours']
                    if hours == "NaN":
                        hours = 0;
                    else:
                        hours = int(hours)
                else: hours = 0
                if 'minutes' in request.GET:
                    minutes = request.GET['minutes']
                    if minutes == "NaN":
                        minutes = 0;
                    else:
                        minutes = int(minutes)
                else: minutes = 0

                if hours == 0 and minutes == 0:
                    is_specified = False
                else:
                    is_specified = True

                delta = timedelta(hours=hours,minutes=minutes)

                if 'pk' in request.GET:
                    if request.GET['pk'] != "no_pk":
                        my_dt = Downtime.objects.filter(pk=parse_downtime_id(request.GET['pk']))[0]
                        output = get_friends_overlapping_downtimes(current_user, my_dt, exclude_friends_list)
                        if output == "NoMatch":
                            return HttpResponse("NoMatch")
                        elif output == "NoFriends":
                            return HttpResponse("NoFriends")
                        json_output = create_event_from_friends_overlapping_downtimes(output[0], my_dt, output[1])
                        if json_output == None:
                            return HttpResponse("Failure")
                        return HttpResponse(json_output)
                    else:
                        ### fix later if patience found
                        start_date = datetime.datetime.utcnow().replace(tzinfo=utc) - timedelta(hours=4)
                        after_today = current_user.downtime_set.filter(end_time__gte=start_date)
                        ordered = after_today.order_by('start_time')
                        if len(ordered) == 0:
                            return HttpResponse(None)
                        
                        # time was not specified
                        if not is_specified:
                            # do what we did before
                            while len(ordered) > 0:
                                my_dt = ordered[0]
                                ordered = ordered.exclude(pk=my_dt.pk)
                                my_friends = current_user.get_friends()
                                if len(my_friends) == 0:
                                    return HttpResponse("NoFriends")
                                my_friends_ord = my_friends.order_by('-date_last_seen')
                                minscore = 0

                                options = []
                                while len(my_friends_ord) > 0:
                                    maxscore = len(my_friends_ord)
                                    amigo = my_friends_ord[int(minscore+(maxscore-minscore)*random.random()**2)].to_user

                                    options = amigo.downtime_set.filter(start_time__gte=my_dt.start_time, 
                                        start_time__lte=my_dt.end_time) | amigo.downtime_set.filter(end_time__gte=my_dt.start_time,
                                         end_time__lte=my_dt.end_time) | amigo.downtime_set.filter(start_time__lte=my_dt.start_time,
                                          end_time__gte=my_dt.end_time)

                                    options = options.exclude(start_time=my_dt.end_time)
                                    options = options.exclude(end_time=my_dt.start_time)

                                    ### what was originall below
                                    my_friends_ord = my_friends_ord.exclude(to_user = amigo)
                                    if len(my_friends_ord) == 0 and len(options) == 0:
                                        if len(ordered) == 0:
                                            return HttpResponse("NoMatch")
                                        break
                                    #for index in indices: #### FIX FIX FIX BSBSBSBSB
                                    #    options = options.exclude(start_time=exclude_list[index].start_time) 
                                    all_options = []

                                    if len(options) > 0:
                                        ## these are the indices where the amigo is in the exclude friends list
                                        indices = [i for i, x in enumerate(exclude_friends_list) if x == amigo]

                                        for option in options:
                                            real_time = max(option.start_time, start_date)
                                            all_options.append([real_time, option.end_time])
                                        for index in indices:
                                            for option in all_options:
                                                if (option[0]>=exclude_list[index].start_time and option[0] <=exclude_list[index].end_time) or (option[1]>=exclude_list[index].start_time and option[1]<=exclude_list[index].end_time) or (option[0]<=exclude_list[index].start_time and option[1]>=exclude_list[index].end_time):
                                                    if not option[0] == exclude_list[index].end_time and not option[1] == exclude_list[index].start_time:
                                                        all_options.remove(option)
                                            
                                                        exclusions = get_exclusions(option, [exclude_list[index].start_time, exclude_list[index].end_time])
                                                        if exclusions:
                                                            for exclusion in exclusions:
                                                                all_options.append(exclusion)

                                        #for option in options.order_by('start_time'):
                                        all_options.sort()
                                    
                                    if len(all_options) > 0:
                                        #option = all_options.order_by('start_time')[0]
                                        overlap = None
                                        i = 0
                                        while overlap == None:
                                            option = all_options[i]
                                            overlap = get_overlap(my_dt, option)
                                            i = i + 1
                                            if i >= len(all_options):
                                                break

                                        if overlap == None:
                                            break

                                        newb = Event.objects.get_or_create(start_time=overlap[0],end_time=overlap[1])[0]
                                        newb.add_user(my_dt.owner)
                                        single.append(newb)

                                        single.append(amigo.user)

                                        json_output = serializers.serialize('json',single)

                                        return HttpResponse(json_output)
                            return HttpResponse("NoMatch")
                        # we have specified a time 
                        else:
                            earliest_unacceptable = None
                            earliest_amigo = None

                            while len(ordered) > 0:
                                my_dt = ordered[0]
                                ordered = ordered.exclude(pk=my_dt.pk)
                                options = []
                               
                                my_friends = current_user.get_friends()
                                if len(my_friends) == 0:
                                    return HttpResponse("NoFriends")
                                my_friends_ord = my_friends.order_by('-date_last_seen')
                                minscore = 0


                                while len(my_friends_ord) > 0:
                                    maxscore = len(my_friends_ord)
                                    amigo = my_friends_ord[int(minscore+(maxscore-minscore)*random.random()**2)].to_user
                                    options = amigo.downtime_set.filter(start_time__gte=my_dt.start_time, 
                                        start_time__lte=my_dt.end_time) | amigo.downtime_set.filter(end_time__gte=my_dt.start_time,
                                         end_time__lte=my_dt.end_time) | amigo.downtime_set.filter(start_time__lte=my_dt.start_time,
                                          end_time__gte=my_dt.end_time)

                                    options = options.exclude(start_time=my_dt.end_time)
                                    options = options.exclude(end_time=my_dt.start_time)

                                    my_friends_ord = my_friends_ord.exclude(to_user = amigo)
                                    if len(my_friends_ord) == 0 and len(options) == 0:
                                        if len(ordered) == 0:

                                            if earliest_unacceptable == None:
                                                return HttpResponse("NoMatch")
                                            else:
                                                overlap = earliest_unacceptable
                                                amigo = earliest_amigo
                                                newb = Event.objects.get_or_create(start_time=overlap[0],end_time=overlap[1])[0]
                                                newb.add_user(my_dt.owner)

                                                single.append(newb)
                                                single.append(amigo.user)
                                                json_output = serializers.serialize('json',single)
                                                if json_output == None:
                                                    return HttpResponse("Failure")
                                                return HttpResponse(json_output)
                                        break

                                    if len(options) > 0:
                                        ## these are the indices where the amigo is in the exclude friends list
                                        indices = [i for i, x in enumerate(exclude_friends_list) if x == amigo]

                                        all_options = []
                                        for option in options:
                                            real_time = max(option.start_time, start_date)
                                            all_options.append([real_time, option.end_time])
                                        for index in indices:
                                            for option in all_options:
                                                if (option[0]>=exclude_list[index].start_time and option[0] <=exclude_list[index].end_time) or (option[1]>=exclude_list[index].start_time and option[1]<=exclude_list[index].end_time) or (option[0]<=exclude_list[index].start_time and option[1]>=exclude_list[index].end_time):
                                                    if not option[0] == exclude_list[index].end_time and not option[1] == exclude_list[index].start_time:
                                                        all_options.remove(option)

                                                        exclusions = get_exclusions(option, [exclude_list[index].start_time, exclude_list[index].end_time])
                                                        if exclusions:
                                                            for exclusion in exclusions:
                                                                all_options.append(exclusion)

                                        #for option in options.order_by('start_time'):
                                        all_options.sort()

                                        for option in all_options:
                                            overlap = get_overlap(my_dt, option)
                                            if overlap != None:
                                                if overlap[1]-overlap[0] < delta:
                                                    if earliest_unacceptable == None:
                                                        earliest_unacceptable = overlap
                                                        earliest_amigo = amigo
                                                    elif overlap[0] < earliest_unacceptable[0]:
                                                        earliest_unacceptable = overlap
                                                        earliest_amigo = amigo

                                                # if it is long enough
                                                else:
                                                    overlap[1] = overlap[0] + delta
                                                    newb = Event.objects.get_or_create(start_time=overlap[0],end_time=overlap[1])[0]
                                                    newb.add_user(my_dt.owner)
                                                    single.append(newb)

                                                    single.append(amigo.user)

                                                    json_output = serializers.serialize('json',single)

                                                    return HttpResponse(json_output)

                            if earliest_unacceptable == None:
                                return HttpResponse("NoMatch")
                            else:
                                overlap = earliest_unacceptable
                                amigo = earliest_amigo
                                newb = Event.objects.get_or_create(start_time=overlap[0],end_time=overlap[1])[0]
                                newb.add_user(my_dt.owner)

                                single.append(newb)
                                single.append(amigo.user)
                                json_output = serializers.serialize('json',single)
                                if json_output == None:
                                    return HttpResponse("Failure")
                                return HttpResponse(json_output)
        else:
            return HttpResponse("You messup!!?!?!?")
    except Exception as e:
        print e

## one is the thing you are cutting up, two is the time chunk you want to exclude
def get_exclusions(one, two):

    exclusions = []
    if one[0] > two[0]: # cases 1 and 4
        if one[1] > two[1]: # case 1
            exclusions.append([two[1],one[1]])
        ## case 4 - do nothing (whole thing gets excluded)
    elif one[0] == two[0]:
        if one[1] > two[1]:
            exclusions.append([two[1], one[1]])
    else: # case 2 and 3
        if one[1] <= two[1]: # case 2
            exclusions.append([one[0], two[0]])
        else: # case 3
            exclusions.append([one[0], two[0]])
            exclusions.append([two[1], one[1]])

    return exclusions

def create_event_from_friends_overlapping_downtimes(options, my_dt, amigo):

    choose = options.order_by('start_time')[0]
    single = []
    overlap = get_overlap(my_dt, choose)
    if overlap:
        newb = Event.objects.get_or_create(start_time=overlap[0],end_time=overlap[1])[0]
        newb.add_user(my_dt.owner)
        single.append(newb)
    else:
        return None
    single.append(amigo.user)
    json_me = serializers.serialize('json',single)
    return json_me

def get_friends_overlapping_downtimes(current_user, my_dt, excluded_amigos):
    #return HttpResponse("Hellow!")
    my_friends = current_user.get_friends()
    if len(my_friends) == 0:
        return "NoFriends"

    my_friends_ord = my_friends.order_by('-date_last_seen')
    for excluded_amigo in excluded_amigos:
        my_friends_ord = my_friends_ord.exclude(to_user__pk=excluded_amigo.pk)
    if len(my_friends_ord) == 0:
        return "NoMatch"

    minscore = 0

    options = []
    while len(options) == 0:
        maxscore = len(my_friends_ord)
        amigo = my_friends_ord[int(minscore+(maxscore-minscore)*random.random()**2)].to_user
        options = amigo.downtime_set.filter(start_time__gte=my_dt.start_time, 
            start_time__lte=my_dt.end_time) | amigo.downtime_set.filter(end_time__gte=my_dt.start_time,
             end_time__lte=my_dt.end_time) | amigo.downtime_set.filter(start_time__lte=my_dt.start_time,
              end_time__gte=my_dt.end_time)

        options = options.exclude(start_time=my_dt.end_time)
        options = options.exclude(end_time=my_dt.start_time)

        my_friends_ord = my_friends_ord.exclude(to_user = amigo)
        if len(my_friends_ord) == 0 and len(options) == 0:
            return "NoMatch"

    return [options, amigo]

# when multiple events overlap with a downtime, act accordingly.  Return any
# newly created, or changed, downtimes
def handle_multiple_overlaps(overlapping_events, downtime):
    overlapping_events = sorted(overlapping_events, key=attrgetter('start_time'))
    num_overlapping_events = len(overlapping_events)

    start_times = []
    end_times = []

    # if change is -1, then all is in order, otherwise it indicates that we are
    # effectively merging two events in terms of their start and end times
    change = -1
    # this is the last endtime from several events that need to be merged
    last_endtime = -1
    # start at the first event to check if the first event has an end time after
    # the second event's start time.  If this is the case, treat the two events
    # as one event with start time being the first's start time and end time
    # being the second's end time.  Continue doing this so we have a list of
    # effective start and end times afterwards
    for i in range(1, num_overlapping_events):
        # if we need to do some merging
        if last_endtime != -1:
            if overlapping_events[i].start_time <= last_endtime:
                if change == -1:
                    change = 1
                    last_endtime = overlapping_events[i-1].end_time
                else: change = change + 1
                if overlapping_events[i].end_time > last_endtime:
                    last_endtime = overlapping_events[i].end_time
            else:
                start_times.append(overlapping_events[i-change-1].start_time)
                end_times.append(last_endtime)
                change = -1
                last_endtime = -1
        # if we have a new merge
        elif overlapping_events[i].start_time <= overlapping_events[i-1].end_time:
            if change == -1:
                change = 1
                last_endtime = overlapping_events[i-1].end_time
            else: change = change + 1
            if overlapping_events[i].end_time > last_endtime:
                last_endtime = overlapping_events[i].end_time
        # if the previous event didn't involve a merge with this event
        # or a past event, then append it as its own event
        elif overlapping_events[i-1].end_time not in end_times:
            start_times.append(overlapping_events[i-1].start_time)
            end_times.append(overlapping_events[i-1].end_time)

    if change == -1:
        # the last two events are merged
        if overlapping_events[i].start_time <= overlapping_events[i-1].end_time:
            start_times.append(overlapping_events[i-1].start_time)
            if overlapping_events[i-1].end_time > overlapping_events[i].end_time:
                end_times.append(overlapping_events[i-1].end_time)
            else: end_times.append(overlapping_events[i].end_time)
            #start_times.append(overlapping_events[i-1].start_time)
            #end_times.append(overlapping_events[i].end_time)
        # the last event is considered its own event (not merged)
        else:
            start_times.append(overlapping_events[num_overlapping_events-1].start_time)
            end_times.append(overlapping_events[num_overlapping_events-1].end_time)
    else:
        # the last 2 + change events are merged
        if overlapping_events[i].start_time <= last_endtime:
            start_times.append(overlapping_events[i-change].start_time)
            if overlapping_events[i].end_time > last_endtime:
                last_endtime = overlapping_events[i].end_time
            end_times.append(last_endtime)
        # previous events are merged and the last event is its own event
        else:
            # merge the previous events
            start_times.append(overlapping_events[i-change-1].start_time)
            end_times.append(last_endtime)
            # append the last event
            start_times.append(overlapping_events[i].start_time)
            end_times.append(overlapping_events[i].end_time)

    preferred_activity = downtime.preferred_activity
    owner = downtime.owner

    # to use for the last downtime
    downtimeEnd = downtime.end_time;

    # the first new downtime
    if start_times[0] > downtime.start_time:
        downtime.end_time = start_times[0]
        downtime.save()
    # a list of downtimes to return
        new_downtimes = [downtime,]
    # delete the downtime if its start_time overlaps with an event
    else:
        temp_downtime = Downtime(start_time=downtime.start_time,
                end_time=downtime.start_time, preferred_activity=downtime.preferred_activity,
                owner=downtime.owner, pk=downtime.pk)
        downtime.delete()
        new_downtimes = [temp_downtime,]

    for i in range(1, len(start_times)):
        new_downtime = Downtime.objects.get_or_create(start_time=end_times[i-1],
                end_time=start_times[i], preferred_activity=preferred_activity,
                owner=owner)[0]
        new_downtimes.append(new_downtime)
    if downtimeEnd > end_times[len(end_times)-1]:
        new_downtime = Downtime.objects.get_or_create(start_time=end_times[len(end_times)-1],
                end_time=downtimeEnd, preferred_activity=preferred_activity,
                owner=owner)[0]
        new_downtimes.append(new_downtime)

    return new_downtimes

# when an event overlaps with a downtime, act accordingly.  Return any newly
# created, or changed, downtimes
def handle_overlap(event, downtime):
    # no overlap
    if event.start_time >= downtime.end_time or event.end_time <= downtime.start_time:
        return
    # event starts before downtime
    if event.start_time <= downtime.start_time:
        # remove the downtime
        if event.end_time >= downtime.end_time:
            # we purposely make the start_time and end_time the same so that when we find
            # this downtime on the front end, we can properly delete it
            temp_downtime = Downtime(start_time=downtime.start_time,
                end_time=downtime.start_time, preferred_activity=downtime.preferred_activity,
                owner=downtime.owner, pk=downtime.pk)
            downtime.delete()
            return [temp_downtime, ]
        # cut out the downtime that overlaps with the event, but keep the part of
        # the downtime that goes later than the event
        else:
            downtime.start_time = event.end_time
            downtime.save()
            return [downtime,]
    # event starts after downtime
    else:
        # remove the end of the downtime's end_time
        if event.end_time >= downtime.end_time:
            downtime.end_time = event.start_time
            downtime.save()
            return [downtime,]
        # split the downtime
        else:
            new_downtime = Downtime.objects.get_or_create(start_time=event.end_time,
                end_time=downtime.end_time, preferred_activity=downtime.preferred_activity,
                owner=downtime.owner)
            downtime.end_time = event.start_time
            downtime.save()
            return [new_downtime[0], downtime]

@login_required
def display_friend_requests(request):
    if request.is_ajax():
        if request.method == 'GET':

            current_uduser = request.user.updoguser
            
            if not current_uduser.new_friend_requests:
                return HttpResponse("No new notifications")

            else:
                requests = Friendship.objects.filter(to_user=current_uduser, is_new = True)
                rl = len(requests)
                request_list = []
                

                for i in xrange(0,rl):
                    request_list.append(requests[i].from_user.user)
                    requests[i].is_new = False
                    requests[i].save()
                requests_out = serializers.serialize('json', request_list)

                return HttpResponse(requests_out)

    return HttpResponse("Failure")

@login_required
def get_num_new_friend_requests(request):
    if request.is_ajax():
        if request.method == 'GET':

            current_uduser = request.user.updoguser
            
            if not current_uduser.new_friend_requests:
                return HttpResponse("No new notifications")

            else:
                requests = Friendship.objects.filter(to_user=current_uduser, is_new = True)
                rl = len(requests)

            return HttpResponse(rl)     

    return HttpResponse("Failure")

@login_required
def get_notifications(request):
    try:
        if request.is_ajax():
            if request.method == 'GET':

                current_uduser = request.user.updoguser
                event_notifications = EventNotification.objects.filter(to_user=current_uduser)
                from_users = []
                events = []

                if event_notifications:
                    el = len(event_notifications)

                    if el > 0:
                      for i in xrange(0,el):
                        if event_notifications[i].is_seen == False:
                            event_notifications[i].is_seen = True
                            event_notifications[i].save()
                        from_users.append(event_notifications[i].from_user.user)
                        events.append(event_notifications[i].event)

                    event_notifications = serializers.serialize('json', event_notifications)
                    from_users = serializers.serialize('json', from_users)
                    events = serializers.serialize('json', events)
                    json_stuff = simplejson.dumps([event_notifications, from_users, events])

                    return HttpResponse(json_stuff, content_type="application/json")
                else:
                    return HttpResponse("No Notifications")

    except Exception as e:
        print e
                    
    return HttpResponse("Failure")

@login_required
def get_num_new_notifications(request):
    if request.is_ajax():
        if request.method == 'GET':

            current_uduser = request.user.updoguser
            event_notifications = EventNotification.objects.filter(to_user=current_uduser, is_seen=False) 
            if event_notifications:
                el = len(event_notifications)


            else: 
                el = 0

            return HttpResponse(el)               

    return HttpResponse("Failure")

@login_required
@csrf_exempt
def send_event_notifications(request):
    if request.is_ajax():
        if request.method == 'POST':
            try:
                current_uduser = request.user.updoguser

                if 'event' in request.POST:
                    event = Event.objects.filter(pk=request.POST['event'])[0]
                    if 'to_users' in request.POST:
                        to_users = json.loads(request.POST['to_users'])

                        if 'data_type' in request.POST:
                            invite_list_pks = []
                            if request.POST['data_type'] == 'pk':
                                for key in to_users:
                                    recipient = UpDogUser.objects.filter(pk=key)[0]
                                    event_notification = EventNotification.objects.get_or_create(to_user=recipient, from_user=current_uduser, event=event)[0]
                                    event_notification.save()
                                    invite_list_pks.append(key) ### FRANKLYN

                            elif request.POST['data_type'] == 'username':

                                for username in to_users:

                                    recipient = UpDogUser.objects.filter(user__username=username)[0]
                                    event_notification = EventNotification.objects.get_or_create(to_user=recipient, from_user=current_uduser, event=event)[0]
                                    event_notification.save()
                                    invite_list_pks.append(recipient.pk) ###FRANKLYN
                    return HttpResponse(json.dumps(invite_list_pks))
            except Exception as e:
                print e


    return HttpResponse("Failure")

@login_required
@csrf_exempt
def respond_to_event_notification(request):
    if request.is_ajax():
        if request.method == 'POST':

            current_uduser = request.user.updoguser

            if 'notification' in request.POST:
                notification = EventNotification.objects.filter(pk=request.POST['notification'])[0]

                if 'response' in request.POST:
                    response = request.POST['response']

                    if response == 'accept':

                        try:
                        
                            current_uduser.update_last_seen(notification.from_user, datetime.datetime.utcnow().replace(tzinfo=utc))

                        except Exception as e:

                            print e
                        ## adds the to user as an owner of the event
                        if current_uduser not in notification.event.owners.all():
                            notification.event.add_user(current_uduser)
                            notification.event.save()

                        ## creates a reply notification for the from user
                        reply_notification = EventNotification(to_user=notification.from_user, from_user=current_uduser, event=notification.event, is_reply=True)
                        reply_notification.save()
                        ## delete the event notification
                        notification.delete()
                        return HttpResponse(serializers.serialize('json', [notification.event]))

                    notification.delete()
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
            json_events = gimme_events(current_user, display) + gimme_downtimes(current_user, display)
            return HttpResponse(serializers.serialize('json', json_events))
    else:
        return HttpResponse("failure")

@login_required
@csrf_exempt
def get_event_owners(request):
    if request.is_ajax():
        if request.method == 'GET':
            if 'pks' in request.GET:
                if 'types' in request.GET:
                    try:
                        list_of_owners = []
                        pks = json.loads(request.GET['pks'])
                        types = json.loads(request.GET['types'])

                        unused_ints = []
                        i = 0
                        for pk in pks:
                            unused_ints.append(i)
                            is_event = types[i]
                            # if this is an event
                            if is_event == True:
                                event = Event.objects.filter(pk=pk)[0]

                                event_owners = []
                                owners =  event.owners.all()
                                owners = owners.exclude(pk=request.user.updoguser.pk)
                                list_of_owners.append(request.user)
                                for owner in owners:
                                    list_of_owners.append(owner.user)

                            # else this is a downtime
                            else:

                                downtime = Downtime.objects.filter(pk=pk)
                                list_of_owners.append(downtime[0].owner.user)


                            i = i + 1
                        json_stuff = serializers.serialize('json', list_of_owners)


                        #return HttpResponse(json_stuff, content_type ="application/json")
                        return HttpResponse(json_stuff)
                    except Exception as e:
                        print e
    else:
        return HttpResponse("Failure.")

@login_required
@csrf_exempt
def is_invited(request):
    if request.is_ajax():
        if request.method == 'GET':
            if 'event' in request.GET:
                if 'users' in request.GET:
                    # do stuff
                    users = json.loads(request.GET['users'])
                    event = Event.objects.filter(pk=request.GET['event'])
                    is_invited = []
                    for user in users:
                        ud_user = UpDogUser.objects.filter(user__username=user)
                        if EventNotification.objects.filter(event=event,to_user=ud_user,is_reply=False):
                            is_invited.append(True)
                        else:
                            is_invited.append(False)

                    return HttpResponse(json.dumps(is_invited))
    else:
        return HttpResponse("Fail!")

@login_required
@csrf_exempt
def who_is_invited(request):
    if request.is_ajax():
        if 'event' in request.GET:

            event = Event.objects.filter(pk=request.GET['event'])
            is_invited = []
            users = UpDogUser.objects.filter()
            for user in users:
                ud_user = UpDogUser.objects.filter(user__username=user)
                if EventNotification.objects.filter(event=event,to_user=ud_user,is_reply=False):
                    is_invited.append(user.user)
            return HttpResponse(serializers.serialize('json', is_invited))

    else:
        return HttpResponse("Fail!")

@login_required
@csrf_exempt
def get_from_user(request):
    if request.is_ajax():
        if 'pk' in request.GET:
            try:
                eventNotey = EventNotification.objects.filter(pk=request.GET['pk'])[0]
                return HttpResponse(serializers.serialize('json', [eventNotey.from_user.user, eventNotey.event]))
            except Exception as e:
                print e
    else:
        return HttpResponse("Fail!")


