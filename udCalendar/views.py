from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from udCalendar.models import UpDogUser, Friendship, Event, Downtime
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from datetime import timedelta
from django.utils.timezone import utc
from django.db.models import Q
from dateutil import parser

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


    #current_user.add_friend(UpDogUser.objects.order_by('-user')[2])
    #current_user.add_friend(UpDogUser.objects.order_by('-user')[3])
    #current_user.add_friend(UpDogUser.objects.order_by('-user')[4])

    #test_to_friendship = Friendship.objects.filter(to_user=UpDogUser.objects.order_by('-user')[4], from_user=current_user)[0]
    #test_from_friendship = Friendship.objects.filter(from_user=UpDogUser.objects.order_by('-user')[4], to_user=current_user)[0]
    #test_to_friendship.is_mutual= True
    #test_from_friendship.is_mutual = True
    #test_to_friendship.is_new = False
    #test_from_friendship.is_new = False
    #test_to_friendship.save()
    #test_from_friendship.save()

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

    ships_list = current_user.get_friends()

    ordered_ships_list = ships_list.order_by('-meeting_count')
    friends_list = []
    for ship in ordered_ships_list:
        friends_list.append(ship.to_user.user)

    # Alex - for local use when rediesigning friends tab 
    #json_friends = serializers.serialize("json", friends_list)

    context_dict = {'friends_list': friends_list}#json_friends}

    json_events = serializers.serialize("json", gimme_events(current_user))
    json_downtimes = serializers.serialize("json", gimme_downtimes(current_user))
    context_dict['events_list'] = json_events
    context_dict['downtimes'] = json_downtimes
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

            new_downtime = Downtime.objects.get_or_create(owner=request.user.updoguser, start_time=startDate, end_time=endDate)[0]
            return HttpResponse(serializers.serialize('json',[new_downtime, ]))

    return HttpResponse("Error!")




@login_required
def add_event(request):
    if request.is_ajax():
        if request.method == 'POST':
            context = RequestContext(request)

            if 'activity' in request.POST:
                activity = request.POST['activity']
            if 'location' in request.POST:
                location = request.POST['location']

            event = Event(activity=activity, location=location, start_time=timezone.now() + timedelta(hours=23), end_time=(timezone.now() + timedelta(hours=24)))
            event.save()
            event.owners.add(request.user.updoguser)

            json_event = serializers.serialize("json", [event, ])

            return HttpResponse(json_event)
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

            json_event = serializers.serialize("json", [event, ])

            print event.pk

            return HttpResponse(json_event)
    else: return HttpResponse("Failure here!!!!")

@login_required
def edit_downtime(request):
    if request.is_ajax():
        if request.method == 'POST':
            downtime = Downtime.objects.filter(pk=request.POST['pk'])[0]
            if 'activity' in request.POST:
                downtime.preferred_activity = request.POST['activity']
            downtime.save()

            json_downtime = serializers.serialize("json", [downtime, ])

            print json_downtime

            return HttpResponse(json_downtime)

    return HttpResponse("Invalid request")

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

@login_required
def change_downtime(request):
    if request.is_ajax():
        if request.method == 'POST':
            downtime = Downtime.objects.filter(pk=request.POST['pk'])[0]
            time_changes = timedelta(days = int(request.POST['day_delta']), 
                minutes = int(request.POST['minute_delta']))

            downtime.end_time = downtime.end_time + time_changes

            if request.POST['resize'] == "false":
                downtime.start_time = downtime.start_time + time_changes

            downtime.save()

        return HttpResponse("Success123")

    else: return HttpResponse("Failure123")

@login_required
def remove_event(request):
    if request.is_ajax():
        if request.method == 'POST':
            event = Event.objects.filter(pk=request.POST['pk'])[0]
            event.delete()

            return HttpResponse("Success here!!!!!")
    else: return HttpResponse("Failure here!!!!")

@login_required
def remove_downtime(request):
    if request.is_ajax():
        if request.method == 'POST':
            downtime = Downtime.objects.filter(pk=request.POST['pk'])[0]
            downtime.delete()

            return HttpResponse("Successfully deleted downtime")

    return HttpResponse("Invalid request")
            
@login_required
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

@login_required
def send_friend_request(request):
    if request.is_ajax():
        if request.method == 'POST':
            if 'new_friend' in request.POST:
                new_friend = UpDogUser.objects.filter(user__username=request.POST['new_friend'])[0]
                current_user = request.user.updoguser

                to_friendship = Friendship.objects.filter(to_user=new_friend, from_user=current_user)

                #if to_friendship:
                 #   return HttpResponse("Request Pending")

                current_user.add_friend(new_friend)

                to_friendship = Friendship.objects.filter(to_user=new_friend, from_user=current_user)[0]
                from_friendship = Friendship.objects.filter(to_user=current_user, from_user=new_friend)[0]

                to_friendship.is_new = True
                new_friend.new_notifications = True

                to_friendship.save()
                new_friend.save()

                return HttpResponse("Success")

    return HttpResponse("Failure!")

@login_required
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
def display_friend_requests(request):
    if request.is_ajax():
        if request.method == 'GET':

            current_uduser = request.user.updoguser
            
            if not current_uduser.new_notifications:
                return HttpResponse("No new notifications")

            else:
                requests = Friendship.objects.filter(to_user=current_uduser)
                print requests
                rl = len(requests)
                request_list = []

                for i in xrange(0,rl):
                    request_list.append(requests[i].from_user.user)
                requests_out = serializers.serialize('json', request_list)

                return HttpResponse(requests_out)

    return HttpResponse("Failure")




