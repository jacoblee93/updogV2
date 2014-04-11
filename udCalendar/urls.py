<<<<<<< HEAD
from django.conf.urls import patterns, url
from django.views.generic import TemplateView
=======
from django.conf.urls import patterns, url, include
>>>>>>> 0925e4d09a8e15ac0eedb13d83e849240bcfe02f
from udCalendar import views

urlpatterns = patterns('',
        url(r'^$', views.calendar, name='calendar'),
        url(r'^test/$', views.test, name='test'),
<<<<<<< HEAD




        # TESTING AJAX
        (r'^test_ajax/$', views.test_ajax),
=======
        url(r'', include('social_auth.urls')),
        url(r'^login/$', views.login, name='login'),
        url(r'^logout_user/$', views.logout_user, name='logout'),
>>>>>>> 0925e4d09a8e15ac0eedb13d83e849240bcfe02f
)
