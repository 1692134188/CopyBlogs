from django.shortcuts import HttpResponse,redirect, render
from repository import models
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from web.Views.Tools import AaronPager
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt,csrf_protect
import time
import json
def index(request, *args, **kwargs):
    """
    博客首页，展示全部博文
    """
    # 设置标签列表（注意，该标签直接从model中获取）
    ms_Type = models.Article.masterStation_type
    # 判断是否有条件（主站分类：ms_Type）传递过来，
    article_list = models.Article.objects.filter(**kwargs).annotate(authorsNum=Count('article_updown'))
    current_ms_Type = 0
    data_count = article_list.count()
    cur_page = request.GET.get('p')
    # reverse方法可以通过别名反向生成url
    base_url = '/'
    if kwargs:
        current_ms_Type = int(kwargs['ms_Type'])
        base_url = reverse('index', kwargs=kwargs)
        # 统计每一篇文章的赞、踩个数
        # bookList =models.Article.objects.annotate(authorsNum=Count('article_updown'))
    aaron_page = AaronPager.AaronPager(data_count, cur_page, 10, 7,base_url )
    article_list = article_list[aaron_page.start():aaron_page.end()]
    return render(request, "Home/index.html",
                  {'masterStation_type': ms_Type, 'article_list': article_list, 'current_ms_Type': current_ms_Type,'aaron_page':aaron_page,})

def home(request, site):
    """
    博主个人首页
    :param request:
    :param site: 博主的网站后缀如：http://xxx.com/Aaron.html
    :return:
    """
    # 根据后缀名获取博客信息
    blogInfo=models.BlogInfo.objects.filter(surfix=site).select_related("user").first()
    if not blogInfo:
        return redirect('/')
    else:
        # 获取分类信息                            这种写法想当于 blog = blogInfo.id
        #category_list = models.Article.objects.filter(blog=blogInfo).select_related("classification_id").values("classification_id","title").annotate(num=Count('classification_id'))
        str = 'select a.nid as nid,a.title as title,count(b.nid) as num  from repository_classification a LEFT JOIN  repository_article b on b.blog_id = a.blog_id and a.nid=b.classification_id_id where a.blog_id =%(n1)d GROUP BY (a.nid)' %{"n1":blogInfo.bid}
        category_list = models.Classification.objects.raw(str)
        # 获取标签信息
        #tag_list=models.Tag.objects.filter(blog=blogInfo).annotate(Num=Count('article.article_set'))
        str = ' select a.nid as nid,a.title as title ,count(c.nid) as num  from repository_Tag a INNER JOIN repository_article_tag b on a.nid=b.tag_id_id LEFT JOIN  repository_article c on c.blog_id = a.blog_id and c.nid=b.article_id_id where a.blog_id =%(n1)d  GROUP BY (a.nid)' %{"n1":blogInfo.bid}
        tag_list = models.Tag.objects.raw(str)
        #获取日期，这种系原生的sql
        str='select nid, count(nid) as num,strftime("%%Y-%%m",create_time) as ctime from repository_article where blog_id =%(n1)d group by strftime("%%Y-%%m",create_time)' %{"n1":blogInfo.bid}
        date_list = models.Article.objects.raw(str)
        # 获取文章信息
        article_list=models.Article.objects.filter(blog=blogInfo).order_by('-nid').all()
        #
        return render(request, "Home/home.html", { 'blog': blogInfo,
            'tag_list': tag_list,
            'category_list': category_list,
            'date_list': date_list,
            'article_list': article_list})

def filter(request,site,condition,val):
    blog = models.BlogInfo.objects.filter(surfix=site).select_related('user').first()

    if not blog:
        return redirect('/')
    # tag_list=models.Tag.objects.filter(blog=blog) #标签
    str = ' select a.nid as nid,a.title as title ,count(c.nid) as num  from repository_Tag a INNER JOIN repository_article_tag b on a.nid=b.tag_id_id LEFT JOIN  repository_article c on c.blog_id = a.blog_id and c.nid=b.article_id_id where a.blog_id =%(n1)d  GROUP BY (a.nid)' % {
        "n1": blog.bid}
    tag_list = models.Tag.objects.raw(str)

    str = 'select a.nid as nid,a.title as title,count(b.nid) as num  from repository_classification a LEFT JOIN  repository_article b on b.blog_id = a.blog_id and a.nid=b.classification_id_id where a.blog_id =%(n1)d GROUP BY (a.nid)' % {
        "n1": blog.bid}
    category_list = models.Classification.objects.raw(str)
    str = 'select nid, count(nid) as num,strftime("%%Y-%%m",create_time) as ctime from repository_article where blog_id =%(n1)d group by strftime("%%Y-%%m",create_time)' % {
        "n1": blog.bid}
    date_list = models.Article.objects.raw(str)
    template_name="Home/home_summary_list.html"
    if condition=="tag":
        template_name="Home/home_title_list.html"
        article_list=models.Article.objects.filter(tags=val,blog=blog).all()
    elif condition=="category":
        article_list=models.Article.objects.filter(classification_id=val,blog=blog).all()
        print(article_list)
    elif condition == 'date':
        article_list = models.Article.objects.filter(blog=blog).extra(
            where=['strftime("%%Y-%%m",create_time)=%s'], params=[val, ]).all()
    else:
        article_list = []

    return render(
        request,
        template_name,
        {
            'blog': blog,
            'tag_list': tag_list,
            'category_list': category_list,
            'date_list': date_list,
            'article_list': article_list
        }
    )

def detail(request, site, nid):
    cur_page = request.GET.get('p')
    blogInfo=models.BlogInfo.objects.filter(surfix=site).select_related("user").first()
    # 这样关联如果可以的话，那实在是太厉害了
    article=models.Article.objects.filter(blog=blogInfo,nid=nid).select_related("article_detail","classification_id").first();
    comment_list = models.Article_Comment.objects.filter(article=article).select_related("reply")
    aaron_page = AaronPager.AaronPager(comment_list.count(), cur_page, 5, 7,nid + '.html')
    comment_list = comment_list[aaron_page.start():aaron_page.end()]
    # tag_list=models.Tag.objects.filter(blog=blog) #标签
    str = ' select a.nid as nid,a.title as title ,count(c.nid) as num  from repository_Tag a INNER JOIN repository_article_tag b on a.nid=b.tag_id_id LEFT JOIN  repository_article c on c.blog_id = a.blog_id and c.nid=b.article_id_id where a.blog_id =%(n1)d  GROUP BY (a.nid)' % {
        "n1": blogInfo.bid}
    tag_list = models.Tag.objects.raw(str)
    # category_list=models.Classification.objects.filter(blog=blog).select_related("article").annotate(Num=Count('article')) #分类
    str = 'select a.nid as nid,a.title as title,count(b.nid) as num  from repository_classification a LEFT JOIN  repository_article b on b.blog_id = a.blog_id and a.nid=b.classification_id_id where a.blog_id =%(n1)d GROUP BY (a.nid)' % {
        "n1": blogInfo.bid}
    category_list = models.Classification.objects.raw(str)
    str = 'select nid, count(nid) as num,strftime("%%Y-%%m",create_time) as ctime from repository_article where blog_id =%(n1)d group by strftime("%%Y-%%m",create_time)' % {
        "n1": blogInfo.bid}
    date_list = models.Article.objects.raw(str)
    return render(request, 'Home/home_detail.html',
                  {
                      'blog': blogInfo,
                      'article': article,
                      'comment_list': comment_list,
                      'tag_list': tag_list,
                      'category_list': category_list,
                      'date_list': date_list,
                      'aaron_page': aaron_page,
                  })
@csrf_exempt
def PublishComment(request):
    return render(request, "Aaron/1.html", {"res": "评论成功"})

