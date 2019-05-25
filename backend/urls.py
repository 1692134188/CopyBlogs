from django.conf.urls import url
from django.conf.urls import include
from .views import user

urlpatterns = [
    url(r'^index.html$', user.index),
    url(r'article-(?P<ms_Type>\d+)-(?P<classification_id>\d+).html$', user.article, name='article'),

]
