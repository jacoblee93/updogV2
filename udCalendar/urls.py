from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf.urls import patterns, url, include
from udCalendar import views

urlpatterns = patterns('',
        url(r'^$', views.calendar, name='calendar'),
        url(r'^test/$', views.test, name='test'),

        # TESTING AJAX
        (r'^test_ajax/$', views.test_ajax),
        url(r'', include('social_auth.urls')),
        url(r'^login/$', views.login, name='login'),
        url(r'^logout_user/$', views.logout_user, name='logout'),
        url(r'^change_event/$', views.change_event, name='change_event'),
        url(r'^change_downtime/$', views.change_downtime, name='change_downtime'),
        url(r'^add_event/$', views.add_event, name='add_event'),
        url(r'^edit_event/$', views.edit_event, name='edit_event'),
        url(r'^edit_downtime/$', views.edit_downtime, name='edit_downtime'),
        url(r'^remove_event/$', views.remove_event, name='remove_event'),
        url(r'^remove_downtime/$', views.remove_downtime, name='remove_downtime'),
        url(r'^find_friends/$', views.find_friends, name='find_friends'),
        url(r'^get_friends_events/$', views.get_friends_events, name='get_friends_events'),
        url(r'^add_downtime/$', views.add_downtime, name='add_downtime'),
        url(r'^get_friends_downtimes/$', views.get_friends_downtimes, name='get_friends_downtimes'),
        url(r'^send_friend_request/$', views.send_friend_request, name='send_friend_request'),
        url(r'^accept_friend_request/$', views.accept_friend_request, name='accept_friend_request'),
        url(r'^reject_friend_request/$', views.reject_friend_request, name='reject_friend_request'),
        url(r'^suggest/$', views.suggest, name='suggest'),
        url(r'^display_friend_requests/$', views.display_friend_requests, name='display_friend_requests'),
        url(r'^get_notifications/$', views.get_notifications, name='get_notifications'),
        url(r'^send_event_notifications/$', views.send_event_notifications, name='send_event_notifications'),
        url(r'^respond_to_event_notification/$', views.respond_to_event_notification, name='respond_to_event_notification'),
        url(r'^get_friends/$', views.get_friends, name='get_friends'),
        url(r'^display/$', views.display, name='display'),
        url(r'^invite_search/$', views.invite_search, name='invite_search'),
        url(r'^search_friends/$', views.search_friends, name='search_friends'),
)
