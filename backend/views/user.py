from django.shortcuts import render
from repository import models
from web.Views.Tools import AaronPager
from web.Views.Tools.pagination import Pagination
from django.urls import reverse
def index(request):
    return render(request, 'Backend/backend_index.html')

def article(request, *args, **kwargs):
    """
    博主个人文章管理
    :param request:
    :return:
    """
    # 通过session拿掉用户的登录信息
    blog_id = request.session['user_info']['bloginfo__bid']
    condition = {}
    # 遍历kwargs条件（ms_Type、classification_id）
    for k, v in kwargs.items():
        if v == '0':
            pass
        else:
            condition[k] = v
    condition['blog_id'] = blog_id
    # 筛选出文章总数
    data_count = models.Article.objects.filter(**condition).count()
    # 获取页数
    page =  Pagination(request.GET.get('p', 1), data_count)
    # 筛选出文章列表
    result = models.Article.objects.filter(**condition).order_by('-nid').only('nid', 'title','blog').select_related('blog')[page.start:page.end]
    #通过通用方法，生成分页
    page_str = page.page_str(reverse('article', kwargs=kwargs))
    #获取分类内容
    category_list = models.Classification.objects.filter(blog_id=blog_id).values('nid', 'title')
    # 获取类型内容
    type_list = map(lambda item: {'nid': item[0], 'title': item[1]}, models.Article.masterStation_type)
    kwargs['p'] = page.current_page
    return render(request,
                  'Backend/backend_article.html',
                  {'result': result,
                   'page_str': page_str,
                   'category_list': category_list,
                   'type_list': type_list,
                   'arg_dict': kwargs,
                   'data_count': data_count
                   }
                  )

