# 引入文件
from django import forms
from django.forms import fields
from django.forms import widgets
from  repository import models

class ArticleForm(forms.Form):
    title = forms.CharField(
       widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '文章标题'})
    )
    summary = forms.CharField(
        widget=widgets.Textarea(attrs={'class':'form-control','placeholder':'文章简介','rows':'3'})
    )
    content = forms.CharField(
        widget=widgets.Textarea(attrs={'class': 'kind-content'})
    )
    # 单选按钮（定义的枚举）
    ms_Type = forms.IntegerField(
        widget=widgets.RadioSelect(choices=models.Article.masterStation_type)
    )
    # 分类
    classification_id=forms.ChoiceField(
        choices=[],
        widget=widgets.RadioSelect
    )
    # 标签
    tags=forms.MultipleChoiceField(
        choices=[],
        widget=widgets.CheckboxSelectMultiple
    )

    def __init__(self,request,*args,**kwargs):
        super(ArticleForm,self).__init__(*args,**kwargs)
        blog_id=request.session['user_info']["bloginfo__bid"]
        self.fields['classification_id'].choices=models.Classification.objects.filter(blog_id=blog_id).values_list('nid','title')
        self.fields['tags'].choices=models.Tag.objects.filter(blog_id=blog_id).values_list('nid','title')



