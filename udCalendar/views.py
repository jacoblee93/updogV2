from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from udCalendar.models import UpDogUser, Friendship
from django.contrib.auth.models import User

# A view in which to test graphics
def test(request):
    context = RequestContext(request)
    return render_to_response('updog/base.html', {}, context)

# The calendar view  
def calendar(request):
    context = RequestContext(request)
    user = UpDogUser.objects.order_by('-user')[2]
    ###JUST TO TEST
    
    ships_list = user.get_friends()
    ordered_ships_list = ships_list.order_by('-meeting_count')
    friends_list = []
    for ship in ordered_ships_list:
        friends_list.append(ship.to_user.user)
    context_dict = {'friends_list': friends_list}
    
    return render_to_response('updog/calendar.html', context_dict, context)
