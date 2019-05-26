from django.conf.urls import url
from django.conf.urls import include
from .views import user

urlpatterns = [
    url(r'^index.html$', user.index),
    url(r'article-(?P<ms_Type>\d+)-(?P<classification_id>\d+).html$', user.article, name='article'),
    url(r'^add-article.html$',user.add_article),  #创建文章路由
    url(r'^del-article-(?P<nid>\d+).html$', user.del_article),#删除文章路由
    url(r'^edit-article-(?P<nid>\d+).html$', user.edit_article),#修改文章路由
]
