from django.conf.urls import url
from web.Views import home,account
from web.Views.Tools import  check_code
from django.urls import path

urlpatterns=[
    url(r'^PublishComment.html', home.PublishComment),  # 发表评论
    url(r'^check_code.html$',check_code.make_code),     # 验证码校验
    url(r'^register.html$', account.register),          # 注册
    url(r'^login.html$', account.login),                # 登录
    url(r'^logout.html$', account.logout),              # 退出
    url(r'^all/(?P<ms_Type>\d+).html$',home.index,name='index'),
    url(r'^(?P<site>\w+).html$', home.home,name='home'),
    url(r'^(?P<site>\w+)/(?P<condition>((tag)|(date)|(category)))/(?P<val>\w+-*\w*).html$', home.filter),# 根据条件过滤
    url(r'^(?P<site>\w+)/(?P<nid>\d+).html$', home.detail), # 文章详情页
    url(r'^', home.index),                              # 默认前台首页
]