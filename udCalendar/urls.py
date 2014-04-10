from django.conf.urls import patterns, url, include
from udCalendar import views

urlpatterns = patterns('',
        url(r'^$', views.calendar, name='calendar'),
        url(r'^test/$', views.test, name='test'),
        url(r'', include('social_auth.urls')),
        url(r'^login/$', views.login, name='login'),
        url(r'^logout_user/$', views.logout_user, name='logout'),
)
