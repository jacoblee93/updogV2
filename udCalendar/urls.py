from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from udCalendar import views

urlpatterns = patterns('',
        url(r'^$', views.calendar, name='calendar'),
        url(r'^test/$', views.test, name='test'),




        # TESTING AJAX
        (r'^test_ajax/$', views.test_ajax),
)
