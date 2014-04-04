from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

# A view in which to test graphics
def test(request):
    context = RequestContext(request)
    return render_to_response('updog/base.html', {}, context)

# The calendar view  
def calendar(request):
    context = RequestContext(request)
    return render_to_response('updog/calendar.html', {}, context)
