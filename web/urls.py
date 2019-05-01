from django.conf.urls import url
from web.Views import home,account
from web.Views.Tools import  check_code
from django.urls import path

urlpatterns=[
    url(r'^check_code.html$',check_code.make_code),
    url(r'^register.html$', account.register),
    url(r'^login.html$', account.login),
    url(r'^logout.html$', account.logout),
    url(r'^all/(?P<ms_Type>\d+).html$',home.index,name='index'),
    url(r'^(?P<site>\w+).html$', home.home,name='home'),
    url(r'^(?P<site>\w+)/(?P<condition>((tag)|(date)|(category)))/(?P<val>\w+-*\w*).html$', home.filter),
    url(r'^(?P<site>\w+)/(?P<nid>\d+).html$', home.detail),
    url(r'^', home.index),
]