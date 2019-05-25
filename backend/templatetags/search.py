#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def category_all(arg_dict):
    ms_Type = arg_dict['ms_Type']
    category_nid = arg_dict['classification_id']
    p = arg_dict['p']
    url = reverse('article', kwargs={'ms_Type': ms_Type, 'classification_id':0 })
    if category_nid == '0':
        temp = '<a class="active" href="%s?p=%s">全部</a>' % (url,p,)
    else:
        temp = '<a href="%s?p=%s">全部</a>' % (url,p,)
    return mark_safe(temp)


@register.simple_tag
def category_combine(obj_list, arg_dict):
    li = []
    ms_Type = arg_dict['ms_Type']
    category_nid = arg_dict['classification_id']
    p = arg_dict['p']
    for obj in obj_list:
        url = reverse('article', kwargs={'ms_Type': ms_Type, 'classification_id': obj['nid']})
        if obj['nid'] == int(category_nid):
            temp = '<a class="active" href="%s?p=%s">%s</a>' % (url,p, obj['title'])
        else:
            temp = '<a href="%s?p=%s">%s</a>' % (url,p, obj['title'])
        li.append(temp)
    return mark_safe(''.join(li))


@register.simple_tag
def article_type_all(arg_dict):
    ms_Type = arg_dict['ms_Type']
    category_nid = arg_dict['classification_id']
    p = arg_dict['p']
    url = reverse('article', kwargs={'ms_Type': 0, 'classification_id': category_nid})
    if ms_Type == '0':
        temp = '<a class="active" href="%s?p=%s">全部</a>' % (url,p,)
    else:
        temp = '<a href="%s?p=%s">全部</a>' % (url,p,)
    return mark_safe(temp)

@register.simple_tag
def article_type_combine(obj_list, arg_dict):
    li = []
    ms_Type = arg_dict['ms_Type']
    category_nid = arg_dict['classification_id']
    p = arg_dict['p']
    for obj in obj_list:
        url = reverse('article', kwargs={'ms_Type': obj['nid'], 'classification_id': category_nid})
        if obj['nid'] == int(ms_Type):
            temp = '<a class="active" href="%s?p=%s">%s</a>' % (url,p, obj['title'])
        else:
            temp = '<a href="%s?p=%s">%s</a>' % (url,p, obj['title'])
        li.append(temp)
    return mark_safe(''.join(li))