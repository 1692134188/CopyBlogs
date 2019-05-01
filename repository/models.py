from django.db import models


# Create your models here.
class UserInfo(models.Model):
    '''用户表'''
    uid = models.BigAutoField(primary_key=True)
    username = models.CharField(verbose_name="用户名", max_length=64, unique=True)
    pwd = models.CharField(verbose_name='密码', max_length=64)
    email = models.EmailField(verbose_name='邮箱', unique=True)
    img = models.ImageField(verbose_name='头像', null=True)


class BlogInfo(models.Model):
    '''博客信息'''
    bid = models.BigAutoField(primary_key=True)
    surfix = models.CharField(verbose_name='博客后缀名', max_length=64)
    theme = models.CharField(verbose_name='博客主题', max_length=64)
    title = models.CharField(verbose_name='博客标题', max_length=1000)
    summary = models.CharField(verbose_name='博客简介', max_length=1000)
    user = models.OneToOneField(to="UserInfo", to_field="uid", on_delete=models.CASCADE, null=True)


class UserFans(models.Model):
    '''互粉表'''
    starUser = models.ForeignKey(verbose_name='博主', to="UserInfo", to_field="uid", related_name="starUsers",
                                 on_delete=models.CASCADE, null=True)
    fansUser = models.ForeignKey(verbose_name='粉丝', to="UserInfo", to_field="uid", related_name='fansUsers',
                                 on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = [
            ('starUser', 'fansUser'),
        ]


class ReportObstacles(models.Model):
    '''报障单'''
    uuid = models.UUIDField(primary_key=True)
    title = models.CharField(verbose_name="报障标题", max_length=1000)
    detail = models.TextField(verbose_name='报障详情')
    reportUser = models.ForeignKey(verbose_name='报修人', to="UserInfo", to_field="uid", related_name="reportUsers",
                                   on_delete=models.CASCADE, null=True)
    processUser = models.ForeignKey(verbose_name='处理人', to="UserInfo", to_field="uid", related_name="processUsers",
                                    on_delete=models.CASCADE, null=True)
    createTime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    processTime = models.DateTimeField(verbose_name='处理时间', auto_now_add=True)
    type_status = [
        (1, '待处理'),
        (2, '处理中'),
        (3, '已处理'),
    ]
    status = models.IntegerField(choices=type_status, default=None)


class Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='BlogInfo', to_field='bid', on_delete=models.CASCADE, null=True)


class Classification(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类名称', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='BlogInfo', to_field='bid', on_delete=models.CASCADE, null=True)


class Article(models.Model):
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name='文章标题', max_length=128)
    summary = models.CharField(verbose_name='简介', max_length=256)
    blog = models.ForeignKey(verbose_name='所属博客', to='BlogInfo', to_field='bid', on_delete=models.CASCADE, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', null=False)
    read_count = models.IntegerField(verbose_name='阅读数量',default=0)
    comment_count = models.IntegerField(verbose_name='评论数量',default=0)
    up_count = models.IntegerField(verbose_name='点赞数量',default=0)
    down_count = models.IntegerField(verbose_name='踩数量',default=0)
    classification_id = models.ForeignKey(verbose_name='文章分类', to='Classification', to_field="nid",
                                          on_delete=models.CASCADE, null=True)
    masterStation_type = [
        (1, "Python"),
        (2, "Linux"),
        (3, "OpenStack"),
        (4, "GoLang"),
    ]
    ms_Type = models.IntegerField(verbose_name='主站分类', choices=masterStation_type, default=None)
    tags=models.ManyToManyField(
        to='Tag',
        through='Article_Tag',
        through_fields=('article_id','tag_id')
    )

class Article_Detail(models.Model):
    detail = models.TextField(verbose_name='文章详细', max_length=models.Max)
    article_id = models.OneToOneField(verbose_name='文章id', to='Article', to_field='nid', on_delete=models.CASCADE,
                                      null=True)


class Article_Tag(models.Model):
    # 文章标签分类
    article_id = models.ForeignKey(verbose_name='文章ID', to='Article', to_field='nid', on_delete=models.CASCADE,
                                   null=True)
    tag_id = models.ForeignKey(verbose_name='标签ID', to='Tag', to_field='nid', on_delete=models.CASCADE, null=True)
    class Meta:
        unique_together=[("article_id","tag_id")]


class Article_upDown(models.Model):
    # 文章标签分类
    article_id = models.ForeignKey(verbose_name='文章ID', to='Article', to_field='nid', on_delete=models.CASCADE,
                                   null=True)
    user = models.ForeignKey(verbose_name='赞或踩用户', to='UserInfo', to_field='uid',on_delete=models.CASCADE, null=True)
    up = models.BooleanField(verbose_name='是否赞', default=True)

    class Meta:
        unique_together = [
            ('article_id', 'user')
        ]


class Article_Comment(models.Model):
    '''评论表'''
    id = models.BigAutoField(verbose_name='评论ID', primary_key=True)
    user = models.ForeignKey(verbose_name='评论人', to='UserInfo', to_field='uid', on_delete=models.CASCADE, null=True)
    comment = models.CharField(verbose_name='评论内容', max_length=1000)
    createTime = models.DateTimeField(verbose_name='评论时间', auto_now_add=True)
    reply = models.ForeignKey(verbose_name='回复评论', to='self', related_name='back', on_delete=models.CASCADE, null=True)
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid',on_delete=models.CASCADE, null=True)
