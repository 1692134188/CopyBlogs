from django.shortcuts import render,redirect,HttpResponse
from repository import models
from web.Views.Tools import AaronPager
from web.Views.Tools.pagination import Pagination
from django.urls import reverse
from forms.article import ArticleForm  #引用form中的文章表单，用于添加、修改文章

from django.db import transaction  #引用事务
from utils.xss import  XSSFilter  #引用Xss安全机制，存储富文本编辑器中内容
from utils.pagination import Pagination
import datetime #引入时间模块

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
    condition['status'] =1
    # 筛选出文章总数
    data_count = models.Article.objects.filter(**condition).count()
    if  request.GET.get("keyWord"):
        data_count = models.Article.objects.filter(**condition,title__contains=request.GET.get("keyWord")).count()
    # 获取页数
    page =  Pagination(request.GET.get('p', 1), data_count)
    # 筛选出文章列表
    result = models.Article.objects.filter(**condition).order_by('-nid').only('nid', 'title','blog').select_related('blog')[page.start:page.end]
    if request.GET.get("keyWord"):
        result = models.Article.objects.filter(**condition, title__contains=request.GET.get("keyWord")).order_by('-nid').only('nid', 'title',
                                                                                  'blog').select_related('blog')[
                 page.start:page.end]
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
                   'data_count': data_count,
                   'keyWord':request.GET.get("keyWord") if request.GET.get("keyWord") else ''
                   }
                  )

def add_article(request):
    # 添加文章
    if request.method == "GET":
        form = ArticleForm(request=request)
        return render(request,"Backend/add_article.html",{'form':form ,'oper':'add','nid':-1})
    elif request.method=='POST':
        oper=request.GET.get('oper', 'add')
        nid =int(request.GET.get('nid', -1))
        if  oper =='add':
            form = ArticleForm(request=request,data=request.POST)
            if form.is_valid():
                with transaction.atomic():
                    tags=form.cleaned_data.pop('tags')
                    content = form.cleaned_data.pop('content')
                    content=XSSFilter().process(content)
                    form.cleaned_data['blog_id']=request.session['user_info']["bloginfo__bid"]
                    # 需要将该值转化一下
                    form.cleaned_data['classification_id']=models.Classification.objects.filter(nid=form.cleaned_data['classification_id']).first()
                    form.cleaned_data['create_time'] = datetime.datetime.now()
                    obj = models.Article.objects.create(**form.cleaned_data)   #添加文章
                    models.Article_Detail.objects.create(detail=content,article_id=obj) #添加文章详细
                    tag_list=[]
                    for tag_id in tags:
                        tag_id=int(tag_id)
                        tag_list.append(models.Article_Tag(article_id_id=obj.nid,tag_id_id=tag_id))
                    models.Article_Tag.objects.bulk_create(tag_list) #批量创建，厉害
                return redirect("backend/article-0-0.html")
            else:
                return render(request, "backend/add_article.html",{'form':form,'oper':'add','nid':-1})
        elif oper=="edit" and nid>0:
            blog_id = request.session['user_info']['bloginfo__bid']
            form = ArticleForm(request=request, data=request.POST)
            if form.is_valid():
                obj = models.Article.objects.filter(nid=nid, blog_id=blog_id, status=1).first()
                if not obj:
                    return HttpResponse('该文章不存在或已删除')
                with transaction.atomic():
                    tags = form.cleaned_data.pop('tags')
                    content = form.cleaned_data.pop('content')
                    content = XSSFilter().process(content)
                    form.cleaned_data['blog_id'] = request.session['user_info']["bloginfo__bid"]
                    # 需要将该值转化一下
                    form.cleaned_data['classification_id'] = models.Classification.objects.filter(
                        nid=form.cleaned_data['classification_id']).first()
                    form.cleaned_data['create_time'] = datetime.datetime.now()
                    obj = models.Article.objects.filter(nid=obj.nid, status=1).update(**form.cleaned_data)  # 修改文章
                    models.Article_Detail.objects.filter(article_id_id=nid, status=1).update(detail=content )  # 修改文章详细
                    models.Article_Tag.objects.filter(article_id_id=nid).delete() #使用之前，先把该文章下面的所有标签删除
                    tag_list = []
                    for tag_id in tags:
                        tag_id = int(tag_id)
                        tag_list.append(models.Article_Tag(article_id_id=nid, tag_id_id=tag_id))
                    models.Article_Tag.objects.bulk_create(tag_list)  # 批量创建，不知道更新的时候是否有问题
                return redirect("backend/article-0-0.html")
            else:
                return render(request, "backend/add_article.html", {'form': form,'oper':'edit','nid':nid})
        else:
            return redirect('/')
    else:
        return redirect('/')

def del_article(request, nid):
    # 删除文章
    blog_id = request.session['user_info']['bloginfo__bid']
    nid=int(nid)
    v=models.Article.objects.filter(blog_id=blog_id,nid=nid).update(status=0)
    if not v:
        return HttpResponse('删除失败')
    return redirect("backend/article-0-0.html")

def edit_article(request, nid):
    # 编辑文章
    blog_id = request.session['user_info']['bloginfo__bid']
    if request.method == "GET":
        # 查找数据库中该条数据
        obj=models.Article.objects.filter(nid=nid,blog_id=blog_id,status=1).first()
        if not obj:
            return HttpResponse('该文章不存在或已删除')
        # 获取该文章的标签
        tags=obj.tags.values_list('nid')
        if tags:
            tags = list(zip(*tags))[0]
        init_dict={
            'nid':obj.nid,
            'title':obj.title,
            'summary':obj.summary,
            'content':obj.article_detail.detail if hasattr(obj, 'article_detail') else '',
            'ms_Type':obj.ms_Type,
            'classification_id':obj.classification_id_id,
            'tags': tags
        }
        form = ArticleForm(request=request, data=init_dict)
        # 页面内容一致，可以简化使用新增的页面
        return render(request, 'Backend/add_article.html', {'form': form,'oper':'edit','nid':nid})
    else:
        return redirect('/')












