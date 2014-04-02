from django.conf.urls import patterns, url
from udCalendar import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
)
