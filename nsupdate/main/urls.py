from django.conf.urls import patterns, include, url
from main.views import HomeView, MyIpView

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^myip/', MyIpView)
)
