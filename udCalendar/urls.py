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
        url(r'^add_event/$', views.add_event, name='add_event'),
        url(r'^edit_event/$', views.edit_event, name='edit_event'),
        url(r'^remove_event/$', views.remove_event, name='remove_event'),
)
