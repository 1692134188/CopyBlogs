from django import forms
from django.forms import fields
from django.core.validators import RegexValidator
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from .base import BaseForm
from repository.models import UserInfo

class AccountInfoForm(BaseForm, forms.Form):
    username = fields.CharField(
        required=True,
        label='用户名：',
        min_length=6,
        max_length=16,
        error_messages={
            'required': '用户名不能为空',
            'min_length': '至少为6个字符',
            'max_length': '最多为16个字符',
        }
    )
    pwd = fields.CharField(
        label='密码：',
        required=True,
        min_length=8,
        max_length=32,
        validators=[
            RegexValidator(r'^(?=.*[0-9])(?=.*[a-zA-Z])(?=.*[!@#$\%\^\&\*\(\)])[0-9a-zA-Z!@#$\%\^\&\*\(\)]{8,32}$',
                           '密码过于简单（包含数字、字母的8位以上数字）')],
        error_messages={
            'required': '密码不能为空',
            'min_length': '至少为6个字符',
            'max_length': '最多为16个字符',
        }
    )
    confirmPwd = fields.CharField(
        label='确认密码：',
        required=True,
        min_length=8,
        max_length=32,
        error_messages={
            'required': '确认密码不能为空',
            'min_length': '至少为8个字符',
            'max_length': '最多为32个字符',
        }
    )
    email = fields.EmailField(
        label='邮箱：',
        required=True,
        min_length=6,
        max_length=18,
        error_messages={
            'required': '邮箱不能为空',
            'min_length': '至少为6个字符',
            'max_length': '最多为18个字符',
            'invalid': '邮箱格式不正确',
        }
    )

    checkCode = fields.CharField(
        error_messages={
            'required': '验证码不能为空',
        }
    )

    def clean(self):
        value_data = self.cleaned_data
        v1 = value_data.get("pwd")
        v2 = value_data.get("confirmPwd")
        if v1 != v2:
            self.add_error("confirmPwd", "密码不一致")
            raise ValidationError("密码不一致")
        return value_data

    def clean_checkCode(self):
        value_data = self.cleaned_data
        if self.request.session['CheckCode'].upper() != value_data.get("checkCode").upper():
            self.add_error("checkCode", "验证码错误")
            raise ValidationError(message='验证码错误', code='invalid')
        return value_data
    def clean_username(self):
        value =self.cleaned_data.get("username")
        if UserInfo.objects.filter(username=value):
            self.add_error("username", "用户名已存在")
        return value
    def clean_email(self):
        value = self.cleaned_data['email']
        if UserInfo.objects.filter(email=value):
            self.add_error("email", "邮箱已存在")
        return value

class LoginForm(BaseForm,forms.Form):
    username = fields.CharField(
        error_messages={
            'required': '用户名不能为空',
        }
    )
    pwd = fields.CharField(
        error_messages={
            'required': '密码不能为空',
        })
    checkCode = fields.CharField(
        error_messages={'required': '验证码不能为空.'}
    )
    rbm = fields.BooleanField(
        required=False,
    )
    def clean_checkCode(self):
        value_data = self.cleaned_data
        if self.request.session['CheckCode'].upper() != value_data.get("checkCode").upper():
            self.add_error("checkCode", "验证码错误")
            raise ValidationError(message='验证码错误', code='invalid')
        return value_data
    def clean(self):
        userName =self.cleaned_data.get("username")
        pwd =self.cleaned_data.get("pwd")
        # 可以使用Q查询 Q(username=userName) & Q(pwd=pwd)
        userInfo = UserInfo.objects.filter(username=userName,pwd=pwd)
        if userInfo:
            # 记录session，可用于修改headTar中的状态。
            self.request.session['user_info'] = userInfo.values(
                       'username').first()
            # 如果勾选了30免登陆，设置session的过期时间
            if self.cleaned_data.get('rbm'):
                self.request.session.set_expiry(60 * 60 * 24 * 7)
        else:
            self.add_error("username", "用户名不存在或密码错误")
            raise ValidationError(message='用户名不存在或密码错误', code='invalid')
        return self.cleaned_data